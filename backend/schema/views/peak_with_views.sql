CREATE VIEW public.peak_with_prices AS
SELECT
    p.start,
    p."end",
    p.type,
    p.lvl,
    p.stock_id,
    sd_start.close AS st_px,
    sd_end.close AS en_px
FROM
    public.peak p
JOIN
    public.stock_data sd_start ON p.start = sd_start.bar_number AND p.stock_id = sd_start.stock_id
JOIN
    public.stock_data sd_end ON p."end" = sd_end.bar_number AND p.stock_id = sd_end.stock_id;