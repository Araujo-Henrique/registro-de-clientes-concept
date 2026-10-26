-- Carga de processos_obt a partir de stg_obt.
-- Pre-requisitos: clientes carregada (06); funcoes de limpeza (05); stg_obt ajustada (04).
--
-- Regras:
--   * cliente = nome sem anotacao entre parenteses; linhas sem consulado ou sem n_solicitantes sao PULADAS
--     (NOT NULL) -- veja a lista no final do arquivo
--   * monitoramento: 'Congelada' -> Concluido, o resto -> Ativo
--   * datas: dd/mm/aa ou dd/mm/aaaa; sem ano, vazio ou texto -> NULL
--   * rascunho/ds160: '#REF!' ou vazio -> Pendente
--   * orientacao: 'Fornecidas (X)' -> Fornecidas + funcionario pela inicial;
--     'dd/mmm. (dia)' -> Agendada (set-dez = 2026, jan-ago = 2027); resto -> Pendente
--   * resultado: Aprovado/Negado normalizados; vazio, data ou texto livre -> Processando
--   * texto livre em resultado -> situacao Concluido (nao vira Limbo)
--   * data_vencimento_taxa: data com ano achada em resultado
--   * casv = 'PAGO' -> data_casv NULL e situacao 'Pago'
--   * codigo de rastreio dentro de situacao (/XX123BR) -> codigo_rastreio, situacao Concluido
--   * as duas colunas '-' da planilha nao sao carregadas

INSERT INTO processos_obt
    (cliente_id, consulado, n_solicitantes, monitoramento,
     data_casv, data_entrevista, data_vencimento_taxa,
     status_rascunho, status_ds,
     orientacao, orientacao_data, orientacao_por_id,
     situacao, codigo_rastreio, resultado)
WITH limpo AS (
    SELECT nome_limpo(solicitante_principal) AS nome,
           btrim(con)                       AS consulado,
           numero_solicitantes::int         AS n_solicitantes,
           CASE WHEN btrim(data_status) = 'Congelada' THEN 'Concluido' ELSE 'Ativo' END AS monitoramento,
           parse_data(casv)         AS data_casv,
           parse_data(entrevista)   AS data_entrevista,
           lower(btrim(casv)) = 'pago'      AS casv_pago,
           COALESCE(initcap(lower(NULLIF(NULLIF(btrim(rascunho), ''), '#REF!'))), 'Pendente') AS rascunho,
           COALESCE(initcap(lower(NULLIF(NULLIF(btrim(ds160), ''), '#REF!'))),    'Pendente') AS ds160,
           btrim(orientacoes)               AS orientacao_bruta,
           btrim(situacao)                  AS situacao_bruta,
           btrim(resultado_rastreio)        AS resultado_bruto
    FROM stg_obt
    WHERE NULLIF(btrim(con), '') IS NOT NULL
      AND NULLIF(btrim(numero_solicitantes), '') IS NOT NULL
),
classif AS (
    SELECT *,
           lower(resultado_bruto) AS r,
           -- texto livre = nao vazio, nao Aprovado/Negado, nao data
           resultado_bruto <> ''
             AND lower(resultado_bruto) !~ '^(aprovado|negado)'
             AND resultado_bruto !~ '\d{1,2}[/-]\d{1,2}' AS resultado_texto_livre
    FROM limpo
)
SELECT c.id, l.consulado, l.n_solicitantes, l.monitoramento,
       l.data_casv, l.data_entrevista,
       -- primeira data com ano em resultado (ex.: 'taxa vence 11/02/26'); sem ano -> NULL
       parse_data(substring(l.resultado_bruto from '(\d{1,2}/\d{1,2}/(?:\d{4}|\d{2}))')),
       l.rascunho, l.ds160,
       CASE WHEN l.orientacao_bruta ~* '^fornecidas' THEN 'Fornecidas'
            WHEN parse_data(substring(l.orientacao_bruta from '^\d{1,2}/\d{1,2}/\d{2,4}')) IS NOT NULL THEN 'Agendada'
            WHEN l.orientacao_bruta ~ '^\d{1,2}/[a-z]{3}\.' THEN 'Agendada'
            ELSE 'Pendente' END,
       -- data completa (dd/mm/aa) quando a planilha traz ano; senao o formato antigo 'dd/mmm. (dia)'
       COALESCE(
         parse_data(substring(l.orientacao_bruta from '^\d{1,2}/\d{1,2}/\d{2,4}')),
         CASE WHEN l.orientacao_bruta ~ '^\d{1,2}/[a-z]{3}\.' THEN
            make_date(
              CASE WHEN substring(l.orientacao_bruta from '/([a-z]{3})\.') IN ('set','out','nov','dez')
                   THEN 2026 ELSE 2027 END,
              array_position(ARRAY['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'],
                             substring(l.orientacao_bruta from '/([a-z]{3})\.')),
              substring(l.orientacao_bruta from '^(\d{1,2})/')::int)
         END),
       -- inicial entre parenteses -> funcionario cuja primeira letra do nome e essa inicial
       (SELECT f.id FROM funcionarios f
         WHERE upper(left(f.nome, 1)) = upper(substring(l.orientacao_bruta from '\(([A-Za-z])\)'))),
       CASE WHEN l.casv_pago                      THEN 'Pago'
            WHEN l.situacao_bruta LIKE '/%'       THEN 'Concluido'
            WHEN l.resultado_texto_livre          THEN 'Concluido'
            WHEN l.situacao_bruta = 'Concluído'   THEN 'Concluido'
            WHEN l.situacao_bruta = '.Cadastro'   THEN 'Cadastro'
            WHEN l.situacao_bruta = '.Boleto'     THEN 'Boleto'
            WHEN l.situacao_bruta = '.Crédito'    THEN 'Credito'
            WHEN l.situacao_bruta = ''            THEN 'Processando'
            ELSE l.situacao_bruta END,
       CASE WHEN l.situacao_bruta LIKE '/%' THEN l.situacao_bruta END,
       CASE WHEN l.r ~ '^aprovado' THEN 'Aprovado'
            WHEN l.r ~ '^negado'   THEN 'Negado'
            ELSE 'Processando' END
FROM classif l
JOIN clientes c ON lower(c.nome) = lower(l.nome);

-- Linhas puladas por falta de consulado ou n_solicitantes (corrigir na planilha de origem):
SELECT solicitante_principal, con, numero_solicitantes
FROM stg_obt
WHERE NULLIF(btrim(con), '') IS NULL OR NULLIF(btrim(numero_solicitantes), '') IS NULL;
