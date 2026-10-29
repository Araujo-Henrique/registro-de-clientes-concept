-- Concept Client Registry: esquema inicial
-- Rodar no Query Tool do pgAdmin, conectado ao banco concept_client_registry.
-- Rode UMA seção por vez (selecione o trecho e F5) e valide antes de seguir.
-- Tabela de REN fica de fora ate resolvermos Despacho e Rastreio/CEP.


-- =========================================================
-- 1. funcionarios (tabela de referencia)
-- =========================================================
CREATE TABLE funcionarios (
    id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome  TEXT    NOT NULL CHECK (nome = btrim(nome) AND nome <> ''),
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- Unicidade sem diferenciar maiusculas: 'Gabriel Vieira' e 'gabriel vieira' colidem.
CREATE UNIQUE INDEX funcionarios_nome_unico ON funcionarios (LOWER(nome));

INSERT INTO funcionarios (nome) VALUES
    ('Gabriel Vieira'),
    ('Marcio Conde'),
    ('Henrique Araujo');

-- Ex-funcionarios (historico de orientacoes): inativos
INSERT INTO funcionarios (nome, ativo) VALUES
    ('Roger Cardoso', FALSE),
    ('Thiago HP',  FALSE),
    ('Esther HP',  FALSE),
    ('Joao Banks',    FALSE);


-- =========================================================
-- 2. clientes (quem e a pessoa/familia)
-- =========================================================
-- email e telefone NAO sao UNIQUE: familias e agencias compartilham.
-- telefone guarda so digitos ja normalizados pela API (ver normaliza_telefone).
-- email/telefone aceitam NULL porque ha registros historicos sem eles
-- (ex.: passaportes); a API continua exigindo para cadastro novo.
CREATE TABLE clientes (
    id       INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome     TEXT NOT NULL CHECK (nome = btrim(nome) AND nome <> ''),
    email    TEXT CHECK (email ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
    telefone TEXT CHECK (telefone ~ '^\d{10,15}$'),
    grupo    TEXT CHECK (grupo IS NULL OR (grupo = btrim(grupo) AND grupo <> ''))
);

-- Postgres NAO indexa FK automaticamente; telefone sera muito consultado
-- para agrupar familias/agencias.
CREATE INDEX clientes_telefone_idx ON clientes (telefone);
CREATE UNIQUE INDEX clientes_nome_unico ON clientes (LOWER(nome));


-- =========================================================
-- 3. processos_obt (obtencao do visto)
-- =========================================================
CREATE TABLE processos_obt (
    id                   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id           INTEGER NOT NULL REFERENCES clientes (id),

    -- 'N/D' = historico antigo sem consulado registrado
    consulado            TEXT NOT NULL
                         CHECK (consulado IN ('POA', 'SP', 'RIO', 'BSB', 'REC', 'N/D')),
    n_solicitantes       INTEGER NOT NULL CHECK (n_solicitantes > 0),
    monitoramento        TEXT NOT NULL DEFAULT 'Ativo'
                         CHECK (monitoramento IN ('Ativo', 'Concluido')),

    data_casv            DATE,
    data_entrevista      DATE,
    data_vencimento_taxa DATE,

    status_rascunho      TEXT NOT NULL
                         CHECK (status_rascunho IN ('Pendente', 'Parcial', 'Enviado')),
    status_ds            TEXT NOT NULL
                         CHECK (status_ds IN ('Pendente', 'Parcial', 'Aberto', 'Preenchido', 'Revisado', 'Fechado')),

    orientacao           TEXT NOT NULL
                         CHECK (orientacao IN ('Opt A', 'Fornecidas', 'Agendada', 'Pendente')),
    orientacao_data      DATE,
    orientacao_por_id    INTEGER REFERENCES funcionarios (id),

    situacao             TEXT NOT NULL
                         CHECK (situacao IN ('Pagamento Pendente', 'Boleto', 'Credito', 'Limbo',
                                             'Processando', 'Cadastro', 'Administrativo', 'Pago', 'Concluido')),
    -- linhas 'AA00XXXXXX - Solicitante' (uma por formulario); montadas e validadas pelo back-end
    codigo_ds160         TEXT
                         CHECK (codigo_ds160 IS NULL
                                OR (codigo_ds160 = btrim(codigo_ds160) AND codigo_ds160 <> '')),
    -- o resto da nota da celula do DS160 (pedidos de alteracao), sem as linhas de codigo
    notas_ds160          TEXT
                         CHECK (notas_ds160 IS NULL
                                OR (notas_ds160 = btrim(notas_ds160) AND notas_ds160 <> '')),
    codigo_rastreio      TEXT
                         CHECK (codigo_rastreio IS NULL
                                OR (codigo_rastreio = btrim(codigo_rastreio) AND codigo_rastreio <> '')),
    resultado            TEXT NOT NULL
                         CHECK (resultado IN ('Processando', 'Aprovado', 'Negado')),

    -- mesma regra do Pydantic: orientacao Agendada exige data
    CONSTRAINT orientacao_agendada_exige_data
        CHECK (orientacao <> 'Agendada' OR orientacao_data IS NOT NULL)
);

CREATE INDEX processos_obt_cliente_idx ON processos_obt (cliente_id);


-- =========================================================
-- 4. passaportes
-- =========================================================
CREATE TABLE passaportes (
    id             INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id     INTEGER NOT NULL REFERENCES clientes (id),
    n_solicitantes INTEGER NOT NULL CHECK (n_solicitantes > 0),
    data_pf        DATE,
    prazo_pf       DATE,
    situacao       TEXT
                   CHECK (situacao IN ('Pendente', 'Pagamento Pendente', 'Pago', 'Boleto',
                                       'Pix', 'Processando', 'Concluido'))
);

CREATE INDEX passaportes_cliente_idx ON passaportes (cliente_id);
