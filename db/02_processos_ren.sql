-- processos_ren (renovacao do visto)
-- Rodar depois de 01_schema.sql (precisa de clientes).
-- Sem monitoramento e sem resultado: nao existem no fluxo de renovacao.

CREATE TABLE processos_ren (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id      INTEGER NOT NULL REFERENCES clientes (id),

    consulado       TEXT NOT NULL
                    CHECK (consulado IN ('POA', 'SP', 'RIO', 'BSB', 'REC')),
    n_solicitantes  INTEGER NOT NULL CHECK (n_solicitantes > 0),

    data_casv       DATE,
    -- sempre 7 dias antes do CASV: o banco calcula, ninguem preenche
    data_despacho   DATE GENERATED ALWAYS AS (data_casv - 7) STORED,

    docs            TEXT NOT NULL
                    CHECK (docs IN ('Pendente', 'Parcial', 'Entregue')),
    status_rascunho TEXT NOT NULL
                    CHECK (status_rascunho IN ('Pendente', 'Parcial', 'Enviado')),
    status_ds       TEXT NOT NULL
                    CHECK (status_ds IN ('Pendente', 'Parcial', 'Aberto', 'Preenchido', 'Revisado', 'Fechado')),

    situacao        TEXT NOT NULL
                    CHECK (situacao IN ('Pagamento Pendente', 'Boleto', 'Credito', 'Limbo',
                                        'Processando', 'Cadastro', 'Administrativo',
                                        'Entrevista', 'Concluido')),

    -- linhas 'AA00XXXXXX - Solicitante' (uma por formulario); montadas e validadas pelo back-end
    codigo_ds160    TEXT CHECK (codigo_ds160 IS NULL
                                OR (codigo_ds160 = btrim(codigo_ds160) AND codigo_ds160 <> '')),
    -- o resto da nota da celula do DS160 (pedidos de alteracao), sem as linhas de codigo
    notas_ds160     TEXT CHECK (notas_ds160 IS NULL
                                OR (notas_ds160 = btrim(notas_ds160) AND notas_ds160 <> '')),
    codigo_rastreio TEXT CHECK (codigo_rastreio IS NULL
                                OR (codigo_rastreio = btrim(codigo_rastreio) AND codigo_rastreio <> '')),
    endereco        TEXT CHECK (endereco IS NULL
                                OR (endereco = btrim(endereco) AND endereco <> ''))
);

CREATE INDEX processos_ren_cliente_idx ON processos_ren (cliente_id);
