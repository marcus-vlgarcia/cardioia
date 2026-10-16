"""Gera os conjuntos adicionais da revisão pós-avaliação da Fase 2.

O script preserva os 288 exemplos avaliados, transforma o antigo teste em
regressão e acrescenta cenários novos, um teste final maior, avaliações externas
baseadas em fontes públicas e testes sintéticos de subgrupos.
"""

import csv
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
MS_INFARTO = "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/i/infarto"
MS_DOR = "https://linhasdecuidado.saude.gov.br/portal/dor-toracica/unidade-de-atencao-primaria/manejo-inicial/"
MS_AVALIACAO = "https://linhasdecuidado.saude.gov.br/portal/dor-toracica/unidade-de-pronto-atendimento/avaliacao-conduta/"
OMS_DCV = "https://www.who.int/health-topics/cardiovascular-diseases"
FONTES_CONDICOES = {
    "coronariana": MS_INFARTO,
    "angina": "https://bvsms.saude.gov.br/angina/",
    "insuficiência cardíaca": "https://linhasdecuidado.saude.gov.br/portal/insuficiencia-cardiaca-%28IC%29-no-adulto/sou-paciente",
    "arritmia": "https://www.ce.gov.br/saude/2019/11/06/arritmia-cardiaca-conheca-mais-sobre-a-doenca-e-saiba-como-trata-la-corretamente/",
    "valvulopatia": MS_AVALIACAO,
    "pericardite": MS_AVALIACAO,
    "miocardite": MS_AVALIACAO,
    "estresse": "https://bvsms.saude.gov.br/sindrome-do-coracao-partido/",
    "dissecção": MS_AVALIACAO,
    "pressão arterial": "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/h/hipertensao",
    "tromboembolismo": "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/t/trombose",
    "refluxo": MS_AVALIACAO,
    "musculoesquelética": MS_AVALIACAO,
    "ansiedade": MS_AVALIACAO,
}


ALTOS = [
    ("Faz meia hora que um peso no peito não passa e comecei a suar gelado.", "Tem uns trinta minutos que meu peito pesa direto e o suor ficou frio."),
    ("Acordei de madrugada sufocado e só consigo respirar sentado.", "Quando deito perco o ar; precisei sentar na cama para voltar a respirar."),
    ("No ônibus, apaguei de repente e ainda estou com o coração disparado.", "Desmaiei durante o trajeto e as batidas continuam muito rápidas."),
    ("A dor rasgou do peito para as costas de uma hora para outra.", "Senti uma dor súbita, como um rasgo entre o tórax e as costas."),
    ("Minha boca entortou e um braço ficou sem força agora há pouco.", "De repente meu rosto ficou torto e não consigo levantar um dos braços."),
    ("Estou grávida e surgiu falta de ar forte com dor ao puxar o ar.", "Na gestação comecei a respirar mal de repente e dói quando inspiro."),
    ("Depois da cirurgia, uma perna inchou e agora fiquei subitamente sem ar.", "Operei recentemente; minha panturrilha inchou e hoje perdi o fôlego de uma vez."),
    ("A pressão no peito vai para a mandíbula e não melhora parado.", "Mesmo em repouso o aperto continua e sobe do tórax para o maxilar."),
    ("Estou com uma fraqueza diferente, enjoo e suor frio, embora o peito quase não doa.", "Mal sinto o tórax, mas o mal-estar veio súbito com náusea e transpiração fria."),
    ("Meu coração bate todo errado e a vista escurece quando tento ficar em pé.", "As batidas estão irregulares e quase desmaio sempre que levanto."),
    ("A dor no peito piora e já dura mais de quarenta minutos.", "Estou há quase uma hora com desconforto torácico cada vez mais forte."),
    ("Não tenho tosse nem febre, porém falta ar até para terminar uma palavra.", "Não parece gripe; mesmo parado não consigo completar uma frase sem respirar."),
    ("Não é verdade que não sinto dor no peito: ela voltou forte com suor frio.", "Não posso dizer que não tenho aperto no tórax; agora veio com transpiração gelada."),
    ("Eu não deixei de sentir falta de ar desde que acordei e agora estou tonto.", "Não parei de ficar sem ar durante a manhã e a tontura está aumentando."),
    ("Primeiro falei que não doía, mas a dor no peito apareceu e ficou intensa.", "No começo neguei dor; depois o tórax passou a apertar sem aliviar."),
    ("Não estou sem falta de ar: preciso parar no meio de cada frase.", "Não fiquei sem dificuldade para respirar; falar já exige várias pausas."),
    ("A dor no peito parece leve, só que veio junto de desmaio.", "O incômodo torácico não é forte, porém apaguei por alguns segundos."),
    ("Suei depois do esforço, mas também apareceu pressão no peito que não passou com descanso.", "O treino acabou e o suor continua frio, com aperto persistente no tórax."),
    ("Fiquei ofegante ao subir a escada e, mesmo sentado, a falta de ar está piorando.", "Parei o esforço há vinte minutos, mas ainda não recupero o fôlego e estou pior."),
    ("Meu coração acelerou após o café e agora há dor no peito e sensação de desmaio.", "Depois da cafeína vieram palpitações, aperto torácico e quase desmaiei."),
    ("Acordei com azia, mas também estou pálido e com pressão forte no peito.", "Achei que fosse queimação; a dor persiste e veio com palidez e suor frio."),
    ("A dor aumenta quando respiro, começou de repente e estou sem ar.", "Cada inspiração dói no peito e a falta de ar surgiu subitamente."),
    ("Tenho diabetes e hoje apareceu um cansaço súbito com suor frio e enjoo.", "Sou diabético; fiquei muito fraco de repente, nauseado e transpirando frio."),
    ("Minha mãe percebeu que estou confuso e eu mal consigo respirar.", "Estou desorientado e com dificuldade importante para puxar o ar."),
    ("Faz dez minutos que perdi a visão de um lado e minha fala enrolou.", "Minha visão falhou de repente e as palavras começaram a sair embaralhadas."),
    ("A batida ficou muito lenta e apaguei enquanto estava sentado.", "Mesmo sem esforço, o coração desacelerou e perdi a consciência."),
    ("Tenho dor forte no peito depois de usar estimulante e estou muito agitado.", "Após consumir uma substância estimulante, surgiu aperto intenso no tórax."),
    ("A falta de ar veio com lábios arroxeados e não melhora sentado.", "Minha boca ficou roxa enquanto tento respirar, mesmo em repouso."),
    ("O desconforto no peito vai e volta desde cedo, mas agora não cede e estou suando frio.", "A pressão torácica era intermitente; tornou-se contínua e veio com suor gelado."),
    ("Não nego falta de ar: ela começou de repente com pontada no peito.", "Não é correto dizer que respiro bem; perdi o fôlego subitamente e o tórax dói."),
    ("Eu disse que estava bem para não preocupar ninguém, mas desmaiei e continuo fraco.", "Apesar de ter negado sintomas antes, perdi a consciência e não recuperei a força."),
    ("A dor parece muscular, porém não muda ao tocar e veio com náusea e suor frio.", "Achei que fosse músculo, mas apertar o local não reproduz a dor e estou nauseado."),
]


BAIXOS = [
    ("Depois da corrida suei e fiquei ofegante, mas em cinco minutos voltei ao normal.", "O treino me fez suar e respirar rápido; descansei e tudo passou completamente."),
    ("A alça da mochila deixou um ponto dolorido no peito que dói ao apertar.", "Consigo reproduzir o incômodo tocando onde a mochila pressionou o tórax."),
    ("Meu peito não dói e respiro bem; só estou rouco depois de cantar.", "A voz cansou no ensaio, sem aperto torácico ou falta de ar."),
    ("Minha mãe está com palpitação; eu apenas cortei o dedo e estou bem.", "Quem sentiu o coração acelerar foi minha mãe, não eu; meu corte é superficial."),
    ("Nunca tive falta de ar hoje, apenas espirros por causa da poeira.", "Estou respirando normalmente e só espirrei enquanto limpava a estante."),
    ("A meia apertada marcou o tornozelo, mas o inchaço sumiu quando tirei.", "O elástico deixou uma marca leve que desapareceu logo, sem dor ou falta de ar."),
    ("Tomei café e percebi o coração um pouco rápido, sem tontura, dor ou desmaio.", "As batidas aceleraram brevemente após a cafeína e já normalizaram."),
    ("Virei o tronco e senti uma fisgada localizada que passa quando fico parado.", "A pontada aparece só ao girar o corpo e consigo apontar o lugar exato."),
    ("Não é verdade que eu tenha falta de ar; consigo conversar e caminhar normalmente.", "Não estou com dificuldade para respirar e mantive minha rotina sem limitação."),
    ("Eu não deixei de respirar bem em nenhum momento; só estou com nariz entupido.", "Continuo respirando sem esforço, apesar da congestão nasal leve."),
    ("Ontem achei que meu peito doía, mas percebi que era a etiqueta da roupa arranhando.", "O desconforto que mencionei era superficial e sumiu ao trocar a camiseta."),
    ("Falei que estava sem ar por nervosismo, porém a respiração normalizou em segundos.", "A ansiedade acelerou a respiração por instantes e ela voltou ao normal por completo."),
    ("Suei carregando caixas, parei e agora estou sem dor, tontura ou falta de ar.", "O suor veio do esforço e cessou após descanso; estou me sentindo normal."),
    ("A palavra infarto apareceu na televisão; comigo há só uma coceira no cotovelo.", "Ouvi uma notícia sobre dor no peito, mas minha única queixa é pele ressecada."),
    ("O relógio marcou pulso alto durante a bicicleta e normalizou logo ao terminar.", "Minha frequência subiu no exercício como esperado e voltou ao habitual no repouso."),
    ("Tenho uma dor pequena no peito que aparece apenas quando pressiono uma contusão antiga.", "O local roxo fica sensível ao toque, sem aperto interno ou outros sintomas."),
    ("A dor no peito durou um segundo ao espirrar e não voltou.", "Senti uma pontada muito breve com o espirro; depois fiquei completamente bem."),
    ("Fiquei sem fôlego ao correr para o ônibus, mas recuperei totalmente assim que parei.", "A corrida curta acelerou a respiração; o descanso resolveu em poucos minutos."),
    ("Senti o coração bater forte durante um susto e ele acalmou logo depois.", "As palpitações ocorreram só no susto e cessaram sem qualquer outro sintoma."),
    ("A queimação veio após uma refeição grande, melhora ao sentar e não há suor frio.", "Depois de comer demais surgiu azia conhecida, sem falta de ar ou mal-estar."),
    ("O ombro dói quando levanto peso, mas não há dor no peito em repouso.", "A dor aparece apenas ao movimentar o braço e melhora quando paro o exercício."),
    ("Minha fala ficou estranha porque mordi a língua; a força dos braços está normal.", "Estou falando com cuidado por causa de uma ferida na boca, sem fraqueza súbita."),
    ("Ao levantar rápido tive tontura por dois segundos, sentei e fiquei bem.", "A visão escureceu brevemente quando me ergui; passou de imediato e não voltou."),
    ("Estou cansado depois de dormir pouco, mas faço minhas tarefas e respiro normalmente.", "A noite mal dormida deixou sonolência leve, sem limitação física ou sinais de alerta."),
    ("Não sinto mais a palpitação mencionada ontem e passei o dia sem sintomas.", "As batidas diferentes não voltaram; hoje estou ativo e me sentindo normal."),
    ("A respiração está normal; dizer que fiquei sem ar foi apenas modo de falar.", "Usei a expressão 'sem ar' como exagero, mas não tive dificuldade respiratória."),
    ("O suor estava quente por causa do sol e parou quando entrei em um local fresco.", "Transpirei no calor, hidratei-me e não tive dor, tontura ou falta de ar."),
    ("Senti pressão onde o cinto de segurança apertou e ela desapareceu ao soltá-lo.", "O cinto comprimiu o tórax por instantes; depois fiquei sem qualquer incômodo."),
    ("Meu coração acelerou na apresentação, mas não houve dor e ele acalmou ao final.", "O nervosismo da fala aumentou as batidas temporariamente, sem outros sintomas."),
    ("Tenho falta de ar somente quando prendo voluntariamente a respiração na natação.", "Fora do exercício de apneia, respiro bem e realizo todas as atividades."),
    ("A dor é na pele do peito por causa de uma picada e coça quando encosto.", "Há uma picada superficial no tórax, com coceira localizada e sem mal-estar."),
    ("Não tive desmaio; apenas cochilei no sofá e acordei normalmente.", "Eu adormeci por cansaço, não perdi a consciência e não havia outros sintomas."),
]


EXTERNOS = [
    ("E01", "Estou com dor intensa e prolongada no peito, suor frio e sensação de desmaio.", "alto risco", MS_INFARTO, "combinação de sinais de alerta descrita pelo Ministério da Saúde"),
    ("E02", "A pressão no tórax se espalha para o braço esquerdo e estou pálido.", "alto risco", MS_INFARTO, "dor irradiada e palidez"),
    ("E03", "Sou idoso e fiquei subitamente sem ar, mesmo sem uma dor forte no peito.", "alto risco", MS_INFARTO, "apresentação atípica descrita para idosos"),
    ("E04", "Tenho diabetes e surgiu um mal-estar repentino com náusea e suor frio.", "alto risco", MS_INFARTO, "possível apresentação sem sinal específico"),
    ("E05", "A dor torácica começou de repente, continua forte e não melhora.", "alto risco", MS_DOR, "dor aguda e persistente"),
    ("E06", "Senti uma dor súbita como rasgo, do peito para as costas.", "alto risco", MS_AVALIACAO, "característica descrita para síndrome aórtica aguda"),
    ("E07", "Comecei a ter falta de ar e dor no peito de forma repentina.", "alto risco", MS_DOR, "sinais que exigem avaliação imediata"),
    ("E08", "Meu rosto perdeu força de um lado e não consigo falar direito.", "alto risco", OMS_DCV, "sinais súbitos compatíveis com alerta de AVC"),
    ("E09", "Um braço ficou fraco de repente e estou com dificuldade para caminhar.", "alto risco", OMS_DCV, "fraqueza unilateral e alteração de marcha"),
    ("E10", "Estou com dor no centro do peito e dificuldade para respirar.", "alto risco", OMS_DCV, "sintomas descritos para ataque cardíaco"),
    ("E11", "A dor vai para a mandíbula e veio acompanhada de enjoo.", "alto risco", OMS_DCV, "irradiação e náusea"),
    ("E12", "Desmaiei e, ao acordar, o coração continuava irregular.", "alto risco", OMS_DCV, "desmaio associado a batimento irregular"),
    ("E13", "A dor piora ao deitar e melhora quando me inclino para a frente.", "alto risco", MS_AVALIACAO, "padrão que requer avaliação de causa cardíaca"),
    ("E14", "A dor no peito apareceu após cirurgia recente e veio com falta de ar.", "alto risco", MS_DOR, "contexto clínico que exige avaliação"),
    ("E15", "Estou confuso, tonto e perdi o equilíbrio de forma súbita.", "alto risco", OMS_DCV, "sinais neurológicos súbitos"),
    ("E16", "A roupa ficou encharcada de suor frio enquanto o peito apertava.", "alto risco", MS_INFARTO, "aperto torácico e sudorese fria"),
    ("E17", "A dor aparece quando aperto exatamente o músculo machucado e melhora sem mexer.", "baixo risco", MS_AVALIACAO, "dor reproduzida por palpação sugere origem musculoesquelética; rótulo apenas didático"),
    ("E18", "O incômodo surge só ao girar o tronco e consigo reproduzi-lo com o movimento.", "baixo risco", MS_AVALIACAO, "dor desencadeada por movimento; rótulo apenas didático"),
    ("E19", "Depois da corrida fiquei ofegante, mas recuperei o fôlego completamente em repouso.", "baixo risco", MS_DOR, "contraste de recuperação completa; não equivale a dispensa clínica"),
    ("E20", "Suei no exercício, parei e o suor cessou sem dor ou tontura.", "baixo risco", MS_INFARTO, "contraste controlado com ausência de combinação de alertas"),
    ("E21", "A dor é superficial, coça e fica limitada à picada na pele.", "baixo risco", MS_AVALIACAO, "exemplo de contraste não cardíaco criado para avaliação"),
    ("E22", "A palpitação aconteceu no susto e desapareceu assim que me acalmei.", "baixo risco", OMS_DCV, "exemplo contrastivo resolvido; rótulo apenas didático"),
    ("E23", "Não estou sem ar e faço minhas atividades normalmente.", "baixo risco", MS_DOR, "negação explícita de sinal de alerta"),
    ("E24", "A pontada durou um segundo ao espirrar e não retornou.", "baixo risco", MS_AVALIACAO, "exemplo contrastivo breve; rótulo apenas didático"),
    ("E25", "A queimação veio após comer e melhorou, sem palidez ou suor frio.", "baixo risco", MS_INFARTO, "contraste com sinais de alerta ausentes; não confirma refluxo"),
    ("E26", "O relógio marcou pulso rápido durante a bicicleta e normalizou no descanso.", "baixo risco", OMS_DCV, "exemplo de contexto de esforço e recuperação"),
    ("E27", "A falta de ar é da pessoa ao meu lado; eu respiro normalmente.", "baixo risco", MS_DOR, "relato de terceiro para testar atribuição"),
    ("E28", "Ontem neguei dor e hoje continuo sem qualquer desconforto no peito.", "baixo risco", MS_DOR, "negação temporal consistente"),
    ("E29", "Não tive desmaio, apenas dormi e acordei sem dificuldade.", "baixo risco", OMS_DCV, "negação de perda de consciência"),
    ("E30", "A marca da roupa no peito sumiu assim que afrouxei o tecido.", "baixo risco", MS_AVALIACAO, "estímulo mecânico superficial e resolvido"),
    ("E31", "Fiquei tonto por um instante ao levantar e o sintoma não voltou.", "baixo risco", OMS_DCV, "exemplo contrastivo resolvido; exige contexto clínico real"),
    ("E32", "A dor do ombro aparece apenas ao levantar peso e some quando paro.", "baixo risco", MS_AVALIACAO, "dor reproduzida por movimento; rótulo apenas didático"),
]


def escrever_csv(caminho, campos, linhas):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=campos, lineterminator="\n")
        writer.writeheader()
        writer.writerows(linhas)


def main():
    caminho_base = RAIZ / "data/frases_risco.csv"
    with caminho_base.open(encoding="utf-8", newline="") as arquivo:
        linhas_atuais = list(csv.DictReader(arquivo))
    if any(r["grupo"].startswith(("C", "D")) for r in linhas_atuais):
        print("A base ampliada já existe. Para reproduzi-la, use expandir_linguagem.py.")
        return
    # Os grupos originais terminam em 72; o filtro torna esta etapa idempotente.
    existentes = [r for r in linhas_atuais if int(r["grupo"][1:]) <= 72]
    novas = []
    particoes_novas = {}
    for prefixo, classe, cenarios in (("A", "alto risco", ALTOS), ("B", "baixo risco", BAIXOS)):
        for numero, frases in enumerate(cenarios, 73):
            grupo = f"{prefixo}{numero:02d}"
            if numero <= 84:
                conjunto = "treino"
            elif numero <= 88:
                conjunto = "calibracao"
            else:
                conjunto = "teste"
            particoes_novas[grupo] = conjunto
            novas.extend({"frase": frase, "situacao": classe, "grupo": grupo} for frase in frases)
    escrever_csv(caminho_base, ["frase", "situacao", "grupo"], existentes + novas)

    caminho_particoes = RAIZ / "data/particoes.csv"
    with caminho_particoes.open(encoding="utf-8", newline="") as arquivo:
        antigas = [r for r in csv.DictReader(arquivo) if int(r["grupo"][1:]) <= 72]
    manifesto = []
    for linha in antigas:
        conjunto = "regressao" if linha["conjunto"] == "teste" else linha["conjunto"]
        manifesto.append({"grupo": linha["grupo"], "conjunto": conjunto})
    manifesto.extend({"grupo": grupo, "conjunto": conjunto} for grupo, conjunto in particoes_novas.items())
    escrever_csv(caminho_particoes, ["grupo", "conjunto"], manifesto)

    externos = [{"id": i, "frase": f, "situacao": s, "fonte": fonte,
                 "criterio_documental": criterio, "uso": "somente_avaliacao"}
                for i, f, s, fonte, criterio in EXTERNOS]
    escrever_csv(RAIZ / "data/avaliacao_externa.csv",
                 ["id", "frase", "situacao", "fonte", "criterio_documental", "uso"], externos)

    pares = []
    for i in range(16):
        pares.append({"par": f"P{i+1:02d}", "frase": ALTOS[16+i][0], "situacao": "alto risco",
                      "contraste": "grave", "uso": "somente_avaliacao"})
        pares.append({"par": f"P{i+1:02d}", "frase": BAIXOS[16+i][0], "situacao": "baixo risco",
                      "contraste": "leve_ou_resolvido", "uso": "somente_avaliacao"})
    escrever_csv(RAIZ / "data/pares_gravidade.csv",
                 ["par", "frase", "situacao", "contraste", "uso"], pares)

    bases_subgrupos = [
        ("S01", "sinto pressão persistente no peito e suor frio", "alto risco"),
        ("S02", "fiquei sem ar em repouso e quase desmaiei", "alto risco"),
        ("S03", "a dor no tórax vai para o braço e não melhora", "alto risco"),
        ("S04", "meu rosto perdeu força de um lado e a fala enrolou", "alto risco"),
        ("S05", "o coração está irregular e a vista escureceu", "alto risco"),
        ("S06", "uma dor súbita atravessou do peito para as costas", "alto risco"),
        ("S07", "suei na caminhada e fiquei bem depois de descansar", "baixo risco"),
        ("S08", "a fisgada aparece somente quando aperto o músculo", "baixo risco"),
        ("S09", "o coração acelerou no susto e já voltou ao normal", "baixo risco"),
        ("S10", "não tenho dor no peito nem dificuldade para respirar", "baixo risco"),
        ("S11", "a queimação começou após comer e melhorou", "baixo risco"),
        ("S12", "tive tontura por um segundo ao levantar e ela passou", "baixo risco"),
    ]
    identidades = [("mulher", "jovem", "Sou uma mulher de 30 anos e"),
                   ("homem", "jovem", "Sou um homem de 30 anos e"),
                   ("mulher", "idosa", "Sou uma mulher de 75 anos e"),
                   ("homem", "idosa", "Sou um homem de 75 anos e")]
    subgrupos = []
    for caso, texto, classe in bases_subgrupos:
        for sexo, faixa, inicio in identidades:
            subgrupos.append({"caso": caso, "frase": f"{inicio} {texto}.", "situacao": classe,
                              "sexo_referido": sexo, "faixa_etaria": faixa, "uso": "somente_auditoria"})
    escrever_csv(RAIZ / "data/avaliacao_subgrupos.csv",
                 ["caso", "frase", "situacao", "sexo_referido", "faixa_etaria", "uso"], subgrupos)

    with (RAIZ / "data/mapa_conhecimento.csv").open(encoding="utf-8", newline="") as arquivo:
        mapa = list(csv.DictReader(arquivo))
    revisao = []
    for numero, linha in enumerate(mapa, 1):
        nome = linha["doenca_associada"].casefold()
        fonte = next((url for chave, url in FONTES_CONDICOES.items() if chave in nome), MS_DOR)
        revisao.append({
            "id_associacao": f"MC{numero:03d}", **linha, "fonte_documental": fonte,
            "triagem_documental": "realizada",
            "validacao_especialista": "pendente",
            "nome_revisor": "", "registro_profissional": "", "data_revisao": "",
            "parecer": "", "observacoes": "A fonte contextualiza a condição; não valida isoladamente este par.",
        })
    escrever_csv(RAIZ / "data/revisao_clinica.csv",
                 ["id_associacao", "sintoma_1", "sintoma_2", "doenca_associada", "fonte_documental",
                  "triagem_documental", "validacao_especialista", "nome_revisor", "registro_profissional",
                  "data_revisao", "parecer", "observacoes"], revisao)

    print(f"Base principal: {len(existentes) + len(novas)} frases.")
    print(f"Avaliação externa: {len(externos)}; pares de gravidade: {len(pares)}; subgrupos: {len(subgrupos)}.")
    print(f"Ficha de revisão clínica: {len(revisao)} associações; validação profissional permanece pendente.")


if __name__ == "__main__":
    main()
