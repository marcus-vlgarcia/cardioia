"""Prepara as partições oficiais do ChestMNIST para a tarefa de cardiomegalia."""

import hashlib
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image
import torch

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / ".dados"
RESULTADOS = RAIZ / "resultados"
URL = "https://zenodo.org/records/10519652/files/chestmnist_64.npz?download=1"
MD5 = "9de6cd0b934ebb5b7426cfba5efbae16"
SEMENTE = 42
COLUNA_CARDIOMEGALIA = 1
TAMANHO_ORIGEM = 64
TAMANHO = 56
PARTICOES = ("train", "val", "test")
CLASSES = ("Sem rótulo de cardiomegalia", "Com rótulo de cardiomegalia")


def hash_arquivo(path, algoritmo):
    with path.open("rb") as arquivo:
        return hashlib.file_digest(arquivo, algoritmo).hexdigest()


def baixar_verificado(url, destino, algoritmo, esperado):
    if destino.exists():
        if hash_arquivo(destino, algoritmo) != esperado:
            raise ValueError(f"Remova o arquivo incompleto ou alterado: {destino}")
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destino.parent) as pasta:
        temporario = Path(pasta) / destino.name
        subprocess.run(["curl", "--fail", "--location", "--silent", "--show-error",
                        "--retry", "2", "--connect-timeout", "15", "--max-time", "1800",
                        "--output", str(temporario), url], check=True)
        if hash_arquivo(temporario, algoritmo) != esperado:
            raise ValueError("O arquivo baixado não confere com o checksum esperado.")
        temporario.replace(destino)
    return destino


def baixar():
    return baixar_verificado(URL, DADOS / "chestmnist_64.npz", "md5", MD5)


def preparar_imagem(imagem):
    """Converte para RGB e redimensiona proporcionalmente com fundo preto."""
    imagem = imagem.convert("RGB")
    if imagem.size != (TAMANHO, TAMANHO):
        escala = TAMANHO / max(imagem.size)
        imagem = imagem.resize(tuple(max(1, round(lado * escala)) for lado in imagem.size),
                               Image.Resampling.BILINEAR)
    tela = Image.new("RGB", (TAMANHO, TAMANHO))
    tela.paste(imagem, tuple((TAMANHO - lado) // 2 for lado in imagem.size))
    return torch.from_numpy(np.array(tela)).permute(2, 0, 1).float() / 255


def indices_particao(rotulos, split):
    rng = np.random.default_rng(SEMENTE + PARTICOES.index(split))
    if split == "train":
        positivos = np.flatnonzero(rotulos == 1)
        negativos = np.flatnonzero(rotulos == 0)
        indices = np.concatenate([positivos, rng.choice(negativos, 2 * len(positivos), replace=False)])
    else:
        indices = rng.choice(len(rotulos), min(8000, len(rotulos)), replace=False)
    return rng.permutation(indices)


class Radiografias(torch.utils.data.Dataset):
    def __init__(self, arquivo, split):
        with np.load(arquivo, allow_pickle=False) as fonte:
            imagens = fonte[f"{split}_images"]
            rotulos = fonte[f"{split}_labels"][:, COLUNA_CARDIOMEGALIA]
        if imagens.shape != (len(rotulos), TAMANHO_ORIGEM, TAMANHO_ORIGEM) or not np.isin(rotulos, [0, 1]).all():
            raise ValueError("Formato ou rótulos incompatíveis com ChestMNIST 64.")
        self.indices = indices_particao(rotulos, split)
        self.imagens = imagens[self.indices]
        self.rotulos = rotulos[self.indices]
        self.total_oficial = len(rotulos)

    def __len__(self):
        return len(self.rotulos)

    def __getitem__(self, idx):
        imagem = preparar_imagem(Image.fromarray(self.imagens[idx]))
        return imagem, int(self.rotulos[idx])


def carregar_particoes(arquivo):
    datasets = {split: Radiografias(arquivo, split) for split in PARTICOES}
    vistos = set()
    for ds in datasets.values():
        manter = np.zeros(len(ds), dtype=bool)
        for i, img in enumerate(ds.imagens):
            chave = hashlib.sha256(img.tobytes()).digest()
            if chave not in vistos:
                manter[i] = True
                vistos.add(chave)
        ds.imagens = ds.imagens[manter]
        ds.rotulos = ds.rotulos[manter]
        ds.indices = ds.indices[manter]
    return datasets
