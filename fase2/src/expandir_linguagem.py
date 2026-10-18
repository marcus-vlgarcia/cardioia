"""Amplia a base com relatos cotidianos e partição por família de cenário.

Cada família possui seis contextos e duas redações. As famílias, e não apenas as
duas paráfrases, ficam inteiras em treino, calibração ou teste.
"""

import csv
import random
import re
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]

# Cada par descreve um contexto específico em duas redações. Os rótulos são
# escolhas didáticas para o exercício, sem validação clínica.
ALTOS = [
    ("sinto aperto no peito que continua e suor frio", "meu tórax está pressionado há um tempo e estou suando gelado"),
    ("a dor no peito desce para o braço e não melhora", "o peito dói sem parar e a dor chegou ao braço"),
    ("fiquei sem ar em repouso e mal consigo falar", "estou parado e a respiração não deixa terminar uma frase"),
    ("meu coração dispara e quase desmaio", "as batidas estão muito rápidas e a vista escurece"),
    ("desmaiei e ainda sinto palpitações", "apaguei por instantes e o coração segue irregular"),
    ("uma dor forte começou de repente no peito e nas costas", "o tórax e as costas doem como um rasgo súbito"),
    ("o rosto entortou e perdi a força de um braço", "minha boca ficou torta e um braço não responde"),
    ("não consigo respirar deitado e preciso sentar", "ao me deitar perco o fôlego e só melhoro sentado"),
    ("estou pálido, enjoado e com pressão no peito", "o aperto no tórax veio com náusea e palidez"),
    ("a dor no peito piora e começou a irradiar para a mandíbula", "o tórax aperta cada vez mais e a dor alcança o maxilar"),
    ("a falta de ar começou subitamente junto de dor ao inspirar", "perdi o fôlego de repente e cada respiração dói"),
    ("minha fala ficou enrolada e a mão perdeu força de uma vez", "as palavras saem confusas e não consigo segurar objetos com uma mão"),
    ("o peito aperta mesmo sem esforço e o suor está frio", "em repouso tenho pressão torácica contínua e transpiração gelada"),
    ("o coração bate estranho e a tontura está aumentando", "sinto batimentos descompassados e preciso me apoiar para não cair"),
    ("meu lábio ficou roxo e puxar o ar está difícil", "a boca está azulada e não recupero a respiração"),
    ("o desconforto no peito não cedeu após o descanso", "parei a atividade mas a pressão no tórax continua"),
    ("a dor no peito voltou mais forte depois de eu dizer que tinha passado", "antes neguei a dor, mas agora o peito aperta sem aliviar"),
    ("não deixei de sentir falta de ar e agora estou fraco", "a dificuldade para respirar persiste e a fraqueza piora"),
    ("tenho enjoo e suor frio com uma pressão estranha no peito", "o mal-estar veio com transpiração gelada e aperto torácico"),
    ("o braço ficou dormente subitamente e minha fala falha", "perdi a sensibilidade de um lado e não falo como antes"),
    ("depois da cirurgia minha perna inchou e fiquei sem ar", "operei há pouco e agora tenho falta de ar súbita com uma perna inchada"),
    ("o esforço acabou, mas o suor frio e a dor no peito continuam", "já estou descansando e mesmo assim o tórax dói com suor gelado"),
    ("a dor parece pequena, porém quase apaguei e estou pálido", "o peito incomoda pouco, mas a sensação de desmaio veio com palidez"),
    ("não é verdade que não sinto dor no peito; ela persiste", "não posso afirmar que estou sem aperto no tórax; ele continua"),
]

BAIXOS = [
    ("suei na caminhada e recuperei totalmente o fôlego ao parar", "a respiração acelerou no passeio e voltou ao normal após descanso"),
    ("a camiseta apertou meu peito e o incômodo sumiu quando a tirei", "o tecido pressionava o tórax; afrouxei a roupa e passou"),
    ("o músculo do peito dói apenas quando aperto o local machucado", "consigo reproduzir a dor tocando a contusão superficial"),
    ("meu coração acelerou no susto e normalizou logo depois", "as batidas aumentaram por um instante e já acalmaram"),
    ("senti uma pontada ao espirrar que durou um segundo e não voltou", "o peito fisgou só no espirro e estou sem incômodo agora"),
    ("fiquei sem ar ao correr para o ônibus e recuperei totalmente ao parar", "a corrida me deixou ofegante por pouco tempo; já respiro normalmente"),
    ("a dor no ombro aparece só quando levanto uma caixa e cessa em repouso", "o braço fica dolorido ao erguer peso, mas não tenho dor parado"),
    ("transpirei no sol e o suor cessou ao entrar na sombra", "o calor me fez suar; depois de beber água fiquei bem"),
    ("a queimação apareceu após comer e passou sem falta de ar", "comi depressa, senti azia conhecida e agora estou normal"),
    ("o relógio mostrou pulso rápido durante a bicicleta e normal depois", "meu coração acelerou no exercício e voltou ao habitual no descanso"),
    ("a fala ficou esquisita porque mordi a língua e já melhorou", "falei com cuidado por uma feridinha na boca, sem fraqueza"),
    ("tive tontura por dois segundos ao levantar e ela não voltou", "a visão escureceu ao erguer rápido, sentei e fiquei bem"),
    ("minha irmã sentiu falta de ar, mas eu respiro normalmente", "quem ficou sem fôlego foi outra pessoa; comigo está tudo bem"),
    ("o cinto apertou o peito e a marca sumiu quando o soltei", "a pressão era só do cinto de segurança e desapareceu"),
    ("o nariz entupiu com poeira mas consigo respirar sem dificuldade", "espirrei na limpeza e continuo respirando normalmente"),
    ("senti o peito sensível onde a mochila bateu e a dor já cessou", "a alça fez uma marca superficial no tórax que passou"),
    ("o café acelerou brevemente as batidas sem tontura ou dor", "percebi palpitação curta após cafeína e agora me sinto normal"),
    ("a falta de ar que mencionei era modo de falar; respiro bem", "usei uma expressão exagerada mas não tive dificuldade respiratória"),
    ("senti uma fisgada ao girar o tronco e passou quando parei", "a pontada apareceu só no movimento e sumiu logo"),
    ("o suor veio do treino e parou junto com a respiração rápida", "depois de descansar do exercício, o suor cessou e fiquei bem"),
    ("minha voz saiu arrastada por sono e normalizou após descansar", "eu estava sonolento e falei devagar; acordei bem e sem fraqueza"),
    ("a pressão no peito era da faixa da mochila e sumiu ao tirá-la", "a mochila comprimia o tórax, mas sem ela não sinto nada"),
    ("o coração disparou na apresentação e acalmou no fim", "fiquei nervoso ao falar em público e as batidas já normalizaram"),
    ("não tive dor no peito nem suor frio; só uma coceira leve no braço", "meu tórax está bem e a única queixa é pele ressecada"),
]

CONTEXTOS = (
    ("direto", "{relato}."),
    ("tempo", "Há algumas horas, {relato}."),
    ("rotina", "Percebi isso no meio do dia: {relato}."),
    ("coloquial", "Olha, tipo assim, {relato}, sabe?"),
    ("hesitacao", "Então... eu acho que {relato}."),
    ("erro_ortografico", "Oi, {relato}."),
)

ERROS = (
    ("peito", "peitto"), ("tórax", "torax"), ("falta", "flata"),
    ("coração", "corasão"), ("respirar", "respriar"), ("suor", "sour"),
    ("tontura", "totnura"), ("braço", "braco"), ("pressão", "presão"),
    ("pálido", "palido"), ("dor", "dorr"), ("batidas", "batids"),
)


def com_erro(texto):
    for correto, variante in ERROS:
        if re.search(rf"\b{re.escape(correto)}\b", texto, flags=re.IGNORECASE):
            return re.sub(rf"\b{re.escape(correto)}\b", variante, texto, count=1, flags=re.IGNORECASE)
    # Uma troca de letras produz um erro comum também nos relatos sem os termos
    # acima. O rótulo e a gravidade do cenário não são alterados.
    palavra = re.search(r"\b[a-záéíóúâêôãõç]{6,}\b", texto, flags=re.IGNORECASE)
    if palavra is None:
        raise ValueError(f"Não há palavra para perturbar neste relato: {texto}")
    original = palavra.group()
    trocada = original[:2] + original[3] + original[2] + original[4:]
    return texto[:palavra.start()] + trocada + texto[palavra.end():]


def ler_csv(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def gravar_csv(caminho, campos, linhas):
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=campos, lineterminator="\n")
        writer.writeheader()
        writer.writerows(linhas)


def main():
    caminho_dados = RAIZ / "data/frases_risco.csv"
    caminho_particoes = RAIZ / "data/particoes.csv"
    antigos = [r for r in ler_csv(caminho_dados) if r["grupo"].startswith(("A", "B"))]
    manifestos = [r for r in ler_csv(caminho_particoes) if r["grupo"].startswith(("A", "B"))]
    if len(antigos) != 416 or len(manifestos) != 208:
        raise ValueError("A expansão espera a base anterior de 416 frases e 208 grupos.")

    for linha in manifestos:
        if linha["conjunto"] == "teste":
            linha["conjunto"] = "regressao"
        linha["familia"] = linha["grupo"]
        linha["variacao"] = "versao_anterior"

    indices = list(range(24))
    random.Random(42).shuffle(indices)
    particao = {i: ("treino" if pos < 10 else "calibracao" if pos < 13 else "teste")
                for pos, i in enumerate(indices)}
    novos = []
    for prefixo, classe, sementes in (("C", "alto risco", ALTOS), ("D", "baixo risco", BAIXOS)):
        assert len(sementes) == 24
        for i, par in enumerate(sementes):
            familia = f"{prefixo}{i + 1:02d}"
            for j, (variacao, formato) in enumerate(CONTEXTOS):
                grupo = f"{familia}-{j + 1}"
                for relato in par:
                    frase = formato.format(relato=com_erro(relato) if variacao == "erro_ortografico" else relato)
                    novos.append({"frase": frase[0].upper() + frase[1:], "situacao": classe, "grupo": grupo})
                manifestos.append({"grupo": grupo, "conjunto": particao[i],
                                   "familia": familia, "variacao": variacao})

    complementares = ler_csv(RAIZ / "data/casos_adicionais.csv")
    if len(complementares) != 120 or len({r["grupo"] for r in complementares}) != 120:
        raise ValueError("Os 120 cenários adicionais devem ter grupos exclusivos.")
    for linha in complementares:
        if linha["situacao"] not in {"alto risco", "baixo risco"}:
            raise ValueError(f"Rótulo desconhecido no cenário {linha['id']}.")
        novos.append({chave: linha[chave] for chave in ("frase", "situacao", "grupo")})
        manifestos.append({"grupo": linha["grupo"], "conjunto": "treino",
                           "familia": linha["grupo"], "variacao": "caso_adicional"})

    todas = antigos + novos
    normalizadas = [r["frase"].casefold().strip() for r in todas]
    if len(set(normalizadas)) != len(normalizadas):
        raise ValueError("A ampliação produziu frases duplicadas.")
    gravar_csv(caminho_dados, ["frase", "situacao", "grupo"], todas)
    gravar_csv(caminho_particoes, ["grupo", "conjunto", "familia", "variacao"], manifestos)
    print(f"Base: {len(todas)} frases; novo teste: {sum(r['conjunto'] == 'teste' for r in manifestos) * 2} frases.")


if __name__ == "__main__":
    main()
