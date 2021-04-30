-- KLC : add info to spatial layer
DROP TABLE IF EXISTS klc.klc_signif;
CREATE TABLE klc.klc_signif
(
    klc_id text COLLATE pg_catalog."default" NOT NULL,
    is_tfca boolean,
    is_copernicushs boolean,
    significance text[] COLLATE pg_catalog."default",
    CONSTRAINT klc_signif_pkey PRIMARY KEY (klc_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE klc.klc_signif
    OWNER to d6biopama;
COMMENT ON TABLE klc.klc_signif
    IS 'significance of KLCs';

-- import data from jrcbox
"C:\\Program Files (x86)\\pgAdmin 4\\v4\\runtime\\psql.exe" --command " "\\copy klc.klc_signif (klc_id, is_tfca, is_copernicushs, significance) FROM 'C:/Users/weyname/jrcbox/BIOPAMA/KLC_AF~1/data/KLC_SI~1.TXT' DELIMITER '|' CSV HEADER QUOTE '\"' ESCAPE '''';""
--------------
DROP TABLE IF EXISTS klc.klc_copy;

CREATE TABLE klc.klc_copy AS
SELECT * FROM klc.klc_last;

ALTER TABLE klc.klc_copy
ADD COLUMN iso3 text[],
ADD COLUMN ecoregion text[],
ADD COLUMN region text[],
ADD COLUMN signif text[],
ADD COLUMN is_tfca boolean,
ADD COLUMN is_copernicushs boolean;
-- iso3 country codes as array
-- get data from klc.v_klc_countries
UPDATE klc.klc_copy
SET iso3 = b.iso3
FROM (
	SELECT
	klc_id,
	ARRAY_AGG(iso3 ORDER BY iso3) AS iso3
	FROM (SELECT klc_id, iso3 FROM klc.klc_countries) AS a
	GROUP BY klc_id
	ORDER BY klc_id
	) AS b
WHERE klc_copy.klc_id = b.klc_id;

-- ecoregion as array
-- get data from klc.v_klc_ecoregions
UPDATE klc.klc_copy
SET ecoregion = b.ecoregion
FROM (
	SELECT
	klc_id,
	ARRAY_AGG(first_level ORDER BY first_level) AS ecoregion
	FROM (SELECT klc_id, first_level FROM klc.klc_ecoregions) AS a
	GROUP BY klc_id
	ORDER BY klc_id
	) AS b
WHERE klc_copy.klc_id = b.klc_id;

-- region ACP regions as array
-- create table with iso3 and region_code
DROP TABLE IF EXISTS klc.acp_countries;
CREATE TABLE klc.acp_countries AS
SELECT iso3, region FROM d6biopama.acp_countries;

ALTER TABLE klc.acp_countries
ADD COLUMN region_code text;

UPDATE klc.acp_countries
SET region_code = translate(lower(region), ' ', '_');

ALTER TABLE klc.acp_countries
DROP COLUMN region;

-- get region_code to klc table
UPDATE klc.klc_copy
SET region = region_code
FROM (SELECT 
	  klc_id, 
	  ARRAY_AGG(DISTINCT region_code ORDER BY region_code) AS region_code
	  FROM (
		 SELECT klc_id, a.iso3, region_code 
		 FROM klc.klc_countries AS a 
		 INNER JOIN LATERAL (
			 SELECT b.iso3, region_code 
			 FROM klc.acp_countries AS b 
			 WHERE a.iso3 = b.iso3
		 ) AS c ON TRUE 
		 GROUP BY klc_id, a.iso3, region_code
		 ORDER BY klc_id
	  ) AS d
	  GROUP BY klc_id
	 ) AS e 
WHERE klc_copy.klc_id = e.klc_id;

-- is_tfca: is there a signed treaty?
-- is_copernicushs: is there high resolution land cover (change) info available from Copernicus Hostspots?
-- signif add contextual info from Larger Than Elephants
-- join from klc_signif.
UPDATE klc.klc_copy
SET is_tfca = a.is_tfca, is_copernicushs = a.is_copernicushs, signif = a.significance
FROM (SELECT * FROM klc.klc_signif) AS a WHERE klc_copy.klc_id = a.klc_id;

SELECT * FROM klc.klc_copy