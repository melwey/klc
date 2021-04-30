-- KLC countries: create REST service on biopama_api

-- create api_klc_countries for REST service
CREATE OR REPLACE VIEW klc.v_klc_countries AS 
  SELECT klc_id, 
		iso3, 
		country_name, 
		cast(area_klc_country as numeric(36, 3)), 
		cast(pc_klc_in_country as numeric(36, 2)), 
		cast(pc_country_in_klc as numeric(36, 2))  
	FROM klc.klc_countries;
ALTER TABLE klc.v_klc_countries
    OWNER TO biopama_api_user;
COMMENT ON VIEW klc.v_klc_countries
    IS 'KLC countries coverage. Analysis by M. Weynants on 23/04/2021. Given klc_id, returns countries covered by KLC : iso3, country name, area in sq.km, percentage of KLC in country and percentage of country in KLC';


DROP FUNCTION IF EXISTS klc.api_klc_countries(text);
CREATE OR REPLACE FUNCTION klc.api_klc_countries(
  klc_id text DEFAULT NULL::text)
  RETURNS SETOF klc.v_klc_countries
  LANGUAGE 'plpgsql'
  VOLATILE
  COST 100
  ROWS 10
AS $BODY$
#variable_conflict use_column             -- how to resolve conflicts
BEGIN
IF $1 is null THEN
	RETURN query 
	SELECT * FROM klc.v_klc_countries;
ELSE
	RETURN query 
	SELECT * FROM klc.v_klc_countries
	WHERE klc_id = $1;
END IF;
END
$BODY$;

ALTER FUNCTION klc.api_klc_countries(text)
    OWNER TO biopama_api_user;

COMMENT ON FUNCTION klc.api_klc_countries(text)
    IS 'KLC countries coverage. Analysis by M. Weynants on 23/04/2021. Given klc_id, returns countries covered by KLC : iso3, country name, area in sq.km, percentage of KLC in country and percentage of country in KLC';

SELECT * FROM klc.api_klc_countries('WAF_04') api_klc_countries;