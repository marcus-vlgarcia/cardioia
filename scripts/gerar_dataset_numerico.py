"""
CardioIA - Fase 1: Batimentos de Dados
Gerador de dados simulados para exercícios acadêmicos.

O script não utiliza informações de pacientes reais. Os valores foram criados
com variáveis comuns em bases cardiológicas e não têm uso clínico.
"""

import argparse
import os
from pathlib import Path
import numpy as np
import pandas as pd

N_PACIENTES_PADRAO = 300
RAIZ_PROJETO = Path(__file__).resolve().parents[1]
CAMINHO_PADRAO = str(RAIZ_PROJETO / "data/numeric/dataset_pacientes_cardiacos.csv")


def gerar_dataset(n: int, seed: int = 42, id_inicial: int = 1) -> pd.DataFrame:
    rng = np.random.default_rng(seed=seed)
    idade = rng.integers(29, 80, size=n)

    # Sexo: 0 = feminino, 1 = masculino (aprox. distribuição do dataset
    # clássico Heart Disease UCI, ~68% masculino)
    sexo = rng.choice([0, 1], size=n, p=[0.32, 0.68])

    # Tipo de dor no peito (chest pain type)
    # 0: assintomático | 1: angina típica | 2: angina atípica | 3: dor não anginosa
    tipo_dor_peito = rng.choice([0, 1, 2, 3], size=n, p=[0.47, 0.16, 0.17, 0.20])

    # Pressão arterial de repouso (mmHg) - correlacionada levemente com a idade
    pressao_arterial_repouso = np.clip(
        rng.normal(loc=120 + (idade - 50) * 0.5, scale=17), 90, 200
    ).round(0)

    # Colesterol total (mg/dL)
    colesterol = np.clip(
        rng.normal(loc=246 + (idade - 50) * 0.6, scale=51), 120, 570
    ).round(0)

    # Glicemia de jejum > 120 mg/dL (0 = não, 1 = sim)
    glicemia_jejum_alta = rng.choice([0, 1], size=n, p=[0.85, 0.15])

    # Resultado do eletrocardiograma de repouso
    # 0: normal | 1: anormalidade onda ST-T | 2: hipertrofia ventricular esquerda
    ecg_repouso = rng.choice([0, 1, 2], size=n, p=[0.50, 0.01, 0.49])

    # Frequência cardíaca máxima atingida em teste de esforço
    freq_cardiaca_maxima = np.clip(
        rng.normal(loc=220 - idade - rng.normal(0, 8, size=n), scale=10), 70, 210
    ).round(0)

    # Angina induzida por exercício (0 = não, 1 = sim)
    angina_exercicio = rng.choice([0, 1], size=n, p=[0.68, 0.32])

    # Depressão do segmento ST induzida pelo exercício em relação ao repouso
    oldpeak = np.clip(rng.exponential(scale=1.0, size=n), 0, 6.2).round(1)

    # Inclinação do segmento ST no pico do exercício
    # 0: descendente | 1: plana | 2: ascendente
    inclinacao_st = rng.choice([0, 1, 2], size=n, p=[0.14, 0.47, 0.39])

    # Número de vasos principais coloridos por fluoroscopia (0-3)
    n_vasos_principais = rng.choice([0, 1, 2, 3], size=n, p=[0.58, 0.22, 0.13, 0.07])

    # IMC (kg/m2)
    imc = np.clip(rng.normal(loc=27, scale=4.5, size=n), 16, 45).round(1)

    # Fumante (0 = não, 1 = sim)
    fumante = rng.choice([0, 1], size=n, p=[0.72, 0.28])

    # Diabetes (0 = não, 1 = sim)
    diabetes = rng.choice([0, 1], size=n, p=[0.83, 0.17])

    # Histórico familiar de doença cardíaca (0 = não, 1 = sim)
    historico_familiar = rng.choice([0, 1], size=n, p=[0.65, 0.35])

    # --- Variável-alvo: presença de doença cardíaca (0 = não, 1 = sim) ---
    # Construída a partir de um score de risco simplificado combinando
    # fatores de risco conhecidos na literatura médica, apenas para dar
    # coerência estatística à base simulada (NÃO é um modelo diagnóstico).
    score_risco = (
        0.03 * (idade - 50)
        + 0.9 * sexo
        + 0.02 * (colesterol - 200)
        + 0.02 * (pressao_arterial_repouso - 120)
        + 1.1 * angina_exercicio
        + 0.5 * oldpeak
        + 0.6 * (tipo_dor_peito == 0)
        + 0.8 * n_vasos_principais
        + 0.4 * historico_familiar
        + 0.3 * fumante
        + 0.3 * diabetes
        + rng.normal(0, 1.3, size=n)
    )
    prob_doenca = 1 / (1 + np.exp(-0.35 * (score_risco - 2)))
    doenca_cardiaca = (rng.random(n) < prob_doenca).astype(int)

    df = pd.DataFrame(
        {
            "paciente_id": [
                f"PAC{str(i).zfill(4)}" for i in range(id_inicial, id_inicial + n)
            ],
            "idade": idade,
            "sexo": sexo,  # 0 = feminino, 1 = masculino
            "tipo_dor_peito": tipo_dor_peito,
            "pressao_arterial_repouso": pressao_arterial_repouso.astype(int),
            "colesterol": colesterol.astype(int),
            "glicemia_jejum_alta": glicemia_jejum_alta,
            "ecg_repouso": ecg_repouso,
            "freq_cardiaca_maxima": freq_cardiaca_maxima.astype(int),
            "angina_exercicio": angina_exercicio,
            "oldpeak": oldpeak,
            "inclinacao_st": inclinacao_st,
            "n_vasos_principais": n_vasos_principais,
            "imc": imc,
            "fumante": fumante,
            "diabetes": diabetes,
            "historico_familiar": historico_familiar,
            "doenca_cardiaca": doenca_cardiaca,  # variável-alvo (0/1)
        }
    )
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Gera dataset simulado de pacientes cardíacos para o CardioIA."
    )
    parser.add_argument(
        "-n", "--n-pacientes", type=int, default=N_PACIENTES_PADRAO,
        help=f"Quantidade de linhas/pacientes a gerar (padrão: {N_PACIENTES_PADRAO}).",
    )
    parser.add_argument(
        "-o", "--out", type=str, default=CAMINHO_PADRAO,
        help=f"Caminho do arquivo CSV de saída (padrão: {CAMINHO_PADRAO}).",
    )
    parser.add_argument(
        "-m", "--modo", choices=["substituir", "anexar"], default="substituir",
        help=(
            "'substituir' (padrão) sobrescreve o arquivo com um novo dataset do zero. "
            "'anexar' mantém as linhas já existentes no arquivo e adiciona novas linhas "
            "após elas, continuando a numeração de paciente_id automaticamente."
        ),
    )
    parser.add_argument(
        "-s", "--seed", type=int, default=None,
        help=(
            "Semente aleatória. Se não informado: usa 42 no modo 'substituir' "
            "(sempre reproduz o mesmo dataset original), ou uma semente aleatória "
            "diferente a cada execução no modo 'anexar' (para gerar linhas novas e "
            "não repetir os mesmos pacientes)."
        ),
    )
    args = parser.parse_args()
    if args.n_pacientes <= 0:
        parser.error("A quantidade de registros deve ser maior que zero.")

    id_inicial = 1
    df_existente = None

    if args.modo == "anexar" and os.path.exists(args.out):
        df_existente = pd.read_csv(args.out)
        # Continua a numeração de paciente_id a partir do maior ID já existente
        maior_id = (
            df_existente["paciente_id"].str.replace("PAC", "", regex=False).astype(int).max()
        )
        id_inicial = maior_id + 1

    seed = args.seed if args.seed is not None else (42 if args.modo == "substituir" else None)
    if seed is None:
        # modo 'anexar' sem --seed: gera uma semente diferente a cada execução,
        # para que as novas linhas não sejam idênticas às já existentes
        seed = np.random.default_rng().integers(0, 1_000_000)

    df_novo = gerar_dataset(args.n_pacientes, seed=seed, id_inicial=id_inicial)

    if args.modo == "anexar" and df_existente is not None:
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)
    else:
        df_final = df_novo

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    df_final.to_csv(args.out, index=False, encoding="utf-8")

    print(f"Modo: {args.modo} | seed usada: {seed}")
    print(f"Linhas novas geradas: {len(df_novo)} | Total no arquivo agora: {len(df_final)}")
    print(f"Arquivo salvo em -> {args.out}")
    print(df_final["doenca_cardiaca"].value_counts(normalize=True))


if __name__ == "__main__":
    main()
