CREATE TABLE public.asset_info (
    id serial PRIMARY KEY,
    symbol text,
    data_source text,
    class text,
    sub_class text,
    type text
);