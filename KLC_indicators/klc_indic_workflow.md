# KLC_indicators workflow

The scripts used to develop the indicators need to be executed in the following order.

## Indicator creation
The indictaors have first to be calculated.

Indicators created on PostGIS use data stored on the biopamarest database hosted at the European Commission JRC, which is not accessible outside te internal network.

1. [klc_ecoregions_biopamarest.sql](https://github.com/melwey/klc/tree/master/KLC_indicators/pgscripts/klc_ecoregions_biopamarest.sql) creates a table with ecoregions coverage of KLCs. It depends on the KLC polygons and the marine and [terrestrial](https://www.worldwildlife.org/publications/terrestrial-ecoregions-of-the-world) ecoregions of the world. The marine ecoregions are the [Marine Ecoregions Of the World (MEOW)](https://www.worldwildlife.org/publications/marine-ecoregions-of-the-world-a-bioregionalization-of-coastal-and-shelf-areas) and the [Pelagic provinces of the world (PPOW)](http://data.unep-wcmc.org/datasets/38).

2. [klc_countries_biopamarest.sql](https://github.com/melwey/klc/tree/master/KLC_indicators/pgscripts/klc_countries_biopamarest.sql) creates a table with countries coverage of KLCs. It depends on the KLC polygons and country polygons. We use a merged layer of [GAUL](http://www.fao.org/geonetwork/srv/en/metadata.show?id=12691) and [EEZ](http://www.marineregions.org/downloads.php).

3. [klc_pas_biopamarest.sql](https://github.com/melwey/klc/tree/master/KLC_indicators/pgscripts/klc_pas_biopamarest.sql) creates a table with countries coverage of KLCs. It depends on KLC polygons and protected areas polygons. We use the latest WDPA available at [protectedplanet.net](https://protectedplanet.net/)

4. [klc_add_info.sql](https://github.com/melwey/klc/tree/master/KLC_indicators/pgscripts/klc_add_info) adds data from the above indicators to the KLC table that is then published on geoserver.

Other indicators are calculated on Google Earth Engine.

- [klc_gclc](https://github.com/melwey/klc/tree/master/KLC_indicators/gee/klc_gclc.js) can be directly executed on [Earth Engine code editor](https://code.earthengine.google.com/b93f5da17bb93f58b11ac3007ca09e83?noload=true). The analysis runs on the [Copernicus global land service Land Cover product](https://lcviewer.vito.be/)

## Indicators preparation

The outputs from GEE need some cleaning before being ingested in the postGIS database for publication.

- [klc_cglc_cleaning.R](https://github.com/melwey/klc/tree/master/KLC_indicators/Rcode/klc_cglc_cleaning.R) downloads the data saved on Google Drive and prepares them for import into PostGIS.

## Indicators publication

The KLC map with information added in klc_add.sql is uploaded on geoserver with [on_geoserver_vt.sql](https://github.com/melwey/klc/tree/master/KLC_indicators/pgscripts/on_geoserver_vt.sql) for visualisation on the BIOPAMA RIS.

Tables are created on the publication database for each indicator and the REST services created.

1. [klc_create_indic.sql](https://github.com/melwey/klc/tree/master/KLC_indicators/pgscripts/klc_create_indic.sql)

2. Import tables to database

3. Create functions:

  - [klc_ecoregions_biopama_api.sql](https://github.com/melwey/klc/tree/master/KLC_indicators/pgscripts/klc_ecoregions_biopama_api.sql)
  
  - [klc_countries_biopama_api.sql](https://github.com/melwey/klc/tree/master/KLC_indicators/pgscripts/klc_coutries_biopama_api.sql)
  
  - [klc_pas_biopama_api.sql](https://github.com/melwey/klc/tree/master/KLC_indicators/pgscripts/klc_pas_biopama_api.sql)
  
  - [klc_cglc_biopama_api.sql](https://github.com/melwey/klc/tree/master/KLC_indicators/pgscripts/klc_cglcs_biopama_api.sql)

