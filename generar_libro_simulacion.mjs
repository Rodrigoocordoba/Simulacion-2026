import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const [, , inputJson, outputXlsx, previewDir] = process.argv;
if (!inputJson || !outputXlsx) {
  throw new Error("Uso: node generar_libro_simulacion.mjs datos.json salida.xlsx [previews]");
}

const payload = JSON.parse(await fs.readFile(inputJson, "utf8"));
const workbook = Workbook.create();

const COLORS = {
  navy: "#1F4E79",
  blue: "#D9EAF7",
  green: "#E2F0D9",
  greenDark: "#006100",
  yellow: "#FFF2CC",
  red: "#FCE4D6",
  gray: "#F2F2F2",
  border: "#B7C9D6",
  white: "#FFFFFF",
  text: "#1F1F1F",
};

function matrix(rows, keys) {
  return rows.map((row) => keys.map((key) => row[key] ?? null));
}

function titleBand(sheet, range, text) {
  sheet.getRange(range).merge();
  const cell = sheet.getRange(range.split(":")[0]);
  cell.values = [[text]];
  cell.format = {
    fill: COLORS.navy,
    font: { bold: true, color: COLORS.white, size: 16 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
  sheet.getRange(range).format.rowHeight = 30;
}

function styleHeader(range) {
  range.format = {
    fill: COLORS.navy,
    font: { bold: true, color: COLORS.white },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: COLORS.border },
  };
  range.format.rowHeight = 34;
}

function styleBody(range) {
  range.format = {
    font: { color: COLORS.text, size: 10 },
    verticalAlignment: "center",
    borders: {
      insideHorizontal: { style: "thin", color: COLORS.border },
      bottom: { style: "thin", color: COLORS.border },
    },
  };
}

function addTable(sheet, name, range) {
  const table = sheet.tables.add(range, true, name);
  table.style = "TableStyleMedium2";
  table.showBandedRows = true;
  table.showFilterButton = true;
  return table;
}

// ---------------------------------------------------------------------------
// Resumen de intervalos
// ---------------------------------------------------------------------------
const summary = workbook.worksheets.add("Resumen IC");
summary.showGridLines = false;
titleBand(summary, "A1:M1", "Entrega Pet - Comparación estadística de políticas PEP/TP");
summary.getRange("A2:M2").merge();
summary.getRange("A2").values = [[
  `${payload.metadata.pares} pares seleccionados | ${payload.metadata.replicas} réplicas de ${payload.metadata.dias} días | IC 95%`,
]];
summary.getRange("A2:M2").format = {
  fill: COLORS.blue,
  font: { italic: true, color: "#595959" },
  horizontalAlignment: "center",
};
summary.getRange("A3:M3").merge();
summary.getRange("A3").values = [[
  `Regla: los pares superpuestos continúan; solo se descartan intervalos completamente superiores al mejor. Generado: ${payload.metadata.generado}`,
]];
summary.getRange("A3:M3").format = {
  font: { color: "#595959", size: 9 },
  horizontalAlignment: "center",
};

const summaryHeaders = [
  "Ranking", "PEP", "TP", "N", "CTF medio", "Desv. estándar",
  "Límite inferior", "Límite superior", "Amplitud IC", "Nivel servicio",
  "Ventas perdidas", "Pedidos", "Estado final",
];
summary.getRange("A5:M5").values = [summaryHeaders];
styleHeader(summary.getRange("A5:M5"));

const summaryRows = payload.resumen.map((row, index) => [
  index + 1,
  row.PEP,
  row.TP,
  row.Replicas,
  row.CTF_media,
  row.CTF_desviacion,
  row.CTF_limite_inferior,
  row.CTF_limite_superior,
  null,
  row.Nivel_Servicio_Porcentaje_media / 100,
  row.Ventas_Perdidas_media,
  row.Pedidos_Realizados_media,
  row.Estado_Final,
]);
const summaryLast = 5 + summaryRows.length;
summary.getRange(`A6:M${summaryLast}`).values = summaryRows;
styleBody(summary.getRange(`A6:M${summaryLast}`));
summary.getRange("I6").formulas = [["=H6-G6"]];
summary.getRange(`I6:I${summaryLast}`).fillDown();
summary.getRange(`E6:I${summaryLast}`).format.numberFormat = '"$"#,##0.00';
summary.getRange(`J6:J${summaryLast}`).format.numberFormat = "0.00%";
summary.getRange(`K6:L${summaryLast}`).format.numberFormat = "#,##0.00";
summary.getRange(`A6:D${summaryLast}`).format.horizontalAlignment = "center";
summary.getRange(`M6:M${summaryLast}`).format.horizontalAlignment = "center";
summary.getRange(`M6:M${summaryLast}`).conditionalFormats.add("containsText", {
  text: "CONTINÚA",
  format: { fill: COLORS.yellow, font: { bold: true, color: "#9C6500" } },
});
summary.getRange(`M6:M${summaryLast}`).conditionalFormats.add("containsText", {
  text: "DESCARTADA",
  format: { fill: COLORS.gray, font: { color: "#7F7F7F" } },
});
addTable(summary, "ResumenPoliticas", `A5:M${summaryLast}`);
summary.freezePanes.freezeRows(5);
const summaryWidths = [10, 8, 8, 7, 17, 17, 17, 17, 16, 17, 16, 12, 18];
summaryWidths.forEach((width, index) => {
  summary.getRangeByIndexes(0, index, summaryLast, 1).format.columnWidth = width;
});

// ---------------------------------------------------------------------------
// Comparación final de intervalos
// ---------------------------------------------------------------------------
const evolution = workbook.worksheets.add("Comparación IC");
evolution.showGridLines = false;
titleBand(evolution, "A1:J1", `Comparación de intervalos de confianza con N = ${payload.metadata.replicas}`);
const evolutionHeaders = [
  "N", "PEP", "TP", "CTF medio", "Límite inferior", "Límite superior",
  "Mejor PEP", "Mejor TP", "Se superpone", "Estado",
];
evolution.getRange("A3:J3").values = [evolutionHeaders];
styleHeader(evolution.getRange("A3:J3"));
const evolutionKeys = [
  "N", "PEP", "TP", "CTF_Media", "IC95_Limite_Inferior",
  "IC95_Limite_Superior", "Mejor_PEP", "Mejor_TP",
  "Se_Superpone_Con_Mejor", "Estado",
];
const evolutionRows = matrix(payload.evolucion, evolutionKeys);
const evolutionLast = 3 + evolutionRows.length;
evolution.getRange(`A4:J${evolutionLast}`).values = evolutionRows;
styleBody(evolution.getRange(`A4:J${evolutionLast}`));
evolution.getRange(`D4:F${evolutionLast}`).format.numberFormat = '"$"#,##0.00';
evolution.getRange(`A4:C${evolutionLast}`).format.horizontalAlignment = "center";
evolution.getRange(`G4:J${evolutionLast}`).format.horizontalAlignment = "center";
evolution.getRange(`J4:J${evolutionLast}`).conditionalFormats.add("containsText", {
  text: "CONTINÚA",
  format: { fill: COLORS.yellow, font: { bold: true, color: "#9C6500" } },
});
evolution.getRange(`J4:J${evolutionLast}`).conditionalFormats.add("containsText", {
  text: "DESCARTADA",
  format: { fill: COLORS.gray, font: { color: "#7F7F7F" } },
});
addTable(evolution, "EvolucionIntervalos", `A3:J${evolutionLast}`);
evolution.freezePanes.freezeRows(3);
[8, 8, 8, 18, 18, 18, 12, 12, 16, 16].forEach((width, index) => {
  evolution.getRangeByIndexes(0, index, evolutionLast, 1).format.columnWidth = width;
});

// ---------------------------------------------------------------------------
// Resultados de todas las réplicas del experimento
// ---------------------------------------------------------------------------
const replicas = workbook.worksheets.add("Réplicas");
replicas.showGridLines = false;
titleBand(replicas, "A1:K1", "Resultados individuales de las réplicas");
const replicaHeaders = [
  "Réplica", "PEP", "TP", "CTF", "Costo almacenamiento",
  "Costo ventas perdidas", "Costo emisión", "Demanda total",
  "Ventas perdidas", "Nivel servicio", "Pedidos",
];
replicas.getRange("A3:K3").values = [replicaHeaders];
styleHeader(replicas.getRange("A3:K3"));
const replicaKeys = [
  "Replica", "PEP", "TP", "CTF", "CTALM", "CVTAP", "CTEP",
  "Demanda_Total", "Ventas_Perdidas", "Nivel_Servicio_Porcentaje",
  "Pedidos_Realizados",
];
const replicaRows = matrix(payload.replicas, replicaKeys).map((row) => {
  row[9] = row[9] / 100;
  return row;
});
const replicasLast = 3 + replicaRows.length;
replicas.getRange(`A4:K${replicasLast}`).values = replicaRows;
styleBody(replicas.getRange(`A4:K${replicasLast}`));
replicas.getRange(`D4:G${replicasLast}`).format.numberFormat = '"$"#,##0.00';
replicas.getRange(`J4:J${replicasLast}`).format.numberFormat = "0.00%";
replicas.getRange(`A4:C${replicasLast}`).format.horizontalAlignment = "center";
replicas.getRange(`H4:K${replicasLast}`).format.horizontalAlignment = "center";
addTable(replicas, "ResultadosReplicas", `A3:K${replicasLast}`);
replicas.freezePanes.freezeRows(3);
[10, 8, 8, 16, 20, 22, 16, 15, 16, 16, 12].forEach((width, index) => {
  replicas.getRangeByIndexes(0, index, replicasLast, 1).format.columnWidth = width;
});

// ---------------------------------------------------------------------------
// Una hoja diaria por cada par
// ---------------------------------------------------------------------------
const dailyHeaders = [
  "Día", "FLL", "Ri lead time", "Lead time", "Tamaño pedido",
  "Ri demanda", "Stock inicial", "Llega pedido", "Demanda", "Ventas",
  "Stock final", "PEP", "Pedido pendiente", "Ventas perdidas",
  "Emite pedido", "Costo emisión", "Costo almacenamiento",
  "Costo ventas perdidas", "Costo total", "CTF acumulado",
];
const dailyKeys = [
  "Dia", "FLL", "Ri_Lead_Time", "Lead_Time", "Tamaño_Pedido",
  "Ri_Demanda", "Stock_Inicial", "Llega_Pedido", "Demanda", "Ventas",
  "Stock_Final", "PEP", "Pedido_Pendiente", "Ventas_Perdidas",
  "Emite_Pedido", "Costo_Emision_Dia", "Costo_Almacenamiento_Dia",
  "Costo_Ventas_Perdidas_Dia", "Costo_Total_Dia", "CTF_Acumulado",
];

for (const pair of payload.pares) {
  const sheetName = `PEP${String(pair.pep).padStart(2, "0")}_TP${String(pair.tp).padStart(2, "0")}`;
  const sheet = workbook.worksheets.add(sheetName);
  sheet.showGridLines = false;
  titleBand(sheet, "A1:T1", `Simulación diaria - PEP ${pair.pep} / TP ${pair.tp}`);

  sheet.getRange("A2:J2").values = [[
    "PEP", pair.pep, "TP", pair.tp, "Demanda total", pair.resumen.Demanda_Total,
    "Ventas perdidas", pair.resumen.Ventas_Perdidas, "Nivel servicio", null,
  ]];
  sheet.getRange("J2").formulas = [["=(F2-H2)/F2"]];
  sheet.getRange("A3:J3").values = [[
    "CTF", null, "Costo almacenamiento", null, "Costo ventas perdidas", null,
    "Costo emisión", null, "Pedidos", pair.resumen.Pedidos_Realizados,
  ]];

  const dataStart = 7;
  const dataEnd = dataStart + pair.dias.length - 1;
  sheet.getRange("B3").formulas = [[`=SUM(S${dataStart}:S${dataEnd})`]];
  sheet.getRange("D3").formulas = [[`=SUM(Q${dataStart}:Q${dataEnd})`]];
  sheet.getRange("F3").formulas = [[`=SUM(R${dataStart}:R${dataEnd})`]];
  sheet.getRange("H3").formulas = [[`=SUM(P${dataStart}:P${dataEnd})`]];

  sheet.getRange("A2:J3").format = {
    fill: COLORS.blue,
    font: { color: COLORS.text },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    borders: { preset: "all", style: "thin", color: COLORS.border },
  };
  sheet.getRange("A2:A3").format.font = { bold: true, color: COLORS.navy };
  sheet.getRange("C2:C3").format.font = { bold: true, color: COLORS.navy };
  sheet.getRange("E2:E3").format.font = { bold: true, color: COLORS.navy };
  sheet.getRange("G2:G3").format.font = { bold: true, color: COLORS.navy };
  sheet.getRange("I2:I3").format.font = { bold: true, color: COLORS.navy };
  sheet.getRange("B3:H3").format.numberFormat = '"$"#,##0.00';
  sheet.getRange("J2").format.numberFormat = "0.00%";

  sheet.getRange("A6:T6").values = [dailyHeaders];
  styleHeader(sheet.getRange("A6:T6"));
  const dailyRows = matrix(pair.dias, dailyKeys);
  sheet.getRange(`A${dataStart}:T${dataEnd}`).values = dailyRows;
  styleBody(sheet.getRange(`A${dataStart}:T${dataEnd}`));
  sheet.getRange(`C${dataStart}:C${dataEnd}`).format.numberFormat = "0.0000";
  sheet.getRange(`F${dataStart}:F${dataEnd}`).format.numberFormat = "0.0000";
  sheet.getRange(`P${dataStart}:T${dataEnd}`).format.numberFormat = '"$"#,##0.00';
  sheet.getRange(`A${dataStart}:B${dataEnd}`).format.horizontalAlignment = "center";
  sheet.getRange(`D${dataStart}:O${dataEnd}`).format.horizontalAlignment = "center";
  sheet.getRange(`H${dataStart}:H${dataEnd}`).conditionalFormats.add("containsText", {
    text: "SI",
    format: { fill: COLORS.green, font: { bold: true, color: COLORS.greenDark } },
  });
  sheet.getRange(`O${dataStart}:O${dataEnd}`).conditionalFormats.add("containsText", {
    text: "SI",
    format: { fill: COLORS.yellow, font: { bold: true, color: "#9C6500" } },
  });
  addTable(sheet, `Detalle_${sheetName}`, `A6:T${dataEnd}`);
  sheet.freezePanes.freezeRows(6);

  const widths = [8, 9, 12, 11, 13, 12, 13, 13, 10, 10, 11, 8, 16, 14, 13, 16, 19, 19, 15, 17];
  widths.forEach((width, index) => {
    sheet.getRangeByIndexes(0, index, dataEnd, 1).format.columnWidth = width;
  });
}

if (previewDir) {
  await fs.mkdir(previewDir, { recursive: true });
  const sheetNames = ["Resumen IC", "Comparación IC", "Réplicas", ...payload.pares.map(
    (pair) => `PEP${String(pair.pep).padStart(2, "0")}_TP${String(pair.tp).padStart(2, "0")}`,
  )];
  for (const sheetName of sheetNames) {
    const preview = await workbook.render({
      sheetName,
      autoCrop: "all",
      scale: sheetName === "Réplicas" ? 0.7 : 1,
      format: "png",
    });
    const bytes = new Uint8Array(await preview.arrayBuffer());
    await fs.writeFile(path.join(previewDir, `${sheetName}.png`), bytes);
  }
}

await fs.mkdir(path.dirname(outputXlsx), { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputXlsx);
console.log(outputXlsx);
