-- Tabelas de staging: recebem os CSVs exatamente como estao (tudo TEXT, sem regras).
-- Uma coluna por coluna do CSV, na ordem do arquivo.
--
-- Depois de rodar este arquivo, importe cada CSV no pgAdmin
-- (botao direito na tabela > Import/Export Data): formato CSV, Header ligado,
-- delimitador ',', quote '"', encoding UTF8. Nao apague nenhuma linha depois.
--
--   Registro Banco de Dados - REN.csv            -> stg_ren
--   Registro Banco de Dados - OBT.csv            -> stg_obt
--   Registro Banco de Dados - PASS.csv           -> stg_pass
--   Cópia de 2021-2023 - OBT.csv (historico)     -> stg_obt_hist
--   Cópia de 2021-2023 - REN.csv (historico)     -> stg_ren_hist
--
-- Conferir as contagens ANTES de seguir (devem bater com o numero de registros de cada CSV):
--   SELECT COUNT(*) FROM stg_ren;  -- etc.
-- Depois rode 04_staging_ajustar.sql.

-- REN (13 colunas). A 1a coluna e uma "Solicitante Principal" oculta, so usada em dashboard.
CREATE TABLE stg_ren (
    solicitante_oculta    TEXT,
    con                   TEXT,
    casv                  TEXT,
    email                 TEXT,
    whatsapp              TEXT,
    solicitante_principal TEXT,
    numero_solicitantes   TEXT,
    docs                  TEXT,
    rascunho              TEXT,
    ds160                 TEXT,
    despacho              TEXT,
    situacao              TEXT,
    rastreio              TEXT
);

-- OBT (16 colunas). 1a coluna oculta; marcador_1 e marcador_2 sao as colunas '-' (nao usadas).
CREATE TABLE stg_obt (
    solicitante_oculta    TEXT,
    con                   TEXT,
    casv                  TEXT,
    entrevista            TEXT,
    email                 TEXT,
    whatsapp              TEXT,
    solicitante_principal TEXT,
    numero_solicitantes   TEXT,
    data_status           TEXT,
    rascunho              TEXT,
    ds160                 TEXT,
    orientacoes           TEXT,
    marcador_1            TEXT,
    situacao              TEXT,
    resultado_rastreio    TEXT,
    marcador_2            TEXT
);

-- PASS (6 colunas)
CREATE TABLE stg_pass (
    data_pf               TEXT,
    prazo_pf              TEXT,
    whatsapp              TEXT,
    solicitante_principal TEXT,
    numero_solicitantes   TEXT,
    situacao              TEXT
);

-- OBT historico 2021-2023 (15 colunas): sem WhatsApp, com ETA no final.
CREATE TABLE stg_obt_hist (
    solicitante_oculta    TEXT,
    con                   TEXT,
    casv                  TEXT,
    entrevista            TEXT,
    email                 TEXT,
    solicitante_principal TEXT,
    numero_solicitantes   TEXT,
    data_status           TEXT,
    rascunho              TEXT,
    ds160                 TEXT,
    orientacoes           TEXT,
    marcador_1            TEXT,
    situacao              TEXT,
    resultado             TEXT,
    eta                   TEXT
);

-- REN historico 2021-2023 (12 colunas): sem WhatsApp, com ETA no final.
CREATE TABLE stg_ren_hist (
    solicitante_oculta    TEXT,
    con                   TEXT,
    casv                  TEXT,
    email                 TEXT,
    solicitante_principal TEXT,
    numero_solicitantes   TEXT,
    docs                  TEXT,
    rascunho              TEXT,
    ds160                 TEXT,
    despacho              TEXT,
    situacao              TEXT,
    eta                   TEXT
);
