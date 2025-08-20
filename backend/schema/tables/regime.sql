CREATE TABLE public.regime (
    id serial PRIMARY KEY,
    start serial NOT NULL,
    "end" serial NOT NULL,
    rg double precision NOT NULL,
    type text NOT NULL,
    stock_id serial NOT NULL
);

-- ALTER TABLE public.regime OWNER TO bjahnke71;