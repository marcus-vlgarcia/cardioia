"""Arquiteturas e inferência usadas no treinamento e na demonstração."""

from pathlib import Path

import torch
from torch import nn
from torchvision.models import ResNet18_Weights, resnet18

from dados import baixar_verificado


def cnn_simples():
    return nn.Sequential(
        nn.Conv2d(3, 16, 3, padding=1), nn.BatchNorm2d(16), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(16, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
        nn.Flatten(), nn.Dropout(0.25), nn.Linear(64 * 7 * 7, 1),
    )


def extrator_resnet():
    pesos = ResNet18_Weights.IMAGENET1K_V1
    destino = Path(torch.hub.get_dir()) / "checkpoints" / Path(pesos.url).name
    baixar_verificado(pesos.url, destino, "sha256",
                      "f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec")
    rede = resnet18(weights=pesos)
    rede.fc = nn.Identity()
    return rede.requires_grad_(False).eval()


def normalizar_imagenet(x):
    media = x.new_tensor([0.485, 0.456, 0.406])[None, :, None, None]
    desvio = x.new_tensor([0.229, 0.224, 0.225])[None, :, None, None]
    return (x - media) / desvio


def classificador_resnet():
    return nn.Linear(512, 1)


def carregar_prototipo(pasta, nome):
    checkpoint = torch.load(pasta / f"{nome}.pt", map_location="cpu", weights_only=True)
    if nome == "cnn":
        modelo = cnn_simples()
        modelo.load_state_dict(checkpoint["estado"])
        return modelo.eval(), checkpoint["limiar"]
    cabeca = classificador_resnet()
    cabeca.load_state_dict(checkpoint["estado"])
    modelo = nn.Sequential(extrator_resnet(), cabeca).eval()

    def inferir(x):
        return modelo(normalizar_imagenet(x))

    return inferir, checkpoint["limiar"]
