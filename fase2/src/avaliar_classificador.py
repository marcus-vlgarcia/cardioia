"""Treina e avalia a revisão do classificador textual da Fase 2."""

import hashlib
import json
import platform
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.frozen import FrozenEstimator
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, brier_score_loss, classification_report,
                             confusion_matrix, ConfusionMatrixDisplay, f1_score, log_loss,
                             precision_score, recall_score)
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold
from sklearn.pipeline import Pipeline

from preprocessar_texto import preparar_texto


RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "outputs"
CLASSES = ["baixo risco", "alto risco"]
SEED = 42


def ler(nome):
    return pd.read_csv(RAIZ / "data" / nome)


def criar_modelo():
    return Pipeline([
        ("tfidf", TfidfVectorizer(preprocessor=preparar_texto, lowercase=False, ngram_range=(1, 2))),
        ("classificador", LogisticRegression(max_iter=1500, random_state=SEED)),
    ])


def candidatos_vetorizacao():
    palavras_2 = TfidfVectorizer(preprocessor=preparar_texto, lowercase=False, ngram_range=(1, 2))
    palavras_3 = TfidfVectorizer(preprocessor=preparar_texto, lowercase=False, ngram_range=(1, 3))
    misto = FeatureUnion([
        ("palavras", TfidfVectorizer(preprocessor=preparar_texto, lowercase=False,
                                      ngram_range=(1, 2))),
        ("caracteres", TfidfVectorizer(preprocessor=preparar_texto, lowercase=False,
                                        analyzer="char_wb", ngram_range=(3, 5), min_df=2)),
    ], transformer_weights={"palavras": 1.0, "caracteres": 0.7})
    return [palavras_2, palavras_3, misto]


def nome_vetorizacao(vetor):
    if isinstance(vetor, FeatureUnion):
        return "palavras_1_2_e_caracteres_3_5"
    return f"palavras_{vetor.ngram_range[0]}_{vetor.ngram_range[1]}"


def prever(modelo, frases, limiar=0.5):
    probabilidades = modelo.predict_proba(frases)[:, list(modelo.classes_).index("alto risco")]
    return np.where(probabilidades >= limiar, "alto risco", "baixo risco"), probabilidades


def metricas_binarias(esperado, previsto):
    matriz = confusion_matrix(esperado, previsto, labels=CLASSES)
    return {
        "n": int(len(esperado)),
        "acuracia": float(accuracy_score(esperado, previsto)),
        "precisao_alto_risco": float(precision_score(esperado, previsto, pos_label="alto risco", zero_division=0)),
        "recall_alto_risco": float(recall_score(esperado, previsto, pos_label="alto risco", zero_division=0)),
        "f1_macro": float(f1_score(esperado, previsto, average="macro", zero_division=0)),
        "falsos_negativos": int(matriz[1, 0]),
        "falsos_positivos": int(matriz[0, 1]),
        "matriz_confusao": matriz.tolist(),
    }


def explicar_frase(modelo_base, frase, limite=8):
    vetor = modelo_base.named_steps["tfidf"]
    classificador = modelo_base.named_steps["classificador"]
    linha = vetor.transform([frase])
    termos = vetor.get_feature_names_out()
    # Na ordenação alfabética do sklearn, a classe positiva do coeficiente
    # binário pode ser "baixo risco". Ajustamos o sinal para sempre explicar
    # contribuições favoráveis a "alto risco".
    sinal = 1 if classificador.classes_[1] == "alto risco" else -1
    contribuicoes = linha.multiply(classificador.coef_[0] * sinal).tocoo()
    itens = sorted(((termos[coluna], valor) for coluna, valor in zip(contribuicoes.col, contribuicoes.data)),
                   key=lambda item: abs(item[1]), reverse=True)[:limite]
    positivos = [f"{termo} ({valor:.3f})" for termo, valor in itens if valor > 0]
    negativos = [f"{termo} ({valor:.3f})" for termo, valor in itens if valor < 0]
    return " | ".join(positivos), " | ".join(negativos)


def avaliar_conjunto(modelo, dados, nome, campo_esperado="situacao"):
    resultado = dados.copy()
    resultado["predicao"], resultado["probabilidade_alto_risco"] = prever(modelo, resultado.frase)
    resultado["acerto"] = resultado[campo_esperado] == resultado.predicao
    resultado.to_csv(SAIDA / f"predicoes_{nome}.csv", index=False)
    return resultado, metricas_binarias(resultado[campo_esperado], resultado.predicao)


def main():
    SAIDA.mkdir(exist_ok=True)
    dados = ler("frases_risco.csv")
    particoes = ler("particoes.csv")
    assert not dados.isna().any().any()
    assert set(dados.situacao) == set(CLASSES)
    assert not dados.frase.str.casefold().str.strip().duplicated().any()
    assert dados.groupby("grupo").situacao.nunique().eq(1).all()
    assert not particoes.grupo.duplicated().any() and set(particoes.grupo) == set(dados.grupo)
    dados = dados.merge(particoes, on="grupo", validate="many_to_one")
    conjuntos = {nome: dados[dados.conjunto == nome].copy()
                 for nome in ("treino", "calibracao", "teste", "regressao")}
    assert tuple(len(conjuntos[n]) for n in conjuntos) == (616, 88, 264, 144)
    assert all(set(conjuntos[a].familia).isdisjoint(conjuntos[b].familia)
               for a in conjuntos for b in conjuntos if a < b)
    dados[["frase", "situacao", "grupo", "conjunto", "familia", "variacao"]].to_csv(
        SAIDA / "divisao_dados.csv", index=False)

    treino = conjuntos["treino"]
    cv = StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=SEED)
    busca = GridSearchCV(criar_modelo(), {
        "tfidf": candidatos_vetorizacao(),
        "classificador__C": [0.5, 2.0, 8.0],
    }, cv=cv, scoring={"acuracia": "accuracy", "f1_macro": "f1_macro"}, refit="f1_macro")
    busca.fit(treino.frase, treino.situacao, groups=treino.familia)
    base = busca.best_estimator_
    comparacao_bruta = pd.DataFrame(busca.cv_results_)
    comparacao = pd.DataFrame({
        "vetorizacao": comparacao_bruta.param_tfidf.map(nome_vetorizacao),
        "C": comparacao_bruta["param_classificador__C"].astype(float),
        "f1_macro_cv": comparacao_bruta.mean_test_f1_macro,
        "acuracia_cv": comparacao_bruta.mean_test_acuracia,
        "desvio_f1_macro_cv": comparacao_bruta.std_test_f1_macro,
        "posicao_f1_macro_cv": comparacao_bruta.rank_test_f1_macro,
    }).sort_values(["posicao_f1_macro_cv", "vetorizacao", "C"])
    comparacao.to_csv(SAIDA / "comparacao_cv.csv", index=False)
    tipo_vetor = nome_vetorizacao(base.named_steps["tfidf"])

    # O calibrador vê apenas o conjunto reservado para calibração. O teste final
    # continua sem participação no treinamento, na seleção ou na calibração.
    calibrado = CalibratedClassifierCV(FrozenEstimator(base), method="sigmoid")
    calibrado.fit(conjuntos["calibracao"].frase, conjuntos["calibracao"].situacao)

    # Reproduz a configuração publicada na revisão anterior com as 496 frases
    # disponíveis então. A nova auditoria não participa de nenhum ajuste.
    treino_anterior = treino[treino.variacao != "caso_adicional"]
    assert len(treino_anterior) == 496
    base_anterior = criar_modelo().set_params(classificador__C=8.0)
    base_anterior.fit(treino_anterior.frase, treino_anterior.situacao)
    calibrado_anterior = CalibratedClassifierCV(FrozenEstimator(base_anterior), method="sigmoid")
    calibrado_anterior.fit(conjuntos["calibracao"].frase, conjuntos["calibracao"].situacao)

    auditoria = ler("auditoria_nova.csv")
    frases_base = set(dados.frase.str.casefold().str.strip())
    assert len(auditoria) == 80 and not any(
        frase.casefold().strip() in frases_base for frase in auditoria.frase)
    assert auditoria.situacao.value_counts().to_dict() == {"alto risco": 40, "baixo risco": 40}
    auditoria["predicao_anterior"], auditoria["probabilidade_anterior"] = prever(
        calibrado_anterior, auditoria.frase)
    auditoria["predicao"], auditoria["probabilidade_alto_risco"] = prever(calibrado, auditoria.frase)
    auditoria["acerto_anterior"] = auditoria.situacao.eq(auditoria.predicao_anterior)
    auditoria["acerto"] = auditoria.situacao.eq(auditoria.predicao)
    auditoria.to_csv(SAIDA / "predicoes_auditoria_nova.csv", index=False)
    met_auditoria_anterior = metricas_binarias(auditoria.situacao, auditoria.predicao_anterior)
    met_auditoria = metricas_binarias(auditoria.situacao, auditoria.predicao)
    por_tema = []
    for tema, bloco in auditoria.groupby("tema"):
        por_tema.append({"tema": tema, "n": len(bloco),
                         "acuracia_anterior": float(bloco.acerto_anterior.mean()),
                         "acuracia_atual": float(bloco.acerto.mean())})
    pd.DataFrame(por_tema).to_csv(SAIDA / "metricas_auditoria_temas.csv", index=False)

    contrastiva = ler("auditoria_contrastiva.csv")
    assert len(contrastiva) == 40 and contrastiva.par.nunique() == 20
    assert contrastiva.groupby("par").situacao.nunique().eq(2).all()
    assert not any(frase.casefold().strip() in frases_base for frase in contrastiva.frase)
    contrastiva["predicao_anterior"], contrastiva["probabilidade_anterior"] = prever(
        calibrado_anterior, contrastiva.frase)
    contrastiva["predicao"], contrastiva["probabilidade_alto_risco"] = prever(
        calibrado, contrastiva.frase)
    contrastiva["acerto_anterior"] = contrastiva.situacao.eq(contrastiva.predicao_anterior)
    contrastiva["acerto"] = contrastiva.situacao.eq(contrastiva.predicao)
    contrastiva.to_csv(SAIDA / "predicoes_auditoria_contrastiva.csv", index=False)
    met_contrastiva_anterior = metricas_binarias(contrastiva.situacao, contrastiva.predicao_anterior)
    met_contrastiva = metricas_binarias(contrastiva.situacao, contrastiva.predicao)

    teste, met_teste = avaliar_conjunto(calibrado, conjuntos["teste"], "teste")
    por_variacao = []
    for variacao, bloco in teste.groupby("variacao"):
        por_variacao.append({"variacao": variacao, **metricas_binarias(bloco.situacao, bloco.predicao)})
    tabela_variacoes = pd.DataFrame(por_variacao)
    tabela_variacoes["matriz_confusao"] = tabela_variacoes.matriz_confusao.map(json.dumps)
    tabela_variacoes.to_csv(SAIDA / "metricas_variacoes.csv", index=False)
    regressao, met_regressao = avaliar_conjunto(calibrado, conjuntos["regressao"], "regressao")
    externo, met_externo = avaliar_conjunto(calibrado, ler("avaliacao_externa.csv"), "externas")
    pares, met_pares = avaliar_conjunto(calibrado, ler("pares_gravidade.csv"), "pares_gravidade")
    subgrupos, met_subgrupos = avaliar_conjunto(calibrado, ler("avaliacao_subgrupos.csv"), "subgrupos")
    desafios, met_desafios = avaliar_conjunto(calibrado, ler("desafios.csv").rename(columns={"esperado": "situacao"}),
                                               "desafios")

    matriz = np.array(met_teste["matriz_confusao"])
    ConfusionMatrixDisplay(matriz, display_labels=CLASSES).plot(cmap="Blues")
    plt.title("Teste histórico de 264 frases simuladas")
    plt.xlabel("Classe prevista")
    plt.ylabel("Classe esperada")
    plt.tight_layout()
    plt.savefig(SAIDA / "matriz_confusao.png", dpi=160)
    plt.close()

    prob_base = base.predict_proba(conjuntos["teste"].frase)[:, list(base.classes_).index("alto risco")]
    prob_cal = teste.probabilidade_alto_risco.to_numpy()
    y_bin = (teste.situacao == "alto risco").astype(int).to_numpy()
    calibracao = pd.DataFrame([
        {"modelo": "regressao_logistica", "brier": brier_score_loss(y_bin, prob_base),
         "log_loss": log_loss(y_bin, prob_base)},
        {"modelo": "regressao_logistica_calibrada", "brier": brier_score_loss(y_bin, prob_cal),
         "log_loss": log_loss(y_bin, prob_cal)},
    ])
    calibracao.to_csv(SAIDA / "metricas_calibracao.csv", index=False)
    plt.figure(figsize=(6.4, 4.8))
    for probabilidades, rotulo in ((prob_base, "Sem calibração"), (prob_cal, "Calibração sigmoide")):
        observado, previsto = calibration_curve(y_bin, probabilidades, n_bins=5, strategy="quantile")
        plt.plot(previsto, observado, marker="o", label=rotulo)
    plt.plot([0, 1], [0, 1], "--", color="gray", label="Referência ideal")
    plt.xlabel("Probabilidade média prevista")
    plt.ylabel("Fração observada de alto risco")
    plt.title("Curva de calibração — teste final")
    plt.legend()
    plt.tight_layout()
    plt.savefig(SAIDA / "curva_calibracao.png", dpi=160)
    plt.close()

    vetor = base.named_steps["tfidf"]
    classificador = base.named_steps["classificador"]
    sinal = 1 if classificador.classes_[1] == "alto risco" else -1
    pd.DataFrame({"termo": vetor.get_feature_names_out(),
                  "coeficiente_para_alto_risco": classificador.coef_[0] * sinal}).to_csv(
        SAIDA / "coeficientes.csv", index=False)

    erros = teste[~teste.acerto].copy()
    investigados = pd.concat([erros, regressao[regressao.grupo == "B69"]], ignore_index=True).drop_duplicates("frase")
    explicacoes = [explicar_frase(base, frase) for frase in investigados.frase]
    investigados["termos_favor_alto_risco"] = [x[0] for x in explicacoes]
    investigados["termos_favor_baixo_risco"] = [x[1] for x in explicacoes]
    investigados["observacao"] = np.where(investigados.grupo.eq("B69"),
        "Falso positivo histórico: suor de exercício já resolvido; verificar peso lexical de suor/treino.",
        "Erro do teste ampliado; contribuições são explicações locais do modelo, não causas clínicas.")
    investigados.to_csv(SAIDA / "investigacao_erros.csv", index=False)

    linhas_subgrupo = []
    for dimensao in ("sexo_referido", "faixa_etaria"):
        for valor, grupo in subgrupos.groupby(dimensao):
            linhas_subgrupo.append({"dimensao": dimensao, "grupo": valor,
                                    **metricas_binarias(grupo.situacao, grupo.predicao)})
    tabela_subgrupos = pd.DataFrame(linhas_subgrupo)
    tabela_subgrupos["matriz_confusao"] = tabela_subgrupos.matriz_confusao.map(json.dumps)
    tabela_subgrupos.to_csv(SAIDA / "metricas_subgrupos.csv", index=False)
    gaps = {}
    for dimensao, grupo in tabela_subgrupos.groupby("dimensao"):
        gaps[dimensao] = {
            "gap_acuracia": float(grupo.acuracia.max() - grupo.acuracia.min()),
            "gap_recall_alto_risco": float(grupo.recall_alto_risco.max() - grupo.recall_alto_risco.min()),
            "gap_falsos_positivos": int(grupo.falsos_positivos.max() - grupo.falsos_positivos.min()),
        }

    dummy = DummyClassifier(strategy="most_frequent").fit(treino[["grupo"]], treino.situacao)
    baseline = accuracy_score(conjuntos["teste"].situacao, dummy.predict(conjuntos["teste"][["grupo"]]))
    metricas = {
        "seed": SEED,
        "quantidades": {nome: len(df) for nome, df in conjuntos.items()},
        "grupos": {nome: int(df.grupo.nunique()) for nome, df in conjuntos.items()},
        "baseline_acuracia": float(baseline),
        "melhores_parametros": {"C": float(busca.best_params_["classificador__C"]),
                               "vetorizacao": tipo_vetor},
        "tipo_vetorizacao": tipo_vetor,
        "auditoria_nova": met_auditoria,
        "auditoria_nova_modelo_anterior": met_auditoria_anterior,
        "auditoria_contrastiva": met_contrastiva,
        "auditoria_contrastiva_modelo_anterior": met_contrastiva_anterior,
        "teste": met_teste,
        "regressao": met_regressao,
        "avaliacao_externa": met_externo,
        "pares_gravidade": met_pares,
        "desafios_legados": met_desafios,
        "auditoria_subgrupos_geral": met_subgrupos,
        "gaps_subgrupos": gaps,
        "variacoes_teste": {r["variacao"]: {"n": r["n"], "acuracia": r["acuracia"],
                          "falsos_negativos": r["falsos_negativos"]} for r in por_variacao},
        "calibracao": calibracao.to_dict(orient="records"),
        "relatorio_teste": classification_report(teste.situacao, teste.predicao, labels=CLASSES,
                                                   output_dict=True, zero_division=0),
        "sha256_dataset": hashlib.sha256((RAIZ / "data/frases_risco.csv").read_bytes()).hexdigest(),
        "sha256_particoes": hashlib.sha256((RAIZ / "data/particoes.csv").read_bytes()).hexdigest(),
        "sha256_casos_adicionais": hashlib.sha256((RAIZ / "data/casos_adicionais.csv").read_bytes()).hexdigest(),
        "sha256_auditoria_nova": hashlib.sha256((RAIZ / "data/auditoria_nova.csv").read_bytes()).hexdigest(),
        "sha256_auditoria_contrastiva": hashlib.sha256((RAIZ / "data/auditoria_contrastiva.csv").read_bytes()).hexdigest(),
        "sha256_preprocessamento": hashlib.sha256((RAIZ / "src/preprocessar_texto.py").read_bytes()).hexdigest(),
        "sha256_contexto": hashlib.sha256((RAIZ / "src/contexto_sintomas.py").read_bytes()).hexdigest(),
        "python": platform.python_version(), "sklearn": sklearn.__version__,
        "numpy": np.__version__, "pandas": pd.__version__,
    }
    (SAIDA / "metricas.json").write_text(json.dumps(metricas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"auditoria_nova": met_auditoria,
                      "auditoria_anterior": met_auditoria_anterior,
                      "auditoria_contrastiva": met_contrastiva,
                      "contrastiva_anterior": met_contrastiva_anterior,
                      "teste_historico": met_teste, "externo": met_externo, "pares": met_pares,
                      "subgrupos": met_subgrupos, "gaps": gaps}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
