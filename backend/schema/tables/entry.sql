CREATE TABLE public.entry (
    id serial PRIMARY KEY,
    entry_date timestamp without time zone,
    symbol text,
    cost double precision,
    stop double precision,
    trail double precision,
    trail_amount double precision,
    target double precision,
    quantity double precision,
    direction bigint,
    risk bigint,
    multiple bigint,
    fraction double precision,
    is_relative boolean,
    stock_id bigint,
    signal_age bigint,
    r_pct double precision
);

-- ALTER TABLE public.entry OWNER TO bjahnke71;