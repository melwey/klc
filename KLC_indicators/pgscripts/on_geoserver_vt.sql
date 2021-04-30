-- DROP TABLE IF EXISTS klc.klc_201909_proposal_backup;

-- CREATE TABLE klc.klc_201909_proposal_backup AS
-- SELECT * FROM klc.klc_201909_proposal;

-- Table: klc.klc_ris

DROP TABLE IF EXISTS klc.klc_ris;

CREATE TABLE klc.klc_ris
(
    id integer,
    geom geometry(MultiPolygonZ,4326),
    fid bigint,
    klc_id character varying COLLATE pg_catalog."default",
    area_km2 double precision,
    klc_name character varying COLLATE pg_catalog."default",
    "Comments" character varying COLLATE pg_catalog."default",
    target_pas character varying COLLATE pg_catalog."default",
    fid_klc integer,
    pa text[] COLLATE pg_catalog."default",
    wdpaid text[] COLLATE pg_catalog."default",
	iso2 text[] COLLATE pg_catalog."default",
    iso3 text[] COLLATE pg_catalog."default",
    country text[] COLLATE pg_catalog."default",
    ecoregion text[] COLLATE pg_catalog."default",
    ecoregion_id text[] COLLATE pg_catalog."default",
    region text[] COLLATE pg_catalog."default",
    signif text[] COLLATE pg_catalog."default",
    is_tfca boolean,
    is_copernicushs boolean
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE klc.klc_ris
    OWNER to biopama;

-- !!!! import file manually!!!!!!!!

-- change text[] to charcter varying
ALTER TABLE klc.klc_ris
	ALTER COLUMN pa TYPE character varying,
    ALTER COLUMN wdpaid TYPE character varying,
    ALTER COLUMN iso2 TYPE character varying,
    ALTER COLUMN iso3 TYPE character varying,
    ALTER COLUMN country TYPE character varying,
    ALTER COLUMN ecoregion TYPE character varying,
    ALTER COLUMN ecoregion_id TYPE character varying,
    ALTER COLUMN region TYPE character varying,
    ALTER COLUMN signif TYPE character varying;


-- add centroids
ALTER TABLE klc.klc_ris
	ADD COLUMN centroid_x numeric(36,5),
	ADD COLUMN centroid_y numeric(36,5);
	
UPDATE klc.klc_ris
	SET centroid_x = ST_X(ST_Centroid(geom)),
		centroid_y = ST_Y(ST_Centroid(geom));

-- copy to table klc_201909_proposal
DROP TABLE IF EXISTS klc.klc_201909_proposal;

CREATE TABLE klc.klc_201909_proposal AS
SELECT * FROM klc.klc_ris;

ALTER TABLE klc.klc_201909_proposal
    OWNER to biopama;
