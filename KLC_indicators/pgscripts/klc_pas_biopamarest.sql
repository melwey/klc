-- KLC pas: view
-- function that selects data from protected_sites.wdpa_acp (SELECT * FROM geo.mv_wdpa WHERE iso3 IN (SELECT iso3 FROM d6biopama.acp_countries))
DROP VIEW IF EXISTS d6biopama.v_klc_pas;
DROP VIEW IF EXISTS klc.v_klc_pas;
DROP FUNCTION IF EXISTS klc.f_klc_pas();
DROP FUNCTION IF EXISTS d6biopama.get_klc_pas(text);

CREATE FUNCTION klc.f_klc_pas() 
RETURNS TABLE(klc_id text,
			  wdpaid integer,
			  pa_name text,
			  iso3 text, 
			  desig_eng text,
			  desig_type text,
			  iucn_cat text,
			  area_klc_pa double precision,
			  pc_pa_in_klc double precision,
			  pc_klc_in_pa double precision)
AS $$
WITH klc_inter_pas AS(
SELECT 
	a.klc_id AS klc_id, 
  	b.wdpaid AS wdpaid,
	b.name AS pa_name, 
	b.iso3 AS iso3, 
	b.desig_eng,
	b.desig_type,
	b.iucn_cat,
	a.area_km2 as klc_area,
	ST_Area(ST_TRANSFORM (b.geom, 54009))/1000000 as pa_area,
	ST_COLLECT(ST_INTERSECTION(a.geom,b.geom)) as geom
FROM klc.klc_last AS a JOIN (SELECT * FROM geo.mv_wdpa WHERE iso3 IN (SELECT iso3 FROM d6biopama.acp_countries)) AS b ON ST_INTERSECTS(a.geom,b.geom)
GROUP BY klc_id, wdpaid, pa_name, iso3, klc_area, pa_area,desig_eng,desig_type,iucn_cat
ORDER BY klc_id
)
SELECT 
	klc_id,
	wdpaid,
	pa_name,
	iso3, 
	desig_eng,
	desig_type,
	iucn_cat,
	(ST_Area(ST_TRANSFORM (geom, 54009))/1000000) AS area_klc_pa,
	(ST_Area(ST_TRANSFORM (geom, 54009))/1000000)/pa_area*100 AS pc_pa_in_klc,
	(ST_Area(ST_TRANSFORM (geom, 54009))/1000000)/klc_area*100 AS pc_klc_in_pa
FROM klc_inter_pas
$$
LANGUAGE SQL
VOLATILE
;			

-- create table using function
DROP TABLE IF EXISTS klc.klc_pas CASCADE;
CREATE TABLE klc.klc_pas
 AS
 SELECT f_klc_pas.klc_id,
    f_klc_pas.wdpaid,
    f_klc_pas.pa_name,
    f_klc_pas.iso3,
    f_klc_pas.desig_eng,
    f_klc_pas.desig_type,
    f_klc_pas.iucn_cat,
    f_klc_pas.area_klc_pa,
    f_klc_pas.pc_pa_in_klc,
    f_klc_pas.pc_klc_in_pa
   FROM klc.f_klc_pas() f_klc_pas(klc_id, wdpaid, pa_name, iso3, desig_eng, desig_type, iucn_cat, area_klc_pa, pc_pa_in_klc, pc_klc_in_pa)
  WHERE f_klc_pas.pc_pa_in_klc > 0.5::double precision
  ORDER BY f_klc_pas.klc_id, f_klc_pas.pc_klc_in_pa DESC;

ALTER TABLE klc.klc_pas
    OWNER TO d6biopama;

-- create view that calls table
CREATE OR REPLACE VIEW d6biopama.v_klc_pas AS 
SELECT * FROM klc.klc_pas;

ALTER TABLE d6biopama.v_klc_pas
    OWNER TO d6biopama;
GRANT ALL ON TABLE d6biopama.v_klc_pas TO d6biopama;
GRANT SELECT ON TABLE d6biopama.v_klc_pas TO h05ibexro WITH GRANT OPTION;
-- GRANT access necessary for REST service to work

-- create function for REST service
CREATE OR REPLACE FUNCTION d6biopama.get_klc_pas(
  klc_id text DEFAULT NULL::text)
  RETURNS TABLE(
        klc_id text,
			  wdpaid integer,
			  pa_name text,
			  iso3 text, 
			  desig_eng text,
			  desig_type text,
			  iucn_cat text,
			  area_klc_pa numeric
        )
  LANGUAGE SQL
  VOLATILE
  COST 100
  ROWS 30
AS $$
SELECT klc_id, 
			  wdpaid,
			  pa_name,
			  iso3, 
			  desig_eng,
			  desig_type,
			  iucn_cat,
        cast(area_klc_pa as numeric(36, 2))  
FROM d6biopama.v_klc_pas
WHERE klc_id = $1 
$$
;

ALTER FUNCTION d6biopama.get_klc_pas(text)
    OWNER TO d6biopama;

GRANT EXECUTE ON FUNCTION d6biopama.get_klc_pas(text) TO PUBLIC;

GRANT EXECUTE ON FUNCTION d6biopama.get_klc_pas(text) TO h05ibexro WITH GRANT OPTION;

GRANT EXECUTE ON FUNCTION d6biopama.get_klc_pas(text) TO d6biopama;

COMMENT ON FUNCTION d6biopama.get_klc_pas(text)
    IS 'Returns protected areas covered by specific KLC, with wdpaid, name, iso3, designation, IUCN category and area covered by KLC in sq.km';

SELECT * FROM d6biopama.get_klc_pas('CAF_03') get_klc_pas;

-- when run from dopa-services, error:
--ProgrammingError('permission denied for schema klc
--LINE 10: FROM klc.v_klc_pas
-- QUERY:  
--         SELECT klc_id, wdpaid, pa_name, iso3, desig_eng, desig_type, iucn_cat, 
--         cast(area_klc_pa as numeric(36, 2)) FROM klc.v_klc_pas WHERE klc_id = $1  
-- CONTEXT:  SQL function \"get_klc_pas\" during startup\\n',)

-- I try again with the view in schema d6biopama, I get
-- ProgrammingError('permission denied for relation v_klc_pas\\nCONTEXT:  SQL function \"get_klc_pas\" statement 1\\n',)

-- So problem is definitely coing from the fact that the data are in klc schema.