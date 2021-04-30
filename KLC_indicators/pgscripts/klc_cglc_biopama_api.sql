-- CGLC

-- add columns total area and percentages
ALTER TABLE klc.klc_cglc
	ADD COLUMN area numeric(36, 2);
UPDATE klc.klc_cglc
	SET area = (bare + crops + grass + moss + shrub + snow + tree + urban + water_permanent + water_seasonal);

ALTER TABLE klc.klc_cglc
	ADD COLUMN pc_bare numeric(36, 2),
	ADD COLUMN pc_crops numeric(36, 2),
	ADD COLUMN pc_grass numeric(36, 2),
	ADD COLUMN pc_moss numeric(36, 2),
	ADD COLUMN pc_shrub numeric(36, 2),
	ADD COLUMN pc_snow numeric(36, 2),
	ADD COLUMN pc_tree numeric(36, 2),
	ADD COLUMN pc_urban numeric(36, 2),
	ADD COLUMN pc_water_permanent numeric(36, 2),
	ADD COLUMN pc_water_seasonal numeric(36, 2);
	
UPDATE klc.klc_cglc
	SET pc_bare = (bare / area * 100),
		pc_crops = (crops / area * 100),
		pc_grass = (grass / area * 100),
		pc_moss = (moss / area * 100),
		pc_shrub = (shrub / area * 100),
		pc_snow = (snow / area * 100),
		pc_tree = (tree / area * 100),
		pc_urban = (urban / area * 100),
		pc_water_permanent = (water_permanent / area * 100),
		pc_water_seasonal = (water_seasonal / area * 100)
	WHERE area > 0;

	
-- create view that calls table
DROP FUNCTION IF EXISTS klc.api_klc_cglc(text);
DROP VIEW IF EXISTS klc.v_klc_cglc;

CREATE OR REPLACE VIEW klc.v_klc_cglc AS 
SELECT klc_id,
    pa,
    cast(year as integer),
    cast(bare as numeric(36, 2)),
    cast(crops as numeric(36, 2)),
    cast(grass as numeric(36, 2)),
    cast(moss as numeric(36, 2)),
    cast(shrub as numeric(36, 2)),
    cast(snow as numeric(36, 2)),
    cast(tree as numeric(36, 2)),
    cast(urban as numeric(36, 2)),
    cast(water_permanent as numeric(36, 2)),
    cast(water_seasonal as numeric(36, 2)),
	area,
    pc_bare,
    pc_crops,
    pc_grass,
    pc_moss,
    pc_shrub,
    pc_snow,
    pc_tree,
    pc_urban,
    pc_water_permanent,
    pc_water_seasonal
FROM klc.klc_cglc;

ALTER TABLE klc.v_klc_cglc
    OWNER TO biopama_api_user;

-- create function for REST service
CREATE OR REPLACE FUNCTION klc.api_klc_cglc(
  klc_id text DEFAULT NULL::text)
  RETURNS SETOF klc.v_klc_cglc
  LANGUAGE 'plpgsql'
  VOLATILE
  COST 100
  ROWS 20
AS $BODY$
#variable_conflict use_column             -- how to resolve conflicts
BEGIN
IF $1 is null THEN
	RETURN query 
	SELECT * FROM klc.v_klc_cglc;
ELSE
	RETURN query 
	SELECT * FROM klc.v_klc_cglc
	WHERE klc_id = $1;
END IF;
END
$BODY$
;

ALTER FUNCTION klc.api_klc_cglc(text)
    OWNER TO biopama_api_user;

COMMENT ON FUNCTION klc.api_klc_cglc(text)
    IS 'KLC Copernicus Global Land Service land cover. Analysis by M. Weynants in April 2021. Given KLC_ID, returns land cover classes coverage for year 2015 to 2019, inside protected areas (pa = true) and overall (pa = false), in sq.km and %';

SELECT * FROM klc.api_klc_cglc('WAF_01') api_klc_cglc;
