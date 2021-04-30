-- import newest file
-- do manually because I've no idea of how to do that!
-- convert clumn names to lower case
-- copy to klc_last
DROP TABLE IF EXISTS klc.klc_last;

CREATE TABLE klc.klc_last AS
SELECT * FROM klc.klc_20200921_proposal;

ALTER TABLE klc.klc_last
RENAME COLUMN "KLC_ID" to klc_id;
ALTER TABLE klc.klc_last
RENAME COLUMN "Area_km2" to area_km2;
ALTER TABLE klc.klc_last
RENAME COLUMN "KLC_name" to klc_name;
ALTER TABLE klc.klc_last
RENAME COLUMN "target_PAs" to target_pas;

-- fix invalid geometries
UPDATE klc.klc_last SET geom = ST_MakeValid(geom)
WHERE ST_IsValid(geom) = FALSE;

