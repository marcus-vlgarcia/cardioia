"""Gera os dois relatórios paginados da Fase 3 a partir dos arquivos Markdown."""

import re
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


FASE3 = Path(__file__).resolve().parents[1]
SAIDA = FASE3 / "output" / "pdf"


def formatar_inline(texto):
    texto = escape(texto)
    texto = re.sub(r"\[([^]]+)\]\((https?://[^)]+)\)",
                   r'<a href="\2" color="#c2185b">\1</a>', texto)
    texto = re.sub(r"\[([^]]+)\]\((?!https?://)[^)]+\)", r"\1", texto)
    texto = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', texto)
    texto = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", texto)
    return texto


def rodape(canvas, documento):
    canvas.saveState()
    largura, _ = A4
    canvas.setStrokeColor(colors.HexColor("#eeeeee"))
    canvas.line(2 * cm, 1.55 * cm, largura - 2 * cm, 1.55 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(2 * cm, 1.15 * cm, "CardioIA - PulseIA | FIAP | Fase 3")
    canvas.drawRightString(largura - 2 * cm, 1.15 * cm, f"Página {documento.page}")
    canvas.restoreState()


def estilos():
    base = getSampleStyleSheet()
    return {
        "titulo": ParagraphStyle(
            "Titulo",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=27,
            textColor=colors.HexColor("#ed145b"),
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "subtitulo": ParagraphStyle(
            "Subtitulo",
            parent=base["Normal"],
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#555555"),
            spaceAfter=20,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#ad1245"),
            spaceBefore=13,
            spaceAfter=7,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#333333"),
            spaceBefore=9,
            spaceAfter=5,
        ),
        "corpo": ParagraphStyle(
            "Corpo",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12.5,
            textColor=colors.HexColor("#222222"),
            alignment=4,
            spaceAfter=5,
        ),
        "lista": ParagraphStyle(
            "Lista",
            parent=base["BodyText"],
            fontSize=9.3,
            leading=12.2,
            textColor=colors.HexColor("#222222"),
            leftIndent=12,
            firstLineIndent=-9,
            spaceAfter=3,
        ),
    }


def ler_blocos(caminho):
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    blocos = []
    paragrafo = []
    lista = []
    tabela = []

    def descarregar_paragrafo():
        if paragrafo:
            blocos.append(("p", " ".join(paragrafo)))
            paragrafo.clear()

    def descarregar_lista():
        if lista:
            blocos.append(("lista", list(lista)))
            lista.clear()

    def descarregar_tabela():
        if tabela:
            if len(tabela) > 1 and all(set(celula) <= {"-", ":", " "} for celula in tabela[1]):
                del tabela[1]
            blocos.append(("tabela", list(tabela)))
            tabela.clear()

    for linha in linhas[1:]:
        limpa = linha.strip()
        if limpa.startswith("## "):
            descarregar_paragrafo(); descarregar_lista(); descarregar_tabela()
            blocos.append(("h2", limpa[3:]))
        elif limpa.startswith("### "):
            descarregar_paragrafo(); descarregar_lista(); descarregar_tabela()
            blocos.append(("h3", limpa[4:]))
        elif limpa.startswith("| ") and limpa.endswith(" |"):
            descarregar_paragrafo(); descarregar_lista()
            tabela.append([c.strip() for c in limpa.strip("|").split("|")])
        elif re.match(r"^(?:\d+\.|-)\s+", limpa):
            descarregar_paragrafo(); descarregar_tabela()
            lista.append(re.sub(r"^(?:\d+\.|-)\s+", "", limpa))
        elif not limpa:
            descarregar_paragrafo(); descarregar_lista(); descarregar_tabela()
        else:
            descarregar_tabela()
            if lista:
                lista[-1] += " " + limpa
            else:
                paragrafo.append(limpa)
    descarregar_paragrafo(); descarregar_lista(); descarregar_tabela()
    return blocos


def gerar(entrada, saida, titulo, minimo_paginas):
    estilos_pdf = estilos()
    historia = [
        Spacer(1, 0.7 * cm),
        Paragraph(titulo, estilos_pdf["titulo"]),
        Paragraph(
            "Projeto CardioIA - Grupo PulseIA<br/>Fase 3: Monitoramento Contínuo - IoT no Pulso do Paciente",
            estilos_pdf["subtitulo"],
        ),
    ]

    for tipo, conteudo in ler_blocos(entrada):
        if tipo in {"h2", "h3", "p"}:
            estilo = estilos_pdf["corpo"] if tipo == "p" else estilos_pdf[tipo]
            historia.append(Paragraph(formatar_inline(conteudo), estilo))
        elif tipo == "lista":
            for item in conteudo:
                historia.append(Paragraph("- " + formatar_inline(item), estilos_pdf["lista"]))
            historia.append(Spacer(1, 3))
        elif tipo == "tabela":
            dados = [[Paragraph(formatar_inline(c), estilos_pdf["lista"]) for c in linha] for linha in conteudo]
            tabela_pdf = Table(dados, colWidths=[5.0 * cm, 11.2 * cm] if len(dados[0]) == 2 else None,
                               repeatRows=1, hAlign="LEFT")
            tabela_pdf.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ed145b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafafa")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            historia.extend([tabela_pdf, Spacer(1, 8)])

    documento = SimpleDocTemplate(
        str(saida), pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=1.8 * cm, bottomMargin=2 * cm,
        title=titulo, author="Grupo PulseIA",
    )
    documento.build(historia, onFirstPage=rodape, onLaterPages=rodape)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    gerar(
        FASE3 / "docs/relatorio_edge.md",
        SAIDA / "relatorio_edge_computing.pdf",
        "Relatório de Edge Computing",
        1,
    )
    gerar(
        FASE3 / "docs/relatorio_mqtt_dashboard.md",
        SAIDA / "relatorio_mqtt_dashboard.pdf",
        "Relatório de MQTT e Dashboard",
        2,
    )


if __name__ == "__main__":
    main()
