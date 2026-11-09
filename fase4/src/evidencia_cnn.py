"""Gera o print da comparação e estima a variação dos ganhos por paciente."""

import csv
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from comparar_cnn import ler_pacientes
from dados import RESULTADOS, SEMENTE, baixar, carregar_particoes


def metricas(matrizes):
    vn, fp, fn, vp = matrizes.T
    acuracia = (vn + vp) / (vn + fp + fn + vp)
    recall = vp / (vp + fn)
    balanceada = (recall + vn / (vn + fp)) / 2
    f1 = 2 * vp / (2 * vp + fp + fn)
    return np.column_stack((acuracia, balanceada, recall, f1))


def intervalos_por_paciente(rotulos, grupos, decisoes):
    quantidade = int(grupos.max()) + 1
    matrizes = np.array([
        np.bincount(4 * grupos + 2 * rotulos + decisao, minlength=4 * quantidade).reshape(-1, 4)
        for decisao in decisoes
    ])
    rng = np.random.default_rng(SEMENTE)
    diferencas = []
    # Sorteia pacientes inteiros e compara os dois modelos nos mesmos sorteios.
    for _ in range(20):
        amostras = rng.integers(quantidade, size=(100, quantidade))
        referencia, candidata = (metricas(m[amostras].sum(axis=1)) for m in matrizes)
        diferencas.append(candidata - referencia)
    return np.quantile(np.concatenate(diferencas), [0.025, 0.975], axis=0).T


def executar():
    caminho = RESULTADOS / "comparacao_cnn.json"
    registro = json.loads(caminho.read_text())
    with (RESULTADOS / "predicoes_comparacao_cnn.csv").open(newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    pacientes = ler_pacientes(carregar_particoes(baixar()))["test"]
    _, grupos = np.unique([pacientes[int(linha["indice_oficial"])] for linha in linhas],
                          return_inverse=True)
    rotulos = np.array([int(linha["rotulo"]) for linha in linhas])
    nomes = ("referencia", "candidata")
    decisoes = [
        np.array([float(linha[nome]) for linha in linhas], dtype=np.float32)
        >= registro["teste"][nome]["limiar"] for nome in nomes
    ]
    chaves = ("acuracia", "acuracia_balanceada", "recall_positivo", "f1_positivo")
    registro["ic95_delta_bootstrap_por_paciente"] = dict(zip(
        chaves, intervalos_por_paciente(rotulos, grupos, decisoes).tolist()))
    caminho.write_text(json.dumps(registro, indent=2) + "\n")

    antes, depois = (registro["teste"][nome] for nome in nomes)
    valores = metricas(np.array([m["matriz_confusao"] for m in (antes, depois)]).reshape(-1, 4))
    rotulos_metricas = ["Acurácia", "Acurácia balanceada", "Recall positivo", "F1 positivo"]
    fig, eixo = plt.subplots(figsize=(10, 4.2), layout="constrained")
    posicoes = np.arange(len(rotulos_metricas))
    for offset, linha, legenda, cor in zip(
        (-.18, .18), valores, ("CNN de referência", "CNN com mais negativos"), ("#658594", "#155672")
    ):
        barras = eixo.barh(posicoes + offset, 100 * linha, height=.32, label=legenda, color=cor)
        eixo.bar_label(barras, labels=[f"{100*v:.1f}%".replace(".", ",") for v in linha], padding=4)
    eixo.set(yticks=posicoes, yticklabels=rotulos_metricas, xlim=(0, 106), xlabel="Porcentagem",
             title="CardioIA | Comparação da CNN com separação por paciente")
    eixo.invert_yaxis()
    eixo.legend(loc="lower right")
    fig.savefig(RESULTADOS / "comparacao_cnn.png", dpi=165)
    plt.close(fig)


if __name__ == "__main__":
    executar()
