-- Carga do historico 2021-2023 (stg_obt_hist e stg_ren_hist) em processos_obt e processos_ren.
-- Pre-requisitos: clientes carregada (06, que ja inclui os clientes do historico);
--   funcoes de limpeza (05); stg_*_hist ajustadas (04); cargas 07 e 09 ja feitas.
-- Rodar UMA unica vez (rodar de novo duplicaria os processos).
--
-- Regras:
--   * linhas sem nome (linhas de espacamento da planilha) sao ignoradas
--   * cliente = nome sem anotacao entre parenteses (mesma regra do 06)
--   * demais regras iguais as de 09_carga_processos_obt.sql e 07_carga_processos_ren.sql
--   * OBT sem consulado -> 'N/D'; REN sem consulado e pulado (veja lista no final)

-- ---------------------------------------------------------
-- 1. processos_obt
-- ---------------------------------------------------------
INSERT INTO processos_obt
    (cliente_id, consulado, n_solicitantes, monitoramento,
     data_casv, data_entrevista,
     status_rascunho, status_ds,
     orientacao, orientacao_por_id,
     situacao, resultado)
WITH limpo AS (
    SELECT nome_limpo(solicitante_principal) AS nome,
           COALESCE(NULLIF(btrim(con), ''), 'N/D')   AS consulado,
           numero_solicitantes::int                  AS n_solicitantes,
           CASE WHEN btrim(data_status) = 'Congelada' THEN 'Concluido' ELSE 'Ativo' END AS monitoramento,
           parse_data(casv)                  AS data_casv,
           parse_data(entrevista)            AS data_entrevista,
           COALESCE(initcap(lower(NULLIF(NULLIF(btrim(rascunho), ''), '#REF!'))), 'Pendente') AS rascunho,
           COALESCE(initcap(lower(NULLIF(NULLIF(btrim(ds160), ''), '#REF!'))),    'Pendente') AS ds160,
           btrim(orientacoes)                        AS orientacao_bruta,
           btrim(situacao)                           AS situacao_bruta,
           btrim(resultado)                          AS resultado_bruto
    FROM stg_obt_hist
    WHERE nome_limpo(solicitante_principal) <> ''
      AND NULLIF(btrim(numero_solicitantes), '') IS NOT NULL
)
SELECT c.id, l.consulado, l.n_solicitantes, l.monitoramento,
       l.data_casv, l.data_entrevista,
       l.rascunho, l.ds160,
       CASE WHEN l.orientacao_bruta ~* '^fornecidas' THEN 'Fornecidas' ELSE 'Pendente' END,
       (SELECT f.id FROM funcionarios f
         WHERE upper(left(f.nome, 1)) = upper(substring(l.orientacao_bruta from '\(([A-Za-z])\)'))),
       CASE WHEN l.resultado_bruto <> ''
                 AND lower(l.resultado_bruto) !~ '^(aprovado|negado)' THEN 'Concluido'  -- texto livre: nao vira Limbo
            WHEN l.situacao_bruta = 'Concluído' THEN 'Concluido'
            WHEN l.situacao_bruta = ''          THEN 'Processando'
            ELSE l.situacao_bruta END,
       CASE WHEN lower(l.resultado_bruto) ~ '^aprovado' THEN 'Aprovado'
            WHEN lower(l.resultado_bruto) ~ '^negado'   THEN 'Negado'
            ELSE 'Processando' END
FROM limpo l
JOIN clientes c ON lower(c.nome) = lower(l.nome);


-- ---------------------------------------------------------
-- 2. processos_ren
-- ---------------------------------------------------------
INSERT INTO processos_ren
    (cliente_id, consulado, n_solicitantes, data_casv,
     docs, status_rascunho, status_ds, situacao)
WITH limpo AS (
    SELECT nome_limpo(solicitante_principal) AS nome,
           btrim(con)                        AS consulado,
           numero_solicitantes::int          AS n_solicitantes,
           parse_data(casv)          AS data_casv,
           -- 'Solicitado', '#REF!' e vazio -> Pendente
           CASE WHEN lower(btrim(docs)) IN ('entregue', 'parcial') THEN initcap(lower(btrim(docs)))
                ELSE 'Pendente' END          AS docs,
           COALESCE(initcap(lower(NULLIF(NULLIF(btrim(rascunho), ''), '#REF!'))), 'Pendente') AS rascunho,
           COALESCE(initcap(lower(NULLIF(NULLIF(btrim(ds160), ''), '#REF!'))),    'Pendente') AS ds160,
           CASE btrim(situacao)
                WHEN 'Concluído' THEN 'Concluido'
                WHEN ''          THEN 'Processando'
                ELSE btrim(situacao) END     AS situacao
    FROM stg_ren_hist
    WHERE nome_limpo(solicitante_principal) <> ''
      AND NULLIF(btrim(con), '') IS NOT NULL
      AND NULLIF(btrim(numero_solicitantes), '') IS NOT NULL
)
SELECT c.id, l.consulado, l.n_solicitantes, l.data_casv,
       l.docs, l.rascunho, l.ds160, l.situacao
FROM limpo l
JOIN clientes c ON lower(c.nome) = lower(l.nome);


-- ---------------------------------------------------------
-- Linhas puladas (corrigir na planilha de origem)
-- ---------------------------------------------------------
SELECT 'OBT' AS aba, solicitante_principal, con, numero_solicitantes
FROM stg_obt_hist
WHERE nome_limpo(solicitante_principal) <> ''
  AND NULLIF(btrim(numero_solicitantes), '') IS NULL
UNION ALL
SELECT 'REN', solicitante_principal, con, numero_solicitantes
FROM stg_ren_hist
WHERE nome_limpo(solicitante_principal) <> ''
  AND (NULLIF(btrim(con), '') IS NULL OR NULLIF(btrim(numero_solicitantes), '') IS NULL);
