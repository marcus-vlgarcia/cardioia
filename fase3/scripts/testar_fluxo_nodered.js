/*
 * Exercita a função "Separar sinais e alertas" exportada pelo Node-RED.
 * Não exige broker, Wokwi ou bibliotecas externas: serve para verificar a
 * regra de interface antes da demonstração integrada.
 */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const fase3 = path.resolve(__dirname, "..");
const fluxo = JSON.parse(
  fs.readFileSync(path.join(fase3, "node-red", "flows_cardioia.json"), "utf8")
);
const noFuncao = fluxo.find((no) => no.id === "tratar_telemetria");

assert.ok(noFuncao, "Nó de tratamento da telemetria não encontrado.");

const memoriaFluxo = new Map();
const avisos = [];
const flow = {
  get: (chave) => memoriaFluxo.get(chave),
  set: (chave, valor) => memoriaFluxo.set(chave, valor),
};
const node = { warn: (aviso) => avisos.push(aviso) };
const tratarTelemetria = new Function("msg", "flow", "node", noFuncao.func);

function executar(payload) {
  return tratarTelemetria({ payload }, flow, node);
}

const normal = executar({
  projeto: "CardioIA",
  origem: "edge_esp32",
  paciente_id: "TESTE_AUTOMATICO",
  sequencia: 1,
  temperatura_c: 36.7,
  umidade_pct: 55,
  bpm: 72,
  alerta: false,
  fila_offline: 0,
  amostras_descartadas: 0,
});
assert.equal(normal.length, 6, "A função deve produzir seis saídas.");
assert.equal(normal[0].payload, 72, "BPM normal não foi encaminhado.");
assert.match(normal[3].payload, /Sem alerta/, "Leitura normal gerou alerta incorreto.");

const alerta = executar({
  projeto: "CardioIA",
  origem: "edge_esp32",
  paciente_id: "TESTE_ALERTA",
  sequencia: 1,
  temperatura_c: 38.2,
  umidade_pct: 58,
  bpm: 126,
  alerta: true,
  fila_offline: 3,
  amostras_descartadas: 0,
});
assert.match(alerta[3].payload, /ALERTA SIMULADO/, "Regra de alerta não foi acionada.");
assert.match(alerta[4].payload, /Fila Edge: 3/, "Fila Edge não foi exibida.");

const comLacuna = executar({
  projeto: "CardioIA",
  origem: "edge_esp32",
  paciente_id: "TESTE_AUTOMATICO",
  sequencia: 4,
  temperatura_c: 36.8,
  umidade_pct: 54,
  bpm: 75,
  alerta: false,
  fila_offline: 0,
  amostras_descartadas: 0,
});
assert.match(comLacuna[4].payload, /lacuna detectada: 2/, "Lacuna de sequência não foi sinalizada.");

const semToques = executar({
  projeto: "CardioIA",
  origem: "edge_esp32",
  paciente_id: "TESTE_AUTOMATICO",
  sequencia: 5,
  temperatura_c: 36.7,
  umidade_pct: 55,
  bpm: 0,
  alerta: false,
});
assert.match(semToques[3].payload, /Sem pulsos simulados/, "Zero BPM foi tratado como leitura normal.");

const temperaturaAltaSemToques = executar({
  projeto: "CardioIA",
  origem: "edge_esp32",
  paciente_id: "TESTE_AUTOMATICO",
  sequencia: 6,
  temperatura_c: 38.2,
  umidade_pct: 55,
  bpm: 0,
  alerta: true,
});
assert.match(temperaturaAltaSemToques[3].payload, /ALERTA SIMULADO: sem pulsos no botão/,
  "Alerta de temperatura com zero BPM deve explicar a ausência de toques.");

for (const payload of [
  { projeto: "Outro", origem: "edge_esp32", paciente_id: "TESTE", sequencia: 1,
    temperatura_c: 36.7, umidade_pct: 55, bpm: 72 },
  { projeto: "CardioIA", origem: "edge_esp32", paciente_id: "TESTE", sequencia: 1,
    temperatura_c: 36.7, umidade_pct: 55, bpm: "72" },
  { projeto: "CardioIA", origem: "edge_esp32", paciente_id: "TESTE", sequencia: 1,
    temperatura_c: 36.7, umidade_pct: 150, bpm: 72 },
  { projeto: "CardioIA", origem: "edge_esp32", paciente_id: "TESTE", sequencia: null,
    temperatura_c: 36.7, umidade_pct: 55, bpm: 72 },
  { projeto: "CardioIA", origem: "edge_esp32", paciente_id: "TESTE", sequencia: 1,
    temperatura_c: 36.7, umidade_pct: 55, bpm: 72, fila_offline: -1 },
]) {
  assert.equal(executar(payload), null, "Payload inválido deveria ser descartado.");
}
assert.equal(avisos.length, 5, "Cada payload inválido deveria gerar um aviso.");

console.log("Teste do fluxo Node-RED: 10 cenários aprovados.");
