"""Dados sintéticos da #157 para API/PostgreSQL reais, em banco vazio de testes.

UNDB_INTEGRATION_TEST=1 python -m tests.seed_resultados > fixture.json
O JSON contém somente contexto público sintético para resultados-browser.mjs.
Não executa importação do SIGAA nem cria schema; aplique as migrations antes.
"""
import json
import os
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import engine
from app.domain.texto import normalizar_busca
from app.models.avaliacao import Avaliacao
from app.models.disciplina import Disciplina
from app.models.enums import Dificuldade, QualidadeMaterial
from app.models.professor import Professor
from app.models.turma import Turma
from app.models.unidade import Unidade
from app.models.usuario import Usuario


def main():
    assert os.environ.get("UNDB_INTEGRATION_TEST") == "1", "Use somente banco de testes."
    assert engine.dialect.name == "postgresql", "A evidência exige PostgreSQL real."
    termo = "Revisão PR183"
    with Session(engine) as db:
        for model in (Professor, Disciplina, Usuario, Unidade):
            assert db.scalar(select(func.count()).select_from(model)) == 0, "Use banco vazio e isolado."
        unidade = Unidade(codigo="PR183", nome="Unidade sintética de verificação")
        nomes = ["Ana", "Ana", "Bruno", "Carla", "Davi", "Eva", "Sem turma"]
        professores = [Professor(
            nome=f"{nome} {termo}", nome_normalizado=normalizar_busca(f"{nome} {termo}"),
            departamento="Instituto de Ciências Exatas e Tecnologias da Informação" if i != 1 else "Faculdade de Educação",
        ) for i, nome in enumerate(nomes)]
        disciplinas = [Disciplina(
            codigo=f"REV183{i + 1}", nome=nome, nome_normalizado=normalizar_busca(nome),
            departamento="Departamento de Ciência da Computação e Sistemas de Informação",
        ) for i, nome in enumerate([
            "Fundamentos de Algoritmos e Estruturas de Dados para Sistemas de Informação",
            "Tópicos Avançados em Desenvolvimento de Software e Engenharia de Requisitos",
        ])]
        usuarios = [Usuario(nome="Estudante sintético", email=f"pr183.{uuid4().hex}@aluno.unb.br",
                            password_hash="conta-de-teste-sem-login", email_confirmado=True) for _ in range(4)]
        db.add_all([unidade, *professores, *disciplinas, *usuarios])
        db.flush()
        for i, professor in enumerate(professores[:6]):
            db.add(Turma(disciplina=disciplinas[0], unidade=unidade, codigo=str(i + 1),
                         semestre="2026.2", professores=[professor]))
        db.add(Turma(disciplina=disciplinas[1], unidade=unidade, codigo="1",
                     semestre="2026.2", professores=[professores[0]]))
        # Duas turmas da mesma matéria não podem duplicá-la no resultado.
        db.add(Turma(disciplina=disciplinas[0], unidade=unidade, codigo="extra",
                     semestre="2026.2", professores=[professores[0]]))
        for i, quantidade in enumerate([4, 3, 3, 4, 2, 0]):
            for j, usuario in enumerate(usuarios[:quantidade]):
                db.add(Avaliacao(usuario=usuario, professor=professores[i], disciplina=disciplinas[0],
                                 didatica=4, dificuldade=Dificuldade.MEDIO,
                                 chamada=(j % 2 == 0) if i == 3 else True,
                                 disponibiliza_material=True, qualidade_material=QualidadeMaterial.BOM,
                                 recomenda=(j < 2) if i == 3 else True))
        db.commit()
        print(json.dumps(dict(termo=termo, professores=[str(p.id) for p in professores],
                              disciplinas=[dict(id=str(d.id), codigo=d.codigo, nome=d.nome) for d in disciplinas]),
                         ensure_ascii=False))


if __name__ == "__main__":
    main()
