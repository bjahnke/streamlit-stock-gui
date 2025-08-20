CREATE TABLE public.stock_info (
    id serial PRIMARY KEY,
    symbol text,
    "Security" text,
    "GICS Sector" text,
    "GICS Sub-Industry" text,
    "Headquarters Location" text,
    "Date added" text,
    "CIK" bigint,
    "Founded" text
);