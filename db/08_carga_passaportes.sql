-- Carga de passaportes a partir de stg_pass.
-- Pre-requisito: clientes ja carregada (06_carga_clientes.sql).
--
-- Regras:
--   * cliente = nome sem anotacao entre parenteses (mesma regra da carga de clientes)
--   * data_pf com duas datas na mesma celula: vale a primeira
--   * datas dd/mm/aaaa (4 digitos no ano); vazio ou fora do formato vira NULL
--   * situacao: normaliza variacoes (PIX/Pix, PAGO/pago, 'Pag pendente'); valor
--     desconhecido (ex.: 'Safado') ou vazio vira NULL

INSERT INTO passaportes (cliente_id, n_solicitantes, data_pf, prazo_pf, situacao)
WITH limpo AS (
    SELECT nome_limpo(solicitante_principal) AS nome,
           numero_solicitantes::int AS n_solicitantes,
           btrim(split_part(data_pf, E'\n', 1))  AS data_pf,
           btrim(split_part(prazo_pf, E'\n', 1)) AS prazo_pf,
           lower(btrim(situacao))                AS situacao
    FROM stg_pass
)
SELECT c.id,
       l.n_solicitantes,
       CASE WHEN l.data_pf  ~ '^\d{2}/\d{2}/\d{4}$' THEN to_date(l.data_pf,  'DD/MM/YYYY') END,
       CASE WHEN l.prazo_pf ~ '^\d{2}/\d{2}/\d{4}$' THEN to_date(l.prazo_pf, 'DD/MM/YYYY') END,
       CASE l.situacao
            WHEN 'concluído'          THEN 'Concluido'
            WHEN 'processando'        THEN 'Processando'
            WHEN 'pendente'           THEN 'Pendente'
            WHEN 'pag pendente'       THEN 'Pagamento Pendente'
            WHEN 'pagamento pendente' THEN 'Pagamento Pendente'
            WHEN 'boleto'             THEN 'Boleto'
            WHEN 'pix'                THEN 'Pix'
            WHEN 'pago'               THEN 'Pago'
       END
FROM limpo l
JOIN clientes c ON lower(c.nome) = lower(l.nome);
