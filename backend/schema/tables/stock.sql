CREATE TABLE public.stock (
    id serial PRIMARY KEY,
    symbol text NOT NULL,
    is_relative boolean NOT NULL,
    "interval" text NOT NULL,
    data_source text NOT NULL,
    market_index text NOT NULL,
    sec_type text NOT NULL
)

-- ALTER TABLE public.stock OWNER TO bjahnke71;