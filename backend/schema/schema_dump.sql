
--
-- PostgreSQL database dump
--

-- Dumped from database version 15.10
-- Dumped by pg_dump version 17.2 (Ubuntu 17.2-1.pgdg22.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: entry; Type: TABLE; Schema: public; Owner: bjahnke71
--

CREATE TABLE public.entry (
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

--
-- Name: floor_ceiling; Type: TABLE; Schema: public; Owner: bjahnke71
--

CREATE TABLE public.floor_ceiling (
    test double precision NOT NULL,
    fc_val double precision NOT NULL,
    fc_date bigint NOT NULL,
    rg_ch_date bigint NOT NULL,
    rg_ch_val double precision NOT NULL,
    type bigint NOT NULL,
    stock_id bigint NOT NULL
);

-- ALTER TABLE public.floor_ceiling OWNER TO bjahnke71;

--
-- Name: peak; Type: TABLE; Schema: public; Owner: bjahnke71
--

CREATE TABLE public.peak (
    start bigint NOT NULL,
    "end" bigint NOT NULL,
    type bigint NOT NULL,
    lvl bigint NOT NULL,
    st_px double precision NOT NULL,
    en_px double precision NOT NULL,
    stock_id bigint NOT NULL
);

-- ALTER TABLE public.peak OWNER TO bjahnke71;

--
-- Name: regime; Type: TABLE; Schema: public; Owner: bjahnke71
--

CREATE TABLE public.regime (
    start bigint NOT NULL,
    "end" bigint NOT NULL,
    rg double precision NOT NULL,
    type text NOT NULL,
    stock_id bigint NOT NULL
);

-- ALTER TABLE public.regime OWNER TO bjahnke71;

--
-- Name: stock; Type: TABLE; Schema: public; Owner: bjahnke71
--

CREATE TABLE public.stock (
    id bigint NOT NULL,
    symbol text NOT NULL,
    is_relative boolean NOT NULL,
    "interval" text NOT NULL,
    data_source text NOT NULL,
    market_index text,
    sec_type text
);

-- ALTER TABLE public.stock OWNER TO bjahnke71;

--
-- Name: stock_data; Type: TABLE; Schema: public; Owner: bjahnke71
--

CREATE TABLE public.stock_data (
    bar_number bigint NOT NULL,
    close double precision NOT NULL,
    stock_id bigint NOT NULL
);

-- ALTER TABLE public.stock_data OWNER TO bjahnke71;

--
-- Name: stock_info; Type: TABLE; Schema: public; Owner: bjahnke71
--

CREATE TABLE public.stock_info (
    index bigint NOT NULL,
    symbol text,
    "Security" text,
    "GICS Sector" text,
    "GICS Sub-Industry" text,
    "Headquarters Location" text,
    "Date added" text,
    "CIK" bigint,
    "Founded" text
);

-- ALTER TABLE public.stock_info OWNER TO bjahnke71;

--
-- Name: test; Type: TABLE; Schema: public; Owner: bjahnke71
--

CREATE TABLE public.test (
);

-- ALTER TABLE public.test OWNER TO bjahnke71;

--
-- Name: test_data; Type: TABLE; Schema: public; Owner: bjahnke71
--

CREATE TABLE public.test_data (
    symbol text,
    bar_number bigint,
    close double precision,
    high double precision,
    low double precision,
    open double precision,
    is_relative boolean,
    "interval" text
);

-- ALTER TABLE public.test_data OWNER TO bjahnke71;

--
-- Name: timestamp_data; Type: TABLE; Schema: public; Owner: bjahnke71
--

CREATE TABLE public.timestamp_data (
    bar_number bigint NOT NULL,
    "interval" text NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    data_source text NOT NULL
);

-- ALTER TABLE public.timestamp_data OWNER TO bjahnke71;

--
-- Name: timestamp_data bar_number_PK01; Type: CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.timestamp_data
--     ADD CONSTRAINT "bar_number_PK01" PRIMARY KEY (bar_number);

--
-- Name: stock id_PK01; Type: CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.stock
--     ADD CONSTRAINT "id_PK01" PRIMARY KEY (id);

--
-- Name: stock_info index_PK01; Type: CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.stock_info
--     ADD CONSTRAINT "index_PK01" PRIMARY KEY (index);

--
-- Name: ix_stock_info_index; Type: INDEX; Schema: public; Owner: bjahnke71
--

-- CREATE INDEX ix_stock_info_index ON public.stock_info USING btree (index);

--
-- Name: stock_data bar_number_FK01; Type: FK CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.stock_data
--     ADD CONSTRAINT "bar_number_FK01" FOREIGN KEY (bar_number) REFERENCES public.timestamp_data(bar_number);

--
-- Name: peak bar_number_FK01; Type: FK CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.peak
--     ADD CONSTRAINT "bar_number_FK01" FOREIGN KEY (start) REFERENCES public.timestamp_data(bar_number);

--
-- Name: regime bar_number_FK01; Type: FK CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.regime
--     ADD CONSTRAINT "bar_number_FK01" FOREIGN KEY (start) REFERENCES public.timestamp_data(bar_number);

--
-- Name: floor_ceiling bar_number_FK02; Type: FK CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.floor_ceiling
--     ADD CONSTRAINT "bar_number_FK02" FOREIGN KEY (fc_date) REFERENCES public.timestamp_data(bar_number);

--
-- Name: peak bar_number_FK02; Type: FK CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.peak
--     ADD CONSTRAINT "bar_number_FK02" FOREIGN KEY ("end") REFERENCES public.timestamp_data(bar_number);

--
-- Name: regime bar_number_FK02; Type: FK CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.regime
--     ADD CONSTRAINT "bar_number_FK02" FOREIGN KEY ("end") REFERENCES public.timestamp_data(bar_number);

--
-- Name: floor_ceiling bar_number_FK03; Type: FK CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.floor_ceiling
--     ADD CONSTRAINT "bar_number_FK03" FOREIGN KEY (rg_ch_date) REFERENCES public.timestamp_data(bar_number);

--
-- Name: floor_ceiling stock_id_FK01; Type: FK CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.floor_ceiling
--     ADD CONSTRAINT "stock_id_FK01" FOREIGN KEY (stock_id) REFERENCES public.stock(id);

--
-- Name: peak stock_id_FK01; Type: FK CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.peak
--     ADD CONSTRAINT "stock_id_FK01" FOREIGN KEY (stock_id) REFERENCES public.stock(id);

--
-- Name: regime stock_id_FK01; Type: FK CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.regime
--     ADD CONSTRAINT "stock_id_FK01" FOREIGN KEY (stock_id) REFERENCES public.stock(id);

--
-- Name: stock_data stock_id_FK02; Type: FK CONSTRAINT; Schema: public; Owner: bjahnke71
--

-- ALTER TABLE ONLY public.stock_data
--     ADD CONSTRAINT "stock_id_FK02" FOREIGN KEY (stock_id) REFERENCES public.stock(id);

--
-- PostgreSQL database dump complete
--