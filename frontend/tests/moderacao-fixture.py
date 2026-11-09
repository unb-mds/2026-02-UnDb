"""Dados sintéticos exclusivos do teste da interface #162; não modifica o backend.

Use UNDB_INTEGRATION_TEST=1 e banco PostgreSQL descartável moderacao_interface_test,
com migrations aplicadas. Execute preparar, verificar e limpar com o mesmo arquivo.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
sys.path.insert(0, str(Path.cwd()))

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.core.database import engine
from app.core.security import gerar_hash_token
from app.models import (Agradecimento, Avaliacao, ComentarioVersao, DecisaoModeracao,
                        Denuncia, Disciplina, Professor, SessaoUsuario, Usuario)
from app.models.enums import EstadoComentario, MotivoDenuncia


def preparar(arquivo):
    marca = uuid4().hex
    resultado = {"casos": [], "usuarios": []}
    with Session(engine) as db:
        professor = Professor(nome="Professor sintético de moderação", departamento="CIC")
        disciplina = Disciplina(codigo=marca[:18], nome="Disciplina sintética", departamento="CIC")
        db.add_all((professor, disciplina))
        usuarios = []
        for i in range(9):
            usuario = Usuario(nome="Autor real de teste" if i >= 3 else "Conta sintética de teste",
                              email=f"{marca}{i}@aluno.unb.br", password_hash="fixture-sem-login-por-senha",
                              email_confirmado=i != 2, moderador=i == 0)
            db.add(usuario)
            db.flush()
            token = uuid4().hex
            db.add(SessaoUsuario(usuario_id=usuario.id, token_hash=gerar_hash_token(token),
                                expires_at=datetime.now(timezone.utc) + timedelta(days=1)))
            usuarios.append(usuario)
            resultado["usuarios"].append(str(usuario.id))
            if i < 3:
                resultado[("moderador", "comum", "naoConfirmado")[i]] = token
        db.flush()

        def versao(usuario, estado, texto):
            avaliacao = Avaliacao(usuario_id=usuario.id, professor_id=professor.id, disciplina_id=disciplina.id,
                                  didatica=4, dificuldade="MEDIO", chamada=True,
                                  disponibiliza_material=False, qualidade_material=None, recomenda=True)
            db.add(avaliacao)
            db.flush()
            comentario = ComentarioVersao(avaliacao_id=avaliacao.id, texto=texto, estado=estado)
            db.add(comentario)
            db.flush()
            return comentario

        configuracoes = [("PENDENTE", "APROVAR", "PUBLICADO"), ("PENDENTE", "REJEITAR", "REJEITADO"),
                         ("PUBLICADO", "MANTER", "PUBLICADO"), ("PUBLICADO", "REMOVER", "REMOVIDO"),
                         ("SUSPENSO", "RESTAURAR", "PUBLICADO"), ("SUSPENSO", "REMOVER", "REMOVIDO")]
        for i, (estado, acao, destino) in enumerate(configuracoes):
            comentario = versao(usuarios[i + 3], EstadoComentario(estado), f"Conteúdo sintético {i}: crítica acadêmica para revisão.")
            resultado["casos"].append({"id": str(comentario.id), "acao": acao, "destino": destino})
            if i == 0:
                anterior = ComentarioVersao(avaliacao_id=comentario.avaliacao_id, texto="Texto anterior suspenso sintético",
                                             estado=EstadoComentario.SUSPENSO)
                db.add(anterior)
                db.flush()
                comentario.substitui_id = anterior.id
                resultado["anterior"] = str(anterior.id)
            if estado != "PENDENTE":
                db.add_all((
                    Denuncia(comentario_versao_id=comentario.id, denunciante_id=usuarios[1].id,
                              motivo=MotivoDenuncia.SPAM, created_at=datetime.now(timezone.utc)),
                    Denuncia(comentario_versao_id=comentario.id, denunciante_id=None,
                              motivo=MotivoDenuncia.SPAM, created_at=datetime.now(timezone.utc)),
                ))
        proprio = versao(usuarios[0], EstadoComentario.PENDENTE, "Caso próprio do moderador sintético")
        denunciado = versao(usuarios[1], EstadoComentario.PUBLICADO, "Caso com denúncia do moderador sintético")
        db.add(Denuncia(comentario_versao_id=denunciado.id, denunciante_id=usuarios[0].id,
                       motivo=MotivoDenuncia.SPAM, created_at=datetime.now(timezone.utc)))
        resultado.update(proprio=str(proprio.id), denunciaPropria=str(denunciado.id),
                         professor=str(professor.id), disciplina=str(disciplina.id))
        db.commit()
    arquivo.write_text(json.dumps(resultado, ensure_ascii=False), encoding="utf8")
    print("Dados sintéticos criados; tokens somente no arquivo temporário do teste.")


def verificar(arquivo):
    dados = json.loads(arquivo.read_text(encoding="utf8"))
    with Session(engine) as db:
        for caso in dados["casos"]:
            versao = db.get(ComentarioVersao, UUID(caso["id"]))
            assert versao.estado.value == caso["destino"]
            assert versao.avaliacao.didatica == 4
            assert db.scalar(select(DecisaoModeracao.id).where(DecisaoModeracao.comentario_versao_id == versao.id)) is not None
            assert db.scalar(select(Denuncia.id).where(Denuncia.comentario_versao_id == versao.id)) is None
            if caso["destino"] == "REJEITADO":
                assert versao.texto is None
        anterior = db.get(ComentarioVersao, UUID(dados["anterior"]))
        assert anterior.estado == EstadoComentario.SUBSTITUIDO and anterior.texto is None
        assert db.get(ComentarioVersao, UUID(dados["proprio"])).estado == EstadoComentario.PENDENTE
        assert db.get(ComentarioVersao, UUID(dados["denunciaPropria"])).estado == EstadoComentario.PUBLICADO
    print("PostgreSQL conferido: seis decisões, encerramentos, critérios preservados e impedimentos sem alteração.")


def limpar(arquivo):
    dados = json.loads(arquivo.read_text(encoding="utf8"))
    with Session(engine) as db:
        avaliacoes = select(Avaliacao.id).where(Avaliacao.professor_id == UUID(dados["professor"]))
        versoes = select(ComentarioVersao.id).where(ComentarioVersao.avaliacao_id.in_(avaliacoes))
        for entidade in (Agradecimento, Denuncia, DecisaoModeracao):
            db.execute(delete(entidade).where(entidade.comentario_versao_id.in_(versoes)))
        db.execute(update(ComentarioVersao).where(ComentarioVersao.id.in_(versoes)).values(substitui_id=None))
        db.execute(delete(ComentarioVersao).where(ComentarioVersao.id.in_(versoes)))
        db.execute(delete(Avaliacao).where(Avaliacao.id.in_(avaliacoes)))
        db.execute(delete(SessaoUsuario).where(SessaoUsuario.usuario_id.in_([UUID(v) for v in dados["usuarios"]])))
        db.execute(delete(Usuario).where(Usuario.id.in_([UUID(v) for v in dados["usuarios"]])))
        db.execute(delete(Professor).where(Professor.id == UUID(dados["professor"])))
        db.execute(delete(Disciplina).where(Disciplina.id == UUID(dados["disciplina"])))
        db.commit()
    arquivo.unlink()
    print("Somente as fixtures desta execução foram removidas.")


if __name__ == "__main__":
    assert os.environ.get("UNDB_INTEGRATION_TEST") == "1", "Exige autorização explícita de ambiente de teste."
    assert engine.dialect.name == "postgresql" and engine.url.database == "moderacao_interface_test", "Use o banco descartável moderacao_interface_test."
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("acao", choices=("preparar", "verificar", "limpar"))
    parser.add_argument("arquivo", type=Path)
    args = parser.parse_args()
    {"preparar": preparar, "verificar": verificar, "limpar": limpar}[args.acao](args.arquivo)
