-- KLC countries: view
-- function that selects data from geo.mv_gaul_eez_dissolved
DROP VIEW IF EXISTS klc.v_klc_countries;
DROP FUNCTION IF EXISTS klc.f_klc_countries();
CREATE FUNCTION klc.f_klc_countries() 
RETURNS TABLE(klc_id text,
			  iso3 text,
			  country_name text,
			  area_klc_country double precision,
			  pc_country_in_klc double precision,
			  pc_klc_in_country double precision)
AS $$
WITH klc_inter_countries AS(
SELECT 
	a.klc_id AS klc_id, 
	b.iso3 AS iso3, 
	b.country_name AS country_name, 
	a.area_km2 as klc_area,
	b.sqkm as country_area,
	ST_COLLECT(ST_INTERSECTION(a.geom,b.geom)) as geom
FROM klc.klc_last AS a JOIN geo.mv_gaul_eez_dissolved AS b ON ST_INTERSECTS(a.geom,b.geom)
GROUP BY klc_id, iso3, country_name, area_km2, sqkm  
ORDER BY klc_id
)
SELECT 
	klc_id,
	iso3,
	country_name,
	(ST_Area(ST_TRANSFORM (geom, 54009))/1000000) AS area_klc_country,
	((ST_Area(ST_TRANSFORM (geom, 54009))/1000000)/country_area*100) AS pc_country_in_klc,
	((ST_Area(ST_TRANSFORM (geom, 54009))/1000000)/klc_area*100) AS pc_klc_in_country
FROM klc_inter_countries			
$$
LANGUAGE SQL
VOLATILE
;			
-- create table that calls function
DROP TABLE IF EXISTS klc.klc_countries CASCADE;
CREATE TABLE klc.klc_countries AS 
SELECT * FROM klc.f_klc_countries() f_klc_countries
ORDER BY klc_id, pc_klc_in_country DESC;
ALTER TABLE klc.klc_countries
    OWNER TO d6biopama;
--GRANT ALL ON TABLE klc.klc_countries TO d6biopama; not necessary
--GRANT ALL ON TABLE klc.klc_countries TO h05ibexro; not necessary

-- create view that calls table
CREATE OR REPLACE VIEW d6biopama.v_klc_countries AS --changed schema from klc to d6biopama
SELECT * FROM klc.klc_countries
ORDER BY klc_id, pc_klc_in_country DESC;
ALTER TABLE d6biopama.v_klc_countries
    OWNER TO d6biopama;
GRANT ALL ON TABLE d6biopama.v_klc_countries TO d6biopama;
GRANT SELECT ON TABLE d6biopama.v_klc_countries TO h05ibexro WITH GRANT OPTION;
-- REST service working only if GRANT access to h05ibexro

-- create get_klc_countries for REST service
CREATE OR REPLACE FUNCTION d6biopama.get_klc_countries(
  klc_id text DEFAULT NULL::text)
  RETURNS TABLE(
        klc_id text,
        iso3 text,
        country_name text,
        area_klc_country numeric
        )
  LANGUAGE SQL
  VOLATILE
  COST 100
  ROWS 10
AS $$
SELECT klc_id, iso3, country_name, cast(area_klc_country as numeric(36, 2))  
FROM d6biopama.v_klc_countries -- changed schema from klc to d6biopama -- changed view to table
WHERE klc_id = $1 
$$
;

ALTER FUNCTION d6biopama.get_klc_countries(text)
    OWNER TO d6biopama;

GRANT EXECUTE ON FUNCTION d6biopama.get_klc_countries(text) TO PUBLIC;

GRANT EXECUTE ON FUNCTION d6biopama.get_klc_countries(text) TO h05ibexro WITH GRANT OPTION;

GRANT EXECUTE ON FUNCTION d6biopama.get_klc_countries(text) TO d6biopama;

COMMENT ON FUNCTION d6biopama.get_klc_countries(text)
    IS 'Returns countries covered by specific iso3, name and area covered by KLC in sq.km';

SELECT * FROM d6biopama.get_klc_countries('CAF_03') get_klc_countries;