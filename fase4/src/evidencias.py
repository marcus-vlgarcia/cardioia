"""Gera a imagem de comparação a partir das métricas registradas."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTADOS = Path(__file__).resolve().parents[1] / "resultados"


def salvar_metricas(resultado, pasta=RESULTADOS):
    nomes = {"cnn": "CNN do zero", "resnet18": "ResNet18 · Transfer Learning"}
    linhas = []
    for nome, modelo in resultado["modelos"].items():
        positiva = modelo["relatorio"]["1"]
        linhas.append([nomes[nome], *[f"{v:.3f}" for v in (
            modelo["acuracia"], positiva["precision"], positiva["recall"],
            positiva["f1-score"], modelo["average_precision"])]])
    teste = resultado["contagens"]["test"]
    base = 1 - teste["positivas"] / teste["usadas"]
    fig, ax = plt.subplots(figsize=(11, 3.2), facecolor="#f1f6f7")
    ax.axis("off")
    ax.text(0.02, 0.93, "CardioIA  |  Comparação no teste reservado",
            fontsize=19, weight="bold", color="#103e53", transform=ax.transAxes)
    ax.text(0.02, 0.76, f'{teste["usadas"]:,} exames · {teste["positivas"]} com rótulo de cardiomegalia',
            fontsize=12, color="#385b6a", transform=ax.transAxes)
    tabela = ax.table(cellText=linhas, colLabels=["Modelo", "Acurácia", "Precisão¹",
                       "Recall¹", "F1¹", "AP"], colWidths=[.30, .14, .14, .14, .14, .14],
                       cellLoc="center", bbox=[0.02, 0.28, 0.96, 0.37])
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    for (linha, coluna), celula in tabela.get_celld().items():
        celula.set_edgecolor("#d0dde0")
        celula.set_facecolor("#103e53" if linha == 0 else "white")
        if linha == 0:
            celula.get_text().set_color("white")
            celula.get_text().set_weight("bold")
    ax.text(0.02, 0.14, f"¹ Classe com rótulo. AP = Average Precision. Acurácia da classe majoritária: {base:.3f}.",
            fontsize=9.5, color="#385b6a", transform=ax.transAxes)
    fig.savefig(pasta / "metricas.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    salvar_metricas(json.loads((RESULTADOS / "metricas.json").read_text()))
