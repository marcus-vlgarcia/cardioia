"""Treina as duas abordagens e exporta resultados do conjunto de teste."""

import copy
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (average_precision_score, accuracy_score, classification_report,
                             ConfusionMatrixDisplay, confusion_matrix, precision_recall_curve)
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from dados import RESULTADOS, SEMENTE, carregar_particoes, baixar
from modelos import cnn_simples, classificador_resnet, extrator_resnet, normalizar_imagenet

EPOCAS = 10
LOTE = 128


def avaliar_escores(modelo, loader, device):
    modelo.eval()
    saidas, rotulos = [], []
    with torch.no_grad():
        for x, y in loader:
            saidas.append(modelo(x.to(device)).flatten().sigmoid().cpu())
            rotulos.append(y)
    return torch.cat(saidas).numpy(), torch.cat(rotulos).numpy()


def ajustar(modelo, loaders, device, taxa):
    otimizador = torch.optim.AdamW(modelo.parameters(), lr=taxa)
    perda = nn.BCEWithLogitsLoss()
    melhor, estado, historico = -1, None, []
    for epoca in range(EPOCAS):
        modelo.train()
        total = 0.0
        for x, y in loaders["train"]:
            otimizador.zero_grad()
            erro = perda(modelo(x.to(device)).flatten(), y.to(device, dtype=torch.float32))
            erro.backward()
            otimizador.step()
            total += erro.item() * len(y)
        scores, y = avaliar_escores(modelo, loaders["val"], device)
        ap = float(average_precision_score(y, scores))
        historico.append({"epoca": epoca + 1, "loss_treino": total / len(loaders["train"].dataset),
                          "ap_validacao": ap})
        print(f"Época {epoca + 1:02d} | AP validação {ap:.4f}", flush=True)
        if ap > melhor:
            melhor, estado = ap, copy.deepcopy(modelo.state_dict())
    modelo.load_state_dict(estado)
    scores, y = avaliar_escores(modelo, loaders["val"], device)
    p, r, limiares = precision_recall_curve(y, scores)
    f1 = 2 * p[:-1] * r[:-1] / np.maximum(p[:-1] + r[:-1], 1e-12)
    return float(limiares[np.argmax(f1)]), historico


def obter_features(loaders, device):
    extrator = extrator_resnet().to(device)
    vetores = {}
    with torch.no_grad():
        for split, loader in loaders.items():
            x_split, y_split = [], []
            for x, y in loader:
                x_split.append(extrator(normalizar_imagenet(x.to(device))).cpu())
                y_split.append(y)
            vetores[split] = TensorDataset(torch.cat(x_split), torch.cat(y_split))
            print(f"ResNet18 | atributos extraídos de {split}", flush=True)
    return vetores


def criar_loaders(datasets):
    return {split: DataLoader(dados, batch_size=LOTE, shuffle=split == "train",
                              generator=torch.Generator().manual_seed(SEMENTE))
            for split, dados in datasets.items()}


def metricas_teste(y, scores, limiar, historico):
    pred = (scores >= limiar).astype(int)
    return {
        "limiar": limiar, "acuracia": float(accuracy_score(y, pred)),
        "average_precision": float(average_precision_score(y, scores)),
        "matriz_confusao": confusion_matrix(y, pred, labels=[0, 1]).tolist(),
        "relatorio": classification_report(y, pred, labels=[0, 1], output_dict=True, zero_division=0),
        "historico": historico,
    }


def salvar_resultados(resultados):
    from evidencias import salvar_metricas

    fig, eixos = plt.subplots(1, 2, figsize=(11, 4.3), layout="constrained")
    for eixo, (nome, m) in zip(eixos, resultados["modelos"].items()):
        matriz = np.array(m["matriz_confusao"])
        ConfusionMatrixDisplay(matriz, display_labels=["Sem rótulo", "Com rótulo"]).plot(
            ax=eixo, colorbar=False, cmap="Blues")
        eixo.set(xlabel="Classe prevista", ylabel="Classe de referência",
                 title="CNN do zero" if nome == "cnn" else "ResNet18 pré-treinada")
    fig.suptitle("CardioIA | Cardiomegalia — matrizes de confusão no teste")
    fig.savefig(RESULTADOS / "matrizes_confusao.png", dpi=155)
    plt.close(fig)
    (RESULTADOS / "metricas.json").write_text(json.dumps(resultados, indent=2) + "\n")
    salvar_metricas(resultados)


def executar():
    torch.manual_seed(SEMENTE)
    torch.set_num_threads(4)
    device = torch.device("cuda" if torch.cuda.is_available() else
                          "mps" if torch.backends.mps.is_available() else "cpu")
    print("Dispositivo:", device, flush=True)
    arquivo = baixar()
    datasets = carregar_particoes(arquivo)
    contagens = {split: {"oficial": ds.total_oficial, "usadas": len(ds),
                         "positivas": int(ds.rotulos.sum())} for split, ds in datasets.items()}
    print(contagens, flush=True)
    RESULTADOS.mkdir(exist_ok=True)
    resultados = {"contagens": contagens, "semente": SEMENTE, "epocas": EPOCAS,
                  "dispositivo": str(device), "torch": str(torch.__version__), "modelos": {}}
    for nome in ("cnn", "resnet18"):
        print(f"Modelo: {nome}", flush=True)
        loaders = criar_loaders(datasets)
        if nome == "cnn":
            modelo, taxa = cnn_simples().to(device), 0.001
        else:
            loaders = criar_loaders(obter_features(loaders, device))
            modelo, taxa = classificador_resnet().to(device), 0.003
        limiar, historico = ajustar(modelo, loaders, device, taxa)
        scores, y = avaliar_escores(modelo, loaders["test"], device)
        resultados["modelos"][nome] = metricas_teste(y, scores, limiar, historico)
        torch.save({"estado": {k: v.cpu() for k, v in modelo.state_dict().items()},
                    "limiar": limiar}, RESULTADOS / f"{nome}.pt")
    salvar_resultados(resultados)
    return resultados


if __name__ == "__main__":
    executar()
