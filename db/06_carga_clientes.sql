-- Carga de clientes a partir de TODAS as tabelas de staging (REN, OBT, PASS e historicos).
-- Pre-requisitos: 05_funcoes_limpeza.sql rodado; staging carregado e ajustado (03 e 04).
-- Se clientes ja tiver linhas de um teste anterior: TRUNCATE clientes RESTART IDENTITY CASCADE;
--
-- Regras:
--   * cliente = nome sem anotacao entre parenteses, sem diferenciar maiuscula nem espacos repetidos
--   * telefone pode repetir entre clientes; o historico nao tem telefone
--   * telefone guardado so com digitos e SEM o 55 do Brasil (ex.: 41999999999), como a API
--   * e-mail fora do formato (ex.: 'SEMACESSO') vira NULL
--   * whatsapp sem digitos e com letra vira grupo; agencias entre parenteses no nome tambem
--   * para cada campo, vale o primeiro valor nao nulo na prioridade:
--     OBT > REN > PASS > OBT historico > REN historico
--   * linhas sem nome, ou que as cargas de processos vao pular (sem consulado / sem
--     n_solicitantes), nao geram cliente por si so

INSERT INTO clientes (nome, email, telefone, grupo)
WITH fontes AS (
    SELECT 1 AS prioridade, solicitante_principal AS nome, email, whatsapp FROM stg_obt
     WHERE NULLIF(btrim(con), '') IS NOT NULL AND NULLIF(btrim(numero_solicitantes), '') IS NOT NULL
    UNION ALL
    SELECT 2, solicitante_principal, email, whatsapp FROM stg_ren
     WHERE NULLIF(btrim(con), '') IS NOT NULL AND NULLIF(btrim(numero_solicitantes), '') IS NOT NULL
    UNION ALL
    SELECT 3, solicitante_principal, NULL, whatsapp FROM stg_pass
    UNION ALL
    SELECT 4, solicitante_principal, email, NULL FROM stg_obt_hist
     WHERE NULLIF(btrim(numero_solicitantes), '') IS NOT NULL
    UNION ALL
    SELECT 5, solicitante_principal, email, NULL FROM stg_ren_hist
     WHERE NULLIF(btrim(con), '') IS NOT NULL AND NULLIF(btrim(numero_solicitantes), '') IS NOT NULL
),
base AS (
    SELECT prioridade,
           nome_limpo(nome)                             AS nome,
           grupo_da_anotacao(nome)                      AS grupo_anotacao,
           CASE WHEN btrim(email) ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$' THEN btrim(email) END AS email,
           regexp_replace(whatsapp, '\D', '', 'g')      AS digitos,
           NULLIF(btrim(whatsapp), '')                  AS bruto
    FROM fontes
),
limpo AS (
    SELECT prioridade, nome, email,
           -- mesma regra da API (normaliza_telefone): tira o 55 do Brasil so quando o tamanho
           -- confirma que e codigo de pais (12-13 digitos), pois 55 tambem e DDD (Santa Maria/RS)
           CASE WHEN digitos LIKE '55%' AND length(digitos) IN (12, 13) THEN substr(digitos, 3)
                WHEN length(digitos) BETWEEN 10 AND 15                  THEN digitos
           END AS telefone,
           COALESCE(grupo_anotacao,
                    CASE WHEN digitos = '' AND bruto ~ '[[:alpha:]]' THEN bruto END) AS grupo
    FROM base
    WHERE nome <> ''
)
SELECT (array_agg(nome ORDER BY prioridade))[1],
       (array_agg(email    ORDER BY prioridade) FILTER (WHERE email    IS NOT NULL))[1],
       (array_agg(telefone ORDER BY prioridade) FILTER (WHERE telefone IS NOT NULL))[1],
       (array_agg(grupo    ORDER BY prioridade) FILTER (WHERE grupo    IS NOT NULL))[1]
FROM limpo
GROUP BY lower(nome);
