"""Valida a estrutura local da Fase 3 sem depender do Wokwi ou do broker."""

import json
import re
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[2]
FASE3 = RAIZ / "fase3"


def exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)


def ids_referenciados(fluxo):
    for no in fluxo:
        for grupo in no.get("wires", []):
            yield from grupo


def main():
    obrigatorios = [
        "README.md",
        "esp32-cardioia/diagram.json",
        "esp32-cardioia/platformio.ini",
        "esp32-cardioia/src/main.cpp",
        "node-red/flows_cardioia.json",
        "docs/relatorio_edge.md",
        "docs/relatorio_mqtt_dashboard.md",
        "docs/seguranca_privacidade.md",
        "docs/checklist_enunciado.md",
        "output/pdf/relatorio_edge_computing.pdf",
        "output/pdf/relatorio_mqtt_dashboard.pdf",
    ]
    for relativo in obrigatorios:
        exigir((FASE3 / relativo).is_file(), f"Arquivo ausente: fase3/{relativo}")
    for nome_pdf in ("relatorio_edge_computing.pdf", "relatorio_mqtt_dashboard.pdf"):
        pdf = FASE3 / "output/pdf" / nome_pdf
        exigir(pdf.read_bytes().startswith(b"%PDF") and pdf.stat().st_size > 5_000,
               f"PDF ausente ou inválido: {nome_pdf}")

    diagrama = json.loads((FASE3 / "esp32-cardioia/diagram.json").read_text(encoding="utf-8"))
    tipos = [parte["type"] for parte in diagrama["parts"]]
    exigir("board-esp32-devkit-c-v4" in tipos, "ESP32 ausente do diagrama.")
    exigir("wokwi-dht22" in tipos, "DHT22 ausente do diagrama.")
    exigir(tipos.count("wokwi-pushbutton") >= 2, "Botões de pulso/rede ausentes.")
    exigir(len(diagrama["connections"]) >= 9, "Circuito com conexões incompletas.")

    codigo = (FASE3 / "esp32-cardioia/src/main.cpp").read_text(encoding="utf-8")
    for trecho in (
        "MAX_AMOSTRAS_OFFLINE = 1000",
        "DHT22",
        "mqtt.publish",
        "conectividadeAtiva",
        "amostrasDescartadas",
        "mqtt.setBufferSize",
        "INTERVALO_RECONEXAO_WIFI_MS",
    ):
        exigir(trecho in codigo, f"Implementação esperada não encontrada: {trecho}")

    fluxo = json.loads((FASE3 / "node-red/flows_cardioia.json").read_text(encoding="utf-8"))
    ids = {no["id"] for no in fluxo}
    exigir(len(ids) == len(fluxo), "IDs duplicados no fluxo Node-RED.")
    exigir(set(ids_referenciados(fluxo)) <= ids, "Fluxo aponta para nó inexistente.")
    tipos_fluxo = [no["type"] for no in fluxo]
    exigir("mqtt in" in tipos_fluxo, "Entrada MQTT ausente.")
    exigir("ui_chart" in tipos_fluxo, "Gráfico de BPM ausente.")
    exigir(tipos_fluxo.count("ui_gauge") >= 2, "Medidores do dashboard ausentes.")
    exigir(tipos_fluxo.count("ui_text") >= 2, "Indicadores visuais ausentes.")
    exigir(tipos_fluxo.count("inject") >= 2, "Casos de teste do dashboard ausentes.")

    funcao = next(no["func"] for no in fluxo if no["id"] == "tratar_telemetria")
    exigir("bpm >= 120" in funcao and "temperatura >= 38" in funcao,
           "Regras de alerta do dashboard divergentes.")
    topico_fluxo = next(no["topic"] for no in fluxo if no["type"] == "mqtt in")
    config = (FASE3 / "esp32-cardioia/include/config.h").read_text(encoding="utf-8")
    topico_codigo = re.search(r'MQTT_TOPICO_TELEMETRIA\s+"([^"]+)"', config)
    exigir(topico_codigo and topico_codigo.group(1) == topico_fluxo,
           "Tópicos MQTT diferentes entre ESP32 e Node-RED.")

    edge = (FASE3 / "docs/relatorio_edge.md").read_text(encoding="utf-8")
    mqtt = (FASE3 / "docs/relatorio_mqtt_dashboard.md").read_text(encoding="utf-8")
    exigir(len(edge.split()) >= 500, "Relatório Edge curto para uma página.")
    exigir(len(mqtt.split()) >= 750, "Relatório MQTT curto para duas páginas.")

    readme = (FASE3 / "README.md").read_text(encoding="utf-8")
    link_pendente = "A publicar após" in readme
    print("Fase 3: circuito, resiliência, MQTT, dashboard e relatórios consistentes.")
    if link_pendente:
        print("PENDÊNCIA EXTERNA: publicar o projeto no Wokwi e substituir o marcador do link.")


if __name__ == "__main__":
    main()
