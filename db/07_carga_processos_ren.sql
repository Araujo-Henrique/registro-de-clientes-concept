-- Carga de processos_ren a partir de stg_ren.
-- Pre-requisito: clientes ja carregada (06_carga_clientes.sql).
--
-- Regras:
--   * cliente = nome sem anotacao entre parenteses (mesma regra da carga de clientes)
--   * '#REF!' em docs/rascunho/ds160 vira 'Pendente'
--   * casv fora do formato dd/mm/aa (vazio, 'PAGO') vira NULL
--   * data_despacho nao entra: e coluna gerada (casv - 7)
--   * rastreio: comeca com '/' = codigo de rastreio (ex.: /AA22222);
--     tem espaco ou virgula = endereco; o resto (datas dd/mm, 'Vencido') e ruido e fica NULL

INSERT INTO processos_ren
    (cliente_id, consulado, n_solicitantes, data_casv,
     docs, status_rascunho, status_ds, codigo_ds160, notas_ds160, situacao, codigo_rastreio, endereco)
WITH limpo AS (
    SELECT nome_limpo(solicitante_principal) AS nome,
           con,
           numero_solicitantes::int AS n_solicitantes,
           CASE WHEN btrim(casv) ~ '^\d{2}/\d{2}/\d{2}$'
                THEN to_date(btrim(casv), 'DD/MM/YY') END AS data_casv,
           initcap(lower(NULLIF(btrim(docs), '#REF!')))     AS docs,
           initcap(lower(NULLIF(btrim(rascunho), '#REF!'))) AS rascunho,
           initcap(lower(NULLIF(btrim(ds160), '#REF!')))    AS ds160,
           linhas_codigo_ds160(notas_ds160)     AS codigo_ds160,
           linhas_nao_codigo_ds160(notas_ds160) AS notas_ds160,
           CASE btrim(situacao)
                WHEN 'Concluído' THEN 'Concluido'
                WHEN '.Cadastro' THEN 'Cadastro'
                ELSE btrim(situacao)
           END AS situacao,
           NULLIF(btrim(rastreio), '') AS rastreio
    FROM stg_ren
)
SELECT c.id, l.con, l.n_solicitantes, l.data_casv,
       COALESCE(l.docs,     'Pendente'),
       COALESCE(l.rascunho, 'Pendente'),
       COALESCE(l.ds160,    'Pendente'),
       l.codigo_ds160, l.notas_ds160,
       l.situacao,
       CASE WHEN l.rastreio ~ '^/' THEN l.rastreio END,
       CASE WHEN l.rastreio !~ '^/' AND l.rastreio ~ '[\s,]' THEN l.rastreio END
FROM limpo l
JOIN clientes c ON lower(c.nome) = lower(l.nome);
