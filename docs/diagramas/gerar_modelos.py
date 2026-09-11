"""Regenera os modelos conceitual e logico.

Dependencia de documentacao: ``python -m pip install reportlab``.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
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


def draw_table(pdf, x, y, width, title, rows, unique_rows=()):
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
        pdf.setFillColor(LIGHT_BLUE if index in unique_rows else (LIGHT_GRAY if index % 2 else colors.white))
        pdf.rect(x + 0.5, row_y, width - 1, row_height, fill=1, stroke=0)
        pdf.setFillColor(GOLD if key else MUTED)
        pdf.setFont("Helvetica-Bold", 6.7)
        pdf.drawString(x + 6, row_y + 5, key or "-")
        pdf.setFillColor(TEXT)
        pdf.setFont("Helvetica", 7.2)
        pdf.drawString(x + 34, row_y + 5, field)
        pdf.setFillColor(MUTED)
        pdf.drawRightString(x + width - 6, row_y + 5, data_type)

    return (x, y, width, height)


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
    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica", 7.5)
    for index, attribute in enumerate(attributes):
        pdf.drawString(x + 9, y + height - header_height - 12 - line_height * index, f"- {attribute}")
    return (x, y, width, height)


def connect(
    pdf,
    points,
    label,
    label_position,
    source_cardinality,
    target_cardinality,
    source_card_position,
    target_card_position,
):
    pdf.saveState()
    pdf.setStrokeColor(colors.HexColor("#7B8794"))
    pdf.setLineWidth(0.9)
    path = pdf.beginPath()
    path.moveTo(*points[0])
    for point in points[1:]:
        path.lineTo(*point)
    pdf.drawPath(path, stroke=1, fill=0)
    mid_x, mid_y = label_position
    label_width = stringWidth(label, "Helvetica-Bold", 7) + 12
    pdf.setFillColor(colors.white)
    pdf.rect(mid_x - label_width / 2, mid_y - 5, label_width, 11, fill=1, stroke=0)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawCentredString(mid_x, mid_y - 2, label)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica-Bold", 6.5)
    pdf.drawCentredString(*source_card_position, source_cardinality)
    pdf.drawCentredString(*target_card_position, target_cardinality)
    pdf.restoreState()


def draw_footer(pdf):
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 7)
    pdf.drawString(32, 17, "G7 - Avaliacao de Professores UnB | Modelo revisado em 11/09/2026")
    pdf.drawRightString(PAGE_WIDTH - 32, 17, "PR #55")


def build_logical_model():
    output = OUTPUT_DIR / "modelo logico.pdf"
    pdf = canvas.Canvas(str(output), pagesize=landscape(A4), invariant=1)
    pdf.setTitle("Modelo logico - G7")
    pdf.setAuthor("G7 - Metodos de Desenvolvimento de Software")
    draw_title(pdf, "Modelo logico de dados", "SQLAlchemy + PostgreSQL")

    boxes = {}
    boxes["departamento"] = draw_table(pdf, 30, 360, 175, "departamento", [
        ("PK", "id_dpto", "INTEGER"),
        ("UQ", "sigla", "VARCHAR(10)"),
        ("", "nome", "VARCHAR(150)"),
    ], unique_rows=(1,))
    boxes["disciplinas"] = draw_table(pdf, 250, 344, 180, "disciplinas", [
        ("PK", "id_disciplinas", "INTEGER"),
        ("FK", "id_departamento", "INTEGER"),
        ("UQ", "codigo", "VARCHAR(20)"),
        ("", "nome", "VARCHAR(150)"),
    ], unique_rows=(2,))
    boxes["turma"] = draw_table(pdf, 475, 312, 180, "turma", [
        ("PK", "id_turma", "INTEGER"),
        ("FK/UQ1", "id_disciplinas", "INTEGER"),
        ("FK", "id_professor", "INTEGER"),
        ("UQ1", "cod_turma", "VARCHAR(10)"),
        ("UQ1", "semestre", "VARCHAR(10)"),
        ("", "horario", "VARCHAR NULL"),
    ], unique_rows=(1, 3, 4))
    boxes["professor"] = draw_table(pdf, 30, 72, 175, "professor", [
        ("PK", "id_professor", "INTEGER"),
        ("FK/UQ1", "id_departamento", "INTEGER"),
        ("UQ1", "nome", "VARCHAR(150)"),
        ("", "lattes", "VARCHAR(255) NULL"),
        ("", "email", "VARCHAR(150) NULL"),
    ], unique_rows=(1, 2))
    boxes["usuario"] = draw_table(pdf, 250, 72, 180, "usuario", [
        ("PK", "matricula", "INTEGER"),
        ("UQ", "email", "VARCHAR(150)"),
        ("", "senha_hash", "VARCHAR(255)"),
    ], unique_rows=(1,))
    boxes["avaliacao"] = draw_table(pdf, 475, 42, 180, "avaliacao", [
        ("PK", "id_review", "INTEGER"),
        ("FK/UQ1", "id_usuario", "INTEGER"),
        ("FK/UQ1", "id_turma", "INTEGER"),
        ("", "didatica", "INTEGER"),
        ("", "qualidade_material", "INTEGER NULL"),
        ("", "chamada", "INTEGER"),
        ("", "recomenda", "BOOLEAN"),
        ("", "disponibiliza_material", "BOOLEAN"),
        ("", "dificuldade", "INTEGER"),
        ("", "comentario", "TEXT NULL"),
    ], unique_rows=(1, 2))
    boxes["estuda"] = draw_table(pdf, 262, 236, 155, "estuda", [
        ("PK/FK", "matricula", "INTEGER"),
        ("PK/FK", "id_disciplinas", "INTEGER"),
    ])

    connect(pdf, [(205, 396), (250, 396)], "oferece", (227, 405), "1", "0..N", (211, 386), (243, 386))
    connect(pdf, [(117, 360), (117, 176)], "pertence", (117, 267), "1", "0..N", (128, 350), (132, 181))
    connect(pdf, [(430, 396), (475, 396)], "possui", (452, 405), "1", "0..N", (436, 386), (468, 386))
    connect(pdf, [(205, 124), (225, 124), (225, 300), (455, 300), (455, 344), (475, 344)], "ministra", (410, 309), "1", "0..N", (211, 114), (464, 333))
    connect(pdf, [(565, 312), (565, 226)], "recebe", (565, 267), "1", "0..N", (576, 302), (579, 231))
    connect(pdf, [(430, 108), (475, 108)], "realiza", (452, 117), "1", "0..N", (436, 98), (468, 98))
    connect(pdf, [(339, 144), (339, 236)], "registra", (339, 189), "1", "0..N", (350, 151), (356, 228))
    connect(pdf, [(339, 344), (339, 292)], "cursada", (339, 316), "1", "0..N", (350, 334), (356, 298))

    pdf.setFillColor(LIGHT_BLUE)
    pdf.roundRect(675, 350, 135, 94, 6, fill=1, stroke=0)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(685, 428, "Legenda")
    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica", 7)
    legend = [
        "PK: chave primaria",
        "FK: chave estrangeira",
        "UQ: chave unica simples",
        "UQ1: mesma chave composta",
        "NULL: campo opcional",
    ]
    for index, item in enumerate(legend):
        pdf.drawString(685, 412 - 13 * index, item)

    draw_footer(pdf)
    pdf.save()


def build_conceptual_model():
    output = OUTPUT_DIR / "modelo conceitual.pdf"
    pdf = canvas.Canvas(str(output), pagesize=landscape(A4), invariant=1)
    pdf.setTitle("Modelo conceitual - G7")
    pdf.setAuthor("G7 - Metodos de Desenvolvimento de Software")
    draw_title(pdf, "Modelo conceitual de dados", "Entidades, atributos e cardinalidades")

    boxes = {}
    boxes["departamento"] = draw_entity(pdf, 35, 370, 165, "Departamento", ["identificador", "sigla", "nome"])
    boxes["disciplina"] = draw_entity(pdf, 250, 370, 165, "Disciplina", ["identificador", "codigo", "nome"])
    boxes["turma"] = draw_entity(pdf, 465, 350, 165, "Turma", ["identificador", "codigo da turma", "semestre", "horario"])
    boxes["professor"] = draw_entity(pdf, 35, 85, 165, "Professor", ["identificador", "nome", "Lattes (opcional)", "e-mail (opcional)"])
    boxes["usuario"] = draw_entity(pdf, 250, 85, 165, "Usuario", ["matricula", "e-mail", "senha protegida"])
    boxes["avaliacao"] = draw_entity(pdf, 465, 45, 165, "Avaliacao", [
        "identificador", "didatica", "qualidade do material", "chamada",
        "recomendacao", "material disponivel", "dificuldade", "comentario",
    ])
    boxes["estuda"] = draw_entity(pdf, 270, 238, 125, "Estuda", ["usuario", "disciplina"])

    connect(pdf, [(200, 421), (250, 421)], "oferece", (225, 430), "1", "0..N", (207, 411), (243, 411))
    connect(pdf, [(117, 370), (117, 178)], "possui", (117, 272), "1", "0..N", (128, 360), (132, 183))
    connect(pdf, [(415, 421), (465, 421)], "possui", (440, 430), "1", "0..N", (422, 411), (458, 411))
    connect(pdf, [(200, 137), (220, 137), (220, 325), (445, 325), (445, 382), (465, 382)], "ministra", (333, 334), "1", "0..N", (207, 127), (454, 371))
    connect(pdf, [(547, 350), (547, 194)], "avaliada em", (547, 267), "1", "0..N", (558, 340), (562, 199))
    connect(pdf, [(415, 129), (465, 129)], "realiza", (440, 138), "1", "0..N", (422, 119), (458, 119))
    connect(pdf, [(332, 164), (332, 238)], "cursa", (332, 199), "1", "0..N", (343, 171), (349, 230))
    connect(pdf, [(332, 370), (332, 303)], "inclui", (332, 333), "1", "0..N", (343, 360), (349, 309))

    pdf.setFillColor(LIGHT_BLUE)
    pdf.roundRect(675, 365, 135, 68, 6, fill=1, stroke=0)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(685, 416, "Leitura")
    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica", 7)
    pdf.drawString(685, 401, "1: exatamente um")
    pdf.drawString(685, 388, "0..N: zero ou muitos")
    pdf.drawString(685, 375, "Estuda: associacao N:N")

    draw_footer(pdf)
    pdf.save()


if __name__ == "__main__":
    build_logical_model()
    build_conceptual_model()
