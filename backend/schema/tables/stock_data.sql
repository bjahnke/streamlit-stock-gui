CREATE TABLE public.stock_data (
    id serial PRIMARY KEY,
    stock_id bigint NOT NULL,
    close double precision NOT NULL,
    open double precision NOT NULL,
    high double precision NOT NULL,
    low double precision NOT NULL,
    volume bigint NOT NULL,
    "timestamp" timestamp without time zone NOT NULL
);

-- ALTER TABLE public.stock_data OWNER TO bjahnke71;