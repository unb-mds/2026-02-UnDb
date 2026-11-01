"""Explicit RF20–22 verification: real HTTP, migrated PostgreSQL and concurrent writes.

Run: python -m tests.integration_moderacao. Never creates schema; removes only
fixtures identified by its generated professor UUID. Use a disposable test database.
"""
import json
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import UUID, uuid4

from sqlalchemy import delete, select, update, func
from sqlalchemy.orm import Session

from app.core.database import engine
from app.core.security import gerar_hash_token
from app.models import (Agradecimento, Avaliacao, ComentarioVersao, DecisaoModeracao,
                        Denuncia, Disciplina, Professor, SessaoUsuario, Turma, Unidade, Usuario)
from app.models.turma import turmas_professores


def main():
    if engine.dialect.name != "postgresql":
        raise RuntimeError("este teste exige PostgreSQL migrado e descartavel")
    marca = uuid4().hex
    contas = []
    with Session(engine) as db:
        professor = Professor(nome=f"Teste moderacao {marca}", departamento="CIC")
        disciplina = Disciplina(codigo=marca[:18], nome="Teste moderacao", departamento="CIC")
        unidade = Unidade(codigo=marca[:18], nome="Teste moderacao")
        turma = Turma(disciplina=disciplina, unidade=unidade, codigo="01", semestre="2026.2", professores=[professor])
        db.add(turma)
        for i in range(55):
            conta = Usuario(nome=f"Conta {i}", email=f"{marca}{i}@aluno.unb.br", password_hash="fixture",
                            email_confirmado=i >= 51, moderador=i >= 53)
            db.add(conta)
            db.flush()
            token = f"{marca}-{i}"
            db.add(SessaoUsuario(usuario_id=conta.id, token_hash=gerar_hash_token(token),
                                expires_at=datetime.now(timezone.utc) + timedelta(days=1)))
            contas.append((conta.id, token))
        db.commit()
        professor_id, disciplina_id, unidade_id, turma_id = professor.id, disciplina.id, unidade.id, turma.id

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        porta = sock.getsockname()[1]
    servidor = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(porta)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

    def http(method, path, payload=None, conta=None):
        headers = {"Content-Type": "application/json"}
        if conta is not None:
            headers["Cookie"] = f"undb_session={contas[conta][1]}"
        request = Request(f"http://127.0.0.1:{porta}{path}", method=method, headers=headers,
                          data=json.dumps(payload).encode() if payload is not None else None)
        try:
            resposta = urlopen(request, timeout=30)
        except HTTPError as erro:
            resposta = erro
        with resposta:
            corpo = resposta.read()
            if path.endswith("/exibido") and resposta.status == 204:
                assert "undb_session=" in resposta.headers.get("Set-Cookie", ""), "Cookie de sessao deve acompanhar a renovacao no servidor"
            return resposta.status, json.loads(corpo) if corpo else None

    def esperar(method, path, status, payload=None, conta=None):
        resultado = http(method, path, payload, conta)
        assert resultado[0] == status, (method, path, resultado)
        return resultado[1]

    def agir(versao_id, acao, moderador=53):
        return http("POST", f"/api/moderacao/comentarios/{versao_id}/acoes",
                    {"acao": acao, "motivo": "Analise humana de fixture"}, moderador)

    def denunciar(versao_id, conta=None):
        return http("POST", f"/api/comentarios/{versao_id}/denuncias", {"motivo": "SPAM"}, conta)

    def enviar_texto(conta, texto):
        esperar("POST", "/api/avaliacoes", 200, {
            "professor_id": str(professor_id), "disciplina_id": str(disciplina_id),
            "didatica": 4, "dificuldade": "MEDIO", "chamada": True,
            "disponibiliza_material": False, "qualidade_material": None,
            "recomenda": True, "comentario": texto,
        }, conta)
        versoes = esperar("GET", "/api/comentarios/meu", 200, conta=conta)
        return next(v["id"] for v in versoes if v["estado"] == "PENDENTE")

    try:
        for _ in range(100):
            try:
                if http("GET", "/health")[0] == 200:
                    break
            except URLError:
                time.sleep(0.1)
        else:
            raise RuntimeError("API nao iniciou")

        versao = enviar_texto(51, "Critica academica de fixture")
        assert denunciar(versao)[0] == 404
        assert agir(versao, "APROVAR")[0] == 200
        assert agir(versao, "APROVAR")[0] == 409
        outra = enviar_texto(52, "Outro texto de fixture")
        assert agir(outra, "APROVAR")[0] == 200
        for _ in range(55):
            assert denunciar(versao)[0] == 201
        with ThreadPoolExecutor(max_workers=8) as pool:
            repetidas = list(pool.map(lambda _: denunciar(versao, 0)[0], range(12)))
        assert repetidas.count(201) == 1 and repetidas.count(409) == 11, repetidas
        with ThreadPoolExecutor(max_workers=8) as pool:
            assert all(code == 201 for code in pool.map(lambda i: denunciar(versao, i)[0], range(1, 49)))
        assert denunciar(outra, 49)[0] == 201
        detalhe = esperar("GET", f"/api/moderacao/comentarios/{versao}", 200, conta=53)
        assert detalhe["estado"] == "PUBLICADO"
        # Two simultaneous candidates for the 50th account cannot count as 51.
        limiar = Barrier(2)
        def atingir_limiar(conta):
            limiar.wait(timeout=10)
            return denunciar(versao, conta)[0]
        with ThreadPoolExecutor(max_workers=2) as pool:
            resultados = list(pool.map(atingir_limiar, (49, 50)))
        assert sorted(resultados) == [201, 404], resultados
        assert denunciar(versao, 50)[0] == 404
        esperar("GET", f"/api/moderacao/comentarios/{versao}/denuncias", 401)
        esperar("GET", f"/api/moderacao/comentarios/{versao}/denuncias", 403, conta=51)
        registros = esperar("GET", f"/api/moderacao/comentarios/{versao}/denuncias", 200, conta=53)
        assert registros["contas_distintas"] == 50 and registros["total_visitantes"] == 55
        with Session(engine) as db:
            assert db.scalar(select(func.count(Agradecimento.id)).where(Agradecimento.comentario_versao_id == UUID(versao))) == 50
        publicos = esperar("GET", f"/api/professores/{professor_id}/disciplinas/{disciplina_id}/comentarios", 200)
        assert all(item["id"] != versao and set(item) == {"id", "texto", "created_at"} for item in publicos)

        # Rejecting an edit preserves the suspended original and all its reports.
        substituto = enviar_texto(51, "Substituto pendente")
        assert agir(substituto, "REJEITAR")[0] == 200
        assert esperar("GET", f"/api/moderacao/comentarios/{versao}", 200, conta=53)["estado"] == "SUSPENSO"
        assert agir(versao, "RESTAURAR")[0] == 200
        assert esperar("GET", f"/api/moderacao/comentarios/{versao}/denuncias", 200, conta=53)["contas_distintas"] == 0
        mensagens = esperar("GET", "/api/agradecimentos", 200, conta=0)
        assert len(mensagens) == 1 and set(mensagens[0]) == {"id", "mensagem"}
        esperar("POST", f"/api/agradecimentos/{mensagens[0]['id']}/exibido", 404, conta=1)
        esperar("POST", f"/api/agradecimentos/{mensagens[0]['id']}/exibido", 204, conta=0)
        assert esperar("GET", "/api/agradecimentos", 200, conta=0) == []
        assert denunciar(versao, 0)[0] == 201
        assert agir(versao, "REMOVER")[0] == 200
        assert agir(versao, "RESTAURAR")[0] == 409
        assert len(esperar("GET", "/api/agradecimentos", 200, conta=0)) == 1

        # Simulate elapsed retention without waiting or changing the product clock.
        with Session(engine) as db:
            antiga = db.get(ComentarioVersao, UUID(versao))
            assert antiga.descartar_em - antiga.updated_at == timedelta(days=7)
            antiga.descartar_em = datetime.now(timezone.utc) - timedelta(seconds=1)
            db.execute(update(DecisaoModeracao).where(DecisaoModeracao.comentario_versao_id == UUID(versao))
                       .values(descartar_em=datetime.now(timezone.utc) - timedelta(seconds=1)))
            db.commit()
        assert esperar("GET", f"/api/moderacao/comentarios/{versao}", 200, conta=53)["texto"] is None
        assert esperar("GET", f"/api/moderacao/comentarios/{versao}/decisoes", 200, conta=53) == []

        # Conflict of interest and concurrent report/removal on the other version.
        assert denunciar(outra, 53)[0] == 201
        assert agir(outra, "MANTER")[0] == 403
        assert agir(outra, "MANTER", 54)[0] == 200
        assert denunciar(outra, 0)[0] == 201
        barreira = Barrier(2)
        def remover():
            barreira.wait(timeout=10)
            return agir(outra, "REMOVER", 54)[0]
        def relatar():
            barreira.wait(timeout=10)
            return denunciar(outra, 1)[0]
        with ThreadPoolExecutor(max_workers=2) as pool:
            remocao = pool.submit(remover)
            relato = pool.submit(relatar)
            assert remocao.result() == 200
            assert relato.result() in (201, 404)
        assert esperar("GET", f"/api/moderacao/comentarios/{outra}/denuncias", 200, conta=54)["contas_distintas"] == 0

        # Approval of a new version discards the old removed text without transferring reports.
        nova = enviar_texto(51, "Nova versao aprovada")
        assert agir(nova, "APROVAR")[0] == 200
        assert denunciar(versao, 2)[0] == 404
        assert denunciar(nova, 2)[0] == 201
        esperar("PATCH", f"/api/comentarios/{nova}/retirar", 200, conta=51)
        assert esperar("GET", f"/api/moderacao/comentarios/{nova}/denuncias", 200, conta=54)["contas_distintas"] == 0
        with Session(engine) as db:
            assert db.scalar(select(Avaliacao).where(Avaliacao.usuario_id == contas[51][0])).didatica == 4
        # Only one competing human decision can change a pending version.
        pendente = enviar_texto(51, "Revisao concorrente")
        revisao = Barrier(2)
        def revisar(acao):
            revisao.wait(timeout=10)
            return agir(pendente, acao)[0]
        with ThreadPoolExecutor(max_workers=2) as pool:
            resultados = list(pool.map(revisar, ("APROVAR", "REJEITAR")))
        assert sorted(resultados) == [200, 409], resultados
        assert len(esperar("GET", f"/api/moderacao/comentarios/{pendente}/decisoes", 200, conta=54)) == 1
        print("RF20–22: HTTP real/PostgreSQL, 49/50, concorrencia, privacidade, acoes, retencao e agradecimentos aprovados")
    finally:
        servidor.terminate()
        servidor.wait(timeout=15)
        with Session(engine) as db:
            versoes = select(ComentarioVersao.id).join(Avaliacao).where(Avaliacao.professor_id == professor_id)
            for entidade in (Agradecimento, Denuncia, DecisaoModeracao):
                db.execute(delete(entidade).where(entidade.comentario_versao_id.in_(versoes)))
            db.execute(update(ComentarioVersao).where(ComentarioVersao.id.in_(versoes)).values(substitui_id=None))
            db.execute(delete(ComentarioVersao).where(ComentarioVersao.id.in_(versoes)))
            db.execute(delete(Avaliacao).where(Avaliacao.professor_id == professor_id))
            db.execute(delete(SessaoUsuario).where(SessaoUsuario.usuario_id.in_([c[0] for c in contas])))
            db.execute(delete(Usuario).where(Usuario.id.in_([c[0] for c in contas])))
            db.execute(delete(turmas_professores).where(turmas_professores.c.turma_id == turma_id))
            db.execute(delete(Turma).where(Turma.id == turma_id))
            db.execute(delete(Unidade).where(Unidade.id == unidade_id))
            db.execute(delete(Professor).where(Professor.id == professor_id))
            db.execute(delete(Disciplina).where(Disciplina.id == disciplina_id))
            db.commit()


if __name__ == "__main__":
    main()
