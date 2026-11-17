"""Validação automatizada da Issue #263: contato, solicitações de titulares e política de moderação.

Cobre os requisitos de:
1. Ciclo completo do canal de contato e verificação de acessos (#263).
2. Atendimento manual a pedidos de titulares LGPD e distinção de operações (#262).
3. Política de moderação: crítica acadêmica permitida vs. violação, revisão manual (#264).
4. Neutralidade estatística: moderação de texto NÃO altera notas da avaliação.
5. Votos de utilidade (#278) NÃO são denúncias e NÃO acionam moderação.
"""

import asyncio
from datetime import datetime, timedelta, timezone
import json
import os
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.auth import SESSION_COOKIE_NAME, obter_usuario_confirmado
from app.core.database import Base, get_db
from app.core.limite_atendimento import _janelas
from app.core.security import gerar_hash_token
from app.main import app
from app.models.avaliacao import Avaliacao
from app.models.comentario_versao import ComentarioVersao
from app.models.denuncia import Denuncia
from app.models.disciplina import Disciplina
from app.models.enums import Dificuldade, EstadoComentario, QualidadeMaterial
from app.models.professor import Professor
from app.models.sessao_usuario import SessaoUsuario
from app.models.turma import Turma
from app.models.unidade import Unidade
from app.models.usuario import Usuario
from app.models.voto_comentario import VotoComentario
from app.repositories import moderacao_repository
from app.repositories import denuncia_repository
from app.services import solicitacao_titular_service as canal_service


class PoliticaModeracaoETitularesTest(unittest.TestCase):
    def setUp(self):
        _janelas.clear()
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

        # Usuários e atores com permissões documentadas
        self.estudante = Usuario(
            id=uuid4(),
            nome="Estudante Titular",
            email="estudante@aluno.unb.br",
            password_hash="hash-teste",
            email_confirmado=True,
        )
        self.moderador = Usuario(
            id=uuid4(),
            nome="Moderador Equipe",
            email="moderador@aluno.unb.br",
            password_hash="hash-teste",
            email_confirmado=True,
            moderador=True,
        )
        self.atendente = Usuario(
            id=uuid4(),
            nome="Vinicius Atendente",
            email="vinicius@aluno.unb.br",
            password_hash="hash-teste",
            email_confirmado=True,
        )
        self.leitor = Usuario(
            id=uuid4(),
            nome="Nicolas Leitor",
            email="nicolas@aluno.unb.br",
            password_hash="hash-teste",
            email_confirmado=True,
        )

        self.db.add_all([self.estudante, self.moderador, self.atendente, self.leitor])

        # Catálogo institucional mínimo
        self.unidade = Unidade(codigo="CIC", nome="Departamento de Ciência da Computação")
        self.professor = Professor(nome="Professor Exemplo", departamento="CIC")
        self.disciplina = Disciplina(
            codigo="CIC0004", nome="Algoritmos e Programação", departamento="CIC"
        )
        self.db.add_all([self.unidade, self.professor, self.disciplina])
        self.db.flush()

        self.turma = Turma(
            disciplina=self.disciplina,
            unidade=self.unidade,
            codigo="01",
            semestre="2026.2",
            professores=[self.professor],
        )
        self.db.add(self.turma)

        # Sessões
        expiracao = datetime.now(timezone.utc) + timedelta(days=1)
        self.token_estudante = "token-estudante"
        self.token_moderador = "token-moderador"
        self.db.add_all(
            [
                SessaoUsuario(
                    usuario_id=self.estudante.id,
                    token_hash=gerar_hash_token(self.token_estudante),
                    expires_at=expiracao,
                ),
                SessaoUsuario(
                    usuario_id=self.moderador.id,
                    token_hash=gerar_hash_token(self.token_moderador),
                    expires_at=expiracao,
                ),
            ]
        )
        self.db.commit()

        # Configuração de injeção de dependência
        def override_db():
            with Session(self.engine) as session:
                yield session

        app.dependency_overrides[get_db] = override_db
        self.client = TestClient(app)

        # Patch nas flags do canal de titulares
        self.canal_flags = patch.multiple(
            canal_service.config,
            CANAL_TITULARES_ATIVO=True,
            CANAL_TITULARES_RETENCAO_APROVADA=True,
            CANAL_TITULARES_ATENDENTES=[str(self.atendente.id)],
            CANAL_TITULARES_LEITORES=[str(self.leitor.id)],
        )
        self.canal_flags.start()

    def tearDown(self):
        self.canal_flags.stop()
        app.dependency_overrides.clear()
        self.db.close()
        self.engine.dispose()

    async def _request(
        self, method: str, path: str, payload: dict | None = None, token: str | None = None
    ) -> tuple[int, dict]:
        url = urlsplit(path)
        path = url.path
        corpo = json.dumps(payload).encode("utf-8") if payload else b""
        headers = [
            (b"origin", b"http://localhost:3000"),
            (b"content-type", b"application/json"),
            (b"content-length", str(len(corpo)).encode("ascii")),
        ]
        if token is not None:
            headers.append((b"cookie", f"{SESSION_COOKIE_NAME}={token}".encode("ascii")))

        recebido = False

        async def receive():
            nonlocal recebido
            if recebido:
                return {"type": "http.disconnect"}
            recebido = True
            return {"type": "http.request", "body": corpo, "more_body": False}

        mensagens = []

        async def send(message):
            mensagens.append(message)

        await app(
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": method,
                "scheme": "http",
                "path": path,
                "raw_path": path.encode("ascii"),
                "query_string": url.query.encode("ascii"),
                "headers": headers,
                "client": ("127.0.0.1", 12345),
                "server": ("testserver", 80),
            },
            receive,
            send,
        )

        status = 500
        resposta_corpo = b""
        for msg in mensagens:
            if msg["type"] == "http.response.start":
                status = msg["status"]
            elif msg["type"] == "http.response.body":
                resposta_corpo += msg.get("body", b"")

        dados = json.loads(resposta_corpo.decode("utf-8")) if resposta_corpo else {}
        return status, dados

    def _criar_avaliacao(self, didatica=4, dificuldade=Dificuldade.MEDIO, recomenda=True):
        avaliacao = Avaliacao(
            usuario_id=self.estudante.id,
            professor_id=self.professor.id,
            disciplina_id=self.disciplina.id,
            didatica=didatica,
            dificuldade=dificuldade,
            chamada=True,
            disponibiliza_material=True,
            qualidade_material=QualidadeMaterial.BOM,
            recomenda=recomenda,
        )
        self.db.add(avaliacao)
        self.db.commit()
        self.db.refresh(avaliacao)
        return avaliacao

    # -------------------------------------------------------------------------
    # 1. Moderação de texto NÃO altera notas estruturadas da avaliação
    # -------------------------------------------------------------------------
    def test_moderacao_texto_nao_altera_notas_da_avaliacao(self):
        """Garante que aprovar, rejeitar, remover ou suspender texto não altera notas."""
        avaliacao = self._criar_avaliacao(didatica=4, dificuldade=Dificuldade.MEDIO, recomenda=True)
        versao = ComentarioVersao(
            avaliacao_id=avaliacao.id,
            texto="Comentário para teste de estabilidade de notas.",
            estado=EstadoComentario.PENDENTE,
        )
        self.db.add(versao)
        self.db.commit()
        self.db.refresh(versao)

        # 1. Aprovação não altera critérios
        code, _ = asyncio.run(
            self._request(
                "POST",
                f"/api/moderacao/comentarios/{versao.id}/acoes",
                {"acao": "APROVAR", "motivo": "Texto respeitoso"},
                self.token_moderador,
            )
        )
        self.assertEqual(code, 200)
        self.db.expire_all()
        avaliacao_banco = self.db.get(Avaliacao, avaliacao.id)
        self.assertEqual(avaliacao_banco.didatica, 4)
        self.assertEqual(avaliacao_banco.dificuldade, Dificuldade.MEDIO)
        self.assertTrue(avaliacao_banco.recomenda)

        # 2. Rejeição de nova versão substituta não altera critérios da avaliação
        versao_substituta = ComentarioVersao(
            avaliacao_id=avaliacao.id,
            texto="Substituto que será rejeitado.",
            estado=EstadoComentario.PENDENTE,
        )
        self.db.add(versao_substituta)
        self.db.commit()
        self.db.refresh(versao_substituta)

        code, _ = asyncio.run(
            self._request(
                "POST",
                f"/api/moderacao/comentarios/{versao_substituta.id}/acoes",
                {"acao": "REJEITAR", "motivo": "Rejeição justificada"},
                self.token_moderador,
            )
        )
        self.assertEqual(code, 200)
        self.db.expire_all()
        avaliacao_banco = self.db.get(Avaliacao, avaliacao.id)
        self.assertEqual(avaliacao_banco.didatica, 4)
        self.assertEqual(avaliacao_banco.dificuldade, Dificuldade.MEDIO)

        # 3. Remoção da versão publicada denunciada preserva os 5 critérios
        from app.models.denuncia import Denuncia
        from app.models.enums import MotivoDenuncia

        denuncia = Denuncia(
            comentario_versao_id=versao.id,
            motivo=MotivoDenuncia.OFENSA_PESSOAL,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(denuncia)
        self.db.commit()

        code, _ = asyncio.run(
            self._request(
                "POST",
                f"/api/moderacao/comentarios/{versao.id}/acoes",
                {"acao": "REMOVER", "motivo": "Remoção humana"},
                self.token_moderador,
            )
        )
        self.assertEqual(code, 200)
        self.db.expire_all()
        avaliacao_banco = self.db.get(Avaliacao, avaliacao.id)
        self.assertEqual(avaliacao_banco.didatica, 4)
        self.assertEqual(avaliacao_banco.chamada, True)
        self.assertEqual(avaliacao_banco.disponibiliza_material, True)

    # -------------------------------------------------------------------------
    # 2. Votos de utilidade (#278) NÃO são denúncias e NÃO acionam moderação
    # -------------------------------------------------------------------------
    def test_votos_utilidade_nao_sao_denuncias_e_nao_acionam_moderacao(self):
        """Votos de utilidade não criam denúncias, não contam no limiar e não entram na fila."""
        avaliacao = self._criar_avaliacao()
        versao = ComentarioVersao(
            avaliacao_id=avaliacao.id,
            texto="Comentário publicado para testar isolamento de votos.",
            estado=EstadoComentario.PUBLICADO,
        )
        self.db.add(versao)
        self.db.commit()

        # O comentário publicado SEM denúncias não aparece na fila de moderação
        fila = moderacao_repository.listar_fila(self.db)
        self.assertNotIn(versao.id, [v.id for v in fila])

        # Votos reais da #278 não criam denúncias nem entram no limiar de suspensão.
        votantes = [
            Usuario(
                id=uuid4(),
                nome=f"Votante sintético {i}",
                email=f"votante-{i}@aluno.unb.br",
                password_hash="hash-teste",
                email_confirmado=True,
            )
            for i in range(50)
        ]
        self.db.add_all(votantes)
        self.db.flush()
        self.db.add_all(
            [
                VotoComentario(
                    comentario_versao_id=versao.id, usuario_id=votante.id, voto="NAO_UTIL"
                )
                for votante in votantes
            ]
        )
        self.db.commit()

        denuncias = self.db.scalars(
            select(Denuncia).where(Denuncia.comentario_versao_id == versao.id)
        ).all()
        self.assertEqual(len(denuncias), 0)
        self.assertEqual(denuncia_repository.contar_contas(self.db, versao.id), 0)
        fila = moderacao_repository.listar_fila(self.db)
        self.assertNotIn(versao.id, [v.id for v in fila])

        # O gatilho de suspensão (50 contas) avalia estritamente denúncias de contas autenticadas
        # Garantir que contagem_denuncias retorna 0 e o comentário permanece PUBLICADO
        self.assertEqual(versao.estado, EstadoComentario.PUBLICADO)

    # -------------------------------------------------------------------------
    # 3. Caso Sintético 1: Pedido de acesso/correção de titular (LGPD - #262)
    # -------------------------------------------------------------------------
    def test_caso_sintetico_1_pedido_acesso_correcao_lgpd(self):
        """Solicitante abre pedido DIREITO_LGPD para correção cadastral; atendimento responde."""
        # 1. Envio sem login estudantil
        payload = {
            "categoria": "DIREITO_LGPD",
            "alvo": f"conta-sintetica:{self.estudante.id}",
            "descricao": "Solicito retificação do meu nome social no cadastro institucional.",
            "evidencia": "Caso fictício; confirmação proporcional simulada, sem documento civil.",
        }
        res_envio = self.client.post("/api/solicitacoes", json=payload)
        self.assertEqual(res_envio.status_code, 201)
        recibo = res_envio.json()
        protocolo = recibo["protocolo"]
        chave = recibo["chave"]

        # 2. Atendente autorizado analisa e emite resposta motivada proporcional
        path_eventos = f"/api/atendimento/{protocolo}/eventos"
        app.dependency_overrides[obter_usuario_confirmado] = lambda: self.atendente

        # Exercício manual com identidade e conta inteiramente sintéticas.
        self.client.post(
            path_eventos,
            json={
                "tipo": "TRIAGEM",
                "texto": "Exercício sintético: confirmação proporcional registrada; sem coletar documento civil.",
            },
        )

        self.estudante.nome = "Pessoa Titular Sintética"
        self.db.commit()
        self.client.post(
            path_eventos,
            json={
                "tipo": "PROVIDENCIA",
                "texto": "Exercício sintético: correção do nome aplicada ao registro de teste.",
            },
        )

        # Registro de resposta ao titular
        res_atendimento = self.client.post(
            path_eventos,
            json={
                "tipo": "RESPOSTA",
                "texto": "Pedido de acesso e correção atendido no exercício: o nome sintético foi atualizado.",
            },
        )
        self.assertEqual(res_atendimento.status_code, 200)

        # 3. Solicitante consulta com protocolo e chave secreta
        res_consulta = self.client.post(
            "/api/solicitacoes/consultar", json={"protocolo": protocolo, "chave": chave}
        )
        self.assertEqual(res_consulta.status_code, 200)
        consulta = res_consulta.json()
        self.assertEqual(consulta["categoria"], "DIREITO_LGPD")
        self.assertEqual(self.estudante.nome, "Pessoa Titular Sintética")

        # Histórico público só contém RESPOSTA, sem vazar TRIAGEM ou identificador do operador
        tipos_historico = [e["tipo"] for e in consulta["historico"]]
        self.assertIn("RESPOSTA", tipos_historico)
        self.assertNotIn("TRIAGEM", tipos_historico)
        self.assertNotIn("PROVIDENCIA", tipos_historico)
        for evento in consulta["historico"]:
            self.assertNotIn("responsavel_id", evento)

    # -------------------------------------------------------------------------
    # 4. Caso Sintético 2: Crítica acadêmica legítima mantida (#264)
    # -------------------------------------------------------------------------
    def test_caso_sintetico_2_critica_academica_legitima_mantida(self):
        """Crítica acadêmica severa sobre didática e ritmo não é rejeitada."""
        avaliacao = self._criar_avaliacao(didatica=2, dificuldade=Dificuldade.DIFICIL)
        texto_critica = (
            "As aulas foram excessivamente teóricas e sem exemplos práticos. "
            "O ritmo foi acelerado e o material recomendado não cobriu a prova."
        )
        versao = ComentarioVersao(
            avaliacao_id=avaliacao.id,
            texto=texto_critica,
            estado=EstadoComentario.PENDENTE,
        )
        self.db.add(versao)
        self.db.commit()

        # Moderador humano avalia e APROVA a crítica acadêmica legítima
        code, resultado = asyncio.run(
            self._request(
                "POST",
                f"/api/moderacao/comentarios/{versao.id}/acoes",
                {
                    "acao": "APROVAR",
                    "motivo": "Crítica acadêmica legítima sobre metodologia, sem ofensas.",
                },
                self.token_moderador,
            )
        )
        self.assertEqual(code, 200)
        self.assertEqual(resultado["estado_posterior"], "PUBLICADO")
        self.db.expire_all()
        self.assertEqual(versao.estado, EstadoComentario.PUBLICADO)

    # -------------------------------------------------------------------------
    # 5. Caso Sintético 3: Violação de moderação (ofensa/ataque pessoal) (#264)
    # -------------------------------------------------------------------------
    def test_caso_sintetico_3_violacao_moderacao_rejeitada(self):
        """Ataque pessoal e difamação são rejeitados com descarte do texto."""
        avaliacao = self._criar_avaliacao()
        texto_ofensivo = "Professor incompetente, corrupto e desprezível. Não merece lecionar."
        versao = ComentarioVersao(
            avaliacao_id=avaliacao.id,
            texto=texto_ofensivo,
            estado=EstadoComentario.PENDENTE,
        )
        self.db.add(versao)
        self.db.commit()

        # Moderador REJEITA a violação
        code, resultado = asyncio.run(
            self._request(
                "POST",
                f"/api/moderacao/comentarios/{versao.id}/acoes",
                {"acao": "REJEITAR", "motivo": "Ataque pessoal e ofensa à honra."},
                self.token_moderador,
            )
        )
        self.assertEqual(code, 200)
        self.assertEqual(resultado["estado_posterior"], "REJEITADO")
        self.db.expire_all()
        self.assertEqual(versao.estado, EstadoComentario.REJEITADO)
        # Texto é imediatamente descartado na rejeição
        self.assertIsNone(versao.texto)
        # Critérios da avaliação continuam íntegros
        self.assertEqual(avaliacao.didatica, 4)

    # -------------------------------------------------------------------------
    # 6. Caso Sintético 4: Revisão manual de decisão via protocolo e complemento (#264)
    # -------------------------------------------------------------------------
    def test_caso_sintetico_4_revisao_manual_de_decisao_via_complemento(self):
        """Autor contesta decisão de moderação via canal de contato com protocolo e chave."""
        # 1. Criação de solicitação referente à contestação
        payload = {
            "categoria": "COMENTARIO_ILICITO",
            "alvo": "comentario-versao-12345",
            "descricao": "Meu comentário foi suspenso por denúncias, mas expressa apenas crítica sobre a prova.",
            "evidencia": "Transcrição do comentário e contexto da turma 2026.2.",
        }
        res_envio = self.client.post("/api/solicitacoes", json=payload)
        self.assertEqual(res_envio.status_code, 201)
        recibo = res_envio.json()
        protocolo = recibo["protocolo"]
        chave = recibo["chave"]

        # 2. Solicitante envia complemento pedindo revisão manual motivada
        res_complemento = self.client.post(
            "/api/solicitacoes/complementos",
            json={
                "protocolo": protocolo,
                "chave": chave,
                "texto": "Solicito revisão manual formal: a expressão utilizada é jargão acadêmico, não ofensa.",
            },
        )
        self.assertEqual(res_complemento.status_code, 200)
        historico_apos_complemento = res_complemento.json()["historico"]
        self.assertEqual(historico_apos_complemento[-1]["tipo"], "COMPLEMENTO")

        # 3. Equipe atende e registra resposta
        app.dependency_overrides[obter_usuario_confirmado] = lambda: self.atendente
        res_atender = self.client.post(
            f"/api/atendimento/{protocolo}/eventos",
            json={
                "tipo": "RESPOSTA",
                "texto": "Revisão concluída por moderador designado: o texto foi reavaliado e restaurado.",
            },
        )
        self.assertEqual(res_atender.status_code, 200)

        # 4. Solicitante consulta a decisão final da revisão
        res_final = self.client.post(
            "/api/solicitacoes/consultar", json={"protocolo": protocolo, "chave": chave}
        )
        consulta_final = res_final.json()
        self.assertEqual(consulta_final["historico"][-1]["tipo"], "RESPOSTA")
        self.assertIn("Revisão concluída", consulta_final["historico"][-1]["texto"])

    # -------------------------------------------------------------------------
    # 7. Ciclo completo do canal de contato e controle de acessos (#263)
    # -------------------------------------------------------------------------
    def test_controle_de_acessos_leitor_vs_atendente(self):
        """Leitor (Nicolas/Tiago) visualiza mas é impedido de responder; Atendente responde."""
        r = self.client.post(
            "/api/solicitacoes",
            json={
                "categoria": "OUTRA",
                "alvo": "alvo-teste",
                "descricao": "Solicitação para verificação de permissões.",
                "evidencia": "Evidência sintética.",
            },
        ).json()
        protocolo = r["protocolo"]

        # Leitor: GET atendimento = 200, POST evento = 403
        app.dependency_overrides[obter_usuario_confirmado] = lambda: self.leitor
        self.assertEqual(self.client.get("/api/atendimento").status_code, 200)
        self.assertEqual(self.client.get(f"/api/atendimento/{protocolo}").status_code, 200)
        res_bloqueado = self.client.post(
            f"/api/atendimento/{protocolo}/eventos",
            json={"tipo": "RESPOSTA", "texto": "Tentativa não autorizada do leitor"},
        )
        self.assertEqual(res_bloqueado.status_code, 403)

        # Atendente: POST evento = 200
        app.dependency_overrides[obter_usuario_confirmado] = lambda: self.atendente
        res_autorizado = self.client.post(
            f"/api/atendimento/{protocolo}/eventos",
            json={"tipo": "RESPOSTA", "texto": "Resposta autorizada do atendente"},
        )
        self.assertEqual(res_autorizado.status_code, 200)
