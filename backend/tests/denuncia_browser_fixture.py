"""Synthetic fixtures for denuncia-browser.mjs; use only a disposable PostgreSQL.

UNDB_INTEGRATION_TEST=1 python -m tests.denuncia_browser_fixture > fixture.json
The caller owns the disposable database/container lifecycle. No production data is read.
"""
import json
import os
from uuid import uuid4

from sqlalchemy.orm import Session
from app.core.database import engine
from app.core.security import gerar_hash_senha
from app.models import Avaliacao, ComentarioVersao, Disciplina, Professor, Turma, Unidade, Usuario
from app.models.enums import Dificuldade, EstadoComentario


def main():
    if os.environ.get("UNDB_INTEGRATION_TEST") != "1" or engine.dialect.name != "postgresql":
        raise RuntimeError("Exige UNDB_INTEGRATION_TEST=1 e PostgreSQL descartavel")
    marca = uuid4().hex
    senha = f"Teste-{marca}!"
    with Session(engine) as db:
        contas = []
        for papel in ("autor", "denunciante", "moderador"):
            conta = Usuario(nome=f"Fixture {papel}", email=f"{papel}-{marca}@aluno.unb.br",
                            password_hash=gerar_hash_senha(senha), email_confirmado=papel != "denunciante",
                            moderador=papel == "moderador")
            db.add(conta)
            contas.append(conta)
        professor = Professor(nome="Prof. Teste Denúncia", departamento="CIC")
        disciplina = Disciplina(codigo=marca[:18], nome="Fixture denúncia", departamento="CIC")
        unidade = Unidade(codigo=marca[:18], nome="Fixture denúncia")
        db.add(Turma(disciplina=disciplina, unidade=unidade, codigo="01", semestre="2026.2", professores=[professor]))
        db.flush()
        avaliacao = Avaliacao(usuario_id=contas[0].id, professor_id=professor.id, disciplina_id=disciplina.id,
                              didatica=4, dificuldade=Dificuldade.MEDIO, chamada=False,
                              disponibiliza_material=False, qualidade_material=None, recomenda=True)
        db.add(avaliacao)
        db.flush()
        versao = ComentarioVersao(avaliacao_id=avaliacao.id, estado=EstadoComentario.PUBLICADO,
                                  texto="Comentário publicado para verificação de denúncia RF21.")
        db.add(versao)
        db.commit()
        print(json.dumps({"professorId": str(professor.id), "disciplinaId": str(disciplina.id),
                          "versaoId": str(versao.id), "denunciante": {"email": contas[1].email, "senha": senha},
                          "moderador": {"email": contas[2].email, "senha": senha},
                          "outraConta": {"email": contas[0].email, "senha": senha}}))


if __name__ == "__main__":
    main()
