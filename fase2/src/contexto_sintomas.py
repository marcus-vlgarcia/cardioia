"""Utilitários simples para reconhecer afirmação, negação e contradição.

O módulo não tenta interpretar toda a língua portuguesa. Ele registra decisões
reproduzíveis para os casos usados neste projeto e sinaliza ambiguidades em vez
de escondê-las.
"""

import re
import unicodedata


CONTRASTES = r"\b(?:mas|porem|contudo|entretanto|so que)\b"
NEGADORES = r"\b(?:nao|nunca|jamais|sem|nego|nega|negou|nem)\b"
PADROES_DUPLA_NEGACAO = (
    r"\bnao\s+(?:e\s+verdade\s+que\s+)?nao\s+(?:tenho|sinto|estou\s+com|apresento)?\s*$",
    r"\bnao\s+(?:deixei|deixo|parei)\s+de\s+(?:ter|sentir|apresentar)\s*$",
    r"\bnao\s+(?:estou|fiquei|fico)\s+sem\s*$",
)


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto.casefold())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip()


def separar_trechos(texto):
    """Separa pontuação e contrastes, mantendo a ordem em que foram relatados."""
    return [t.strip() for t in re.split(rf"[.;!?]+|{CONTRASTES}", normalizar(texto)) if t.strip()]


def estado_da_ocorrencia(trecho, inicio):
    """Classifica a menção pelo contexto imediatamente anterior à expressão."""
    prefixo = trecho[max(0, inicio - 90):inicio].strip()
    # Uma nova oração com verbo afirmativo encerra o alcance da negação anterior:
    # "não tenho dor no peito e sinto falta de ar".
    reinicios = list(re.finditer(
        r"\be\s+(?:agora\s+)?(?:sinto|tenho|estou\s+com|apresento|comecei\s+a\s+sentir)\b",
        prefixo,
    ))
    if reinicios:
        prefixo = prefixo[reinicios[-1].start():]
    palavras = prefixo.split()
    janela = " ".join(palavras[-10:])
    if any(re.search(padrao, janela) for padrao in PADROES_DUPLA_NEGACAO):
        return "afirmado_dupla_negacao"
    if re.search(NEGADORES, janela):
        return "negado"
    return "afirmado"


def classificar_expressao(texto, expressao):
    """Retorna estados das ocorrências e informa se há versões contraditórias."""
    padrao = r"(?<!\w)" + re.escape(normalizar(expressao)) + r"(?!\w)"
    estados = []
    for trecho in separar_trechos(texto):
        estados.extend(estado_da_ocorrencia(trecho, m.start()) for m in re.finditer(padrao, trecho))
    afirmado = any(e.startswith("afirmado") for e in estados)
    negado = "negado" in estados
    return {
        "estados": estados,
        "afirmado": afirmado,
        "negado": negado,
        "dupla_negacao": "afirmado_dupla_negacao" in estados,
        "contraditorio": afirmado and negado,
    }


def analisar_expressoes(texto, expressoes):
    resultado = {e: classificar_expressao(texto, e) for e in expressoes}
    return {
        "afirmadas": sorted(e for e, estado in resultado.items() if estado["afirmado"]),
        "negadas": sorted(e for e, estado in resultado.items() if estado["negado"]),
        "dupla_negacao": sorted(e for e, estado in resultado.items() if estado["dupla_negacao"]),
        "contraditorias": sorted(e for e, estado in resultado.items() if estado["contraditorio"]),
    }
