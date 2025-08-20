CREATE TABLE public.floor_ceiling (
    id serial PRIMARY KEY,
    test double precision NOT NULL,
    fc_val double precision NOT NULL,
    fc_date serial NOT NULL,
    rg_ch_date serial NOT NULL,
    rg_ch_val double precision NOT NULL,
    type bigint NOT NULL,
    stock_id serial NOT NULL
);

-- ALTER TABLE public.floor_ceiling OWNER TO bjahnke71;