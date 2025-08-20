
ALTER TABLE ONLY public.peak ADD CONSTRAINT "bar_number_FK01" FOREIGN KEY (start) REFERENCES public.stock_data(id);
ALTER TABLE ONLY public.regime ADD CONSTRAINT "bar_number_FK01" FOREIGN KEY (start) REFERENCES public.stock_data(id);
ALTER TABLE ONLY public.floor_ceiling ADD CONSTRAINT "bar_number_FK02" FOREIGN KEY (fc_date) REFERENCES public.stock_data(id);
ALTER TABLE ONLY public.peak ADD CONSTRAINT "bar_number_FK02" FOREIGN KEY ("end") REFERENCES public.stock_data(id);
ALTER TABLE ONLY public.regime ADD CONSTRAINT "bar_number_FK02" FOREIGN KEY ("end") REFERENCES public.stock_data(id);
ALTER TABLE ONLY public.floor_ceiling ADD CONSTRAINT "bar_number_FK03" FOREIGN KEY (rg_ch_date) REFERENCES public.stock_data(id);
ALTER TABLE ONLY public.floor_ceiling ADD CONSTRAINT "stock_id_FK01" FOREIGN KEY (stock_id) REFERENCES public.stock(id);
ALTER TABLE ONLY public.peak ADD CONSTRAINT "stock_id_FK01" FOREIGN KEY (stock_id) REFERENCES public.stock(id);
ALTER TABLE ONLY public.regime ADD CONSTRAINT "stock_id_FK01" FOREIGN KEY (stock_id) REFERENCES public.stock(id);
ALTER TABLE ONLY public.stock_data ADD CONSTRAINT "stock_id_FK02" FOREIGN KEY (stock_id) REFERENCES public.stock(id);