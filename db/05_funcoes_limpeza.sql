-- Funcoes de limpeza usadas pelas cargas (06 a 10). Rodar uma vez, depois do 04.

-- nome sem a anotacao entre parenteses, ex.: 'Fulano (Retirada)' -> 'Fulano';
-- tambem colapsa qualquer espaco em branco (inclusive TAB) e apara as pontas
CREATE OR REPLACE FUNCTION nome_limpo(t TEXT) RETURNS TEXT AS $$
    SELECT btrim(regexp_replace(regexp_replace(t, '\([^)]*\)', '', 'g'), '\s+', ' ', 'g'))
$$ LANGUAGE sql IMMUTABLE;

-- a anotacao so vira grupo quando e uma agencia conhecida (ampliar a lista se necessario)
CREATE OR REPLACE FUNCTION grupo_da_anotacao(t TEXT) RETURNS TEXT AS $$
    SELECT CASE WHEN lower(btrim(substring(t from '\(([^)]*)\)'))) IN ('selettra', 'fast vistos')
                THEN btrim(substring(t from '\(([^)]*)\)')) END
$$ LANGUAGE sql IMMUTABLE;

-- dd/mm/aa ou dd/mm/aaaa (dia e mes com 1 ou 2 digitos); qualquer outra coisa -> NULL
CREATE OR REPLACE FUNCTION parse_data(t TEXT) RETURNS DATE AS $$
    SELECT CASE
        WHEN btrim(t) ~ '^\d{1,2}/\d{1,2}/\d{4}$' THEN to_date(btrim(t), 'DD/MM/YYYY')
        WHEN btrim(t) ~ '^\d{1,2}/\d{1,2}/\d{2}$'  THEN to_date(btrim(t), 'DD/MM/YY')
    END
$$ LANGUAGE sql STABLE;
