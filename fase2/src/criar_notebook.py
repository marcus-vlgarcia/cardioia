"""Recria o notebook didático a partir do experimento versionado."""

from pathlib import Path

import nbformat as nbf


DESTINO = Path(__file__).resolve().parents[1] / "notebooks/classificador_risco.ipynb"


def main():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# Classificação textual de risco — PulseIA\n\n"
            "Frases simuladas, TF-IDF e Regressão Logística. Este exercício não produz diagnóstico "
            "nem probabilidade de risco clínico. A versão avaliada na Fase 2 está preservada "
            "na branch `fase2-entrega`."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import sys\n"
            "import pandas as pd\n"
            "from IPython.display import display\n"
            "from sklearn.calibration import CalibratedClassifierCV\n"
            "from sklearn.frozen import FrozenEstimator\n"
            "from sklearn.metrics import classification_report, ConfusionMatrixDisplay, confusion_matrix\n"
            "from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold\n"
            "import matplotlib.pyplot as plt\n\n"
            "RAIZ = next(p for p in [Path.cwd(), *Path.cwd().parents] "
            "if (p / 'fase2/data/frases_risco.csv').exists())\n"
            "sys.path.insert(0, str(RAIZ / 'fase2/src'))\n"
            "from avaliar_classificador import criar_modelo, candidatos_vetorizacao, nome_vetorizacao, prever, metricas_binarias\n"
            "dados = pd.read_csv(RAIZ / 'fase2/data/frases_risco.csv')\n"
            "particoes = pd.read_csv(RAIZ / 'fase2/data/particoes.csv')\n"
            "dados = dados.merge(particoes, on='grupo', validate='many_to_one')\n"
            "display(dados.head())"
        ),
        nbf.v4.new_markdown_cell(
            "## Composição e separação\n\n"
            "As frases são sintéticas. Duas redações do mesmo grupo e seis variações da mesma "
            "família permanecem na mesma partição. O teste final foi reservado antes da busca "
            "de configurações; a regressão contém casos de versões anteriores."
        ),
        nbf.v4.new_code_cell(
            "display(dados.groupby(['conjunto', 'situacao']).agg(" 
            "frases=('frase', 'size'), grupos=('grupo', 'nunique'), familias=('familia', 'nunique')))\n"
            "conjuntos = {n: dados[dados.conjunto == n].copy() "
            "for n in ('treino', 'calibracao', 'teste', 'regressao')}\n"
            "assert tuple(len(conjuntos[n]) for n in conjuntos) == (496, 88, 264, 144)\n"
            "assert not dados.frase.str.casefold().str.strip().duplicated().any()\n"
            "for a in conjuntos:\n"
            "    for b in conjuntos:\n"
            "        if a < b:\n"
            "            assert set(conjuntos[a].familia).isdisjoint(conjuntos[b].familia)"
        ),
        nbf.v4.new_markdown_cell(
            "## TF-IDF, seleção e treinamento\n\n"
            "Comparamos palavras de 1–2 e 1–3 termos e uma opção combinada de palavras e "
            "caracteres. A validação cruzada usa apenas o treino, agrupado por família, "
            "para escolher a configuração pelo F1 macro. Não escolhemos a configuração "
            "pela acurácia do teste final."
        ),
        nbf.v4.new_code_cell(
            "treino = conjuntos['treino']\n"
            "busca = GridSearchCV(criar_modelo(), {\n"
            "    'tfidf': candidatos_vetorizacao(),\n"
            "    'classificador__C': [0.5, 2.0, 8.0],\n"
            "}, cv=StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=42),\n"
            "   scoring={'acuracia': 'accuracy', 'f1_macro': 'f1_macro'}, refit='f1_macro')\n"
            "busca.fit(treino.frase, treino.situacao, groups=treino.familia)\n"
            "modelo_base = busca.best_estimator_\n"
            "comparacao = pd.DataFrame(busca.cv_results_)\n"
            "comparacao['vetorizacao'] = comparacao.param_tfidf.map(nome_vetorizacao)\n"
            "display(comparacao[['rank_test_f1_macro', 'mean_test_f1_macro', "
            "'mean_test_acuracia', 'vetorizacao', 'param_classificador__C']]" 
            ".sort_values('rank_test_f1_macro'))\n"
            "print('Configuração escolhida:', nome_vetorizacao(modelo_base.named_steps['tfidf']), "
            "'C=', busca.best_params_['classificador__C'])"
        ),
        nbf.v4.new_markdown_cell(
            "## Avaliação reservada\n\n"
            "A calibração sigmoide usa somente 88 frases próprias. O teste tem 264 frases, "
            "mas apenas 22 famílias novas: variações da mesma família não equivalem a "
            "pacientes ou casos clínicos independentes."
        ),
        nbf.v4.new_code_cell(
            "modelo = CalibratedClassifierCV(FrozenEstimator(modelo_base), method='sigmoid')\n"
            "modelo.fit(conjuntos['calibracao'].frase, conjuntos['calibracao'].situacao)\n"
            "teste = conjuntos['teste'].copy()\n"
            "teste['predicao'], teste['probabilidade_alto_risco'] = prever(modelo, teste.frase)\n"
            "teste['acerto'] = teste.situacao.eq(teste.predicao)\n"
            "display(pd.DataFrame(classification_report(teste.situacao, teste.predicao, "
            "output_dict=True, zero_division=0)).T)\n"
            "display(pd.DataFrame([metricas_binarias(teste.situacao, teste.predicao)]))\n"
            "ConfusionMatrixDisplay(confusion_matrix(teste.situacao, teste.predicao, "
            "labels=['baixo risco', 'alto risco']), "
            "display_labels=['baixo risco', 'alto risco']).plot(cmap='Blues')\n"
            "plt.show()"
        ),
        nbf.v4.new_code_cell(
            "display(teste.groupby('variacao').agg(n=('acerto', 'size'), "
            "acuracia=('acerto', 'mean')))\n"
            "display(teste[~teste.acerto][['familia', 'variacao', 'frase', 'situacao', "
            "'predicao']].head(30))"
        ),
        nbf.v4.new_markdown_cell(
            "## Conjuntos complementares e limites\n\n"
            "As frases externas são redigidas a partir de fontes públicas, não são relatos "
            "reais nem têm rótulo validado por especialista. Pares de gravidade testam "
            "vocabulário semelhante em contextos diferentes. As probabilidades representam "
            "a saída do classificador nesta amostra, não risco clínico."
        ),
        nbf.v4.new_code_cell(
            "linhas = []\n"
            "for arquivo in ('avaliacao_externa.csv', 'pares_gravidade.csv', "
            "'avaliacao_subgrupos.csv'):\n"
            "    df = pd.read_csv(RAIZ / 'fase2/data' / arquivo)\n"
            "    df['predicao'], _ = prever(modelo, df.frase)\n"
            "    linhas.append({'conjunto': arquivo, **metricas_binarias(df.situacao, df.predicao)})\n"
            "display(pd.DataFrame(linhas))\n"
            "print('Erros do teste final:', len(teste[~teste.acerto]))"
        ),
    ]
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}}
    nbf.write(nb, DESTINO)
    print("Notebook criado:", DESTINO)


if __name__ == "__main__":
    main()
