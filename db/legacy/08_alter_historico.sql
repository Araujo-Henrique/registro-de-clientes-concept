-- Ajustes para receber o historico 2021-2023 (rodar UMA vez, antes de 09_carga_historico.sql).
-- Quem criar o banco do zero com o 01_schema.sql atual NAO precisa rodar este arquivo.

-- 1. ex-funcionario (inativo) citado nas orientacoes antigas
INSERT INTO funcionarios (nome, ativo) VALUES ('Joao Banks', FALSE);

-- 2. historico sem consulado registrado entra como 'N/D'
ALTER TABLE processos_obt DROP CONSTRAINT processos_obt_consulado_check;
ALTER TABLE processos_obt ADD CONSTRAINT processos_obt_consulado_check
    CHECK (consulado IN ('POA', 'SP', 'RIO', 'BSB', 'REC', 'N/D'));
