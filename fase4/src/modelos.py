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


def carregar_prototipo(pasta, nome, device="cpu"):
    checkpoint = torch.load(pasta / f"{nome}.pt", map_location="cpu", weights_only=True)
    if nome in ("cnn", "cnn_ampliada"):
        modelo = cnn_simples()
        modelo.load_state_dict(checkpoint["estado"])
        return modelo.to(device).eval(), checkpoint["limiar"]
    if checkpoint.get("arquitetura") == "resnet18_adaptada":
        modelo = ResNetAdaptada()
        modelo.extrator.layer4.load_state_dict(checkpoint["estado"]["layer4"])
        modelo.saida.load_state_dict(checkpoint["estado"]["saida"])
        return modelo.to(device).eval(), checkpoint["limiar"]
    cabeca = classificador_resnet()
    cabeca.load_state_dict(checkpoint["estado"])
    modelo = nn.Sequential(NormalizacaoImageNet(), extrator_resnet(), cabeca)
    return modelo.to(device).eval(), checkpoint["limiar"]


class NormalizacaoImageNet(nn.Module):
    def forward(self, x):
        return normalizar_imagenet(x)


class ResNetAdaptada(nn.Module):
    """Mantém os primeiros blocos fixos e ajusta o último bloco e a saída."""

    def __init__(self):
        super().__init__()
        self.extrator = extrator_resnet()
        self.extrator.layer4.requires_grad_(True)
        self.saida = classificador_resnet()

    def train(self, mode=True):
        super().train(mode)
        self.extrator.eval()
        self.extrator.layer4.train(mode)
        return self

    def forward(self, x):
        return self.saida(self.extrator(normalizar_imagenet(x)))

    def estado_adaptado(self):
        return {"layer4": self.extrator.layer4.state_dict(), "saida": self.saida.state_dict()}
