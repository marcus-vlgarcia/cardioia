"""Confere arquivos, rastreabilidade e resultados das duas fases sem modificá-los."""

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def ler_csv(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)


def main():
    numericos = ler_csv(RAIZ / "data/numeric/dataset_pacientes_cardiacos.csv")
    exigir(len(numericos) == 300 and len(numericos[0]) == 18, "Base numérica inesperada.")
    textos = list((RAIZ / "assets/textos").glob("*.txt"))
    exigir(len(textos) >= 2, "Faltam textos da Fase 1.")
    for texto in textos:
        exigir("https://" in texto.read_text(encoding="utf-8"), f"Texto sem fonte: {texto.name}")

    visuais = RAIZ / "assets/imagens/ecg_mitbih"
    manifesto = ler_csv(visuais / "manifesto_imagens.csv")
    exigir(len(manifesto) == 100, "Manifesto visual incompleto.")
    caminhos = {linha["relative_path"] for linha in manifesto}
    exigir(len(caminhos) == 100, "Imagens repetidas no manifesto.")
    exigir(caminhos == {str(p.relative_to(visuais)) for p in visuais.rglob("*.png")},
           "Imagens e manifesto não correspondem.")
    origem = defaultdict(set)
    for linha in manifesto:
        imagem = visuais / linha["relative_path"]
        exigir(hashlib.sha256(imagem.read_bytes()).hexdigest() == linha["sha256"],
               f"Hash visual divergente: {imagem.name}")
        origem[linha["source_record"]].add(linha["split"])
    exigir(len(origem) == 10 and all(len(conjuntos) == 1 for conjuntos in origem.values()),
           "Registros de ECG repetidos entre conjuntos.")
    print("Fase 1: 300 registros/18 colunas, dois textos com fonte e 100 imagens com hashes válidos.")

    fase = RAIZ / "fase2"
    relatos = (fase / "data/relatos_sintomas.txt").read_text(encoding="utf-8").splitlines()
    exigir(len(relatos) == 10 and all(relatos), "Relatos originais incompletos.")
    mapa = ler_csv(fase / "data/mapa_conhecimento.csv")
    exigir(len(mapa) == 83 and all(all(linha.values()) for linha in mapa), "Mapa incompleto.")
    dados = ler_csv(fase / "data/frases_risco.csv")
    exigir(len(dados) == 1112, "Quantidade de frases inesperada.")
    exigir(Counter(r["situacao"] for r in dados) == {"alto risco": 556, "baixo risco": 556},
           "Distribuição de classes divergente.")
    exigir(len({r["frase"].casefold().strip() for r in dados}) == len(dados), "Frases duplicadas.")
    grupos = defaultdict(list)
    for linha in dados:
        grupos[linha["grupo"]].append(linha)
    exigir(all(len(v) == (1 if grupo.startswith("N") else 2) and
               len({r["situacao"] for r in v}) == 1 for grupo, v in grupos.items()),
           "Paráfrases ou rótulos inconsistentes por grupo.")
    linhas_particoes = ler_csv(fase / "data/particoes.csv")
    particoes = {r["grupo"]: r["conjunto"] for r in linhas_particoes}
    exigir(len(particoes) == len(linhas_particoes) and set(particoes) == set(grupos),
           "Manifesto de partições inconsistente.")
    exigir(Counter(particoes[r["grupo"]] for r in dados) ==
           {"treino": 616, "calibracao": 88, "teste": 264, "regressao": 144},
           "Divisão de treino/teste/regressão divergente.")
    familias = defaultdict(set)
    for linha in linhas_particoes:
        familias[linha["familia"]].add(linha["conjunto"])
    exigir(all(len(conjuntos) == 1 for conjuntos in familias.values()),
           "Família de cenários distribuída entre partições.")
    exigir(len([r for r in linhas_particoes if r["variacao"] == "erro_ortografico" and
                r["conjunto"] == "teste"]) == 22, "Faltam exemplos com erro ortográfico no teste.")
    complementares = ler_csv(fase / "data/casos_adicionais.csv")
    exigir(len(complementares) == 120 and
           {r["grupo"] for r in complementares} == {g for g in grupos if g.startswith("N")} and
           all(particoes[r["grupo"]] == "treino" for r in complementares),
           "Casos adicionais ou sua partição inconsistentes.")
    auditoria = ler_csv(fase / "data/auditoria_nova.csv")
    contrastiva = ler_csv(fase / "data/auditoria_contrastiva.csv")
    frases_treino = {r["frase"] for r in dados}
    exigir(len(auditoria) == 80 and
           Counter(r["situacao"] for r in auditoria) == {"alto risco": 40, "baixo risco": 40} and
           all(r["frase"] not in frases_treino for r in auditoria),
           "Auditoria nova incompleta ou com frase duplicada na base principal.")
    pares_contrastivos = defaultdict(set)
    for linha in contrastiva:
        pares_contrastivos[linha["par"]].add(linha["situacao"])
    exigir(len(contrastiva) == 40 and len(pares_contrastivos) == 20 and
           all(valor == {"alto risco", "baixo risco"} for valor in pares_contrastivos.values()) and
           all(r["frase"] not in frases_treino for r in contrastiva),
           "Auditoria contrastiva incompleta ou duplicada.")
    externos = ler_csv(fase / "data/avaliacao_externa.csv")
    exigir(len(externos) == 32 and all(r["fonte"].startswith("https://") for r in externos),
           "Avaliação externa incompleta ou sem fontes.")
    pares = ler_csv(fase / "data/pares_gravidade.csv")
    exigir(len(pares) == 32 and len({r["par"] for r in pares}) == 16,
           "Pares de gravidade incompletos.")
    subgrupos = ler_csv(fase / "data/avaliacao_subgrupos.csv")
    exigir(len(subgrupos) == 48, "Auditoria de subgrupos incompleta.")
    revisao = ler_csv(fase / "data/revisao_clinica.csv")
    exigir(len(revisao) == len(mapa) and
           all(r["triagem_documental"] == "realizada" and
               r["validacao_especialista"] in {"pendente", "aprovada", "ajustar", "remover"}
               for r in revisao), "Ficha de revisão clínica inconsistente.")

    metricas = json.loads((fase / "outputs/metricas.json").read_text(encoding="utf-8"))
    exigir(hashlib.sha256((fase / "src/preprocessar_texto.py").read_bytes()).hexdigest()
           == metricas["sha256_preprocessamento"], "Resultados desatualizados em relação ao pré-processamento.")
    exigir(hashlib.sha256((fase / "src/contexto_sintomas.py").read_bytes()).hexdigest()
           == metricas["sha256_contexto"], "Resultados desatualizados em relação à análise contextual.")
    for nome, campo in (("frases_risco.csv", "sha256_dataset"), ("particoes.csv", "sha256_particoes")):
        exigir(hashlib.sha256((fase / "data" / nome).read_bytes()).hexdigest() == metricas[campo],
               f"Resultados desatualizados em relação a {nome}.")
    for nome, campo in (("casos_adicionais.csv", "sha256_casos_adicionais"),
                        ("auditoria_nova.csv", "sha256_auditoria_nova"),
                        ("auditoria_contrastiva.csv", "sha256_auditoria_contrastiva")):
        exigir(hashlib.sha256((fase / "data" / nome).read_bytes()).hexdigest() == metricas[campo],
               f"Resultados desatualizados em relação a {nome}.")
    predicoes = ler_csv(fase / "outputs/predicoes_teste.csv")
    esperadas = {(r["frase"], r["situacao"], r["grupo"]) for r in dados if particoes[r["grupo"]] == "teste"}
    exigir(len(predicoes) == len(esperadas) and
           {(r["frase"], r["situacao"], r["grupo"]) for r in predicoes} == esperadas,
           "Predições não correspondem ao teste reservado.")
    classes = ["baixo risco", "alto risco"]
    matriz = [[0, 0], [0, 0]]
    for linha in predicoes:
        exigir(linha["predicao"] in classes, "Predição com classe desconhecida.")
        matriz[classes.index(linha["situacao"])][classes.index(linha["predicao"])] += 1
    exigir(matriz == metricas["teste"]["matriz_confusao"], "Matriz de confusão divergente.")
    acuracia = sum(matriz[i][i] for i in range(2)) / len(predicoes)
    exigir(abs(acuracia - metricas["teste"]["acuracia"]) < 1e-12, "Acurácia divergente.")
    for nome, linhas, chave_atual, chave_anterior in (
        ("auditoria_nova", auditoria, "auditoria_nova", "auditoria_nova_modelo_anterior"),
        ("auditoria_contrastiva", contrastiva, "auditoria_contrastiva", "auditoria_contrastiva_modelo_anterior"),
    ):
        preds = ler_csv(fase / "outputs" / f"predicoes_{nome}.csv")
        exigir(len(preds) == len(linhas), f"Predições incompletas em {nome}.")
        for campo, metrica in (("predicao", chave_atual), ("predicao_anterior", chave_anterior)):
            certos = sum(r["situacao"] == r[campo] for r in preds)
            exigir(abs(certos / len(preds) - metricas[metrica]["acuracia"]) < 1e-12,
                   f"Métrica divergente em {nome}: {campo}.")
    variacoes = ler_csv(fase / "outputs/metricas_variacoes.csv")
    exigir(len(variacoes) == 6 and sum(int(r["n"]) for r in variacoes) == 264,
           "Análise por tipo de linguagem incompleta.")
    notebook = json.loads((fase / "notebooks/classificador_risco.ipynb").read_text(encoding="utf-8"))
    for celula in notebook["cells"]:
        if celula["cell_type"] == "code":
            exigir(celula.get("execution_count") is not None, "Notebook sem execução completa.")
            exigir(not any(o["output_type"] == "error" for o in celula["outputs"]), "Notebook com erro.")
    exigir((fase / "outputs/curva_calibracao.png").stat().st_size > 0, "Curva de calibração ausente.")
    print(f"Fase 2: 10 relatos, 83 associações, 1112 frases; teste histórico de 264 frases e duas auditorias novas válidas ({acuracia:.2%} no histórico).")
    print("O vídeo e o acesso público aos links devem ser conferidos na entrega; este script verifica arquivos locais.")


if __name__ == "__main__":
    main()
