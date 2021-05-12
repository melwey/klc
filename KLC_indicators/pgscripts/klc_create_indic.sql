-- create indicator tables (created in and exported from biopamarest; imported into biopama_api)

-- add image to schema
COMMENT ON SCHEMA klc IS 'Key Landscapes for Conservation {{''img'':''https://raw.githubusercontent.com/melwey/klc/master/img/LargerThanElephants2015.png?token=AK64EHIC6MA76DYIHBS5NETATLUJW''}}';

-- Table: klc.klc_countries

DROP TABLE IF EXISTS klc.klc_countries;

CREATE TABLE klc.klc_countries
(
    klc_id text COLLATE pg_catalog."default",
    iso2 text COLLATE pg_catalog."default",

    iso3 text COLLATE pg_catalog."default",
    country_name text COLLATE pg_catalog."default",
    area_klc_country double precision,
    pc_country_in_klc double precision,
    pc_klc_in_country double precision
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE klc.klc_countries
    OWNER to biopama_api_user;

COMMENT ON TABLE klc.klc_countries
    IS 'Country coverage statistics of KLCs. Imported by M. Weynants on 26/04/2021.';
	
-- import file
-- COPY klc.klc_countries (klc_id, iso2, iso3, country_name, area_klc_country, pc_country_in_klc, pc_klc_in_country) FROM '~/klc/KLC_indicators/outputs/tables/klc_countries.txt' DELIMITER '|';

-- Table: klc.klc_ecoregions

DROP TABLE IF EXISTS klc.klc_ecoregions;

CREATE TABLE klc.klc_ecoregions
(
    klc_id text COLLATE pg_catalog."default",
    first_level_code integer,
    first_level text COLLATE pg_catalog."default",
    area_klc_ecoregion double precision,
    pc_ecoregion_in_klc double precision,
    pc_klc_in_ecoregion double precision
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE klc.klc_ecoregions
    OWNER to biopama_api_user;

COMMENT ON TABLE klc.klc_ecoregions
    IS 'Ecoregions coverage statistics of KLCs. Imported by M. Weynants on 23/04/2021.';

-- import file
-- COPY klc.klc_ecoregions (klc_id, first_level_code, first_level, area_klc_ecoregion, pc_ecoregion_in_klc, pc_klc_in_ecoregion) FROM '~/klc/KLC_indicators/outputs/tables/klc_ecoregions.txt' DELIMITER '|';

-- Table: klc.klc_pas

DROP TABLE IF EXISTS klc.klc_pas;

CREATE TABLE klc.klc_pas
(
    klc_id text COLLATE pg_catalog."default",
    wdpaid integer,
    pa_name text COLLATE pg_catalog."default",
    iso3 text COLLATE pg_catalog."default",
    desig_eng text COLLATE pg_catalog."default",
    desig_type text COLLATE pg_catalog."default",
    iucn_cat text COLLATE pg_catalog."default",
    area_klc_pa double precision,
    pc_pa_in_klc double precision,
    pc_klc_in_pa double precision
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE klc.klc_pas
    OWNER to biopama_api_user;

COMMENT ON TABLE klc.klc_pas
    IS 'Protected areas coverage statistics of KLCs. Imported by M. Weynants on 23/04/2021.';

-- import file
-- COPY klc.klc_pas (klc_id, wdpaid, pa_name, iso3, desig_eng, desig_type,iucn_cat,area_klc_pa, pc_pa_in_klc, pc_klc_in_pa) FROM '~/klc/KLC_indicators/outputs/tables/klc_pas.txt' DELIMITER '|';


-- Table CGLCstats_KLC
DROP FUNCTION IF EXISTS klc.api_klc_cglc(text);
DROP VIEW IF EXISTS klc.v_klc_cglc;
DROP TABLE IF EXISTS klc.klc_cglc;

CREATE TABLE klc.klc_cglc(
	klc_id text,
	pa text,
	year double precision,
	bare double precision,
	crops double precision,
	grass double precision,
	moss double precision,
	shrub double precision,
	snow double precision,
	tree double precision,
	urban double precision,
	water_permanent double precision,
	water_seasonal double precision
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE klc.klc_cglc
    OWNER to biopama_api_user;

COMMENT ON TABLE klc.klc_cglc
    IS 'Copernicus global land coverage statistics of KLCs. Imported by M. Weynants on 27/04/2021.';
	
	