"""Gera uma auditoria descritiva dos dados entregues na Fase 1.

O relatório não faz inferência clínica. Seu objetivo é tornar explícitas as
distribuições e limitações do dataset sintético e do conjunto visual antes de
experimentos nas fases seguintes.
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median


RAIZ_PROJETO = Path(__file__).resolve().parents[1]
ARQUIVO_NUMERICO = RAIZ_PROJETO / "data/numeric/dataset_pacientes_cardiacos.csv"
MANIFESTO_IMAGENS = RAIZ_PROJETO / "assets/imagens/ecg_mitbih/manifesto_imagens.csv"


def percentual(valor: int, total: int) -> str:
    return f"{valor / total * 100:.1f}%".replace(".", ",")


def distribuicao(linhas: list[dict[str, str]], coluna: str) -> str:
    contagens = Counter(linha[coluna] for linha in linhas)
    total = len(linhas)
    return "; ".join(
        f"{valor}: {quantidade} ({percentual(quantidade, total)})"
        for valor, quantidade in sorted(contagens.items())
    )


def resumo_alvo_por_grupo(
    linhas: list[dict[str, str]], coluna: str
) -> list[tuple[str, int, int]]:
    grupos: defaultdict[str, list[int]] = defaultdict(list)
    for linha in linhas:
        grupos[linha[coluna]].append(int(linha["doenca_cardiaca"]))
    return [
        (grupo, sum(alvos), len(alvos))
        for grupo, alvos in sorted(grupos.items())
    ]


def distribuicao_faixas_idade(linhas: list[dict[str, str]]) -> str:
    faixas = (("29–39", 29, 39), ("40–49", 40, 49), ("50–59", 50, 59),
              ("60–69", 60, 69), ("70–79", 70, 79))
    total = len(linhas)
    return "; ".join(
        f"{nome}: {quantidade} ({percentual(quantidade, total)})"
        for nome, inicio, fim in faixas
        for quantidade in [sum(inicio <= int(linha["idade"]) <= fim for linha in linhas)]
    )


def main() -> None:
    with ARQUIVO_NUMERICO.open(encoding="utf-8", newline="") as arquivo:
        dados = list(csv.DictReader(arquivo))
    with MANIFESTO_IMAGENS.open(encoding="utf-8", newline="") as arquivo:
        imagens = list(csv.DictReader(arquivo))

    idades = sorted(int(linha["idade"]) for linha in dados)
    print(f"Dataset numérico: {len(dados)} registros e {len(dados[0])} colunas")
    print(f"Sexo: {distribuicao(dados, 'sexo')} (0=feminino; 1=masculino)")
    print(f"Doença cardíaca: {distribuicao(dados, 'doenca_cardiaca')}")
    print(f"Diabetes: {distribuicao(dados, 'diabetes')}")
    print(f"Tabagismo: {distribuicao(dados, 'fumante')}")
    print(f"Histórico familiar: {distribuicao(dados, 'historico_familiar')}")
    print(f"Glicemia de jejum alta: {distribuicao(dados, 'glicemia_jejum_alta')}")
    print(f"Angina por exercício: {distribuicao(dados, 'angina_exercicio')}")
    print(f"Idade: {idades[0]} a {idades[-1]} anos; média {sum(idades) / len(idades):.1f}; mediana {median(idades):g}")
    print(f"Faixas etárias: {distribuicao_faixas_idade(dados)}")

    for coluna in ("sexo", "diabetes", "fumante"):
        print(f"\nDoença cardíaca por {coluna}:")
        for grupo, positivos, total in resumo_alvo_por_grupo(dados, coluna):
            print(f"  {grupo}: {positivos}/{total} ({percentual(positivos, total)})")

    por_split = Counter(linha["split"] for linha in imagens)
    por_registro = Counter(linha["source_record"] for linha in imagens)
    print(f"\nConjunto visual: {len(imagens)} imagens de {len(por_registro)} registros de origem")
    print("Divisão: " + "; ".join(f"{nome}: {qtd}" for nome, qtd in sorted(por_split.items())))


if __name__ == "__main__":
    main()
