# klc
Key Landscapes for Conservation in Sub-Saharan Africa

Key Landscapes for Conservation (KLC) are areas recognised to be of global wildlife importance with intact ecosystems that are capable of sustaining wildlife populations in the face of increasing isolation from other similar areas (Larger Than Elephants - Inputs for EU strategic approach to wildlife conservation in Africa - Regional Analysis, European Commission, 2016).

## KLC_2015
Larger than Elephants was published in 2016.

In the framework of EU funded ACP programme [BIOPAMA](https://biopama.org) some coverage analyses were derived in 2018. The scripts are available in folder [KLC_2015](https://github.com/melwey/klc/tree/master/KLC_2015).

However the spatial polygons had not been drown to perform analyses, but were just indicative areas of interest. Deriving sound indicators demanded the redesign of the spatial layer.

## KLC_2019

In 2019 and 2020, following discussions with experts, the JRC proposed an update of the layer published in 2016.
The 2020 layer was created in QGIS with python.

Folder [KLC_2019](https://github.com/melwey/klc/tree/master/KLC_2019) holds the scripts used to create the update.


## KLC indicators
The 2020 layer was used to produce some coverage analyses and indicators to be published on the BIOPAMA Reference Information System (https://rris.biopama.org).

The indicators were computed in R, javaScipt (Google Earth Engine) or PostGIS.

For the coverage statistics for countries, ecoregions and individual protected areas (vector data), we used a PostgreSQL database with PostGIS.

For the statistics based on raster data, we used GEE o R package raster.

They are published as REST services on the BIOPAMA API (https://api.biopama.org)

Folder [KLC_indicators](https://github.com/melwey/klc/tree/master/KLC_indicators) holds the scripts used to create and publish the indicators.
