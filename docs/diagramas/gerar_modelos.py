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
    pdf.drawString(32, 17, "G7 - Avaliacao de Professores UnB | Modelo revisado em 19/09/2026")
    pdf.drawRightString(PAGE_WIDTH - 32, 17, "Issues #25 e #48 - ADR 07")


def build_logical_model():
    pdf = canvas.Canvas(str(OUTPUT_DIR / "modelo logico.pdf"), pagesize=landscape(A4), invariant=1)
    pdf.setTitle("Modelo logico - G7")
    pdf.setAuthor("G7 - Metodos de Desenvolvimento de Software")
    draw_title(pdf, "Modelo logico de dados", "SQLAlchemy + Alembic + PostgreSQL")

    draw_table(pdf, 30, 410, 220, "usuarios", [
        ("PK", "id", "UUID"), ("", "nome", "VARCHAR(100)"),
        ("UQ", "email", "VARCHAR(150)"), ("", "password_hash", "VARCHAR(255)"),
        ("", "email_confirmado", "BOOLEAN"), ("", "created_at", "TIMESTAMPTZ"),
    ])
    draw_table(pdf, 30, 280, 220, "unidades", [
        ("PK", "id", "UUID"), ("UQ1", "fonte", "VARCHAR(30)"),
        ("UQ1", "codigo", "VARCHAR(30)"),
        ("UQ", "identificador_externo", "VARCHAR(50) NULL"),
        ("", "nome", "VARCHAR(200)"),
    ])
    draw_table(pdf, 300, 390, 220, "professores", [
        ("PK", "id", "UUID"), ("", "nome", "VARCHAR(150)"),
        ("", "nome_normalizado", "VARCHAR(150)"),
        ("", "departamento", "VARCHAR(100)"), ("UQ", "siape", "VARCHAR(30) NULL"),
        ("UQ", "identidade_origem", "VARCHAR(255) NULL"),
        ("", "identidade_confirmada", "BOOLEAN"),
    ])
    draw_table(pdf, 300, 235, 220, "disciplinas", [
        ("PK", "id", "UUID"), ("UQ", "codigo", "VARCHAR(20)"),
        ("", "identificador_externo", "VARCHAR(50) NULL"),
        ("", "nome", "VARCHAR(150)"), ("", "nome_normalizado", "VARCHAR(150)"),
        ("", "departamento", "VARCHAR(100)"),
        ("", "creditos", "SMALLINT NULL"),
    ])
    draw_table(pdf, 30, 90, 220, "turmas", [
        ("PK", "id", "UUID"), ("FK/UQ1", "disciplina_id", "UUID"),
        ("FK/UQ1", "unidade_id", "UUID"), ("UQ1", "fonte", "VARCHAR(30)"),
        ("UQ1", "codigo", "VARCHAR(30)"), ("UQ1", "semestre", "VARCHAR(10)"),
        ("", "ativa", "BOOLEAN"), ("", "ultima_observacao_em", "TIMESTAMPTZ"),
    ])
    draw_table(pdf, 300, 130, 220, "turmas_professores", [
        ("PK/FK", "turma_id", "UUID"), ("PK/FK", "professor_id", "UUID"),
    ])
    draw_table(pdf, 560, 315, 250, "avaliacoes", [
        ("PK", "id", "UUID"), ("FK/UQ1", "usuario_id", "UUID"),
        ("FK/UQ1", "professor_id", "UUID"), ("FK/UQ1", "disciplina_id", "UUID"),
        ("CK", "didatica", "SMALLINT 1-5"), ("", "dificuldade", "ENUM"),
        ("", "chamada", "BOOLEAN"), ("", "disponibiliza_material", "BOOLEAN"),
        ("CK", "qualidade_material", "ENUM NULL"), ("", "recomenda", "BOOLEAN"),
        ("", "created_at", "TIMESTAMPTZ"), ("", "updated_at", "TIMESTAMPTZ"),
    ])

    draw_table(pdf, 560, 145, 250, "email_confirmation_tokens", [
        ("PK", "id", "UUID"), ("FK", "usuario_id", "UUID"),
        ("UQ", "token_hash", "VARCHAR(64)"), ("", "expires_at", "TIMESTAMPTZ"),
        ("", "used_at", "TIMESTAMPTZ NULL"), ("", "created_at", "TIMESTAMPTZ"),
    ])

    draw_note(pdf, 300, 35, 510, 86, "Relacionamentos e restricoes", [
        "professores N:N turmas; unidades e disciplinas 1:N turmas",
        "turmas UQ1: disciplina + fonte + unidade + semestre + codigo",
        "avaliacoes UQ1: usuario_id + professor_id + disciplina_id",
        "usuario 1:N tokens de confirmacao; hash unico com validade de 24 horas",
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
    draw_entity(pdf, 35, 250, 175, "Unidade", [
        "identificador", "fonte", "codigo", "id externo", "nome",
    ])
    draw_entity(pdf, 245, 410, 175, "Professor", [
        "identificador", "nome", "departamento", "SIAPE (opcional)",
        "identidade de origem", "identidade confirmada",
    ])
    draw_entity(pdf, 455, 390, 175, "Disciplina", [
        "identificador", "codigo", "id externo", "nome", "departamento",
        "creditos (opcional)",
    ])
    draw_entity(pdf, 245, 235, 175, "Turma", [
        "identificador", "fonte", "unidade", "disciplina", "codigo", "semestre",
        "ativa",
    ])
    draw_entity(pdf, 430, 80, 210, "Avaliacao", [
        "identificador", "usuario", "professor", "disciplina", "didatica (1 a 5)",
        "dificuldade", "faz chamada", "disponibiliza material",
        "qualidade do material (condicional)", "recomendacao", "datas de criacao e alteracao",
    ])
    draw_entity(pdf, 665, 245, 145, "Token de confirmacao", [
        "identificador", "usuario", "hash do token", "expira em", "usado em", "criado em",
    ])

    draw_note(pdf, 35, 95, 365, 125, "Cardinalidades", [
        "Um usuario realiza zero ou muitas avaliacoes.",
        "Um professor recebe avaliacoes e ministra zero ou muitas turmas.",
        "Uma disciplina recebe zero ou muitas avaliacoes e possui turmas.",
        "Cada unidade possui turmas; cada turma vincula zero ou muitos professores.",
        "Cada usuario avalia um par professor-disciplina no maximo uma vez.",
        "Um usuario possui zero ou muitos tokens de confirmacao de e-mail.",
    ])
    draw_note(pdf, 665, 405, 145, 90, "Escopo", [
        "7 entidades", "vinculo N:N", "avaliacao estruturada", "sem comentario livre",
        "sem dados academicos",
    ])
    draw_footer(pdf)
    pdf.save()


if __name__ == "__main__":
    build_logical_model()
    build_conceptual_model()
