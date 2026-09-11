"""Regenera os modelos conceitual e logico do banco de dados.

Dependencia de documentacao: ``python -m pip install reportlab``.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path(__file__).resolve().parent
PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)

NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#2D6A9F")
LIGHT_BLUE = colors.HexColor("#EAF3FA")
LIGHT_GRAY = colors.HexColor("#F5F7F9")
GOLD = colors.HexColor("#D9A441")
TEXT = colors.HexColor("#1F2933")
MUTED = colors.HexColor("#52606D")


def draw_title(pdf, title, subtitle):
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawString(32, PAGE_HEIGHT - 34, title)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 8.5)
    pdf.drawRightString(PAGE_WIDTH - 32, PAGE_HEIGHT - 31, subtitle)
    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.line(32, PAGE_HEIGHT - 44, PAGE_WIDTH - 32, PAGE_HEIGHT - 44)


def draw_table(pdf, x, y, width, title, rows):
    header_height = 24
    row_height = 16
    height = header_height + row_height * len(rows)
    pdf.setFillColor(colors.white)
    pdf.setStrokeColor(NAVY)
    pdf.roundRect(x, y, width, height, 5, fill=1, stroke=1)
    pdf.setFillColor(NAVY)
    pdf.roundRect(x, y + height - header_height, width, header_height, 5, fill=1, stroke=0)
    pdf.rect(x, y + height - header_height, width, 6, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x + 8, y + height - 16, title)

    for index, (key, field, data_type) in enumerate(rows):
        row_y = y + height - header_height - row_height * (index + 1)
        pdf.setFillColor(LIGHT_GRAY if index % 2 else colors.white)
        pdf.rect(x + 0.5, row_y, width - 1, row_height, fill=1, stroke=0)
        pdf.setFillColor(GOLD if key else MUTED)
        pdf.setFont("Helvetica-Bold", 6.5)
        pdf.drawString(x + 6, row_y + 5, key or "-")
        pdf.setFillColor(TEXT)
        pdf.setFont("Helvetica", 7.2)
        pdf.drawString(x + 45, row_y + 5, field)
        pdf.setFillColor(MUTED)
        pdf.drawRightString(x + width - 6, row_y + 5, data_type)


def draw_entity(pdf, x, y, width, title, attributes):
    header_height = 25
    line_height = 14
    height = header_height + 12 + line_height * len(attributes)
    pdf.setFillColor(colors.white)
    pdf.setStrokeColor(BLUE)
    pdf.setLineWidth(1.2)
    pdf.roundRect(x, y, width, height, 7, fill=1, stroke=1)
    pdf.setFillColor(BLUE)
    pdf.roundRect(x, y + height - header_height, width, header_height, 7, fill=1, stroke=0)
    pdf.rect(x, y + height - header_height, width, 7, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(x + width / 2, y + height - 17, title)
    # Repaint the body so the rounded border path cannot leave internal seams on renderers.
    pdf.setFillColor(colors.white)
    pdf.rect(x + 1, y + 1, width - 2, height - header_height - 1, fill=1, stroke=0)
    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica", 7.5)
    for index, attribute in enumerate(attributes):
        pdf.drawString(x + 9, y + height - header_height - 12 - line_height * index, f"- {attribute}")


def draw_note(pdf, x, y, width, height, title, lines):
    pdf.setFillColor(LIGHT_BLUE)
    pdf.roundRect(x, y, width, height, 6, fill=1, stroke=0)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(x + 10, y + height - 18, title)
    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica", 7.3)
    for index, line in enumerate(lines):
        pdf.drawString(x + 10, y + height - 34 - 14 * index, line)


def draw_footer(pdf):
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 7)
    pdf.drawString(32, 17, "G7 - Avaliacao de Professores UnB | Modelo revisado em 11/09/2026")
    pdf.drawRightString(PAGE_WIDTH - 32, 17, "PR #55")


def build_logical_model():
    pdf = canvas.Canvas(str(OUTPUT_DIR / "modelo logico.pdf"), pagesize=landscape(A4), invariant=1)
    pdf.setTitle("Modelo logico - G7")
    pdf.setAuthor("G7 - Metodos de Desenvolvimento de Software")
    draw_title(pdf, "Modelo logico de dados", "SQLAlchemy + Alembic + PostgreSQL")

    draw_table(pdf, 30, 385, 220, "usuarios", [
        ("PK", "id", "UUID"), ("", "nome", "VARCHAR(100)"),
        ("UQ", "email", "VARCHAR(150)"), ("", "password_hash", "VARCHAR(255)"),
        ("", "email_confirmado", "BOOLEAN"), ("", "created_at", "TIMESTAMPTZ"),
    ])
    draw_table(pdf, 300, 433, 220, "professores", [
        ("PK", "id", "UUID"), ("", "nome", "VARCHAR(150)"),
        ("", "departamento", "VARCHAR(100)"),
    ])
    draw_table(pdf, 300, 270, 220, "disciplinas", [
        ("PK", "id", "UUID"), ("UQ", "codigo", "VARCHAR(20)"),
        ("", "nome", "VARCHAR(150)"), ("", "departamento", "VARCHAR(100)"),
        ("", "creditos", "SMALLINT NULL"),
    ])
    draw_table(pdf, 30, 245, 220, "turmas", [
        ("PK", "id", "UUID"), ("FK/UQ1", "disciplina_id", "UUID"),
        ("FK/UQ1", "professor_id", "UUID"), ("UQ1", "semestre", "VARCHAR(10)"),
    ])
    draw_table(pdf, 560, 315, 250, "avaliacoes", [
        ("PK", "id", "UUID"), ("FK/UQ1", "usuario_id", "UUID"),
        ("FK/UQ1", "professor_id", "UUID"), ("FK/UQ1", "disciplina_id", "UUID"),
        ("CK", "didatica", "SMALLINT 1-5"), ("", "dificuldade", "ENUM"),
        ("", "chamada", "BOOLEAN"), ("", "disponibiliza_material", "BOOLEAN"),
        ("CK", "qualidade_material", "ENUM NULL"), ("", "recomenda", "BOOLEAN"),
        ("", "created_at", "TIMESTAMPTZ"), ("", "updated_at", "TIMESTAMPTZ"),
    ])

    draw_note(pdf, 300, 80, 510, 145, "Relacionamentos e restricoes", [
        "usuarios 1:N avaliacoes; professores 1:N turmas e avaliacoes",
        "disciplinas 1:N turmas e avaliacoes",
        "turmas UQ1: disciplina_id + professor_id + semestre",
        "avaliacoes UQ1: usuario_id + professor_id + disciplina_id",
        "qualidade_material e obrigatoria somente quando ha material disponivel",
        "Nao armazenar matricula, CPF, historico academico ou comentario livre",
    ])
    draw_note(pdf, 30, 80, 220, 115, "Legenda", [
        "PK: chave primaria", "FK: chave estrangeira", "UQ: chave unica",
        "UQ1: mesma chave composta", "CK: check constraint",
    ])
    draw_footer(pdf)
    pdf.save()


def build_conceptual_model():
    pdf = canvas.Canvas(
        str(OUTPUT_DIR / "modelo conceitual.pdf"), pagesize=landscape(A4), invariant=1
    )
    pdf.setTitle("Modelo conceitual - G7")
    pdf.setAuthor("G7 - Metodos de Desenvolvimento de Software")
    draw_title(pdf, "Modelo conceitual de dados", "Entidades, atributos e cardinalidades")

    draw_entity(pdf, 35, 390, 175, "Usuario", [
        "identificador", "nome", "e-mail institucional", "senha protegida",
        "e-mail confirmado", "data de criacao",
    ])
    draw_entity(pdf, 245, 430, 175, "Professor", ["identificador", "nome", "departamento"])
    draw_entity(pdf, 455, 390, 175, "Disciplina", [
        "identificador", "codigo", "nome", "departamento", "creditos (opcional)",
    ])
    draw_entity(pdf, 245, 255, 175, "Turma", [
        "identificador", "disciplina", "professor", "semestre",
    ])
    draw_entity(pdf, 455, 95, 250, "Avaliacao", [
        "identificador", "usuario", "professor", "disciplina", "didatica (1 a 5)",
        "dificuldade", "faz chamada", "disponibiliza material",
        "qualidade do material (condicional)", "recomendacao", "datas de criacao e alteracao",
    ])

    draw_note(pdf, 35, 95, 365, 125, "Cardinalidades", [
        "Um usuario realiza zero ou muitas avaliacoes.",
        "Um professor recebe zero ou muitas avaliacoes e ministra turmas.",
        "Uma disciplina recebe zero ou muitas avaliacoes e possui turmas.",
        "Cada turma vincula exatamente uma disciplina e um professor.",
        "Cada usuario avalia um par professor-disciplina no maximo uma vez.",
    ])
    draw_note(pdf, 665, 405, 145, 90, "Escopo", [
        "5 entidades", "avaliacao estruturada", "sem comentario livre",
        "sem dados academicos",
    ])
    draw_footer(pdf)
    pdf.save()


if __name__ == "__main__":
    build_logical_model()
    build_conceptual_model()
