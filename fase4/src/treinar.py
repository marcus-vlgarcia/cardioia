"""Treina as duas abordagens e exporta resultados do conjunto de teste."""

import copy
import csv
import json
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (average_precision_score, accuracy_score, classification_report,
                             ConfusionMatrixDisplay, confusion_matrix, precision_recall_curve,
                             balanced_accuracy_score, roc_auc_score)
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision.transforms.functional import affine
from torchvision.transforms import InterpolationMode

from dados import RESULTADOS, SEMENTE, carregar_particoes, baixar
from modelos import cnn_simples, ResNetAdaptada, carregar_prototipo

EPOCAS = {"cnn": 16, "resnet18": 8}
LOTE = 128


def avaliar_escores(modelo, loader, device):
    modelo.eval()
    saidas, rotulos = [], []
    with torch.no_grad():
        for x, y in loader:
            saidas.append(modelo(x.to(device)).flatten().sigmoid().cpu())
            rotulos.append(y)
    return torch.cat(saidas).numpy(), torch.cat(rotulos).numpy()


def aumentar(x, rng):
    # Transformações leves de aquisição, sem espelhar a anatomia.
    x = affine(x, angle=rng.uniform(-4, 4), translate=[rng.randint(-2, 2) for _ in range(2)],
               scale=rng.uniform(0.96, 1.04), shear=[0, 0],
               interpolation=InterpolationMode.BILINEAR)
    return (x * rng.uniform(0.9, 1.1)).clamp(0, 1)


def ajustar(modelo, loaders, device, nome):
    if nome == "cnn":
        grupos = [{"params": modelo.parameters(), "lr": 0.001}]
    else:
        grupos = [{"params": modelo.extrator.layer4.parameters(), "lr": 0.0002},
                  {"params": modelo.saida.parameters(), "lr": 0.001}]
    otimizador = torch.optim.AdamW(grupos)
    agenda = torch.optim.lr_scheduler.CosineAnnealingLR(otimizador, T_max=EPOCAS[nome])
    rng = random.Random(SEMENTE)
    perda = nn.BCEWithLogitsLoss()
    melhor, estado, historico = -1, None, []
    for epoca in range(EPOCAS[nome]):
        modelo.train()
        total = 0.0
        for x, y in loaders["train"]:
            otimizador.zero_grad()
            erro = perda(modelo(aumentar(x.to(device), rng)).flatten(), y.to(device, dtype=torch.float32))
            erro.backward()
            otimizador.step()
            total += erro.item() * len(y)
        agenda.step()
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


def criar_loaders(datasets):
    return {split: DataLoader(dados, batch_size=LOTE, shuffle=split == "train",
                              generator=torch.Generator().manual_seed(SEMENTE))
            for split, dados in datasets.items()}


def metricas_teste(y, scores, limiar, historico):
    pred = (scores >= limiar).astype(int)
    return {
        "limiar": limiar, "acuracia": float(accuracy_score(y, pred)),
        "average_precision": float(average_precision_score(y, scores)),
        "acuracia_balanceada": float(balanced_accuracy_score(y, pred)),
        "roc_auc": float(roc_auc_score(y, scores)),
        "matriz_confusao": confusion_matrix(y, pred, labels=[0, 1]).tolist(),
        "relatorio": classification_report(y, pred, labels=[0, 1], output_dict=True, zero_division=0),
        "historico": historico,
    }


def salvar_resultados(resultados, escores, teste):
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
    with (RESULTADOS / "predicoes_teste.csv").open("w", newline="") as arquivo:
        writer = csv.writer(arquivo, lineterminator="\n")
        writer.writerow(["indice_oficial", "rotulo", *escores])
        writer.writerows(zip(teste.indices, teste.rotulos, *escores.values()))
    fig, eixo = plt.subplots(figsize=(7, 5), layout="constrained")
    for nome, scores in escores.items():
        precisao, recall, _ = precision_recall_curve(teste.rotulos, scores)
        ap = average_precision_score(teste.rotulos, scores)
        eixo.plot(recall, precisao, label=f"{nome} · AP {ap:.3f}")
    eixo.axhline(teste.rotulos.mean(), color="gray", linestyle="--", label="Prevalência do rótulo")
    eixo.set(xlabel="Recall", ylabel="Precisão", xlim=(0, 1), ylim=(0, 1),
             title="Precisão × recall no teste reservado")
    eixo.legend()
    fig.savefig(RESULTADOS / "curva_precisao_recall.png", dpi=155)
    plt.close(fig)



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
                  "dispositivo": str(device), "torch": str(torch.__version__),
                  "modelos": {}, "referencia_cb3cc82": {}}
    escores = {}
    for nome in ("cnn", "resnet18"):
        print(f"Modelo: {nome}", flush=True)
        torch.manual_seed(SEMENTE)
        loaders = criar_loaders(datasets)
        modelo = (cnn_simples() if nome == "cnn" else ResNetAdaptada()).to(device)
        limiar, historico = ajustar(modelo, loaders, device, nome)
        scores, y = avaliar_escores(modelo, loaders["test"], device)
        resultados["modelos"][nome] = metricas_teste(y, scores, limiar, historico)
        escores[nome] = scores
        estado = modelo.cpu().state_dict() if nome == "cnn" else modelo.cpu().estado_adaptado()
        torch.save({"estado": estado, "limiar": limiar,
                    "arquitetura": "cnn" if nome == "cnn" else "resnet18_adaptada"},
                   RESULTADOS / f"{nome}.pt")
        anterior, limiar_anterior = carregar_prototipo(RESULTADOS / "referencia", nome, device)
        scores, y = avaliar_escores(anterior, loaders["test"], device)
        resultados["referencia_cb3cc82"][nome] = metricas_teste(y, scores, limiar_anterior, [])
        escores[f"{nome} (anterior)"] = scores
    salvar_resultados(resultados, escores, datasets["test"])
    return resultados


if __name__ == "__main__":
    executar()
