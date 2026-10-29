// Copia as NOTAS das celulas do DS160 para uma coluna nova (as notas nao saem no CSV).
// Como usar: Extensoes > Apps Script > cole este codigo > ajuste ABAS > execute copiaNotasDS160 UMA vez por planilha.
// A coluna 'notas_ds160' e criada na ULTIMA coluna de cada aba (mesma ordem que 03_staging_criar.sql espera).

// aba -> titulo (parcial) da coluna do DS160
const ABAS = {
  'REN': 'DS160',
  'OBT': 'DS160',
};

function copiaNotasDS160() {
  const planilha = SpreadsheetApp.getActiveSpreadsheet();
  Object.entries(ABAS).forEach(([nomeAba, tituloDS]) => {
    const aba = planilha.getSheetByName(nomeAba);
    const ultimaLinha = aba.getLastRow();
    const cabecalho = aba.getRange(1, 1, 1, aba.getLastColumn()).getValues()[0];
    const colDS = cabecalho.findIndex(t => String(t).toUpperCase().includes(tituloDS)) + 1;
    if (colDS === 0) throw new Error('Coluna ' + tituloDS + ' nao encontrada em ' + nomeAba);

    const notas = aba.getRange(2, colDS, ultimaLinha - 1, 1).getNotes();  // [[nota], [nota], ...]
    const colNova = aba.getLastColumn() + 1;
    aba.getRange(1, colNova).setValue('notas_ds160');
    aba.getRange(2, colNova, notas.length, 1).setValues(notas);  // quebras de linha viram aspas no CSV
  });
}
