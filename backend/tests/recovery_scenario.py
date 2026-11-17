"""Cenário #267, chamado apenas pelo runner Docker descartável em scripts/.

Não é comando operacional de produção. Fixtures e diário sintéticos ficam no
tmpfs privado do container; somente resultados agregados saem para o relatório.
"""

import json
import os
import re
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from uuid import UUID, uuid4

from sqlalchemy import delete, inspect, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import engine, Base
from app.core.security import gerar_hash_senha, gerar_hash_token
from app.domain.termos import TERMOS_VERSAO
from app.models import (
    Avaliacao,
    ComentarioVersao,
    Disciplina,
    Professor,
    SessaoUsuario,
    TokenConfirmacaoEmail,
    TokenRecuperacaoSenha,
    Usuario,
    VotoComentario,
)
from app.models.enums import EstadoComentario
from app.models.registro_acesso import RegistroAcesso
from app.models.solicitacao_titular import EventoSolicitacao, SolicitacaoTitular
from app.models.turma import Turma
from app.models.unidade import Unidade
from app.services import comentario_service, retencao_service

PRIVATE = Path("/tmp/issue267-private")


def check(condition, label):
    if not condition:
        raise AssertionError(label)


def save(name, value):
    PRIVATE.mkdir(mode=0o700, exist_ok=True)
    path = PRIVATE / name
    with path.open("w", encoding="utf-8") as stream:
        os.chmod(path, 0o600)
        json.dump(value, stream, default=str, sort_keys=True)


def load(name):
    return json.loads((PRIVATE / name).read_text(encoding="utf-8"))


def snapshot():
    """Compara todos os valores (só em memória privada), além do DDL refletido."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    schema, rows = {}, {}
    with engine.connect() as conn:
        for table in tables:
            schema[table] = {
                "columns": [
                    {k: str(c[k]) for k in ("name", "type", "nullable", "default")}
                    for c in inspector.get_columns(table)
                ],
                "pk": inspector.get_pk_constraint(table),
                "fk": inspector.get_foreign_keys(table),
                "unique": inspector.get_unique_constraints(table),
                "checks": [
                    {**constraint, "sqltext": canonical_check(constraint["sqltext"])}
                    for constraint in inspector.get_check_constraints(table)
                ],
                "indexes": inspector.get_indexes(table),
            }
            quoted = engine.dialect.identifier_preparer.quote(table)
            rows[table] = sorted(
                json.dumps(dict(row), default=str, sort_keys=True)
                for row in conn.execute(text(f"SELECT * FROM {quoted}")).mappings()
            )
        schema["enums"] = inspector.get_enums()
        schema["persistence"] = list(
            conn.execute(
                text(
                    "SELECT relname, relpersistence FROM pg_class "
                    "WHERE relnamespace='public'::regnamespace AND relkind='r' ORDER BY relname"
                )
            ).tuples()
        )
        revision = conn.scalar(text("SELECT version_num FROM alembic_version"))
    # Canonicalização transforma tuples/objetos refletidos em valores JSON.
    return json.loads(
        json.dumps({"schema": schema, "rows": rows, "revision": revision}, default=str)
    )


def canonical_check(expression):
    # pg_dump/restore reanalisa ANY(ARRAY[varchar]::text[]) em ARRAY[varchar::text].
    # Canonicaliza somente essas coerções literais de texto, sem apagar casts
    # numéricos, de domínio, de coluna ou outros elementos da constraint.
    expression = re.sub(
        r"'((?:[^']|'')*)'::character varying(?:::text)?", r"'\1'::text", expression
    )
    return re.sub(r"(ARRAY\[[^\]]*\])::text\[\]", r"\1", expression)


def seed():
    now = datetime.now(timezone.utc)
    fixture = {"now": now.isoformat(), "password": secrets.token_urlsafe(24)}
    with Session(engine) as db:
        users = []
        for index in range(5):
            user = Usuario(
                nome="Conta sintética descartável",
                email=f"recovery267-{index}@aluno.unb.br",
                password_hash=gerar_hash_senha(fixture["password"]),
                email_confirmado=True,
                moderador=index == 4,
                termos_versao=TERMOS_VERSAO,
                termos_ciencia_em=now,
            )
            db.add(user)
            users.append(user)
        professor = Professor(nome="Docente sintético 267", departamento="TESTE")
        disciplina = Disciplina(
            nome="Disciplina sintética 267", codigo="DESCARTAVEL267", departamento="TESTE"
        )
        unidade = Unidade(nome="Unidade sintética 267", codigo="DESC267", fonte="SINTETICA")
        db.add_all([professor, disciplina, unidade])
        db.flush()
        turma = Turma(
            disciplina_id=disciplina.id,
            unidade_id=unidade.id,
            codigo="DESC267",
            semestre="2026.2",
            fonte="SINTETICA",
        )
        turma.professores.append(professor)
        db.add(turma)
        db.flush()
        avaliacoes, comentarios = [], []
        for user in users:
            avaliacao = Avaliacao(
                usuario_id=user.id,
                professor_id=professor.id,
                disciplina_id=disciplina.id,
                didatica=4,
                dificuldade="MEDIO",
                chamada=False,
                disponibiliza_material=False,
                recomenda=True,
            )
            db.add(avaliacao)
            db.flush()
            comentario = ComentarioVersao(
                avaliacao_id=avaliacao.id,
                texto="Comentário inteiramente sintético.",
                estado=EstadoComentario.PUBLICADO,
            )
            db.add(comentario)
            db.flush()
            avaliacoes.append(str(avaliacao.id))
            comentarios.append(str(comentario.id))
        db.add(
            VotoComentario(
                usuario_id=users[0].id, comentario_versao_id=UUID(comentarios[1]), voto="UTIL"
            )
        )
        fixture.update(
            users=[str(u.id) for u in users],
            evaluations=avaliacoes,
            comments=comentarios,
            professor=str(professor.id),
            disciplina=str(disciplina.id),
        )
        for model, key in (
            (SessaoUsuario, "session"),
            (TokenRecuperacaoSenha, "reset"),
            (TokenConfirmacaoEmail, "confirmation"),
        ):
            token = secrets.token_urlsafe(32)
            item = model(
                usuario_id=users[0].id,
                token_hash=gerar_hash_token(token),
                expires_at=now + timedelta(days=1),
            )
            db.add(item)
            db.flush()
            fixture[key] = {"id": str(item.id), "token": token}
        for expired in (True, False):
            item = RegistroAcesso(
                ocorrido_em=now,
                expira_em=now + timedelta(days=-1 if expired else 180),
                operacao="ensaio267",
                ip_conexao="192.0.2.1",
                resultado="200",
                requisicao_id=uuid4(),
            )
            db.add(item)
            db.flush()
            fixture["expired_access" if expired else "active_access"] = str(item.id)
        request_key = secrets.token_urlsafe(32)
        pedido = SolicitacaoTitular(
            chave_hash=gerar_hash_token(request_key),
            categoria="DIREITO_LGPD",
            alvo="alvo sintético",
            descricao="Pedido fictício de ensaio.",
            evidencia="Sem dados reais.",
        )
        db.add(pedido)
        db.flush()
        db.add_all(
            [
                EventoSolicitacao(
                    solicitacao_id=pedido.id,
                    autor_id=users[4].id,
                    tipo="TRIAGEM",
                    texto="Análise sintética interna.",
                ),
                EventoSolicitacao(
                    solicitacao_id=pedido.id,
                    autor_id=None,
                    tipo="COMPLEMENTO",
                    texto="Complemento sintético.",
                ),
            ]
        )
        fixture["request"] = str(pedido.id)
        fixture["request_hash"] = pedido.chave_hash
        db.commit()
    save("fixture.json", fixture)
    save("baseline.json", snapshot())
    return {
        "fixtures_sinteticas": True,
        "tabelas_povoadas": [k for k, v in snapshot()["rows"].items() if v],
    }


def apply_events(events):
    """Reusa serviços vigentes; não exporta nem define um diário de produção."""
    for event in events:
        when = datetime.fromisoformat(event["at"])
        with Session(engine) as db:
            user = db.get(Usuario, UUID(event["user"]))
            with (
                patch.object(retencao_service, "agora_utc", return_value=when),
                patch.object(comentario_service, "agora_utc", return_value=when),
            ):
                if event["operation"] == "account":
                    retencao_service.excluir_conta(db, user)
                elif event["operation"] == "evaluation":
                    retencao_service.excluir_avaliacao(db, user, UUID(event["id"]))
                elif event["operation"] == "comment":
                    item = db.get(ComentarioVersao, UUID(event["id"]))
                    if item.estado != EstadoComentario.RETIRADO:
                        comentario_service.retirar(db, item.id, user)
                elif event["operation"] == "role":
                    user.moderador = user.reconciliador = False
                    db.commit()
                else:
                    model = {
                        "session": SessaoUsuario,
                        "reset": TokenRecuperacaoSenha,
                        "confirmation": TokenConfirmacaoEmail,
                    }[event["operation"]]
                    db.execute(delete(model).where(model.id == UUID(event["id"])))
                    db.commit()


def late_changes():
    f = load("fixture.json")
    when = (datetime.fromisoformat(f["now"]) + timedelta(seconds=1)).isoformat()
    events = [
        {"operation": "account", "user": f["users"][1]},
        {"operation": "evaluation", "user": f["users"][2], "id": f["evaluations"][2]},
        {"operation": "comment", "user": f["users"][3], "id": f["comments"][3]},
        {"operation": "role", "user": f["users"][4]},
    ]
    events += [
        {"operation": key, "user": f["users"][0], "id": f[key]["id"]}
        for key in ("session", "reset", "confirmation")
    ]
    for event in events:
        event["at"] = when
    save("events.json", events)
    apply_events(events)
    save("after-events.json", snapshot()["rows"])
    return {
        "eventos_posteriores_ao_backup": len(events),
        "diario": "sintético em tmpfs; não operacional",
    }


def verify_restore():
    actual, baseline = snapshot(), load("baseline.json")
    differences = []
    for table, expected in baseline["schema"].items():
        if actual["schema"].get(table) != expected:
            if isinstance(expected, dict):
                differences.extend(
                    f"schema:{table}:{key}"
                    for key in expected
                    if actual["schema"].get(table, {}).get(key) != expected[key]
                )
            else:
                differences.append("schema:" + table)
    differences.extend(
        "rows:" + table
        for table, expected in baseline["rows"].items()
        if actual["rows"].get(table) != expected
    )
    check(actual == baseline, "schema/revisão/valores diferentes: " + ",".join(differences))
    check(set(Base.metadata.tables) <= set(actual["rows"]), "tabela do modelo ausente")
    with Session(engine) as db:
        check(
            db.get(Usuario, UUID(load("fixture.json")["users"][1])).excluido_em is None,
            "cópia deveria demonstrar estado anterior à exclusão",
        )
    return {
        "schema_e_valores_iguais": True,
        "revisao": actual["revision"],
        "contagens": {k: len(v) for k, v in actual["rows"].items()},
        "constraints": sum(
            len(s[k])
            for s in actual["schema"].values()
            if isinstance(s, dict)
            for k in ("fk", "unique", "checks")
        ),
        "copia_ainda_insegura_antes_da_reaplicacao": True,
    }


def replay():
    def domain_rows(rows):
        # func.now() registra a hora técnica da nova escrita. Datas originais de
        # exclusão/purga seguem comparadas; antes do replay TODOS os valores são.
        for table in ("avaliacoes", "comentario_versoes"):
            values = [json.loads(row) for row in rows[table]]
            for row in values:
                row.pop("updated_at")
            rows[table] = sorted(json.dumps(row, sort_keys=True) for row in values)
        return rows

    events = load("events.json")
    apply_events(events)
    first = domain_rows(snapshot()["rows"])
    apply_events(events)
    check(
        domain_rows(snapshot()["rows"]) == first == domain_rows(load("after-events.json")),
        "reaplicação divergente/não idempotente",
    )
    return {
        "exclusoes_retirada_revogacoes_reaplicadas": True,
        "idempotencia": True,
        "limite_comparacao_replay": "updated_at técnico pode mudar; exclusão e janela originais preservadas",
    }


def constraints():
    f = load("fixture.json")
    cases = [
        ("check", "UPDATE avaliacoes SET didatica=6 WHERE id=:id", {"id": f["evaluations"][0]}),
        (
            "fk",
            "UPDATE avaliacoes SET professor_id=:id WHERE id=:a",
            {"id": str(uuid4()), "a": f["evaluations"][0]},
        ),
        (
            "unique",
            "UPDATE usuarios SET email=:email WHERE id=:id",
            {"email": "recovery267-0@aluno.unb.br", "id": f["users"][4]},
        ),
        (
            "not_null",
            "UPDATE avaliacoes SET usuario_id=NULL WHERE id=:id",
            {"id": f["evaluations"][0]},
        ),
        ("termos", "UPDATE usuarios SET termos_versao=NULL WHERE id=:id", {"id": f["users"][0]}),
    ]
    for name, statement, params in cases:
        with engine.connect() as conn:
            tx = conn.begin()
            try:
                conn.execute(text(statement), params)
            except IntegrityError:
                pass
            else:
                raise AssertionError(f"constraint {name} não impediu escrita")
            finally:
                tx.rollback()
    return [name for name, _, _ in cases]


def journey():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.services.email_service import get_email_sender
    from tests.auth_http_fixtures import TransporteEmMemoria

    f = load("fixture.json")
    checks = constraints()
    sender = TransporteEmMemoria()
    app.dependency_overrides[get_email_sender] = lambda: sender
    # Única substituição: e-mail em memória. Banco/autenticação/limites reais.
    try:
        with TestClient(
            app, base_url="https://api.example", headers={"Origin": "https://frontend.example"}
        ) as client:

            def request(method, path, expected, **kwargs):
                response = client.request(method, path, **kwargs)
                check(
                    response.status_code == expected,
                    f"HTTP {method} {path.split('?')[0]}: {response.status_code} esperado {expected}",
                )
                return response

            path = f"/api/professores/{f['professor']}/disciplinas/{f['disciplina']}"
            request("GET", "/api/disciplinas?nome=sintética", 200)
            check(
                request("GET", path, 200).json()["total_avaliacoes"] == 3,
                "excluídas voltaram ao agregado",
            )
            published = request("GET", path + "/comentarios", 200).json()
            check(
                {c["id"] for c in published} == {f["comments"][0], f["comments"][4]},
                "comentário removido reexposto",
            )
            check(
                all(set(c) == {"id", "texto", "created_at"} for c in published), "autoria pública"
            )
            request(
                "POST", "/api/comentarios/" + f["comments"][4] + "/voto", 401, json={"voto": "UTIL"}
            )
            client.cookies.set("undb_session", f["session"]["token"])
            check(
                not request("GET", "/api/auth/sessao", 200).json()["autenticado"],
                "sessão revogada ressuscitou",
            )
            client.cookies.clear()
            request(
                "POST",
                "/api/auth/redefinir-senha",
                400,
                json={"token": f["reset"]["token"], "senha": secrets.token_urlsafe(24)},
            )
            request("POST", "/api/auth/confirmar", 400, json={"token": f["confirmation"]["token"]})
            request(
                "POST",
                "/api/auth/login",
                401,
                json={"email": "recovery267-1@aluno.unb.br", "senha": f["password"]},
            )
            # Papel revogado deve negar moderação após login normal.
            request(
                "POST",
                "/api/auth/login",
                200,
                json={"email": "recovery267-4@aluno.unb.br", "senha": f["password"]},
            )
            request("DELETE", "/api/moderacao/avaliacoes/" + f["evaluations"][0], 403)
            request("GET", "/api/atendimento", 403)
            request("DELETE", "/api/avaliacoes/" + f["evaluations"][0], 404)
            request("POST", "/api/auth/logout", 200)
            dados = {
                "nome": "Jornada sintética",
                "email": "jornada267@aluno.unb.br",
                "senha": secrets.token_urlsafe(24),
            }
            request("POST", "/api/auth/cadastro", 422, json=dados)
            request(
                "POST",
                "/api/auth/cadastro",
                202,
                json={**dados, "ciencia_termos": True, "termos_versao": TERMOS_VERSAO},
            )
            request("POST", "/api/auth/confirmar", 200, json={"token": sender.token()})
            login = request(
                "POST", "/api/auth/login", 200, json={k: dados[k] for k in ("email", "senha")}
            )
            check(
                all(
                    flag in login.headers["set-cookie"]
                    for flag in ("HttpOnly", "Secure", "SameSite=lax")
                ),
                "cookie inseguro",
            )
            check(request("GET", "/api/auth/sessao", 200).json()["autenticado"], "sessão ausente")
            request("POST", "/api/auth/logout", 403, headers={"Origin": "https://externa.example"})
            payload = {
                "professor_id": f["professor"],
                "disciplina_id": f["disciplina"],
                "didatica": 5,
                "dificuldade": "MEDIO",
                "chamada": False,
                "disponibiliza_material": False,
                "recomenda": True,
            }
            request("POST", "/api/avaliacoes", 200, json=payload)
            check(
                request("GET", path, 200).json()["total_avaliacoes"] == 4, "escrita não persistiu"
            )
            vote = "/api/comentarios/" + f["comments"][4] + "/voto"
            response = request("POST", vote, 200, json={"voto": "UTIL"})
            check(response.json()["meu_voto"] == "UTIL", "voto não persistiu")
            check(response.headers["cache-control"] == "no-store", "resposta privada cacheável")
            request("POST", vote, 200, json={"voto": None})
            request("POST", "/api/auth/logout", 200)
            check(
                not request("GET", "/api/auth/sessao", 200).json()["autenticado"], "logout falhou"
            )
        with Session(engine) as db:
            user = db.scalar(select(Usuario).where(Usuario.email == dados["email"]))
            check(
                user.termos_versao == TERMOS_VERSAO and user.termos_ciencia_em is not None,
                "ciência ausente",
            )
            pedido = db.get(SolicitacaoTitular, UUID(f["request"]))
            check(pedido.chave_hash == f["request_hash"], "hash de acompanhamento alterado")
            check(
                len(
                    list(
                        db.scalars(
                            select(EventoSolicitacao).where(
                                EventoSolicitacao.solicitacao_id == pedido.id
                            )
                        )
                    )
                )
                == 2,
                "eventos sem pedido",
            )
    finally:
        app.dependency_overrides.clear()
    return {
        "jornada_api_no_destino": [
            "busca",
            "agregado",
            "cadastro/Termos",
            "confirmação",
            "login",
            "avaliação",
            "voto/retirada",
            "logout",
        ],
        "controles": [
            "sessão/token revogados",
            "conta excluída",
            "papel revogado",
            "autoria",
            "origem",
            "cookie",
            "no-store",
            "pedido/eventos/hash",
        ],
        "constraints_exercitadas": checks,
        "transporte_email": "memória; sem envio externo",
    }


def retention():
    f = load("fixture.json")
    when = datetime.fromisoformat(load("events.json")[0]["at"]) + timedelta(days=7)
    with Session(engine) as db:
        with patch.object(
            retencao_service, "agora_utc", return_value=when - timedelta(microseconds=1)
        ):
            retencao_service.purgar(db)
        check(db.get(Avaliacao, UUID(f["evaluations"][2])) is not None, "purga antes da janela")
        with patch.object(retencao_service, "agora_utc", return_value=when):
            while retencao_service.purgar(db):
                pass
        db.expire_all()
        for index in (1, 2):
            check(
                db.get(Avaliacao, UUID(f["evaluations"][index])) is None,
                "avaliação vencida preservada",
            )
        for index in (1, 2, 3):
            check(
                db.get(ComentarioVersao, UUID(f["comments"][index])) is None,
                "texto vencido preservado",
            )
        check(
            db.get(Avaliacao, UUID(f["evaluations"][3])) is not None, "retirar texto apagou notas"
        )
        check(
            db.get(RegistroAcesso, UUID(f["expired_access"])) is None, "acesso vencido preservado"
        )
        check(
            db.get(RegistroAcesso, UUID(f["active_access"])) is not None, "acesso vigente apagado"
        )
        check(
            db.get(Usuario, UUID(f["users"][1])).password_hash is None,
            "credencial de excluída recuperada",
        )
        check(
            db.scalar(
                select(VotoComentario).where(
                    VotoComentario.comentario_versao_id == UUID(f["comments"][1])
                )
            )
            is None,
            "voto órfão após purga",
        )
        check(
            db.get(SolicitacaoTitular, UUID(f["request"])) is not None,
            "inventou descarte de pedidos",
        )
    return {
        "fronteira_sete_dias": True,
        "cascata_votos": True,
        "acesso_expirado_purgado": True,
        "acesso_vigente_preservado": True,
        "conta_minima_e_pedidos_sem_prazo_inventado": True,
    }


def main():
    url = make_url(os.environ["DATABASE_URL"])
    check(
        os.environ.get("ISSUE267_DISPOSABLE") == "1"
        and url.host == "issue267-db"
        and url.database in {"undb267_disposable_source", "undb267_disposable_restore"},
        "ambiente não descartável",
    )
    os.umask(0o077)
    stage = sys.argv[1]
    try:
        result = {
            "seed": seed,
            "late": late_changes,
            "verify": verify_restore,
            "replay": replay,
            "journey": journey,
            "retention": retention,
        }[stage]()
        print("ISSUE267_RESULT=" + json.dumps(result, ensure_ascii=False))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
