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
    OWNER to biopama_api_user;

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

-- add comment
COMMENT ON TABLE klc.klc_ris
    IS 'KLCs for Sub-saharan Africa. Imported by M. Weynants on 11/05/2021.';

-- copy to table api_klc
DROP TABLE IF EXISTS klc.api_klc;

CREATE TABLE klc.api_klc AS
SELECT * FROM klc.klc_ris;

ALTER TABLE klc.api_klc
	DROP COLUMN geom,
	DROP COLUMN fid,
	DROP COLUMN fid_klc;

COMMENT ON COLUMN klc.api_klc.klc_id 
	IS 'KLC identifier (text)';
COMMENT ON COLUMN klc.api_klc.area_km2
	IS 'KLC area in sq.km (double precision)';
COMMENT ON COLUMN klc.api_klc.klc_name
	IS 'KLC name (text)';
COMMENT ON COLUMN klc.api_klc."Comments"
	IS 'Comments on the creation of the KLC (text)';
COMMENT ON COLUMN klc.api_klc.target_pas
	IS 'List of target/emblematic protected areas identifiers (WDPAID) (text)'; 
COMMENT ON COLUMN klc.api_klc.pa
	IS 'List of all protected areas intersecting the KLC (text)'; 
COMMENT ON COLUMN klc.api_klc.wdpaid
	IS 'List of all protected areas (WDPAID) intersecting the KLC (text)'; 
COMMENT ON COLUMN klc.api_klc.iso2
	IS 'List of all countries (identified by their ISO2 code) intersecting the KLC (text)';
COMMENT ON COLUMN klc.api_klc.iso3
	IS 'List of all countries (identified by their ISO3 code) intersecting the KLC (text)';
COMMENT ON COLUMN klc.api_klc.country
	IS 'List of all countries intersecting the KLC (text)';
COMMENT ON COLUMN klc.api_klc.ecoregion
	IS 'List of all ecoregions intersecting the KLC (text)';
COMMENT ON COLUMN klc.api_klc.ecoregion_id
	IS 'List of all ecoregions (identified by their first level code) intersecting the KLC (text)';
COMMENT ON COLUMN klc.api_klc.region
	IS 'List of all regions intersecting the KLC (text)';
COMMENT ON COLUMN klc.api_klc.signif
	IS 'Significance or main features of KLC (text)';
COMMENT ON COLUMN klc.api_klc.is_tfca
	IS 'Is the KLC an established Transfrontier Conservation Area? (boolean)';
COMMENT ON COLUMN klc.api_klc.is_copernicushs
	IS 'Is the KLC a Copernicus hotspot for which high resolution land cover is available? (boolean)';
COMMENT ON COLUMN klc.api_klc.centroid_x
	IS 'Longitude of KLC centroid';
COMMENT ON COLUMN klc.api_klc.centroid_y
	IS 'Latitude of KLC centroid';

-- add comment
COMMENT ON TABLE klc.api_klc
    IS 'KLCs for Sub-saharan Africa. Imported by M. Weynants on 11/05/2021. The geometries can be downloaded from the BIOPAMA Geonode: https://geonode-rris.biopama.org/layers/geonode:klc_201909_proposal#/';


ALTER TABLE klc.api_klc
    OWNER to biopama_api_user;