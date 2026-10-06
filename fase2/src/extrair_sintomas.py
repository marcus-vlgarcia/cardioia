"""Associa expressões a condições usando um mapa didático, sem diagnóstico clínico."""

import argparse
import csv
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
AVISO = "Simulação acadêmica: as associações não confirmam nem excluem doenças."


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(c for c in texto if not unicodedata.combining(c))


def ler_mapa(caminho):
    with Path(caminho).open(encoding="utf-8", newline="") as arquivo:
        mapa = list(csv.DictReader(arquivo))
    if not mapa or not {"sintoma_1", "sintoma_2", "doenca_associada"} <= mapa[0].keys():
        raise ValueError("Mapa vazio ou sem as três colunas obrigatórias.")
    if any(not (linha.get(coluna) or "").strip()
           for linha in mapa for coluna in ("sintoma_1", "sintoma_2", "doenca_associada")):
        raise ValueError("O mapa contém sintomas ou associações vazios.")
    return mapa


def expressoes_afirmadas(texto, expressoes):
    # Negação simples até a próxima pontuação ou conjunção de contraste.
    # Não resolve negação dupla, fala de terceiros ou contexto temporal complexo.
    trechos = re.split(r"[.,;!?]|\b(?:mas|porem|contudo)\b", normalizar(texto))
    encontrados = set()
    for expressao in expressoes:
        padrao = r"(?<!\w)" + re.escape(normalizar(expressao)) + r"(?!\w)"
        for trecho in trechos:
            for ocorrencia in re.finditer(padrao, trecho):
                prefixo = trecho[:ocorrencia.start()]
                if not re.search(r"\b(?:nao|sem|nego|nega|nem)\b", prefixo):
                    encontrados.add(expressao)
    return sorted(encontrados)


def expressoes_mais_especificas(expressoes):
    """Evita exibir tanto uma expressão como sua versão contida em outra."""
    return sorted(
        expressao for expressao in expressoes
        if not any(
            expressao != outra
            and normalizar(expressao) in normalizar(outra)
            for outra in expressoes
        )
    )


def analisar(frase, mapa):
    expressoes = {r[c] for r in mapa for c in ("sintoma_1", "sintoma_2")}
    sintomas = expressoes_afirmadas(frase, expressoes)
    # Os dois sintomas da linha precisam estar presentes. Todas as associações
    # compatíveis são mantidas: uma palavra isolada não define uma doença.
    condicoes = sorted({r["doenca_associada"] for r in mapa
                        if r["sintoma_1"] in sintomas and r["sintoma_2"] in sintomas})
    return {"frase": frase, "sintomas": " | ".join(expressoes_mais_especificas(sintomas)),
            "associacoes": " | ".join(condicoes) or "Associação insuficiente no mapa",
            "aviso": AVISO}


def remover_inicio(texto, expressoes):
    texto = texto.strip().rstrip(".")
    for expressao in expressoes:
        if texto.casefold().startswith(expressao):
            return texto[len(expressao):].lstrip()
    return texto


def montar_frase(tempo, sintomas, impacto):
    """Organiza três respostas curtas no padrão dos relatos da atividade."""
    tempo = tempo.strip().rstrip(".")
    sintomas = remover_inicio(sintomas, ("eu sinto ", "sinto ", "eu tenho ", "tenho ", "estou com "))
    impacto = remover_inicio(impacto, ("isso ", "os sintomas "))
    if not all((tempo, sintomas, impacto)):
        raise ValueError("Preencha tempo, sintomas e impacto na rotina.")
    return f"{tempo[:1].upper()}{tempo[1:]}, sinto {sintomas}, e {impacto}."


def salvar_historico(resultado, caminho):
    """Acrescenta um relato interativo e sua análise a um CSV local separado."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    possui_conteudo = caminho.exists() and caminho.stat().st_size > 0
    if possui_conteudo:
        with caminho.open(encoding="utf-8", newline="") as arquivo:
            if csv.DictReader(arquivo).fieldnames != list(resultado):
                raise ValueError("O histórico existente possui colunas incompatíveis.")
    with caminho.open("a", encoding="utf-8", newline="") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=resultado.keys(), lineterminator="\n")
        if not possui_conteudo:
            writer.writeheader()
        writer.writerow(resultado)


def coletar_relato_interativo():
    """Abre três campos de resposta para criar um relato adicional."""
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError as erro:
        raise RuntimeError("A interface interativa requer o módulo tkinter.") from erro

    respostas = {}
    janela = tk.Tk()
    janela.title("CardioIA — novo relato")
    janela.geometry("650x360")
    janela.resizable(False, False)
    # Em alguns ambientes macOS, janelas Tk podem abrir atrás do VS Code.
    # Elevar a janela por um instante deixa a coleta visível para quem executa.
    janela.lift()
    janela.attributes("-topmost", True)
    janela.after(250, lambda: janela.attributes("-topmost", False))
    janela.focus_force()
    tk.Label(janela, text="Novo relato de sintomas", font=("Arial", 16, "bold")).pack(pady=(20, 8))
    tk.Label(janela, text="Use respostas curtas. Ex.: dor no peito e falta de ar.").pack()
    campos = (
        ("O que você está sentindo?", "Ex.: dor no peito e falta de ar"),
        ("Como isso afeta sua rotina?", "Ex.: precisei interromper minha caminhada"),
        ("Há quanto tempo sente isso ou quando começou?", "Ex.: há dois dias"),
    )
    entradas = []
    for rotulo, exemplo in campos:
        tk.Label(janela, text=rotulo, anchor="w").pack(fill="x", padx=35, pady=(12, 2))
        entrada = tk.Entry(janela, width=72)
        entrada.insert(0, exemplo)
        entrada.pack(padx=35)
        entradas.append((entrada, exemplo))

    def enviar():
        valores = [entrada.get().strip() for entrada, _ in entradas]
        if not all(valores) or any(valor == exemplo for valor, (_, exemplo) in zip(valores, entradas)):
            messagebox.showwarning("Respostas incompletas", "Preencha as três respostas antes de continuar.")
            return
        respostas["sintomas"], respostas["impacto"], respostas["tempo"] = valores
        janela.destroy()

    tk.Button(janela, text="Formular e analisar relato", command=enviar).pack(pady=22)
    janela.mainloop()
    if not respostas:
        raise RuntimeError("Coleta cancelada sem criar um relato.")
    return montar_frase(respostas["tempo"], respostas["sintomas"], respostas["impacto"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frases", type=Path, default=RAIZ / "data/relatos_sintomas.txt")
    parser.add_argument("--mapa", type=Path, default=RAIZ / "data/mapa_conhecimento.csv")
    parser.add_argument("--saida", type=Path,
                        help="CSV de resultados; o padrão depende do modo de execução.")
    parser.add_argument("--historico", type=Path, default=RAIZ / "outputs/relatos_interativos.csv",
                        help="CSV local que guarda os relatos enviados no modo interativo.")
    parser.add_argument("--interativo", action="store_true",
                        help="Abre três campos para criar e analisar um relato adicional.")
    args = parser.parse_args()
    if args.saida is None:
        nome_saida = "diagnosticos_interativos.csv" if args.interativo else "diagnosticos_sugeridos.csv"
        args.saida = RAIZ / "outputs" / nome_saida
    protegidos = {args.frases.resolve(), args.mapa.resolve()}
    if args.saida.resolve() in protegidos:
        parser.error("A saída não pode sobrescrever os relatos ou o mapa.")
    if args.interativo and (args.historico.resolve() in protegidos
                           or args.historico.resolve() == args.saida.resolve()):
        parser.error("O histórico deve ser separado dos dados de entrada e da saída.")
    frases = [f.strip() for f in args.frases.read_text(encoding="utf-8").splitlines() if f.strip()]
    if not frases:
        parser.error("O arquivo de relatos está vazio.")
    mapa = ler_mapa(args.mapa)
    if args.interativo:
        frase_adicional = coletar_relato_interativo()
        frases.append(frase_adicional)
        salvar_historico(analisar(frase_adicional, mapa), args.historico)
        print(f"Relato formulado: {frase_adicional}")
    resultados = [analisar(frase, mapa) for frase in frases]
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with args.saida.open("w", encoding="utf-8", newline="") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=resultados[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(resultados)
    for i, resultado in enumerate(resultados, 1):
        print(f"{i:02d}. {resultado['associacoes']}\n    Sintomas: {resultado['sintomas']}")
    print(AVISO)


if __name__ == "__main__":
    main()
