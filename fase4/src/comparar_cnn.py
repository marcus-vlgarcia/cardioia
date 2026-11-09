"""Compara uma CNN com mais negativos, auditando pacientes pelo índice oficial."""

import csv
import json

import numpy as np
import torch
from sklearn.metrics import average_precision_score

from dados import DADOS, RESULTADOS, SEMENTE, baixar, baixar_verificado, carregar_particoes, hash_imagem
from modelos import carregar_prototipo, cnn_simples
from treinar import ajustar, avaliar_escores, criar_loaders, metricas_teste

URL_INDICE = (
    "https://drive.usercontent.google.com/download?"
    "id=1eY4En_i6XYWzwzXxI2JKDsFspW-ho__I&export=download&confirm=t"
)
SHA_INDICE = "3cfe66207037f1f99b1bf457f1f009b0cfc2346ea7a710505a23e02c8ff492e9"
EPOCAS_CANDIDATA = 18
NEGATIVOS_POR_POSITIVO = 8


def ler_pacientes(datasets):
    caminho = baixar_verificado(URL_INDICE, DADOS / "chestmnist_split_info.csv", "sha256", SHA_INDICE)
    pacientes = {split: {} for split in datasets}
    with caminho.open(newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            particao = pacientes[linha["split"]]
            indice = int(linha["index"])
            paciente, separador, exame = linha["image_id"].partition("_")
            if indice in particao or not (paciente.isdigit() and separador and exame.isdigit()):
                raise ValueError("Identificador ou índice de origem inválido.")
            particao[indice] = paciente
    for split, ds in datasets.items():
        if pacientes[split].keys() != set(range(ds.total_oficial)):
            raise ValueError(f"Índice oficial incompleto em {split}.")
    return pacientes


def selecionar(ds, posicoes):
    ds.imagens = ds.imagens[posicoes]
    ds.rotulos = ds.rotulos[posicoes]
    ds.indices = ds.indices[posicoes]


def preparar_comparacao(arquivo):
    datasets = carregar_particoes(arquivo)
    pacientes = ler_pacientes(datasets)
    treino, validacao, teste = (datasets[nome] for nome in ("train", "val", "test"))
    grupos = {s: {pacientes[s][i] for i in ds.indices} for s, ds in datasets.items()}
    sobreposicao = grupos["test"] & (grupos["train"] | grupos["val"])
    antes = len(teste)
    selecionar(teste, [i for i, indice in enumerate(teste.indices)
                       if pacientes["test"][indice] not in sobreposicao])
    grupos["test"] -= sobreposicao

    # Mantém os exemplos originais e acrescenta negativos sem repetir paciente
    # de validação/teste ou imagem das partições usadas para avaliar.
    vistos = treino.hashes_teste_anterior | teste.hashes_teste_anterior
    for ds in (treino, validacao, teste):
        vistos.update(hash_imagem(imagem) for imagem in ds.imagens)
    bloqueados = grupos["val"] | grupos["test"]
    with np.load(arquivo, allow_pickle=False) as fonte:
        imagens = fonte["train_images"]
        rotulos = fonte["train_labels"][:, 1]
    rng = np.random.default_rng(SEMENTE)
    faltam = NEGATIVOS_POR_POSITIVO * int(treino.rotulos.sum()) - int((treino.rotulos == 0).sum())
    novos = []
    for i in rng.permutation(np.flatnonzero(rotulos == 0)):
        if pacientes["train"][i] in bloqueados:
            continue
        chave = hash_imagem(imagens[i])
        if chave in vistos:
            continue
        novos.append(i)
        vistos.add(chave)
        if len(novos) == faltam:
            break
    if len(novos) != faltam:
        raise ValueError("Negativos elegíveis insuficientes.")
    treino.imagens = np.concatenate([treino.imagens, imagens[novos]])
    treino.rotulos = np.concatenate([treino.rotulos, rotulos[novos]])
    treino.indices = np.concatenate([treino.indices, novos])
    grupos["train"].update(pacientes["train"][i] for i in novos)
    if grupos["train"] & grupos["val"] or grupos["train"] & grupos["test"] or grupos["val"] & grupos["test"]:
        raise ValueError("Há pacientes compartilhados na comparação.")
    auditoria = {
        "pacientes_compartilhados_antes": len(sobreposicao),
        "exames_excluidos_do_teste": antes - len(teste),
        "negativos_adicionados": len(novos),
        "particoes": {s: {"exames": len(ds), "positivos": int(ds.rotulos.sum()),
                          "pacientes": len(grupos[s])} for s, ds in datasets.items()},
    }
    return datasets, auditoria


def executar():
    torch.manual_seed(SEMENTE)
    torch.set_num_threads(4)
    device = torch.device("cuda" if torch.cuda.is_available() else
                          "mps" if torch.backends.mps.is_available() else "cpu")
    datasets, auditoria = preparar_comparacao(baixar())
    print(auditoria, flush=True)
    loaders = criar_loaders(datasets)
    referencia, limiar_ref = carregar_prototipo(RESULTADOS, "cnn", device)
    candidata = cnn_simples().to(device)
    limiar, historico = ajustar(candidata, loaders, device, "cnn", epocas=EPOCAS_CANDIDATA)

    validacao = {}
    for nome, modelo in (("referencia", referencia), ("candidata", candidata)):
        escores, rotulos = avaliar_escores(modelo, loaders["val"], device)
        validacao[nome] = float(average_precision_score(rotulos, escores))
    escolhido = max(validacao, key=validacao.get)
    print(f"Escolha pela AP de validação: {escolhido} {validacao}", flush=True)

    comparacao = {}
    predicoes = {}
    for nome, modelo, corte in (("referencia", referencia, limiar_ref),
                                 ("candidata", candidata, limiar)):
        escores, rotulos = avaliar_escores(modelo, loaders["test"], device)
        comparacao[nome] = metricas_teste(rotulos, escores, corte, historico if nome == "candidata" else [])
        predicoes[nome] = escores
    registro = {"auditoria": auditoria, "ap_validacao": validacao, "escolha_validacao": escolhido,
                "teste": comparacao, "epocas": EPOCAS_CANDIDATA, "semente": SEMENTE,
                "torch": str(torch.__version__), "dispositivo": str(device)}
    torch.save({"estado": candidata.cpu().state_dict(), "limiar": limiar}, RESULTADOS / "cnn_ampliada.pt")
    (RESULTADOS / "comparacao_cnn.json").write_text(json.dumps(registro, indent=2) + "\n")
    with (RESULTADOS / "predicoes_comparacao_cnn.csv").open("w", newline="") as arquivo:
        writer = csv.writer(arquivo, lineterminator="\n")
        writer.writerow(["indice_oficial", "rotulo", *predicoes])
        writer.writerows(zip(datasets["test"].indices, rotulos, *predicoes.values()))
    return registro


if __name__ == "__main__":
    executar()
