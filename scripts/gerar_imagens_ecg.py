"""
CardioIA - Fase 1: Batimentos de Dados
Gerador de imagens sintéticas de ECG para estudo.

As imagens geradas aqui são complementares. O conjunto visual da entrega está
em `assets/imagens/ecg_mitbih/` e foi obtido da MIT-BIH Arrhythmia Database.
"""

import argparse
import glob
import os
import re
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

N_IMAGENS_PADRAO = 100
RAIZ_PROJETO = Path(__file__).resolve().parents[1]
OUT_DIR_PADRAO = str(RAIZ_PROJETO / "assets/imagens/ecg_sintetico")


def batimento_pqrst(t, offset=0.0, amp_r=1.0):
    """Gera um único ciclo PQRST simplificado centrado em 'offset'."""
    onda = np.zeros_like(t)
    onda += 0.10 * np.exp(-((t - offset - 0.10) ** 2) / (2 * 0.015 ** 2))      # P
    onda -= 0.10 * np.exp(-((t - offset - 0.18) ** 2) / (2 * 0.006 ** 2))      # Q
    onda += amp_r * np.exp(-((t - offset - 0.20) ** 2) / (2 * 0.010 ** 2))     # R
    onda -= 0.25 * np.exp(-((t - offset - 0.22) ** 2) / (2 * 0.008 ** 2))      # S
    onda += 0.20 * np.exp(-((t - offset - 0.35) ** 2) / (2 * 0.03 ** 2))       # T
    return onda


def gerar_traçado(tipo: str, rng: np.random.Generator, duracao_s: float = 4.0, fs: int = 250):
    t = np.linspace(0, duracao_s, int(duracao_s * fs))
    sinal = np.zeros_like(t)

    if tipo == "normal":
        bpm = rng.uniform(60, 100)
    elif tipo == "bradicardia":
        bpm = rng.uniform(35, 59)
    elif tipo == "taquicardia":
        bpm = rng.uniform(101, 160)
    else:  # arritmia_ectopica
        bpm = rng.uniform(60, 100)

    intervalo = 60.0 / bpm
    tempo_batida = intervalo
    while tempo_batida < duracao_s:
        amp_r = 1.0
        if tipo == "arritmia_ectopica" and rng.random() < 0.18:
            tempo_batida -= intervalo * 0.45  # antecipa a batida em relação ao ciclo esperado
            amp_r = 0.75
        sinal += batimento_pqrst(t, offset=tempo_batida, amp_r=amp_r)
        tempo_batida += intervalo

    # ruído leve simulando captação do eletrodo
    sinal += rng.normal(0, 0.015, size=t.shape)
    return t, sinal, round(bpm)


def salvar_imagem(t, sinal, tipo, bpm, idx, out_dir):
    fig, ax = plt.subplots(figsize=(4, 2.4), dpi=100)
    ax.plot(t, sinal, color="black", linewidth=0.9)
    ax.set_facecolor("#fdeeee")
    fig.patch.set_facecolor("#fdeeee")
    # grade estilo "papel de ECG"
    ax.set_xticks(np.arange(0, t[-1], 0.2), minor=False)
    ax.set_yticks(np.arange(-1, 1.6, 0.5), minor=False)
    ax.grid(which="major", color="#e8a0a0", linewidth=0.5)
    ax.set_ylim(-1, 1.8)
    ax.set_xlim(0, t[-1])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_title(f"ECG simulado | {tipo} | ~{bpm} bpm", fontsize=8)
    fig.tight_layout(pad=0.4)
    fig.savefig(f"{out_dir}/ecg_{idx:04d}.png")
    plt.close(fig)


def proximo_indice_inicial(out_dir: str) -> int:
    """Olha os arquivos ecg_XXXX.png já existentes na pasta e retorna o
    próximo número livre, para o modo 'anexar' nunca sobrescrever nada."""
    existentes = glob.glob(os.path.join(out_dir, "ecg_*.png"))
    maior = 0
    for caminho in existentes:
        m = re.search(r"ecg_(\d+)\.png$", os.path.basename(caminho))
        if m:
            maior = max(maior, int(m.group(1)))
    return maior + 1


def main():
    parser = argparse.ArgumentParser(
        description="Gera imagens sintéticas de ECG para o CardioIA."
    )
    parser.add_argument(
        "-n", "--n-imagens", type=int, default=N_IMAGENS_PADRAO,
        help=f"Quantidade de imagens a gerar (padrão: {N_IMAGENS_PADRAO}).",
    )
    parser.add_argument(
        "-o", "--out-dir", type=str, default=OUT_DIR_PADRAO,
        help=f"Pasta de saída das imagens (padrão: {OUT_DIR_PADRAO}).",
    )
    parser.add_argument(
        "-m", "--modo", choices=["substituir", "anexar"], default="substituir",
        help=(
            "'substituir' (padrão) apaga as imagens ecg_*.png já existentes na "
            "pasta e gera um novo conjunto do zero, numerado a partir de 0001. "
            "'anexar' mantém as imagens já existentes e adiciona novas após elas, "
            "continuando a numeração automaticamente."
        ),
    )
    parser.add_argument(
        "-s", "--seed", type=int, default=None,
        help=(
            "Semente aleatória. Se não informado: usa 7 no modo 'substituir' "
            "(sempre reproduz o mesmo conjunto original), ou uma semente "
            "diferente a cada execução no modo 'anexar' (para não repetir "
            "os mesmos traçados)."
        ),
    )
    args = parser.parse_args()
    if args.n_imagens <= 0:
        parser.error("A quantidade de imagens deve ser maior que zero.")

    os.makedirs(args.out_dir, exist_ok=True)

    if args.modo == "substituir":
        for f in glob.glob(os.path.join(args.out_dir, "ecg_*.png")):
            os.remove(f)
        idx_inicial = 1
    else:
        idx_inicial = proximo_indice_inicial(args.out_dir)

    seed = args.seed if args.seed is not None else (7 if args.modo == "substituir" else None)
    if seed is None:
        seed = int(np.random.default_rng().integers(0, 1_000_000))
    rng = np.random.default_rng(seed=seed)

    tipos = rng.choice(
        ["normal", "normal", "bradicardia", "taquicardia", "arritmia_ectopica"],
        size=args.n_imagens,
    )
    for offset, tipo in enumerate(tipos):
        idx = idx_inicial + offset
        t, sinal, bpm = gerar_traçado(tipo, rng)
        salvar_imagem(t, sinal, tipo, bpm, idx, args.out_dir)

    total_na_pasta = len(glob.glob(os.path.join(args.out_dir, "ecg_*.png")))
    print(f"Modo: {args.modo} | seed usada: {seed}")
    print(f"Imagens novas geradas: {args.n_imagens} | Total agora em {args.out_dir}: {total_na_pasta}")


if __name__ == "__main__":
    main()
