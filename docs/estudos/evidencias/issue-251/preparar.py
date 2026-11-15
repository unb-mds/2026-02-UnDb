"""Ensaio documental #251. Só cria SQLite em memória e JSON junto deste arquivo."""
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from uuid import NAMESPACE_URL, UUID, uuid5

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "backend"))
# Não carregar conexão de .env do operador.
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SECRET_KEY"] = "ensaio-sintetico-251"

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable
from app.core.database import Base
import app.models
from app.domain.texto import normalizar_busca
from app.models.disciplina import Disciplina
from app.models.professor import Professor
from app.models.professor_correspondencia import ProfessorCorrespondencia
from app.models.unidade import Unidade
from app.repositories import disciplina_repository as dr, professor_repository as pr

OUT = Path(__file__).resolve().parent
def uid(label):
    return str(uuid5(NAMESPACE_URL, "undb-issue-251-sintetico/" + label))

profs = [
    ("P1", "Maria Emília dos Santos", "CIC"),
    ("P2", "Maria Emília dos Santos", "MAT"),
    ("P3", "Maria Elisa de Sousa", "CIC"),
    ("P4", "João-Pedro D'Ávila", "ENM"),
    ("P5", "José Álvaro Lima", "MAT"),
    ("P6", "Ana Clara Costa", "CIC"),
    ("P7", "Ana Carolina Costa", "MAT"),
    ("P8", "Bruno Nascimento", "CIC"),
    ("P9", "José Lima", "CIC"),
    ("P10", "Mario Santos", "CIC"),
    ("P11", "Santos", "ENM"),
    ("P12", "Maria Emília dos Santos", "CIC"),  # alias excluído da listagem
]
discs = [
    ("D1", "CIC0004", "Algoritmos e Programação de Computadores", "CIC"),
    ("D2", "CIC0005", "Programação Orientada a Objetos", "CIC"),
    ("D3", "MAT0025", "Cálculo 1", "MAT"),
    ("D4", "MAT0026", "Cálculo 2", "MAT"),
    ("D5", "CIC0099", "Banco de Dados", "CIC"),
    ("D6", "EST0101", "Estatística Aplicada", "EST"),
    ("D7", "ENM0001", "Métodos Numéricos", "ENM"),
    ("D8", "CIC0002", "Fundamentos Teóricos da Computação", "CIC"),
    ("D9", "FGA0004", "Algoritmos", "FGA"),
    ("D10", "CIC0014", "Algoritmos e Estruturas de Dados", "CIC"),
]
units = {"CIC": "Departamento de Ciência da Computação", "MAT": "Departamento de Matemática",
         "ENM": "Departamento de Engenharia Mecânica", "EST": "Departamento de Estatística",
         "FGA": "Faculdade do Gama"}
records = []
for label, nome, dep in profs:
    records.append(dict(label=label, id=uid(label), tipo="professores", nome=nome,
                        nome_normalizado=normalizar_busca(nome), departamento=dep,
                        departamento_nome=units[dep], alias=label == "P12"))
for label, codigo, nome, dep in discs:
    records.append(dict(label=label, id=uid(label), tipo="disciplinas", codigo=codigo,
                        nome=nome, nome_normalizado=normalizar_busca(nome), departamento=dep,
                        departamento_nome=units[dep], alias=False))

# Julgamentos sintéticos por intenção, não requisitos nem avaliações de pessoas reais.
cases_raw = [
    ("01", "professores", "Maria Emília dos Santos", ["P1", "P2"], "nome exato"),
    ("02", "professores", "emilia", ["P1", "P2"], "nome parcial"),
    ("03", "professores", "santos", ["P1", "P2", "P10", "P11"], "sobrenome"),
    ("04", "professores", "emliia", ["P1", "P2"], "transposição"),
    ("05", "professores", "MARIA EMILIA DOS SANTOS", ["P1", "P2"], "caixa/acentos"),
    ("06", "professores", "maria emlia santos", ["P1", "P2"], "composto/omissão"),
    ("07", "professores", "maria emília", ["P1", "P2"], "homônimos"),
    ("08", "disciplinas", "Algoritmos e Programação de Computadores", ["D1"], "nome exato"),
    ("09", "disciplinas", "programacao", ["D1", "D2"], "nome parcial"),
    ("10", "disciplinas", "CIC0004", ["D1"], "código exato"),
    ("11", "disciplinas", "CIC004", ["D1"], "código/omissão"),
    ("12", "professores", "a", [], "curto; UI não consulta"),
    ("13", "professores", "zzqxv", [], "sem correspondência"),
    ("14", "professores", "ana costa", ["P6", "P7"], "múltiplos candidatos"),
    ("15", "professores", "emiilia", ["P1", "P2"], "duplicação"),
    ("16", "professores", "  santos   maria  ", ["P1", "P2"], "espaços/ordem"),
    ("17", "professores", "joao pedro davila", ["P4"], "pontuação omitida"),
    ("18", "professores", "joao-pedro d'avila", ["P4"], "pontuação preservada"),
    ("19", "disciplinas", "CIC000", ["D1", "D2", "D8"], "prefixo de código"),
    ("20", "disciplinas", "calculo", ["D3", "D4"], "acentos/ambiguidade"),
    ("21", "professores", "ma", ["P1", "P2", "P3", "P5", "P9", "P10"], "duas letras; substring"),
    ("22", "professores", "%%", [], "curingas LIKE; nenhuma intenção nominal"),
    ("23", "professores", "maria alvaro", [], "nomes incompatíveis"),
    ("24", "disciplinas", "CIC0400", ["D1"], "código/transposição; intenção não inferível"),
    ("25", "disciplinas", "algortimos", ["D1", "D9", "D10"], "nome/transposição"),
    ("26", "professores", "nascimnto", ["P8"], "sobrenome/omissão"),
]

class Capture:
    def __init__(self): self.statements = []
    def scalars(self, stmt):
        self.statements.append(stmt)
        return self
    def all(self): return []

engine = create_engine("sqlite+pysqlite:///:memory:")
Base.metadata.create_all(engine)
with Session(engine) as db:
    db.add_all([Unidade(id=UUID(uid("U" + dep)), fonte="SIGAA", codigo=dep, nome=nome)
                for dep, nome in units.items()])
    for r in records:
        kw = dict(id=UUID(r["id"]), nome=r["nome"], nome_normalizado=r["nome_normalizado"],
                  departamento=r["departamento"])
        db.add(Professor(**kw, identidade_confirmada=False) if r["tipo"] == "professores"
               else Disciplina(**kw, codigo=r["codigo"]))
    db.flush()
    db.add(ProfessorCorrespondencia(origem_id=UUID(uid("P12")), destino_id=UUID(uid("P1")),
                                   evidencia="alias sintético do ensaio"))
    db.commit()
    cases = []
    dialect = postgresql.dialect(paramstyle="numeric_dollar")
    labels = {r["id"]: r["label"] for r in records}
    for cid, tipo, term, relevant, reason in cases_raw:
        cap = Capture()
        if tipo == "professores":
            found = pr.listar(db, term)
            pr.listar(cap, term)
        else:
            found = dr.listar(db, codigo=term) + dr.listar(db, nome=term)
            dr.listar(cap, codigo=term)
            dr.listar(cap, nome=term)
        queries = []
        for stmt in cap.statements:
            c = stmt.compile(dialect=dialect)
            queries.append(dict(sql=str(c), params=[c.params[k] for k in c.positiontup]))
        cases.append(dict(id=cid, tipo=tipo, termo=term, normalizado=normalizar_busca(term),
                          relevantes=relevant, cenario=reason, queries_atual=queries,
                          sqlite_ids=list(dict.fromkeys(labels[str(r.id)] for r in found))))
    ddl = [str(CreateTable(Base.metadata.tables[t]).compile(dialect=dialect))
           for t in ("unidades", "professores", "disciplinas", "professor_correspondencias")]
payload = dict(origem="dados integralmente sintéticos", commit=subprocess.check_output(
    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), python=platform.python_version(),
    sqlalchemy=sqlalchemy.__version__, ddl=ddl, unidades=[dict(id=uid("U" + dep), codigo=dep, nome=n)
    for dep,n in units.items()], registros=records, casos=cases)
(OUT / "dataset.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print(f"Preparados {len(records)} registros, {len(cases)} consultas; SQLite em memória; SQL PostgreSQL do repository real.")
