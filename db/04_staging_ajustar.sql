-- Remove do staging as colunas que nao vao para o banco definitivo.
-- Rodar UMA vez, depois de importar todos os CSVs e conferir as contagens.

-- coluna "Solicitante Principal" oculta (so alimentava dashboard)
ALTER TABLE stg_ren      DROP COLUMN solicitante_oculta;
ALTER TABLE stg_obt      DROP COLUMN solicitante_oculta;
ALTER TABLE stg_obt_hist DROP COLUMN solicitante_oculta;
ALTER TABLE stg_ren_hist DROP COLUMN solicitante_oculta;

-- ETA: o prazo do DS160 e calculado no back-end, nao fica no banco
ALTER TABLE stg_obt_hist DROP COLUMN eta;
ALTER TABLE stg_ren_hist DROP COLUMN eta;
