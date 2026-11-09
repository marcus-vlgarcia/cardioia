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

const leituraRevisada = {
  projeto: "CardioIA", origem: "edge_esp32", paciente_id: "TESTE_REVISAO",
  sequencia: 1, temperatura_c: 36.7, umidade_pct: 55, bpm: 72,
  idade_ms: 100, coletada_em_ms: Date.now() - 100, recuperada: false,
};
const atual = executar(leituraRevisada);
assert.equal(atual[0].timestamp, leituraRevisada.coletada_em_ms);
assert.equal(atual[0].topic, "Atual");
assert.equal(atual[1].payload, 36.7);

const coletaAnterior = Date.now() - 60000;
const recuperada = executar({ ...leituraRevisada, sequencia: 2,
  coletada_em_ms: coletaAnterior, idade_ms: 60000, recuperada: true,
  bpm: 126, temperatura_c: 39.8 });
assert.equal(recuperada[0].timestamp, coletaAnterior);
assert.equal(recuperada[0].topic, "Recuperada");
assert.deepEqual(recuperada.slice(1, 4), [null, null, null]);
assert.match(recuperada[4].payload, /amostra recuperada/);

const antesDaRecepcao = Date.now();
const semRelogio = executar({ ...leituraRevisada, sequencia: 3,
  coletada_em_ms: null, idade_ms: 30000 });
assert.equal(semRelogio[0].topic, "Recuperada (horário estimado)");
assert.ok(semRelogio[0].timestamp >= antesDaRecepcao - 30000);
assert.ok(semRelogio[0].timestamp <= Date.now() - 30000);
assert.deepEqual(semRelogio.slice(1, 4), [null, null, null]);

const falhaDht = executar({ ...leituraRevisada, sequencia: 4,
  temperatura_c: null, umidade_pct: null, bpm: 126 });
assert.equal(falhaDht[0].payload, 126);
assert.deepEqual(falhaDht.slice(1, 3), [null, null]);
assert.match(falhaDht[3].payload, /ALERTA SIMULADO: 126 BPM.*temperatura indisponível.*umidade indisponível/);

const falhaParcial = executar({ ...leituraRevisada, sequencia: 5, umidade_pct: null });
assert.equal(falhaParcial[1].payload, 36.7);
assert.equal(falhaParcial[2], null);
assert.match(falhaParcial[3].payload, /umidade indisponível/);

assert.equal(executar({ ...leituraRevisada, idade_ms: -1 }), null);

console.log("Teste do fluxo Node-RED: 16 cenários aprovados.");
