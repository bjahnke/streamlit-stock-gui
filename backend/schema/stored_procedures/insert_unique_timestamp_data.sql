CREATE OR REPLACE PROCEDURE insert_unique_timestamp_data(
    incoming_data jsonb
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Create a temporary table for incoming data
    CREATE TEMP TABLE temp_stock_data (
        id serial PRIMARY KEY,
        stock_id bigint NOT NULL,
        close double precision NOT NULL,
        open double precision NOT NULL,
        high double precision NOT NULL,
        low double precision NOT NULL,
        volume bigint NOT NULL,
        "timestamp" timestamp without time zone NOT NULL
    ) ON COMMIT DROP;

    -- Insert the incoming JSONB data into the temporary table
    INSERT INTO temp_stock_data (stock_id, close, open, high, low, volume, "timestamp")
    SELECT
        (data->>'stock_id')::BIGINT,
        (data->>'close')::DOUBLE PRECISION,
        (data->>'open')::DOUBLE PRECISION,
        (data->>'high')::DOUBLE PRECISION,
        (data->>'low')::DOUBLE PRECISION,
        (data->>'volume')::DOUBLE PRECISION,
        (data->>'timestamp')::TIMESTAMP
    FROM jsonb_array_elements(incoming_data) AS data;

    -- Insert unique rows into the main table
    INSERT INTO stock_data (timestamp, stock_id, close, open, high, low, volume)
    SELECT t."timestamp", t.stock_id, t.close, t.open, t.high, t.low, t.volume
    FROM temp_stock_data t
    WHERE NOT EXISTS (
        SELECT 1
        FROM stock_data sd
        WHERE sd."timestamp" = t."timestamp"
          AND sd.stock_id = t.stock_id
    );
END;
$$;
