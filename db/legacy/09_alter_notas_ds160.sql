-- Adiciona codigo_ds160 e notas_ds160 em bancos ja criados com a versao anterior do schema.
-- Rodar UMA vez. Quem criar o banco do zero com 01/02 atuais NAO precisa.
-- Para preencher: recriar os staging (03) com a coluna nova, importar os CSVs e rodar as cargas 07, 09, 10
-- (ou um UPDATE ligando por cliente, se as cargas ja foram feitas).

ALTER TABLE processos_obt ADD COLUMN codigo_ds160 TEXT
    CHECK (codigo_ds160 IS NULL OR (codigo_ds160 = btrim(codigo_ds160) AND codigo_ds160 <> ''));
ALTER TABLE processos_obt ADD COLUMN notas_ds160 TEXT
    CHECK (notas_ds160 IS NULL OR (notas_ds160 = btrim(notas_ds160) AND notas_ds160 <> ''));

ALTER TABLE processos_ren ADD COLUMN codigo_ds160 TEXT
    CHECK (codigo_ds160 IS NULL OR (codigo_ds160 = btrim(codigo_ds160) AND codigo_ds160 <> ''));
ALTER TABLE processos_ren ADD COLUMN notas_ds160 TEXT
    CHECK (notas_ds160 IS NULL OR (notas_ds160 = btrim(notas_ds160) AND notas_ds160 <> ''));
