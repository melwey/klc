-- KLC pas: view
-- create view that calls table
CREATE OR REPLACE VIEW klc.v_klc_pas AS 
SELECT klc_id, 
			  wdpaid,
			  pa_name,
			  iso3, 
			  desig_eng,
			  desig_type,
			  iucn_cat,
              cast(area_klc_pa as numeric(36, 2)),
              cast(pc_klc_in_pa as numeric(36, 2)),
              cast(pc_pa_in_klc as numeric(36, 2))
FROM klc.klc_pas;

ALTER TABLE klc.v_klc_pas
    OWNER TO biopama_api_user;

-- create function for REST service
CREATE OR REPLACE FUNCTION klc.api_klc_pas(
  klc_id text DEFAULT NULL::text)
  RETURNS SETOF klc.v_klc_pas
  LANGUAGE 'plpgsql'
  VOLATILE
  COST 100
  ROWS 20
AS $BODY$
#variable_conflict use_column             -- how to resolve conflicts
BEGIN
IF $1 is null THEN
	RETURN query 
	SELECT * FROM klc.v_klc_pas;
ELSE
	RETURN query 
	SELECT * FROM klc.v_klc_pas
	WHERE klc_id = $1;
END IF;
END
$BODY$
;

ALTER FUNCTION klc.api_klc_pas(text)
    OWNER TO biopama_api_user;

COMMENT ON FUNCTION klc.api_klc_pas(text)
    IS 'KLC protected area coverage. Analysis by M. Weynants on 23/04/2021. Given KLC_ID, returns proetected areas covered by specific KLC with wdpaid, proetected area name, iso3 country code, designation, IUCN category, area covered by KLC and PA in sq.km, and percentages of KLC in PA and of PA in KLC ';

SELECT * FROM klc.api_klc_pas('CAF_03') api_klc_pas;
