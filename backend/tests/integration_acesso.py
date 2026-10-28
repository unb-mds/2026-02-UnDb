"""#158: cadastro, confirmação, login e retorno pelas telas, com PostgreSQL real.

UNDB_INTEGRATION_TEST=1 python -m tests.integration_acesso
Exige migrations e build frontend prévios. --prepare/--inspect/--cleanup permitem
usar a mesma verificação com API externa em container, sem endpoint de testes.
"""
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID, uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.database import engine
from app.domain.texto import normalizar_busca
from app.models.avaliacao import Avaliacao
from app.models.disciplina import Disciplina
from app.models.professor import Professor
from app.models.sessao_usuario import SessaoUsuario
from app.models.token_confirmacao_email import TokenConfirmacaoEmail
from app.models.turma import Turma, turmas_professores
from app.models.unidade import Unidade
from app.models.usuario import Usuario
from tests.integration_avaliacao import requisicao


def preparar():
    suffix = uuid4().hex[:12]
    fixture = dict(professores=[str(uuid4()), str(uuid4())], disciplinaId=str(uuid4()),
                   unidadeId=str(uuid4()), turmas=[str(uuid4()), str(uuid4())],
                   emails=[f"acesso.{suffix}.{i}@aluno.unb.br" for i in range(2)],
                   senha="senha-local-integracao", codigo=f"A{suffix}")
    with Session(engine) as db:
        professores = [Professor(id=UUID(pid), nome=f"Professor de acesso {i + 1}",
                                nome_normalizado=normalizar_busca(f"Professor de acesso {i + 1}"), departamento="CIC")
                       for i, pid in enumerate(fixture["professores"])]
        disciplina = Disciplina(id=UUID(fixture["disciplinaId"]), codigo=fixture["codigo"],
                                nome="Disciplina de acesso e confirmação",
                                nome_normalizado=normalizar_busca("Disciplina de acesso e confirmação"), departamento="CIC")
        unidade = Unidade(id=UUID(fixture["unidadeId"]), codigo=suffix, nome="Unidade sintética de acesso")
        db.add_all([*professores, disciplina, unidade])
        for i, professor in enumerate(professores):
            db.add(Turma(id=UUID(fixture["turmas"][i]), disciplina=disciplina, unidade=unidade,
                         codigo=str(i + 1), semestre="2026.2", professores=[professor]))
        db.commit()
    return fixture


def inspecionar(fixture):
    with Session(engine) as db:
        usuarios = list(db.scalars(select(Usuario).where(Usuario.email.in_(fixture["emails"]))))
        return dict(usuarios=[dict(email=u.email, confirmado=u.email_confirmado,
                                   sessoes=db.scalar(select(func.count()).select_from(SessaoUsuario).where(SessaoUsuario.usuario_id == u.id)),
                                   tokensUsados=db.scalar(select(func.count()).select_from(TokenConfirmacaoEmail).where(
                                       TokenConfirmacaoEmail.usuario_id == u.id, TokenConfirmacaoEmail.used_at.is_not(None))))
                              for u in usuarios],
                    avaliacoes=[dict(id=str(a.id), email=a.usuario.email, professorId=str(a.professor_id),
                                     didatica=a.didatica, chamada=a.chamada, recomenda=a.recomenda,
                                     disponibilizaMaterial=a.disponibiliza_material)
                                for a in db.scalars(select(Avaliacao).where(
                                    Avaliacao.professor_id.in_([UUID(p) for p in fixture["professores"]])))])


def limpar(fixture):
    with Session(engine) as db:
        usuarios = list(db.scalars(select(Usuario.id).where(Usuario.email.in_(fixture["emails"]))))
        db.execute(delete(Avaliacao).where(Avaliacao.professor_id.in_([UUID(p) for p in fixture["professores"]])))
        for model in (SessaoUsuario, TokenConfirmacaoEmail):
            db.execute(delete(model).where(model.usuario_id.in_(usuarios)))
        db.execute(delete(Usuario).where(Usuario.id.in_(usuarios)))
        turmas = [UUID(t) for t in fixture["turmas"]]
        db.execute(delete(turmas_professores).where(turmas_professores.c.turma_id.in_(turmas)))
        db.execute(delete(Turma).where(Turma.id.in_(turmas)))
        db.execute(delete(Professor).where(Professor.id.in_([UUID(p) for p in fixture["professores"]])))
        db.execute(delete(Disciplina).where(Disciplina.id == UUID(fixture["disciplinaId"])))
        db.execute(delete(Unidade).where(Unidade.id == UUID(fixture["unidadeId"])))
        db.commit()


def verificar_porta_api(porta=8000):
    # Depois da suíte anterior, conexões encerradas podem ficar em TIME_WAIT.
    # Um bind de sondagem acusa ocupação nesse estado, mesmo sem servidor ativo.
    # Recusamos um listener existente; o Uvicorn faz o bind real com reutilização.
    with socket.socket() as conexao:
        conexao.settimeout(1)
        if conexao.connect_ex(("127.0.0.1", porta)) == 0:
            raise RuntimeError(f"A porta {porta} já possui um serviço em execução.")


def main():
    assert os.environ.get("UNDB_INTEGRATION_TEST") == "1", "Use banco isolado de testes."
    assert engine.dialect.name == "postgresql", "A integração exige PostgreSQL real."
    if "--inspect" in sys.argv or "--cleanup" in sys.argv:
        fixture = json.loads(os.environ["E2E_ACESSO_FIXTURE"])
        if "--inspect" in sys.argv:
            print(json.dumps(inspecionar(fixture)))
        else:
            limpar(fixture)
        return
    if "--prepare" in sys.argv:
        print(json.dumps(preparar()))
        return
    verificar_porta_api()
    fixture = preparar()
    api = None
    try:
        with TemporaryDirectory(prefix="undb-acesso-") as temporario:
            log_path = Path(temporario) / "api.log"
            env = {**os.environ, "DEBUG": "True", "CORS_ORIGINS": "http://localhost:3100",
                   "FRONTEND_URL": "http://localhost:3100", "EMAIL_BACKEND": "console",
                   "E2E_ACESSO_FIXTURE": json.dumps(fixture), "E2E_PYTHON": sys.executable,
                   "E2E_EMAIL_LOG_FILE": str(log_path)}
            # O link/token é lido do adaptador console real, sem gerar ou confirmar
            # tokens por fora da API. O log temporário não é evidência versionada.
            with log_path.open("w", encoding="utf8") as log:
                api = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"],
                                       env=env, stdout=log, stderr=subprocess.STDOUT)
                try:
                    for _ in range(100):
                        if api.poll() is not None:
                            raise RuntimeError("A API não iniciou.")
                        try:
                            if requisicao("/health")[0] == 200:
                                break
                        except OSError:
                            pass
                        time.sleep(0.1)
                    else:
                        raise TimeoutError("API indisponível")
                    subprocess.run(["node", "tests/acesso-browser.mjs"], env=env, check=True,
                                   cwd=Path(__file__).resolve().parents[2] / "frontend")
                finally:
                    api.terminate()
                    api.wait(timeout=15)
    finally:
        limpar(fixture)


if __name__ == "__main__":
    main()
