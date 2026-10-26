-- Ajustes em processos_obt e funcionarios (para o banco que ja foi criado com a versao antiga do 01_schema.sql).
-- Rodar UMA vez, antes de 07_carga_processos_obt.sql. Quem criar o banco do zero com o 01 atual NAO precisa.

-- 1. ex-funcionarios (inativos) para o historico de orientacoes
INSERT INTO funcionarios (nome, ativo) VALUES
    ('Roger Cardoso', FALSE),
    ('Thiago Matos',  FALSE),
    ('Esther Matos',  FALSE);

-- 2. orientacao ganha 'Pendente'
ALTER TABLE processos_obt DROP CONSTRAINT processos_obt_orientacao_check;
ALTER TABLE processos_obt ADD CONSTRAINT processos_obt_orientacao_check
    CHECK (orientacao IN ('Opt A', 'Fornecidas', 'Agendada', 'Pendente'));

-- 3. situacao ganha 'Pago'
ALTER TABLE processos_obt DROP CONSTRAINT processos_obt_situacao_check;
ALTER TABLE processos_obt ADD CONSTRAINT processos_obt_situacao_check
    CHECK (situacao IN ('Pagamento Pendente', 'Boleto', 'Credito', 'Limbo',
                        'Processando', 'Cadastro', 'Administrativo', 'Pago', 'Concluido'));

-- 4. nova coluna de rastreio
ALTER TABLE processos_obt ADD COLUMN codigo_rastreio TEXT
    CHECK (codigo_rastreio IS NULL
           OR (codigo_rastreio = btrim(codigo_rastreio) AND codigo_rastreio <> ''));
