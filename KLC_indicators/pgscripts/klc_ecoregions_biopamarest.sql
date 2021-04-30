-- KLC ecoregions: view
-- function that selects data from habitats_and_biotopes.ecoregions (the mv on geo has topology exceptions: Ring Self-intersection)
-- same error with local version of ecoregions. use _copy where geometries are made valid
DROP VIEW IF EXISTS klc.v_klc_ecoregions CASCADE;
DROP VIEW IF EXISTS d6biopama.v_klc_ecoregions CASCADE;
DROP FUNCTION IF EXISTS klc.f_klc_ecoregions() CASCADE;
DROP FUNCTION IF EXISTS d6biopama.get_klc_ecoregions(text) CASCADE;

CREATE FUNCTION klc.f_klc_ecoregions() 
RETURNS TABLE(klc_id text,
			  first_level_code integer,
			  first_level text,
			  area_klc_ecoregion double precision,
			  pc_ecoregion_in_klc double precision,
			  pc_klc_in_ecoregion double precision)
AS $$
WITH klc_inter_ecoregions AS(
SELECT 
	a.klc_id AS klc_id, 
	b.first_level_code AS first_level_code, 
	b.first_level AS first_level, 
	a.area_km2 as klc_area,
	b.sqkm as ecoregion_area,
	ST_COLLECT(ST_INTERSECTION(a.geom,b.geom)) as geom
FROM klc.klc_last AS a JOIN (SELECT * FROM habitats_and_biotopes.ecoregions_copy) AS b ON ST_Intersects(a.geom,b.geom)
GROUP BY klc_id, first_level_code, first_level, area_km2, sqkm  
ORDER BY klc_id
)
SELECT 
	klc_id,
	first_level_code,
	first_level,
	(ST_Area(ST_TRANSFORM (geom, 54009))/1000000) AS area_klc_ecoregion,
	((ST_Area(ST_TRANSFORM (geom, 54009))/1000000)/ecoregion_area*100) AS pc_ecoregion_in_klc,
	((ST_Area(ST_TRANSFORM (geom, 54009))/1000000)/klc_area*100) AS pc_klc_in_ecoregion
FROM klc_inter_ecoregions			
$$
LANGUAGE SQL
VOLATILE
;			
-- create table that calls function
DROP TABLE IF EXISTS klc.klc_ecoregions;
CREATE TABLE klc.klc_ecoregions AS 
SELECT * FROM klc.f_klc_ecoregions() f_klc_ecoregions
WHERE pc_klc_in_ecoregion > 0.5
ORDER BY klc_id, pc_klc_in_ecoregion DESC;

ALTER TABLE klc.klc_ecoregions
    OWNER TO d6biopama;

-- create view that calls table
CREATE OR REPLACE VIEW d6biopama.v_klc_ecoregions AS 
SELECT * FROM klc.klc_ecoregions;

ALTER TABLE d6biopama.v_klc_ecoregions
    OWNER TO d6biopama;
GRANT ALL ON TABLE d6biopama.v_klc_ecoregions TO d6biopama;
GRANT SELECT ON TABLE d6biopama.v_klc_ecoregions TO h05ibexro WITH GRANT OPTION;
-- GRANT access necessary for REST service to work

-- create get_klc_ecoregions for REST service
CREATE OR REPLACE FUNCTION d6biopama.get_klc_ecoregions(
  klc_id text DEFAULT NULL::text)
  RETURNS TABLE(
        klc_id text,
        first_level_code integer,
        first_level text,
        area_klc_ecoregion numeric
        )
  LANGUAGE SQL
  VOLATILE
  COST 100
  ROWS 20
AS $$
SELECT klc_id, first_level_code, first_level, cast(area_klc_ecoregion as numeric(36, 2))  
FROM d6biopama.v_klc_ecoregions
WHERE klc_id = $1 
$$
;

ALTER FUNCTION d6biopama.get_klc_ecoregions(text)
    OWNER TO d6biopama;

GRANT EXECUTE ON FUNCTION d6biopama.get_klc_ecoregions(text) TO PUBLIC;

GRANT EXECUTE ON FUNCTION d6biopama.get_klc_ecoregions(text) TO h05ibexro WITH GRANT OPTION;

GRANT EXECUTE ON FUNCTION d6biopama.get_klc_ecoregions(text) TO d6biopama;

COMMENT ON FUNCTION d6biopama.get_klc_ecoregions(text)
    IS 'Returns ecoregions covered by specific KLC with first_level_code (ecoregion code as used in DOPA), first_level (ecoregion name) and area covered by KLC in sq.km';


SELECT * FROM d6biopama.get_klc_ecoregions('CAF_03') get_klc_ecoregions