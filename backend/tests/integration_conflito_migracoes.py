"""Ensaio destrutivo APENAS em banco descartável reservado para testes."""

import os
import runpy
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url


def semear(conn):
    usuario, eleitor = uuid4(), uuid4()
    agora = datetime.now(timezone.utc)
    for id in (usuario, eleitor):
        conn.execute(
            text(
                "INSERT INTO usuarios (id,nome,email,password_hash,email_confirmado,moderador,reconciliador) VALUES (:id,'Sintético',:email,'sem-login',true,false,false)"
            ),
            {"id": id, "email": f"{id.hex}@aluno.unb.br"},
        )
    ciencia = "termos_versao" in {c["name"] for c in inspect(conn).get_columns("usuarios")}
    if ciencia:
        conn.execute(
            text(
                "UPDATE usuarios SET termos_versao='2026-11-17',termos_ciencia_em=:agora WHERE id=:id"
            ),
            {"id": usuario, "agora": agora},
        )
    contador = inspect(conn).has_table("contadores_abuso")
    if contador:
        conn.execute(
            text(
                "INSERT INTO contadores_abuso (operacao,chave,quantidade,inicio_em,expira_em) VALUES ('ensaio_reconciliacao',repeat('a',64),7,now(),now()+interval '1 hour')"
            )
        )
    voto = None
    if inspect(conn).has_table("votos_comentario"):
        professor, disciplina, avaliacao, comentario = (uuid4() for _ in range(4))
        conn.execute(
            text(
                "INSERT INTO professores (id,nome,nome_normalizado,departamento) VALUES (:id,'Sintético','sintetico','TESTE')"
            ),
            {"id": professor},
        )
        conn.execute(
            text(
                "INSERT INTO disciplinas (id,codigo,nome,nome_normalizado,departamento) VALUES (:id,:codigo,'Sintética','sintetica','TESTE')"
            ),
            {"id": disciplina, "codigo": disciplina.hex[:12]},
        )
        conn.execute(
            text(
                "INSERT INTO avaliacoes (id,usuario_id,professor_id,disciplina_id,didatica,dificuldade,chamada,disponibiliza_material,recomenda) VALUES (:id,:usuario,:professor,:disciplina,3,'MEDIO',false,false,true)"
            ),
            {"id": avaliacao, "usuario": usuario, "professor": professor, "disciplina": disciplina},
        )
        conn.execute(
            text(
                "INSERT INTO comentario_versoes (id,avaliacao_id,texto,estado) VALUES (:id,:avaliacao,'Texto sintético','PUBLICADO')"
            ),
            {"id": comentario, "avaliacao": avaliacao},
        )
        conn.execute(
            text(
                "INSERT INTO votos_comentario (comentario_versao_id,usuario_id,voto) VALUES (:comentario,:usuario,'UTIL')"
            ),
            {"comentario": comentario, "usuario": eleitor},
        )
        voto = (comentario, eleitor, "UTIL")
    return usuario, agora if ciencia else None, contador, voto


def main():
    url = make_url(os.environ["MIGRATION_DATABASE_URL"])
    if url.host not in {"127.0.0.1", "localhost", "::1"} or url.database not in {
        "undb_266_test",
        "ci",
    }:
        raise ValueError("Exige banco local reservado undb_266_test ou ci, nunca produção.")
    cfg = Config("alembic.ini")
    engine = create_engine(url, hide_parameters=True)
    for origem in ("develop_02", "votos_03", "retencao_02", "acessos_03", "pr280_04"):
        command.downgrade(cfg, "base")
        command.upgrade(cfg, "20261115_02")
        if origem == "develop_02":
            command.upgrade(cfg, "20261117_02")
        elif origem == "votos_03":
            command.upgrade(cfg, "20261117_03")
        elif origem == "pr280_04":
            command.upgrade(cfg, "20261117_04")
        else:
            command.upgrade(cfg, "20261117_01")
            with engine.begin() as conn, Operations.context(MigrationContext.configure(conn)):
                runpy.run_path(str(Path("alembic/versions/20261117_02_retencao.py")))["upgrade"]()
                if origem == "acessos_03":
                    runpy.run_path(str(Path("alembic/versions/20261117_03_registros_acesso.py")))[
                        "upgrade"
                    ]()
            command.stamp(
                cfg, "20261117_02" if origem == "retencao_02" else "20261117_03", purge=True
            )
        with engine.begin() as conn:
            usuario, ciencia, contador, voto = semear(conn)
        command.upgrade(cfg, "head")
        command.check(cfg)
        with engine.connect() as conn:
            assert conn.scalar(text("SELECT version_num FROM alembic_version")) == "20261117_05"
            cols = {c["name"] for c in inspect(conn).get_columns("usuarios")}
            assert {"termos_versao", "termos_ciencia_em", "excluido_em"} <= cols
            assert {"votos_comentario", "registros_acesso"} <= set(inspect(conn).get_table_names())
            assert (
                conn.scalar(
                    text("SELECT termos_ciencia_em FROM usuarios WHERE id=:id"), {"id": usuario}
                )
                == ciencia
            )
            if contador:
                assert (
                    conn.scalar(
                        text(
                            "SELECT quantidade FROM contadores_abuso WHERE operacao='ensaio_reconciliacao'"
                        )
                    )
                    == 7
                )
            if voto:
                assert (
                    conn.execute(
                        text("SELECT comentario_versao_id,usuario_id,voto FROM votos_comentario")
                    ).one()
                    == voto
                )
        print(origem + ": migracao/check aprovados")
    # O ensaio deixa o banco migrado e vazio para as próximas suítes do CI.
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    command.check(cfg)
    engine.dispose()


if __name__ == "__main__":
    main()
