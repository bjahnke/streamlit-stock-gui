CREATE OR REPLACE FUNCTION create_price_view(table_name text, foreign_key_columns text[])
RETURNS void AS $$
DECLARE
    fk_column text;
    join_clauses text := '';
    select_clauses text := '';
BEGIN
    FOREACH fk_column IN ARRAY foreign_key_columns LOOP
        join_clauses := join_clauses || format('
            LEFT JOIN public.stock_data sd_%I ON t.%I = sd_%I.bar_number
        ', fk_column, fk_column, fk_column);
        select_clauses := select_clauses || format('
            sd_%I.close AS %I_px,
        ', fk_column, fk_column);
    END LOOP;

    EXECUTE format('
        CREATE OR REPLACE VIEW %I_price_view AS
        SELECT t.*, %s
        FROM %I t
        %s
    ', table_name, rtrim(select_clauses, ','), table_name, join_clauses);
END;
$$ LANGUAGE plpgsql;