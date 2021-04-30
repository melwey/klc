-- KLC ecoregions

-- create view that calls table
CREATE OR REPLACE VIEW klc.v_klc_ecoregions AS 
SELECT klc_id,
        first_level_code,
        first_level, 
		cast(area_klc_ecoregion as numeric(36, 3)), 
		cast(pc_klc_in_ecoregion as numeric(36, 2)), 
		cast(pc_ecoregion_in_klc as numeric(36, 2))   
FROM klc.klc_ecoregions;

ALTER TABLE klc.v_klc_ecoregions
    OWNER TO biopama_api_user;

-- create function api_klc_ecoregions for REST service
DROP FUNCTION IF EXISTS klc.api_klc_ecoregions(text);
CREATE OR REPLACE FUNCTION klc.api_klc_ecoregions(
  klc_id text DEFAULT NULL::text)
  RETURNS SETOF klc.v_klc_ecoregions
  LANGUAGE 'plpgsql'
  VOLATILE
  COST 100
  ROWS 20
AS $BODY$
#variable_conflict use_column             -- how to resolve conflicts
BEGIN
IF $1 is null THEN
	RETURN query 
	SELECT * FROM klc.v_klc_ecoregions;
ELSE
	RETURN query 
	SELECT * FROM klc.v_klc_ecoregions
	WHERE klc_id = $1;
END IF;
END
$BODY$
;

ALTER FUNCTION klc.api_klc_ecoregions(text)
    OWNER TO biopama_api_user;

COMMENT ON FUNCTION klc.api_klc_ecoregions(text)
    IS 'KLC ecoregions coverage. Analysis by M. Weynants on 23/04/2021. Given KLC_ID, returns ecoregions covered by specific KLC with first_level_code (ecoregion code as used in DOPA), first_level (ecoregion name), area covered by KLC in sq.km, percentage of KLC in ecoregion and percentage of ecoregion in KLC';


SELECT * FROM klc.api_klc_ecoregions('CAF_03') api_klc_ecoregions