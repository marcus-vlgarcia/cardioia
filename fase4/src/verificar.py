"""Confere a consistência entre predições, métricas e arquivos da entrega."""

import csv
import json

import numpy as np
from sklearn.metrics import average_precision_score, confusion_matrix
import torch

from dados import RESULTADOS, RAIZ


def exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)


def executar():
    resumo = json.loads((RESULTADOS / "metricas.json").read_text())
    with (RESULTADOS / "predicoes_teste.csv").open(newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    rotulos = np.array([int(linha["rotulo"]) for linha in linhas])
    indices = {int(linha["indice_oficial"]): int(linha["rotulo"]) for linha in linhas}
    teste = resumo["contagens"]["test"]
    exigir(len(linhas) == len(indices) == teste["usadas"], "Índices de teste repetidos ou ausentes.")
    exigir(rotulos.sum() == teste["positivas"], "Total de positivos inconsistente.")

    for chave in ("modelos", "referencia_cb3cc82"):
        for nome, metrica in resumo[chave].items():
            coluna = nome if chave == "modelos" else f"{nome} (anterior)"
            scores = np.array([float(linha[coluna]) for linha in linhas], dtype=np.float32)
            exigir(np.isfinite(scores).all() and (0 <= scores).all() and (scores <= 1).all(),
                   f"Escore inválido em {coluna}.")
            previstos = scores >= metrica["limiar"]
            matriz = confusion_matrix(rotulos, previstos, labels=[0, 1]).tolist()
            exigir(matriz == metrica["matriz_confusao"], f"Matriz divergente em {coluna}.")
            exigir(np.isclose(average_precision_score(rotulos, scores), metrica["average_precision"]),
                   f"AP divergente em {coluna}.")
            pasta = RESULTADOS if chave == "modelos" else RESULTADOS / "referencia"
            pesos = torch.load(pasta / f"{nome}.pt", map_location="cpu", weights_only=True)
            exigir(pesos["limiar"] == metrica["limiar"], f"Limiar divergente em {coluna}.")

    with np.load(RESULTADOS / "amostras_demo.npz", allow_pickle=False) as amostras:
        exigir(amostras["imagens"].shape == (6, 64, 64), "Amostras do protótipo inválidas.")
        exigir(all(indices.get(int(i)) == int(y) for i, y in zip(amostras["indices"], amostras["rotulos"])),
               "Amostra do protótipo fora do teste.")

    notebooks = list((RAIZ / "notebooks").glob("*.ipynb"))
    exigir(len(notebooks) == 3, "A Fase 4 deve conter três notebooks.")
    for arquivo in notebooks:
        notebook = json.loads(arquivo.read_text())
        for celula in notebook["cells"]:
            if celula["cell_type"] == "code":
                exigir(celula["execution_count"] is not None, f"Célula não executada em {arquivo.name}.")
                exigir(not any(o["output_type"] == "error" for o in celula["outputs"]),
                       f"Erro registrado em {arquivo.name}.")
    for nome in ("metricas.png", "matrizes_confusao.png", "curva_precisao_recall.png"):
        exigir((RESULTADOS / nome).read_bytes().startswith(b"\x89PNG\r\n\x1a\n"),
               f"Evidência inválida: {nome}.")
    exigir((RAIZ / "output/pdf/relatorio_preprocessamento.pdf").read_bytes().startswith(b"%PDF"),
           "Relatório PDF inválido.")
    print("Fase 4: predições, métricas, pesos, amostras, notebooks e evidências consistentes.")


if __name__ == "__main__":
    executar()
