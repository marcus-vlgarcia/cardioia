"""Exporta exemplos fixos da base pública para a demonstração sem o dataset completo."""

import numpy as np

from dados import RESULTADOS, SEMENTE, baixar, carregar_particoes


def executar():
    teste = carregar_particoes(baixar())["test"]
    rng = np.random.default_rng(SEMENTE)
    posicoes = np.concatenate([
        rng.choice(np.flatnonzero(teste.rotulos == classe), size=3, replace=False)
        for classe in (0, 1)
    ])
    np.savez_compressed(RESULTADOS / "amostras_demo.npz",
                        imagens=teste.imagens[posicoes],
                        rotulos=teste.rotulos[posicoes],
                        indices=teste.indices[posicoes])


if __name__ == "__main__":
    executar()
