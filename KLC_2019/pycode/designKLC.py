# KLC definition according to Larger than elephants AND DEVCO suggestion of 50 km buffer
# results of days workshop with Conrad Aveling
import qgis.utils
from qgis.gui import *

import processing
import numpy as np
import os
# set current directory
os.chdir("E:/weyname/BIOPAMA/GIS/KLC_Africa/pyCode")

# Get the project instance
project = QgsProject.instance()
# set CRS to Mollweide to do the buffers
project.setCrs(QgsCoordinateReferenceSystem("EPSG:54009"))
# Draw layers with missing projection in project's CRS
settings = QSettings()
defaultProjValue = settings.value( "/Projections/defaultBehaviour", "prompt", type=str )
settings.setValue( "/Projections/defaultBehaviour", "useProject" )

# load PA
#wdpa = QgsVectorLayer("//ies-ud01/spatial_data/Original_Datasets/WDPA/archives/2019/WDPA_Feb2019_Public.gdb|layername=WDPA_poly_Feb2019","pa", "ogr")
wdpa = QgsVectorLayer("dbname=\'d6biopamarest\' host=pgsql96-srv1.jrc.org port=5432 sslmode=disable authcfg=xky3xl0 key=\'wdpaid\' srid=4326 type=MultiPolygon table=\"geo\".\"mv_wdpa\" (geom) sql=", "pa", "postgres")    
# problem with dopa wdpa: doesn't have proposed PAs that can be of interest here.
    
if not wdpa.isValid():
  print("PA layer failed to load!")

# select features that intersect with ssa
wdpa.selectByRect(QgsRectangle(QgsPointXY(-26,27),QgsPointXY(60,-37)),
    QgsVectorLayer.SetSelection)
# save selection to Mollweide
error = QgsVectorFileWriter.writeAsVectorFormat(
    wdpa,       # layer: QgsVectorLayer
    "../output/spatial_data/WDPA_May2019_poly_ssa_54009",         # fileName: str
    "utf-8",         # fileEncoding: str
    QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    "GPKG",       # driverName: str
    True             # onlySeleted: bool
    )
if error[0] != QgsVectorFileWriter.NoError:
    print("File not written!")
# remove old layer and load selection
project.removeMapLayer(wdpa)
# define projection
processing.run("qgis:assignprojection", {
    'INPUT':"../output/spatial_data/WDPA_May2019_poly_ssa_54009.gpkg|layername=WDPA_May2019_poly_ssa_54009",
    'CRS':'EPSG:54009',
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/WDPA_May2019_poly_ssa_54009.gpkg\' table=\"assigned_54009\" (geom) sql='})
wdpa = iface.addVectorLayer("../output/spatial_data/WDPA_May2019_poly_ssa_54009.gpkg|layername=assigned_54009", 
    "pa", "ogr")
if not wdpa:
  print("pa layer failed to load!")

# Other input layers:
# TFCA
tfca = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/tfca/sadc_TFCA_Boundaries_2017.shp", "tfca", "ogr")
# GROADS
groads = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/gROADS/uncompressed/gROADS_v1.gdb|layername=Global_Roads", "roads", "ogr")
# water bodies
# reproject africa Water bodies to Mollweide
waterBodies = QgsVectorLayer("E:\weyname\BIOPAMA\GIS\data\Original\rcmrd\africawaterbody.geojson", 'waterBodies', 'ogr')
error = QgsVectorFileWriter.writeAsVectorFormat(
    waterBodies,       # layer: QgsVectorLayer
    "../output/spatial_data/africawaterbody_54009",         # fileName: str
    "utf-8",         # fileEncoding: str
    QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    "GPKG",       # driverName: str
    )
project.removeMapLayer(waterBodies)
waterBodies = iface.addVectorLayer("../output/spatial_data/africawaterbody_54009.gpkg|layername=africawaterbody_54009", "waterBodies", "ogr")

# rivers
riv = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/HydroSHEDS/RIV/af_riv_15s/af_riv_15s.shp", "af_riv_15s", "ogr")
# hydro basins level 6
hybas6 = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/HydroSHEDS/hybas_af_lev01-06_v1c/hybas_af_lev06_v1c.shp", "hybas_af_lev06", "ogr")
hybas = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/HydroSHEDS/hybas_af_lev00_v1c/hybas_af_lev00_v1c.shp", "hybas_af_lev00", "ogr")

# countries
countries = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Processed/DOPA_PROCESSING_2018/dopa.gpkg|layername=countries", "countries", "ogr")
# gaul L2
gaul2 = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/GAUL/V2015/g2015_2014_2/g2015_2014_2.shp", "GAUL_2", "ogr")

# copernicus HotSpots
cop_klc = iface.addVectorLayer('dbname=\'d6copernicus\' host=pgsql96-srv1.jrc.org port=5432 key=\'id\' srid=4326 type=MultiPolygonZ table=\"public\".\"cop_klc\" (geom) user=d6copernicus password=ChangeMe! sql=', "cop_klc", "postgres")

# birdLife IBA
iba = QgsVectorLayer("//ies-ud01/spatia_data/Original_Datasets/RESTRICTED_IBAs/uncompressed/IBAs20150709\IbaMapGlobal_20150709.shp", "iba", "ogr")

# birdLife KBA
kba = QgsVectorLayer("//ies-ud01/spatia_data/Original_Datasets/RESTICTED_BIRDLIFE/RESTRICTED_KBAs/uncompressed/KBAsGlobal_2019_01\KbaMapGlobal_POL.shp", "kba", "ogr")

# global mangrove watch
gmw = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/wcmc_marine/GMW_001_GlobalMangroveWatch/01_Data/GMW_2010_v2.shp", "GMW", "ogr")
# WCMW seagrass
seagr = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/wcmc_marine/014_001_WCMC013-014_SeagrassPtPy2018_v6/01_Data/WCMC_013_014_SeagrassesPy_v6.shp", "seagrass", "ogr")

def getFieldsNames(layer):
    fields = []
    for field in layer.fields():
      fields = fields + [field.name()]
    return(fields)

def editAttribute(layer, fieldName, expression):
    #expression.prepare(layer.pendingFields())
    index = layer.dataProvider().fieldNameIndex(fieldName)
    layer.startEditing()
    for feature in layer.getFeatures():
        value = expression.evaluate()
        layer.changeAttributeValue(feature.id(), index, value)
    layer.commitChanges()

def area2Field(layer, fieldName):
    index = layer.dataProvider().fieldNameIndex(fieldName)
    layer.startEditing()
    for feature in layer.getFeatures():
        d = QgsDistanceArea()
        value = d.measurePolygon(feature.geometry().asPolygon()[0])
        layer.changeAttributeValue(feature.id(), index, value)
    layer.commitChanges()
    
# For each KLC, select PAs, buffer them. 
# buffer selection and fill holes
def buffer_selection(klc, layer = wdpa, buf = 50):
    # buffer 50 km following DEVCO's input (Philippe Mayaux 11/03/2019)
    print(layer.name())
    tmp = processing.run("native:buffer",{
        'INPUT':QgsProcessingFeatureSourceDefinition(layer.id(), True),
        'DISTANCE':buf*1000,
        'SEGMENTS':5,
        'END_CAP_STYLE':0,
        'JOIN_STYLE':0,
        'MITER_LIMIT':2,
        'DISSOLVE':True,
        'OUTPUT':'memory:'
        })
    # delete holes
    tmp1 = processing.run("native:deleteholes", {
        'INPUT':tmp['OUTPUT'],
        'MIN_AREA':0,
        'OUTPUT':'memory:'
        })
#    # drop attributes
#    tmp2 = processing.run("qgis:deletecolumn", {
#        'INPUT':tmp1['OUTPUT'],
#        'COLUMN':['fid','OBJECTID','WDPAID','WDPA_PID','PA_DEF','NAME','ORIG_NAME','DESIG','DESIG_ENG','DESIG_TYPE','IUCN_CAT','INT_CRIT','MARINE','REP_M_AREA','GIS_M_AREA','REP_AREA','GIS_AREA','NO_TAKE','NO_TK_AREA','STATUS','STATUS_YR','GOV_TYPE','OWN_TYPE','MANG_AUTH','MANG_PLAN','VERIF','METADATAID','SUB_LOC','PARENT_ISO3','ISO3','Shape_Length','Shape_Area'],
#        'OUTPUT':'memory:'})
    # deleteAttributes
    tmp1['OUTPUT'].dataProvider().deleteAttributes(tmp1['OUTPUT'].attributeList())
    # add attribute KLC ID
    output = processing.run("qgis:advancedpythonfieldcalculator", {
        'INPUT':tmp1['OUTPUT'],
        'FIELD_NAME':'KLC_ID',
        'FIELD_TYPE':2,
        'FIELD_LENGTH':13,
        'FIELD_PRECISION':0,
        'GLOBAL':'',
        'FORMULA':'value = \"' + klc + '\"',
        #'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"' + klc + '\" (geom) sql='
        'OUTPUT':'ogr:dbname=\'C:/Users/weyname/jrcbox/BIOPAMA/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"' + klc + '\" (geom) sql='
        })
    return output
 
# create dictionary with KLC name
KLC_name = {}
# create dictionary with target PAs for each KLC
KLC_PA = {}
# create dictionary with comments?
KLC_comments = {}
# additional layers required for map of KLC
KLC_addLayers = {}

### CAF_01: Cross River-Takamanda-Mt Cameroon-Korup (page 352)
KLC_name['CAF_01'] = "Cross River-Takamanda-Mt Cameroon-Korup"
# I add Kimbi-Fungom NP 146627, designated in 2015
# After discussing with Conrad: remove Faro (clip to border), add Afi river 36919, Cross river South FR 37010 , Oban group 37013, Cross River North FR 37009
# + add small FR and GR to make conection 37014, 37012, 36359, 354003, 11597, 36900, 369001, 36902, 36903, 36904, 36905, 36906, 36907, 36908, 36908, 36909, 36910, 36911, 36912, 36913, 36899, 300870
KLC_PA['CAF_01'] = (20299, 20058, 555547996, 555547994, 7873, 555548871, 146627, 36919, 37010, 37013, 37009)
wdpa.selectByExpression('"WDPAID" IN (20299, 20058, 555547996, 555547994, 7873, 555548871, 146627, 36919, 37010, 37013, 37009, 37014, 37012, 36359, 354003, 11597, 36900, 369001, 36902, 36903, 36904, 36905, 36906, 36907, 36908, 36908, 36909, 36910, 36911, 36912, 36913, 36899, 300870)', 
    QgsVectorLayer.SetSelection)
##  create polygons to fill holes
caf_01_sites = QgsVectorLayer("Polygon?crs=epsg:54009&field=fid:integer&field=OBJECTID:integer&field=WDPAID:integer&field=WDPA_PID:integer&field=PA_DEF:integer&field=NAME:string(120)&field=DESIG:string(120)&field=IUCN_CAT&index=yes",
    "caf_01_sites", "memory")
# add features
# south
fet = QgsFeature()
fet.setGeometry(QgsGeometry.fromPolygonXY([[
        QgsPointXY(890284, 602213), 
        QgsPointXY(898577, 586749),
        QgsPointXY(902761, 579776),
        QgsPointXY(922485, 549493),
        QgsPointXY(908937, 546505),
        QgsPointXY(907144, 568818),
        QgsPointXY(890409, 590136),
        QgsPointXY(885229, 600097)]]))
fet.setAttributes([NULL, NULL, NULL, NULL, NULL, "link South", "", ""])
caf_01_sites.dataProvider().addFeatures([fet])
# between Cross River south and Afi
fet = QgsFeature()
fet.setGeometry(QgsGeometry.fromPolygonXY([[
        QgsPointXY(883411, 757910),
        QgsPointXY(900146, 745159),
        QgsPointXY(890982, 735796),
        QgsPointXY(872454, 746355)]]))
fet.setAttributes([NULL, NULL, NULL, NULL, NULL, "link Cross South Afi", "", ""])
caf_01_sites.dataProvider().addFeatures([fet])
# between Cross River and Kashimbila
fet = QgsFeature()
fet.setGeometry(QgsGeometry.fromPolygonXY([[
        QgsPointXY(939195, 799349),
        QgsPointXY(956926, 805525),
        QgsPointXY(960512, 798552),
        QgsPointXY(946367, 787595)]]))
fet.setAttributes([NULL, NULL, NULL, NULL, NULL, "link Cross Kashimbila", "", ""])
caf_01_sites.dataProvider().addFeatures([fet])
# between Kimbi and Gashaka
fet = QgsFeature()
fet.setGeometry(QgsGeometry.fromPolygonXY([[
        QgsPointXY(1064571,865279),
        QgsPointXY(1062777, 857205),
        QgsPointXY(1070626, 849580),
        QgsPointXY(1085203, 849356),
        QgsPointXY(1101126, 853617),
        QgsPointXY(1102023, 871334),
        QgsPointXY(1097986, 880753),
        QgsPointXY(1082064, 880304)]]))
fet.setAttributes([NULL, NULL, NULL, NULL, NULL, "link Kimbi Gashaka", "", ""])
caf_01_sites.dataProvider().addFeatures([fet])
# copy selected wdpa to caf_01_sites
caf_01_sites.dataProvider().addFeatures(wdpa.selectedFeatures())
caf_01_sites.updateExtents()
#project.addMapLayer(caf_01_sites)
# write sites to gpkg
error = QgsVectorLayerExporter.exportLayer(caf_01_sites, "E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg", "ogr", QgsCoordinateReferenceSystem("EPSG:54009"), False, {"update":True, "overwrite" : True, "driverName" : 'GPKG', "layerName":"CAF_01_sites"})
# exportLayer(layer: QgsVectorLayer, uri: str, providerKey: str, destCRS: QgsCoordinateReferenceSystem, onlySelected: bool = False, options: Dict[str, Any] = {}, feedback: QgsFeedback = None)
if error[0] != QgsVectorLayerExporter.NoError:
    print("File not written!")

# select all features and run buffer
caf_01_sites.selectAll()
tmp = buffer_selection("CAF_01", layer=caf_01_sites, buf=15)
project.addMapLayer(tmp['OUTPUT'])
# clip to Faro.
# select Faro
wdpa.selectByExpression('"WDPAID" IN (1241)', 
    QgsVectorLayer.SetSelection)
# overlay CAF_01 and Faro. Difference.
tmp1 = processing.run("native:difference", {
    'INPUT':tmp['OUTPUT'].id(),
    'OVERLAY':QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'OUTPUT':'TEMPORARY_OUTPUT'
    })
## save to gpkg
#error = QgsVectorLayerExporter.exportLayer(tmp1['OUTPUT'], "E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg", "ogr", QgsCoordinateReferenceSystem("EPSG:54009"), False, {"update":True, "overwrite" : True, "driverName" : 'GPKG', "layerName":"CAF_01"})
## exportLayer(layer: QgsVectorLayer, uri: str, providerKey: str, destCRS: QgsCoordinateReferenceSystem, onlySelected: bool = False, options: Dict[str, Any] = {}, feedback: QgsFeedback = None)
#if error[0] != QgsVectorLayerExporter.NoError:
#    print("File not written!")
## TO DO: would be better to clean still the polygon...
#
## Copernicus Hotspot Cross River is larger than mine (20 km rather than 15) and includes Faro.
# TO DO: intersect with Copernicus version
# select cop_klc CAF_01 and reproject to 54009
cop_klc.selectByExpression("\"klc_code\" = 'CAF_01'", QgsVectorLayer.SetSelection)
# save selection to Mollweide
tmp2 = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':'memory:'
    })
# modify ring0, vertex 275 so that it is equal to ring 1 vertex 1221
tmp2['OUTPUT'].startEditing()
iVertex = 275
######
# moveVertex(self, x: float, y: float, atFeatureId: int, atVertex: int)
tmp2['OUTPUT'].moveVertex(900820, 600226, 1,iVertex)
tmp2['OUTPUT'].commitChanges()
tmp2_diss = processing.run("native:dissolve", {
    'INPUT':tmp2['OUTPUT'],
    'OUTPUT':"memory:"
    })
tmp3 = processing.run("native:intersection", {
    'INPUT':tmp1['OUTPUT'],
    'OVERLAY':tmp2_diss['OUTPUT'],
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"CAF_01\" (geom) sql='
    })
#####
KLC_comments['CAF_01'] = "There is a Copernicus Hotspot for which land cover has been mapped, but we kept a slightly smaller buffer around the target PAs. Faro NP (CMR) has been moved to KLC CAF_17."

### CAF_02: Greater Virunga ( page 262; page 157)
KLC_name['CAF_02'] = "Greater Virunga"
#• Virunga WHS/NP (CD) 2017
#• Volcans NP (RW) 863
#• Mgahinga NP (UG) 313109
#• Queen Elizabeth NP (UG) 957
#• Bwindi WHS/NP (UG) 18437/61609
#• Semuliki NP (UG) 40042
#• Ruwenzori WHS/NP (UG) 18438
#• Kibale NP (UG) 40002
#• Kasyoha-Kitomi FR (UG) 315143
#• Kalinzu-Maramgambo FR (UG) 40027
#• Kayumbura WR (UG) 1446
# add FR North Maramba 315408, south Maramba 317282, Rutshuru 20331,  Fort Portal to fill hole 40051
KLC_PA['CAF_02'] =  (2017, 863, 313109, 957, 61609, 40042, 61608, 40002, 18438, 40002, 315143, 40027, 1446)
#wdpa.selectByExpression('"WDPAID" IN (2017, 863, 313109, 957, 61609, 40042, 61608, 40002, 18438, 40002, 315143, 40027, 1446, 315408, 317282, 20331, 40051)', 
#    QgsVectorLayer.SetSelection)
#buffer_selection("CAF_02", buf = 10) # OK
# Use polygon from Copernicus Hotspots for compatibility
cop_klc.selectByExpression("\"klc_code\" = 'CAF_02'", QgsVectorLayer.SetSelection)
# save selection to Mollweide
tmp = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"CAF_02\" (geom) sql='
    })
KLC_comments['CAF_02'] = "For this KLC, we use the Copernicus Hotspot for which land cover has been mapped."

### CAF_03: TRIDOM/TNS (page 262). need to fill (big) holes in the middle of KLC
KLC_name['CAF_03'] = "TRIDOM/TNS"
#• Minkébé NP (GA) 72324
#• Ivindo NP (GA) 303873
#• Mwagne NP (GA) 303878
#• Dja WR (CM) WHS in Danger 17758
#• Nki NP (CM) 30675
#• Boumba Bek NP (CM) 308624
#• Lac Lobeke NP (CM) part of TNS WHS 1245
#• Odzala NP (CG) 643
#• Nouabalé-Ndoki NP (CG) part of TNS WHS 72332
#• Ntoukou-Pikounda NP (CG) 354010
#• Lac Tele CR (CG) 313494
#• Dzanga-Ndoki NP (CF) part of TNS WHS 31458
#• Dzanga SR (CF) 31459
#• Lopé NP (GA) WHS (natural and cultural) 303875
# add sites 308636, 555547997, 555622119, 903089, 109035, 300342 to fill holes
KLC_PA['CAF_03'] = (72324, 303873, 303878, 17758, 30674, 308624, 1245, 643, 72332, 354010, 313494, 31458, 31459, 303875)
wdpa.selectByExpression('"WDPAID" IN (72324, 303873, 303878, 17758, 30674, 308624, 1245, 643, 72332, 354010, 313494, 31458, 31459, 303875, 308636, 555547997, 555622119, 903089, 109035, 300342)', 
    QgsVectorLayer.SetSelection)
#buffer_selection("CAF_03", buf = 20)
caf03_buf = processing.run("native:buffer",{
        'INPUT':QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
        'DISTANCE':20*1000,
        'SEGMENTS':5,
        'END_CAP_STYLE':0,
        'JOIN_STYLE':0,
        'MITER_LIMIT':2,
        'DISSOLVE':False,
        'OUTPUT':'memory:'
        })
    
# delete attributes
caf03_buf['OUTPUT'].dataProvider().deleteAttributes(caf03_buf['OUTPUT'].attributeList())
# add attributes
caf03_buf['OUTPUT'].dataProvider().addAttributes(
    [QgsField("id",QVariant.Int),
    QgsField("desc",QVariant.String),
    QgsField("KLC_ID", QVariant.String)])
caf03_buf['OUTPUT'].updateFields()
# set KLC_ID to "CAF_03"
for fet in caf03_buf['OUTPUT'].getFeatures():
    fet.setAttributes([NULL, 'PA','CAF_03'])
    caf03_buf['OUTPUT'].updateFeature(fet)
project.addMapLayer(caf03_buf['OUTPUT'])
### !! not working !! done manually in Attribute table

# create link sites using roads. buffer on one side.
groads.selectByExpression('"OBJECTID" IN (59850, 124577, 235873, 154005, 61698, \
    61330, 218881, 216354, 102518, 142260, \
    132274, 43592, 124889, 165426, 12131, 201093, 39325, 132476, 115816,\
    64842, 172798, 85554, 33226, 146546, 147065, 234100, 87514, 24023, 156532, \
    45766,  214730, 96000, 111703, 95796, 202630, 5600, 110561, 174013, 41849, \
    145142, 168102, 175935, \
    94286, 185236, 206445, 230813, 45997, 115329, 85992, 59149, 93314, 176751,\
    169120, 131008, 139537, 61458, 218842)', 
    QgsVectorLayer.SetSelection)
# buffer
tmp = processing.run("qgis:buffer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(groads.id(), True),
    'DISTANCE':0.0001, # degrees
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':True,
    'OUTPUT':'memory:'
    })
# reproject selected features to 54009
tmp1 = processing.run("native:reprojectlayer", {
    'INPUT': tmp['OUTPUT'], #QgsProcessingFeatureSourceDefinition(groad.id(), True),
    'TARGET_CRS': 'EPSG:54009',
    'OUTPUT': 'memory:'})
#project.addMapLayer(tmp1['OUTPUT'])
# remove attributes
tmp2 = processing.run("qgis:deletecolumn", {
        'INPUT':tmp1['OUTPUT'],
        'COLUMN':getFieldsNames(tmp1['OUTPUT']),
        'OUTPUT':'memory:'})
# add attributes
tmp2['OUTPUT'].dataProvider().addAttributes(
    [QgsField("id",QVariant.Int),
    QgsField("desc",QVariant.String),
    QgsField("KLC_ID", QVariant.String)])
tmp2['OUTPUT'].updateFields()
# update current feature field KLC_ID 
# !!! not working !!!!
for fet in tmp2['OUTPUT'].getFeatures():
    fet.setAttributes([NULL, "roads","CAF_03"])
    tmp2['OUTPUT'].updateFeature(fet)
project.addMapLayer(tmp2['OUTPUT'])
# !!! not working !!!! Done manually in Attribute Table

# add features
# between Ntokou and Lac Télé
fet1 = QgsFeature()
fet1.setGeometry(QgsGeometry.fromPolygonXY([[
        QgsPointXY(1676983, 89496),
        QgsPointXY(1697712, 82335),
        QgsPointXY(1697335, 85350),
        QgsPointXY(1672461, 99295)]]))
fet1.setAttributes([NULL, "between Ntokou and Lac Télé","CAF_03"])
fet2 = QgsFeature()
# between Lac Télé and Sangha
fet2.setGeometry(QgsGeometry.fromPolygonXY([[
        QgsPointXY(1680646,254984),
        QgsPointXY(1681399,244808),
        QgsPointXY(1683284,239155),
        QgsPointXY(1687430,229733),
        QgsPointXY(1694967,224833),
        QgsPointXY(1697229,221064),
        QgsPointXY(1685922,226718),
        QgsPointXY(1679892,240663),
        QgsPointXY(1677631,248577),
        ]
        ]))
fet2.setAttributes([NULL, "between Lac Télé and Sangha","CAF_03"])
tmp2['OUTPUT'].dataProvider().addFeatures([fet1,fet2])
project.addMapLayer(tmp2['OUTPUT'])

# merge vectorlayers
tmp3 = processing.run("native:mergevectorlayers", {
    'LAYERS':[tmp2['OUTPUT'], caf03_buf['OUTPUT']],
    'CRS': "EPSG:54009",
    'OUTPUT':"memory:"})
project.addMapLayer(tmp3['OUTPUT'])
# multipart to singleparts
tmp4 = processing.run("native:multiparttosingleparts", {
    'INPUT': tmp3['OUTPUT'],
    'OUTPUT': "memory:"
    })
# dissolve
tmp5 = processing.run("native:dissolve", {
    'INPUT': tmp4['OUTPUT'],
    'FIELD': "KLC_ID",
    'OUTPUT': "memory:"})
project.addMapLayer(tmp5['OUTPUT'])
# fill holes
tmp6 = processing.run("native:deleteholes", {
    'INPUT': tmp5['OUTPUT'],
    'MIN_AREA':0,
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"CAF_03\" (geom) sql='
    })
project.addMapLayer(tmp6['OUTPUT'])    
# 
# original KLC OK, just need to be refined on the edges.
# DONE: follow roads
KLC_comments['CAF_03'] = "We took a 20 km buffer around the target PAs and joined them following the roads."

# CAF_04: Gamba-Mayumba-Conkouati (page 262)
KLC_name['CAF_04_SAF_11'] =  "Gamba-Mayumba-Conkouati-Maiombe"
# on the North, put a 20 km
KLC_PA['CAF_04_SAF_11'] = (303874, 303877, 301850, 313401, 28846)
#wdpa.selectByExpression('"WDPAID" IN (303874, 303877, 301850, 313401, 28846)', 
#    QgsVectorLayer.SetSelection)
#buffer_selection("CAF_04_20", buf=20)
# TO DO: merge with SAF_11, including the TFCA.
# Investigate on why there was a lump on the East of Monts Doudou included. SEE EMAIL.
# Conrad has contected WWF. They work with Compagnie Bois du Gabon which is FSC certified and Olam Palm Oil that are RSPO
# get data from WRI. but only available as arcgis MapServer. Digitalize

# RSPO_oil_palm.selectByExpression("Group" = 'Olam International Ltd.')
RSPO = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/KLC/CAF_04_Gamba/Olam_RSPO.gpkg|layername=Olam_RSPO", "Olam_RSPO", "ogr")
# Managed_forests.selectByExpression("Group" = 'CBG')
CBG =  QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/KLC/CAF_04_Gamba/CBG_FSC.gpkg|layername=CBG_FSC", "CBG_FSC", "ogr")
CBG_buf = processing.run("qgis:buffer", {
    'INPUT':CBG,
    'DISTANCE':2500, # meters
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':False,
    'OUTPUT':'memory:'
    })
# CAPG 

wdpa.selectByExpression('"WDPAID" IN ( 303874, 303877, 301850, 313401, 28846, \
    28847, 28844, 28840, 28845,\
    555512071, 555512069, 37044)', 
    QgsVectorLayer.SetSelection)
tmp_wdpa = processing.run("qgis:buffer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'DISTANCE':10000, # meters
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':False,
    'OUTPUT':'memory:'
    })
    
tfca_maiombe = processing.run('native:extractbyexpression', {
    'INPUT':tfca,
    'EXPRESSION': '"ABBR" = \'Maiombe TFCA\'',
    'OUTPUT':"memory:"
    })

# use buffer around river to connect Mangrove patch to TFCA AND RSPO to CBG
riv.selectByExpression('"ARCID" IN (573399, 573797, 574211, 574323, 574985, \
                        538127, 538254)', 
    QgsVectorLayer.SetSelection)
# reproject and buffer
# reproject selected features to 54009
tmp = processing.run("native:reprojectlayer", {
    'INPUT': QgsProcessingFeatureSourceDefinition(riv.id(), True),
    'TARGET_CRS': 'EPSG:54009',
    'OUTPUT': 'memory:'})
tmp1 = processing.run("qgis:buffer", {
    'INPUT':tmp['OUTPUT'],
    'DISTANCE':2500, # meters
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':False,
    'OUTPUT':'memory:'
    })

# merge selected features from layers
tmp2 = processing.run("native:mergevectorlayers", {
    'LAYERS':[tmp1['OUTPUT'],
        tfca_maiombe['OUTPUT'],
        tmp_wdpa['OUTPUT'],
        CBG_buf['OUTPUT'],
        RSPO],
    'CRS': "EPSG:54009",
    'OUTPUT':"memory:"})
project.addMapLayer(tmp2['OUTPUT'])
# remove all attributes and add KLC_ID
tmp3 = processing.run("qgis:deletecolumn", {
        'INPUT':tmp2['OUTPUT'],
        'COLUMN':getFieldsNames(tmp2['OUTPUT']),
        'OUTPUT':'memory:'})
tmp3['OUTPUT'].dataProvider().addAttributes([QgsField("KLC_ID", QVariant.String)])
tmp3['OUTPUT'].setDefaultValueDefinition(0, QgsDefaultValue("CAF_04_SAF_11", True))
tmp3['OUTPUT'].updateFields()
project.addMapLayer(tmp3['OUTPUT'])

### Polygons do not all touch. Maybe useful to make larger buffer on wdpa and CBG?!!!
# dissolve
tmp4 = processing.run("native:dissolve", {
    'INPUT': tmp3['OUTPUT'],
    'OUTPUT': "memory:"})
project.addMapLayer(tmp4['OUTPUT'])
# fill holes
tmp5 = processing.run("native:deleteholes", {
    'INPUT': tmp4['OUTPUT'],
    'MIN_AREA':0,
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"CAF_04_SAF_11\" (geom) sql='
    })
project.addMapLayer(tmp5['OUTPUT'])    
# Done: merge CAF_04 (including RSPO and FSC concessions in Gabon) and SAF_11 (including Maiombe mangrove (COD and AGO) through TFCA Maiombe
KLC_comments['CAF_04_SAF_11'] = "We merged CAF_04 and SAF_11. Besides the target PAs (20 km buffer), we included forest \
concessions in Gabon where WWF works with Compagnie Bois du Gabon which is FSC certified and Olam Palm Oil that \
are RSPO (2.5 km buffer) and the Maiombe mangrove (COD and AGO) through the Maiombe TFCA."
KLC_addLayers['CAF_04_SAF_11'] = [
'QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/KLC/CAF_04_Gamba/Olam_RSPO.gpkg|layername=Olam_RSPO", "Olam RSPO", "ogr")',
'QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/KLC/CAF_04_Gamba/CBG_FSC.gpkg|layername=CBG_FSC", "CBG FSC", "ogr")'
]

# CAF_05: Garamba-Latot_Bili Uere-Chinko (page 263)
KLC_name['CAF_05'] = "Garamba-Latot_Bili Uere-Chinko"
#wdpa.selectByExpression('"WDPAID" IN (4327, 20324, 903, 10737, 2259)', 
#    QgsVectorLayer.SetSelection)
#buffer_selection("CAF_05")
## Conrad is not keen on including Southern (South Sudan)
## Conrad is looking for a shpaefile for Chinko (which is larger than just Zemongo)
## keep Southern, include Bomu as buffer, as well as Bangangai, Bire Kapatuos, etc.
KLC_PA['CAF_05'] = (4327, 20324, 903, 10737, 2259)
#wdpa.selectByExpression('"WDPAID" IN (903, 4327, 20324, 10737, 2259, 555512073, 555512064, 1370, 555583105, 1377, 20327)', 
#    QgsVectorLayer.SetSelection)
#buffer_selection("CAF_05_20", buf=20)
# TO DO: see Conrad email. Include Chinko + generous buffer to the North of it.
Chinko = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/KLC/Chinko_SIG_V2/Occupation du sol/Chinko_Conservation_Area.shp", "Chinko", "ogr")
cop_klc.selectByExpression('"klc_code" = \'CAF_05\'')
# fill holes
tmp = processing.run("native:deleteholes", {
    'INPUT': QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),
    'MIN_AREA':0,
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"CAF_05\" (geom) sql='
    })
project.addMapLayer(tmp['OUTPUT'])    
# Done: take Copernicus KLC
KLC_comments['CAF_05'] = "For this KLC, we use the Copernicus Hotspot for which land cover has been mapped. The Chinko conservation area is not in the WDPA, but is located West of Zemongo."
KLC_addLayers['CAF_05'] = ['QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/KLC/Chinko_SIG_V2/Occupation du sol/Chinko_Conservation_Area.shp", "Chinko Conservation Area", "ogr")']

# CAF_06: Manovo-Gounda-St Floris -Bamingui-Bangoran (page 263). I add Ouandji-Vakaga Faunal Reserve 2260
KLC_name['CAF_06'] = "Manovo-Gounda-St Floris -Bamingui-Bangoran"
## add faunal and private reserves around Bamingi-Bangoran NP (2262, 2265, 2257) and around Manova-Gounda-Saint Floris NP (2260, 2555)
## Conrad: add André Félix NP 2258 and Yata-Ngaya FR 2261
## add Aouk (in Chad) to be sure to go up to the border)
KLC_PA['CAF_06'] = (2256, 639, 301830)
#wdpa.selectByExpression('"WDPAID" IN (2256, 639, 301830, 2262, 2265, 2257, 2260, 2555, 2258, 2261, 555558303)', 
#    QgsVectorLayer.SetSelection)
## create memory layer with sites to be included
#caf_06_sites = QgsVectorLayer("Polygon?crs=epsg:54009&field=fid:integer&field=OBJECTID:integer&field=WDPAID:integer&field=WDPA_PID:integer&field=PA_DEF:integer&field=NAME:string(120)&field=DESIG:string(120)&field=IUCN_CAT&index=yes",
#    "caf_06_sites", "memory")
## add features
#fet = QgsFeature()
#fet.setGeometry(QgsGeometry.fromPolygonXY([[QgsPointXY(2256068, 1149750),
#        QgsPointXY(2263730, 1131874),
#        QgsPointXY(2267135, 1119957),
#        QgsPointXY(2263730, 1100378),
#        QgsPointXY(2263730, 1089312),
#        QgsPointXY(2262027, 1074841),
#        QgsPointXY(2262027, 1067180),
#        QgsPointXY(2273093, 1067180),
#        QgsPointXY(2287564, 1069733),
#        QgsPointXY(2288416, 1081651), 
#        QgsPointXY(2287564, 1098676),
#        QgsPointXY(2288416, 1108890), 
#        QgsPointXY(2293523, 1125064), 
#        QgsPointXY(2287564, 1137833), 
#        QgsPointXY(2280754, 1142940), 
#        QgsPointXY(2275647, 1153155),
#        QgsPointXY(2256068, 1149750)]]))
#fet.setAttributes([NULL, NULL, NULL, NULL, NULL, "link East 2", "", ""])
#caf_06_sites.dataProvider().addFeatures([fet])
## copy selected wdpa to caf_06_sites
#caf_06_sites.dataProvider().addFeatures(wdpa.selectedFeatures())
#caf_06_sites.updateExtents()
##project.addMapLayer(caf_06_sites)
## write sites to gpkg
#error = QgsVectorLayerExporter.exportLayer(caf_06_sites, "E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg", "ogr", QgsCoordinateReferenceSystem("EPSG:54009"), False, {"update":True, "overwrite" : True, "driverName" : 'GPKG', "layerName":"CAF_06_sites"})
## exportLayer(layer: QgsVectorLayer, uri: str, providerKey: str, destCRS: QgsCoordinateReferenceSystem, onlySelected: bool = False, options: Dict[str, Any] = {}, feedback: QgsFeedback = None)
#if error[0] != QgsVectorLayerExporter.NoError:
#    print("File not written!")
#
## select all features and run buffer
#caf_06_sites.selectAll()
#tmp = buffer_selection("CAF_06", layer = caf_06_sites, buf = 20) # OK but fill in the indents on the North and South-east and clip to the border.
##project.addMapLayer(tmp['OUTPUT'])
#### clip to border
### select CAF
#countries = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Processed/DOPA_PROCESSING_2018/dopa.gpkg|layername=countries", "countries", "ogr")
#countries.selectByExpression('"iso3" = \'CAF\'', QgsVectorLayer.SetSelection)
### intersection
#tmp1 = processing.run("native:intersection", {
#    'INPUT':tmp['OUTPUT'].id(),#'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=CAF_06',
#    'OVERLAY':QgsProcessingFeatureSourceDefinition(countries.id(), True),
#    'INPUT_FIELDS':['KLC_ID'],'OVERLAY_FIELDS':['iso3'],
#    'OUTPUT':'TEMPORARY_OUTPUT'})
### load layer
##project.addMapLayer(tmp1['OUTPUT'])
### write output to CAF_06
#error = QgsVectorLayerExporter.exportLayer(tmp1['OUTPUT'], "E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg", "ogr", QgsCoordinateReferenceSystem("EPSG:54009"), False, {"update":True, "overwrite" : True, "driverName" : 'GPKG', "layerName":"CAF_06"})
## exportLayer(layer: QgsVectorLayer, uri: str, providerKey: str, destCRS: QgsCoordinateReferenceSystem, onlySelected: bool = False, options: Dict[str, Any] = {}, feedback: QgsFeedback = None)
#if error[0] != QgsVectorLayerExporter.NoError:
#    print("File not written!")
## TO DO: create a single transboundary KLC joining this with Zakouma (CAF_18) through Anouk
# BUT CAF_06 already mapped in Copernicus Hotspots, so use italic
cop_klc.selectByExpression("\"klc_code\" = 'CAF_06'", QgsVectorLayer.SetSelection)
# save selection to Mollweide
tmp = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"CAF_06\" (geom) sql='
    })
# Done: Copernicus HS
KLC_comments['CAF_06'] = "For this KLC, we use the Copernicus Hotspot for which land cover has been mapped. "


# CAF_07: Salonga (page 263). There's a shift between the limits of the WHS 10906 (shifted 18 km towards NNW) and the NP 478292 compared to natural features from Google/Bing imagery
KLC_name['CAF_07'] = "Salonga"
KLC_PA['CAF_07']=(478292)
#wdpa.selectByExpression('"WDPAID" IN (478292)', 
#    QgsVectorLayer.SetSelection)
#buffer_selection("CAF_07_20", buf=20) #OK button# TO DO: fill in the indent on the North West.
cop_klc.selectByExpression("\"klc_code\" = 'CAF_07'", QgsVectorLayer.SetSelection)
# save selection to Mollweide
tmp = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"CAF_07\" (geom) sql='
    })
# Done: Copernicus HS
KLC_comments['CAF_07'] = "For this KLC, we use the Copernicus Hotspot for which land cover has been mapped. "

# CAF_08: Okapi (page 263)
KLC_name['CAF_08'] = "Okapi"
KLC_PA['CAF_08']=(37043)
wdpa.selectByExpression('"WDPAID" IN (37043)', 
    QgsVectorLayer.SetSelection)
#buffer_selection("CAF_08_10", buf=10)
tmp_wdpa = processing.run("qgis:buffer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'DISTANCE':20000, # meters
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':False,
    'OUTPUT':'memory:'
    })
# include town of Mambasa.
# WCS is working in an area North East of the park, which could be included.
# TO DO: look for info on that area. Conrad will get back to me on that.
# Concessions Forestières de Communauté Locale (CFCL) under creation with WCS 
# must be included: Andikau (East-North East), Andibuta (East, just North of Mambasa), 
# Bafwakoa (West). Create layer with sites.
caf_08_sites = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/KLC/CAF_08_Okapi/WCS_CFCL_mela.gpkg|layername=WCS_CFCL_mela", "caf_08_sites", "ogr")
# merge layers and dissolve
tmp2 = processing.run("native:mergevectorlayers", {
    'LAYERS':[tmp_wdpa['OUTPUT'],
        caf_08_sites],
    'CRS': "EPSG:54009",
    'OUTPUT':"memory:"})
project.addMapLayer(tmp2['OUTPUT'])
# remove all attributes and add KLC_ID
#if tmp2['OUTPUT'].dataProvider().capabilities() & QgsVectorDataProvider.DeleteAttributes:
res = tmp2['OUTPUT'].dataProvider().deleteAttributes(list(range(0, len(getFieldsNames(tmp2['OUTPUT'])))))
res = tmp2['OUTPUT'].dataProvider().addAttributes([QgsField("KLC_ID", QVariant.String)])
tmp2['OUTPUT'].updateFields()
# dissolve
tmp3 = processing.run("native:dissolve", {
    'INPUT': tmp2['OUTPUT'],
    'OUTPUT': "memory:"})
project.addMapLayer(tmp3['OUTPUT'])
# fill holes
tmp4 = processing.run("native:deleteholes", {
    'INPUT': tmp3['OUTPUT'],
    'MIN_AREA':0,
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"CAF_08\" (geom) sql='
    })
project.addMapLayer(tmp4['OUTPUT'])    
# Done: 20 km buffer around park merged with WCS CFCL
KLC_comments['CAF_08'] = "We took a 20 km buffer around the Okapi Wildlife Reserve and included the \
\'Concessions Forestières de Communauté Locale\' (CFCL) under creation with WCS: \
Andikau (East-North East), Andibuta (East, just North of Mambasa), \
Bafwakoa (West)."
KLC_addLayers['CAF_08'] = ['QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/KLC/CAF_08_Okapi/WCS_CFCL_mela.gpkg|layername=WCS_CFCL_mela", "WCS CFCL", "ogr")']


# CAF_09: Kahuzi-Biega (page 263) (NP limits seem to better follow nat. features than WHS)
KLC_name['CAF_09'] = "Kahuzi-Biega"
KLC_PA['CAF_09'] = (1082)
wdpa.selectByExpression('"WDPAID" IN (1082)', 
    QgsVectorLayer.SetSelection)
caf_09 = buffer_selection("CAF_09", buf=15) # OK but
# TO DO: narrow the buffer on the eastern side to 5 km.
# snap to road
# select road
groads.selectByExpression('"OBJECTID" IN (54526, 58725, 59895, 60578, 62442, 62771,\
    63233, 63474, 64375, 69961, 72100, 78037, 86088, 100380, 100762, 100784,\
    124335, 140636, 152408, 156910, 157097, 161332, 166985, 175486, 177142, 182788, \
    189695, 191557, 236868, 241662)',
    QgsVectorLayer.SetSelection)
# join lines
tmp_roads = processing.run("native:dissolve", {
    'INPUT': QgsProcessingFeatureSourceDefinition(groads.id(), True),
    'OUTPUT': "memory:"})
tmp = processing.run("native:mergelines", {
    'INPUT': tmp_roads['OUTPUT'],
    'OUTPUT': "memory:"})
# split with lines
tmp1 = processing.run("native:splitwithlines", {
    'INPUT':caf_09['OUTPUT'],
    'LINES':tmp['OUTPUT'],
    'OUTPUT':"memory:"
    })
project.addMapLayer(tmp1['OUTPUT'])
tmp1['OUTPUT'].selectByExpression('$area > 1e10',QgsVectorLayer.SetSelection)
# save selection to gpkg
tmp = processing.run("native:saveselectedfeatures", {
    'INPUT':tmp1['OUTPUT'],
    'OUTPUT': 'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"CAF_09\" (geom) sql='
    })
KLC_comments['CAF_09'] = "We took a 15 km  buffer around the Kahuzi-Biega NP, that we narrowed to the North, East and South following the roads."

# CAF_10: Maiko-Tayna (page 263)
KLC_name['CAF_10'] = "Maiko-Tayna"
# + Kisimba Ikobo Primate Nature reserve 350001
KLC_PA['CAF_10'] = (1080, 317056, 350001)
wdpa.selectByExpression('"WDPAID" IN (1080, 317056, 350001)', 
    QgsVectorLayer.SetSelection)
#buffer_selection("CAF_10", buf=15) # OK but
tmp_wdpa = processing.run("qgis:buffer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'DISTANCE':15000, # meters
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':False,
    'OUTPUT':'memory:'
    })
# TO DO: clip to the road on the South West and to Virunga KLC to the East
# select riv
riv.selectByExpression('"ARCID" in (528891, 528417, 528418, 528419, 528479, 528709)', QgsVectorLayer.SetSelection)
# buffer and reproject
tmp = processing.run("native:reprojectlayer", {
    'INPUT': QgsProcessingFeatureSourceDefinition(riv.id(), True),
    'TARGET_CRS': 'EPSG:54009',
    'OUTPUT': 'memory:'})
tmp1 = processing.run("qgis:buffer", {
    'INPUT':tmp['OUTPUT'],
    'DISTANCE':500, # meters
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':False,
    'OUTPUT':'memory:'
    })
# merge
tmp2 = processing.run("native:mergevectorlayers", {
    'LAYERS':[tmp1['OUTPUT'],
        tmp_wdpa['OUTPUT']],
    'CRS': "EPSG:54009",
    'OUTPUT':"memory:"})
#project.addMapLayer(tmp2['OUTPUT'])
# dissolve
tmp3 = processing.run("native:dissolve", {
    'INPUT': tmp2['OUTPUT'],
    'OUTPUT': "memory:"})
#project.addMapLayer(tmp3['OUTPUT'])
# fill holes
tmp4 = processing.run("native:deleteholes", {
    'INPUT': tmp3['OUTPUT'],
    'MIN_AREA':0,
    'OUTPUT':"memory:"
    })
#project.addMapLayer(tmp4['OUTPUT'])    
# clip to road and Virunga KLC
groads.selectByExpression('"OBJECTID" IN (184159, 156244, 122709)', 
    QgsVectorLayer.SetSelection)
# dissolve selected features
tmp_roads = processing.run("native:dissolve", {
    'INPUT': QgsProcessingFeatureSourceDefinition(groads.id(), True),
    'OUTPUT': "memory:"})
# merge lines (because original lines are not all in the same direction)
tmp5 = processing.run("native:mergelines", {
    'INPUT': tmp_roads['OUTPUT'],
    'OUTPUT': "memory:"})
# split with lines
tmp6 = processing.run("native:splitwithlines", {
    'INPUT':tmp4['OUTPUT'],
    'LINES':tmp5['OUTPUT'],
    'OUTPUT':"memory:"
    })
project.addMapLayer(tmp6['OUTPUT'])
# remove/add attributes
res = tmp6['OUTPUT'].dataProvider().deleteAttributes(list(range(0, len(getFieldsNames(tmp6['OUTPUT'])))))
res = tmp6['OUTPUT'].dataProvider().addAttributes([QgsField("KLC_ID", QVariant.String), QgsField("Area", QVariant.Double)])
#res = tmp6['OUTPUT'].dataProvider().changeAttributeValue()
tmp6['OUTPUT'].updateFields()
area2Field(tmp6['OUTPUT'], "Area")
editAttribute(tmp6['OUTPUT'], "KLC_ID", QgsExpression("'CAF_10'"))
# select feature with max(Area)
tmp6['OUTPUT'].selectByExpression('"Area" > 1e9',QgsVectorLayer.SetSelection)
# Difference with CAF_02
caf_02 = QgsVectorLayer('E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=CAF_02', "CAF_02", "ogr")
tmp7 = processing.run("native:difference", {
    'INPUT':QgsProcessingFeatureSourceDefinition(tmp6['OUTPUT'].id(),True),
    'OVERLAY':caf_02,
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"CAF_10\" (geom) sql='
    })
project.addMapLayer(tmp7['OUTPUT'])
KLC_comments['CAF_10'] = "We took a 15 km buffer around the target PAs, clipped to the road in the South and to the adjacent CAF_02 to the East."

# CAF_11: Upemba-Kundelungu (page 263)
KLC_name['CAF_11'] = "Upemba-Kundelungu"
KLC_PA['CAF_11'] = (1079, 1084, 555512067)
wdpa.selectByExpression('"WDPAID" IN (1079, 1084, 555512067)', 
    QgsVectorLayer.SetSelection)
#buffer_selection("CAF_11", buf=20) # OK
# does not encompass totality of Ramsar site Bassin de la Lufira 555625801
# Use polygon from Copernicus Hotspots for compatibility
cop_klc.selectByExpression("\"klc_code\" = 'CAF_11'", QgsVectorLayer.SetSelection)
# save selection to Mollweide
tmp = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"CAF_11\" (geom) sql='
    })
KLC_comments['CAF_11'] = "For this KLC, we use the Copernicus Hotspot for which land cover has been mapped."

# CAF_12: Lomako-Yokokala (page 263)
KLC_name['CAF_12'] = "Lomako-Yokokala"
KLC_PA['CAF_12'] = (555512077)
wdpa.selectByExpression('"WDPAID" IN (555512077)', 
    QgsVectorLayer.SetSelection)
buffer_selection("CAF_12", buf = 15, layer = wdpa) #OK
KLC_comments['CAF_12'] = "We took a 15 km buffer around the Lomako-Yokokala Nature Reserve."

# CAF_13: Tumba-Ledima (page 264)
KLC_name['CAF_13'] = "Tumba-Ledima"
KLC_PA['CAF_13'] = (555512076)
# Include the southern part of Ramsar site 478028, up tothe southern limit of the Réserve du triangle de la Ngiri. Then no buffer.
wdpa.selectByExpression('"WDPAID" IN (555512076)', 
    QgsVectorLayer.SetSelection)
buffer_selection("CAF_13") # no buffer 
# TO DO.
# 2019-5-17 update looking up on WWF website, they work with communities of Mushie, Kwamouth, Bolobo and Yumbi in the province of Mai-Ndombe, on the south of the park
# + agroforestry villages: LOBOBI and LADI
# https://wwf.panda.org/our_work/forests/forest_publications_news_and_reports/?333754/MA-NDOMBE--Remarkable-achievements-with-the-Integrated-REDD-project---PIREDD
# there are bonobos in Bolobo https://wwf.be/fr/nos-projets/province-mai-ndombe/
# so i would rather follow the congo river on the west and the Kwa, then Fimi (upstream of Mushie) up to the Mai Ndombe lake.

wdpa.selectByExpression('"WDPAID" IN (478028)', 
    QgsVectorLayer.SetSelection)
# create Northern boundary following the river to the Tumba lake (include Lake?)
# split with line along river
riv.selectByExpression('"ARCID" IN (526069, 525659, 525578, 525334, 524906, 524822, \
        525386, 525730, 525803, 525804, 525731, 525617, 525579, 525580, 525242, 525280, 525281)', 
    QgsVectorLayer.SetSelection)
# dissolve, merge lines, split
tmp_riv = processing.run("native:dissolve", {
    'INPUT': QgsProcessingFeatureSourceDefinition(riv.id(), True),
    'OUTPUT': "memory:"})
# merge lines (because original lines are not all in the same direction)
tmp5 = processing.run("native:mergelines", {
    'INPUT': tmp_riv['OUTPUT'],
    'OUTPUT': "memory:"
    })
# split with lines
tmp6 = processing.run("native:splitwithlines", {
    'INPUT':QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'LINES':tmp5['OUTPUT'],
    'OUTPUT':"memory:"
    })
project.addMapLayer(tmp6['OUTPUT'])
res = tmp6['OUTPUT'].dataProvider().deleteAttributes(list(range(0, len(getFieldsNames(tmp6['OUTPUT'])))))
res = tmp6['OUTPUT'].dataProvider().addAttributes([QgsField("KLC_ID", QVariant.String), QgsField("Area", QVariant.Double)])
#res = tmp6['OUTPUT'].dataProvider().changeAttributeValue()
tmp6['OUTPUT'].updateFields()
area2Field(tmp6['OUTPUT'], "Area")
editAttribute(tmp6['OUTPUT'], "KLC_ID", QgsExpression("'CAF_13'"))
# select feature with max(Area)
tmp6['OUTPUT'].selectByExpression('"Area" > 4*1e10',QgsVectorLayer.SetSelection)
tmp_wdpa = processing.run("native:saveselectedfeatures", {
    'INPUT':tmp6['OUTPUT'],
    'OUTPUT':"memory:"
    })

# create southern border by buffering rivers
riv.selectByExpression('"ARCID" IN (538381,538885, 539358, 539568, 539655, \
        540235, 540647, 540734, 541471, 541843, 542062, 542487, 542793, 543028, \
        543341, 543437, 544017, 544166, 544450, 544741, 545097, 545125, 545415, \
        545798, 546103, 547098, 547758, 547846, 548656, 548734, 548995, 549040, \
        549089, 549126, 549175, 549224, 549256, 549259, 549351, 549456, 549457, \
        549496, 549542, 549599, 549643, 549802, 549803, 549804, 549849, 549851, \
        549931, 549932, 549933, 549934, 550033, 550034, 550082, 550123, 550124, \
        550125, 550169, 550212, 550213, 550214, 550329, 550411, 550480, 550803, \
        551088, 551089)', 
    QgsVectorLayer.SetSelection)
# reproject and buffer
tmp = processing.run("native:reprojectlayer", {
    'INPUT': QgsProcessingFeatureSourceDefinition(riv.id(), True),
    'TARGET_CRS': 'EPSG:54009',
    'OUTPUT': 'memory:'})
tmp1 = processing.run("qgis:buffer", {
    'INPUT':tmp['OUTPUT'],
    'DISTANCE':500, # meters
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':False,
    'OUTPUT':'memory:'
    })
# merge with wdpa selection
tmp2 = processing.run("native:mergevectorlayers", {
    'LAYERS':[tmp_wdpa['OUTPUT'],
        tmp1['OUTPUT']],
    'CRS': "EPSG:54009",
    'OUTPUT':"memory:"})
#project.addMapLayer(tmp2['OUTPUT'])
# dissolve
tmp3 = processing.run("native:dissolve", {
    'INPUT': tmp2['OUTPUT'],
    'OUTPUT': "memory:"})
#project.addMapLayer(tmp3['OUTPUT'])
# fill holes
tmp4 = processing.run("native:deleteholes", {
    'INPUT': tmp3['OUTPUT'],
    'MIN_AREA':0,
    'OUTPUT':"memory:"
    })
project.addMapLayer(tmp4['OUTPUT'])
# remove attributes
res = tmp4['OUTPUT'].dataProvider().deleteAttributes(list(range(1, len(getFieldsNames(tmp4['OUTPUT'])))))
tmp4['OUTPUT'].updateFields()
# save to file
error = QgsVectorLayerExporter.exportLayer(tmp4['OUTPUT'], 
    "E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg",
    "ogr", QgsCoordinateReferenceSystem("EPSG:54009"), False, {
    "update":True, "overwrite" : True, "driverName" : 'GPKG', "layerName":"CAF_13"})
KLC_comments['CAF_13'] = "We included the southern part of Ngiri Tumba-Maindombe Ramsar site (478028),\
up to the southern limit of the Réserve du triangle de la Ngiri. We also included communities of Mushie,\
Kwamouth, Bolobo and Yumbi in the province of Mai-Ndombe, on the south of the park, \
with which the [WWF is working](\
https://wwf.panda.org/our_work/forests/forest_publications_news_and_reports/?333754/MA-NDOMBE--Remarkable-achievements-with-the-Integrated-REDD-project---PIREDD). \
The limit of the KLC follows the Congo river on the West then the Kwa and the Fimi rivers (upstream of Mushie) up to the Mai Ndombe lake on the South."

# CAF_14: Itombwe-Kabobo (page 264)
KLC_name['CAF_14'] = "Itombwe-Kabobo"
KLC_PA['CAF_14'] = (72312)
wdpa.selectByExpression('"WDPAID" IN (72312)', 
    QgsVectorLayer.SetSelection)
buffer_selection("CAF_14", buf = 10) # OK
KLC_comments['CAF_14'] = "We took a 10 km buffer around the Itombwe Nature Reserve." 

# CAF_15: Lomami (page 264) [original KLC polygon is off]
KLC_name['CAF_15'] = "Lomami"
KLC_PA['CAF_15'] = (555625665)
wdpa.selectByExpression('"WDPAID" IN (555625665)', 
    QgsVectorLayer.SetSelection)
#buffer_selection("CAF_15_15", buf = 15) # OK
# use Copernicus HS
cop_klc.selectByExpression("\"klc_code\" = 'CAF_15'", QgsVectorLayer.SetSelection)
# save selection to Mollweide
tmp = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"CAF_15\" (geom) sql='
    })
KLC_comments['CAF_15'] = "For this KLC, we use the Copernicus Hotspot for which land cover has been mapped."

# CAF_16: Mbam Djerem  (page 264) + Deng Deng
KLC_name['CAF_1'] = "Mbam Djerem"
KLC_PA['CAF_16'] = (20166)
wdpa.selectByExpression('"WDPAID" IN (20166, 555547995)', 
    QgsVectorLayer.SetSelection)
# buffer_selection("CAF_16_20", buf= 20) # OK
# Use copernicus HS BUT does not include Deng Deng
cop_klc.selectByExpression("\"klc_code\" = 'CAF_16'", QgsVectorLayer.SetSelection)
# save selection to Mollweide
tmp = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"CAF_16\" (geom) sql='
    })
KLC_comments['CAF_16'] = "For this KLC, we use the Copernicus Hotspot for which land cover has been mapped."

# CAF_17: Bouba Ndjida-Benoue (page 264). 
KLC_name['CAF_17'] = "Bouba Ndjida-Benoue"
# add Sena Oura NP (555558302)
# TO DO: add Faro 1241 to this complex and remove it from CAF_01 (which will be contiguous)
# see map sent by Conrad. + include 32 ZIC (zone d'intérêt cynégétique)
# Done: email Quentin Jungers to ask for ZICs' polygons.
KLC_PA['CAF_17'] = (606, 607, 555558302, 1241)
wdpa.selectByExpression('"WDPAID" IN (606, 607, 555558302, 1241)', 
    QgsVectorLayer.SetSelection)    
zic = QgsVectorLayer("/vsizip/E:/weyname/BIOPAMA/GIS/data/Original/KLC/CAF_17/ZIC_NordCameroun.zip/ZICs_NordCAM.shp", 'ZICs_NordCAM', "ogr")
# merge
tmp = processing.run("native:union", {
    'INPUT':QgsProcessingFeatureSourceDefinition(wdpa.id(), True), 
    'OVERLAY': zic,
    'OUTPUT':"memory:"
    })
project.addMapLayer(tmp['OUTPUT'])
tmp['OUTPUT'].selectAll()
buffer_selection("CAF_17", buf = 10, layer = tmp['OUTPUT']) 
# difference with CAF_01
tmp = processing.run("native:difference", {
    'INPUT': QgsVectorLayer('E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=CAF_17', "caf_17", "ogr"),
    'OVERLAY':  QgsVectorLayer('E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=CAF_01', "caf_01", "ogr"),
    'OUTPUT' :  "memory:"
    })
# export to file
error = QgsVectorLayerExporter.exportLayer(tmp['OUTPUT'], 
   "E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg",
   "ogr", QgsCoordinateReferenceSystem("EPSG:54009"), False, {
   "update":True, "overwrite" : True, "driverName" : 'GPKG', "layerName":"CAF_17"})
if error[0] != QgsVectorLayerExporter.NoError:
   print("File not written!")    

KLC_addLayers['CAF_17'] = ['QgsVectorLayer("/vsizip/E:/weyname/BIOPAMA/GIS/data/Original/KLC/CAF_17/ZIC_NordCameroun.zip/ZICs_NordCAM.shp", "ZIC Nord Cameroun", "ogr")']
KLC_comments['CAF_17'] = "We added the Faro NP to this complex and removed it from CAF_01 (which is contiguous). We also included \
32 ZIC (zone d'intérêt cynégétique) provided by Quentin Jungers from OFAC."

# CAF_18: Zakouma-Siniah (page 264)
KLC_name['CAF_18'] = "Zakouma-Siniah"
# Conrad: gThe Greater Zakouma landscape includes:
# Parc National de Zakouma (PNZ) 641, Réserves de Faune du Barh Salamat 5164,
# + include Siniaka-Minia 5165
KLC_PA['CAF_18'] = (641, 5165)
wdpa.selectByExpression('"WDPAID" IN (641, 5165, 5164)', 
    QgsVectorLayer.SetSelection)
buffer_selection("CAF_18", buf = 20)
KLC_comments['CAF_18'] = "We took a 20 km buffer around the target PAs, including the Bahr Salamat Faunal Reserve."
# TO DO: 
# add Abou Telfane, Domaine de Chasse de Melfi-Roukoum (no wdpa id, no map, but should be close to Melfi).
# join with CAF_06 through Domaine de chasse de l'Anouk 555558303? (but CAF_06 has been mapped by Copernicus hotspots)
caf_06_sites = iface.addVectorLayer('E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=CAF_06_sites','caf_06_sites', 'ogr')
# add selected wdpa
caf_06_sites.dataProvider().addFeatures(wdpa.selectedFeatures())
caf_06_sites.selectAll()
tmp = buffer_selection("CAF_06_18", layer = caf_06_sites, buf = 20)
# there are 4 strange subpolygons in the middle of the big polygon...
# delete Vertex 717:
tmp['OUTPUT'].startEditing()
iVertex = 760
while iVertex >= 717:
    tmp['OUTPUT'].deleteVertex(1,iVertex)
    iVertex = iVertex - 1
iVertex = 10
while iVertex >= 0:
    tmp['OUTPUT'].deleteVertex(1,iVertex)
    iVertex = iVertex - 1

tmp['OUTPUT'].commitChanges()

KLC_PA['CAF_06_18'] = (641, 5165, 5164, 555558303, 2256, 639, 301830, 2258, 2261)
KLC_comments['CAF_06_18'] = "We propose to merge KLCs CAF_06 and CAF_18 in a transboundary landscape through the Domaine de Chasse de l'Aouk."
KLC_name['CAF_06_18'] = KLC_name['CAF_06'] + "-" + KLC_name['CAF_18']

# CAF_19: Monts de Cristal-Altos de Nsork
KLC_name['CAF_19'] = "Monts de Cristal-Altos de Nsork"
KLC_PA['CAF_19'] = (306237, 20268)
wdpa.selectByExpression('"WDPAID" IN (306237, 20268)', 
    QgsVectorLayer.SetSelection)
# buffer 20 km without dissolving
tmp = processing.run("native:buffer", {
    'INPUT': QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'DISTANCE':20000, # meters
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':False,
    'OUTPUT':'memory:'
    })
# intersect with country
countries.selectByExpression('"iso3" IN (\'GAB\',\'GNQ\')',  QgsVectorLayer.SetSelection)
tmp1 = processing.run("native:intersection", {
    'INPUT':tmp['OUTPUT'],
    'OVERLAY': QgsProcessingFeatureSourceDefinition(countries.id(), True),
    'OUTPUT':"memory:"
    })
# select equal iso3
tmp1['OUTPUT'].selectByExpression('"iso3_2" = "ISO3"', QgsVectorLayer.SetSelection)
tmp2 = processing.run("native:saveselectedfeatures", {
    'INPUT':tmp1['OUTPUT'],
    'OUTPUT':"memory:"
    })
## link    
# link centroids and buffer 25 km
tmp1 = processing.run("native:centroids",{ 
    'ALL_PARTS' : True, 
    'INPUT' : QgsProcessingFeatureSourceDefinition(wdpa.id(), True), 
    'OUTPUT' : 'memory:' 
    })
# add field with y coordinate
res = tmp1['OUTPUT'].dataProvider().addAttributes([QgsField("X", QVariant.Double)])
tmp1['OUTPUT'].updateFields()
editAttribute(tmp1['OUTPUT'], "X", QgsExpression("$x")) # not working i don't know why!!!! Did it manually
project.addMapLayer(tmp1['OUTPUT'])
# !!!!!!!
tmp= processing.run('qgis:pointstopath', {
    'INPUT': tmp1['OUTPUT'],
    'ORDER_FIELD': 'X',
    'OUTPUT': 'memory:'
    })
# deleteVertex 0
tmp['OUTPUT'].startEditing()
tmp['OUTPUT'].deleteVertex(1,0)
tmp['OUTPUT'].commitChanges()
# buffer line
tmp1 = processing.run('native:buffer', {
    'INPUT': tmp['OUTPUT'],
    'DISTANCE': 20000,
    'OUTPUT': 'memory:'
    })
project.addMapLayer(tmp1['OUTPUT'])
# merge and buffer_selection
tmp = processing.run("native:mergevectorlayers",{
    'LAYERS': [tmp2['OUTPUT'],tmp1['OUTPUT']],
    'CRS':"EPSG:54009",
    'OUTPUT':"memory:"
    })
project.addMapLayer(tmp['OUTPUT'])
tmp['OUTPUT'].selectAll()
buffer_selection("CAF_19", buf = 0, layer = tmp['OUTPUT'])
# Done!
KLC_comments['CAF_19'] = "We took a 20 km buffer around the target PAs and clipped to the borders North of \
monts de Cristal NP (Gabon) and East of Altos de Nsork (Equatorial Guinea), linking both areas through a 40 km wide corridor."

# CAF_20: Picos and Obo
KLC_name['CAF_20'] = "Picos and Obo"
KLC_PA['CAF_20'] = (20264, 124355, 555592842, 20269)
wdpa.selectByExpression('"WDPAID" IN (20264, 124355, 555592842, 20269)', 
    QgsVectorLayer.SetSelection)
tmp = processing.run("native:buffer", {
    'INPUT': QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'DISTANCE':25000, # meters
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':False,
    'OUTPUT':'memory:'
    })

tmp1 = processing.run("native:centroids",{ 
    'ALL_PARTS' : True, 
    'INPUT' : QgsProcessingFeatureSourceDefinition(wdpa.id(), True), 
    'OUTPUT' : 'memory:' 
    })
# add field with y coordinate
res = tmp1['OUTPUT'].dataProvider().addAttributes([QgsField("X", QVariant.Double)])
tmp1['OUTPUT'].updateFields()
editAttribute(tmp1['OUTPUT'], "X", QgsExpression("$x")) # not working i don't know why!!!! Did it manually
project.addMapLayer(tmp1['OUTPUT'])
# !!!!!!!
tmp2= processing.run('qgis:pointstopath', {
    'INPUT': tmp1['OUTPUT'],
    'ORDER_FIELD': 'X',
    'OUTPUT': 'memory:'
    })
# buffer line
tmp3 = processing.run('native:buffer', {
    'INPUT': tmp2['OUTPUT'],
    'DISTANCE': 25000,
    'OUTPUT': 'memory:'
    })
project.addMapLayer(tmp3['OUTPUT'])
# merge and buffer_selection
tmp4 = processing.run("native:mergevectorlayers",{
    'LAYERS': [tmp['OUTPUT'],tmp3['OUTPUT']],
    'CRS':"EPSG:54009",
    'OUTPUT':"memory:"
    })
project.addMapLayer(tmp4['OUTPUT'])
tmp4['OUTPUT'].selectAll()
buffer_selection("CAF_20", buf = 0, layer = tmp4['OUTPUT'])

KLC_comments['CAF_20'] = "We took a 25 km buffer around the target PAs, linking them through a 50 km wide corridor."

# for EAF get KLC boundaries from TFCA when available

# EAF_01: Mara-Serengeti-Ngorongoro (Savannah)
KLC_name['EAF_01'] = "Mara-Serengeti-Ngorongoro (without Loliondo)"
KLC_name['EAF_01_w_Loliondo'] = "Mara-Serengeti-Ngorongoro (with Loliondo)"
# Maasai Mara NR (KE) 1297
#• Serengeti WHS/NP (TZ) 916
#• Maswa GR (TZ) 7437 (North), 555623828 (South)
#• Grumeti GR (TZ) 31595
#• Ikorongo GCA (TZ) 32811
#• Loliondo GCA (TZ) 555623786 (borders Natron Lake!) - not in original KLC BUT in Larger than Elephants
#• Ngorongoro WHS/CA (TZ) 555623796
#• + conservancies  555555512, 555555513, 555555514, 555555515, 555555516, 555555517, 555555518
#• + whole Mara Catchment (mostly KE)
# 2 WHS (Ngorongoro and Serengeti)
# Ngorongoro: dif between WHS and National designations: National seems more coherent.
# Serengeti encroaches on Kenya???
# Masai-Mara limit not correct: shifted/distorted: do not follow natural features on Google imagery
# I added Ikona WMA in TZ 352222
# Should I add forest reserves upstream of Mara catchment: 33443, 7705, 7730, 33499, 7631 
#(but polygons are shifted! and (East African montane) forest is not the objective of this KLC)

KLC_PA['EAF_01'] = (1297, 916, 7437, 555623828, 31595, 32811, 555623796)
KLC_PA['EAF_01_wLoliondo'] = (1297, 916, 7437, 555623828, 31595, 32811, 555623796, 555623786)
wdpa.selectByExpression('"WDPAID" IN (1297, 916, 7437, 555623828, 31595, 32811, \
    555623796, \
    555555512, 555555513, 555555514, 555555515, 555555516, 555555517, 555555518,\
    352222)', 
    QgsVectorLayer.SetSelection)
#• + whole Mara Catchment (mostly KE) take from HydroSHEDS hybas_af_lev06 ARCID 530520 intersect with Kenya
hybas6.selectByExpression('"HYBAS_ID" = 1061159550', QgsVectorLayer.SetSelection)
# intersect with Kenya
countries.selectByExpression('"ISO3" = \'KEN\'', QgsVectorLayer.SetSelection)
tmp = processing.run("native:intersection", {
    'INPUT': QgsProcessingFeatureSourceDefinition(hybas6.id(), True),
    'OVERLAY': QgsProcessingFeatureSourceDefinition(countries.id(), True),
    'OUTPUT': "memory:"
    })
# merge layers
tmp1 = processing.run("native:union", {
    'INPUT': QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'OVERLAY': tmp['OUTPUT'],
    'OUTPUT': "memory:"
    })
# buffer 5 km
tmp1['OUTPUT'].selectAll()
project.addMapLayer(tmp1['OUTPUT'])
buffer_selection("EAF_01", buf = 5, layer = tmp1['OUTPUT'])
# problem : intersect with Lake Natron (Loliondo GCA): clip which? or discard Loliondo? and reduce Natron
KLC_comments['EAF_01'] = "We took a 5 km buffer around the target PAs (including community conservancies, discarding Loliondo GCA) and the Kenyan part of the Mara catchment."
KLC_comments['EAF_01_wLoliondo'] = "We took a 5 km buffer around the target PAs (including community conservancies) and the Kenyan part of the Mara catchment."
# TO DO
# use EAF_01, merge with Loliondo (555623786), rename as EAF_01
# make tmp copy of layer
layer = QgsVectorLayer('E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=EAF_01', "eaf_01", "ogr")
layer.selectAll()
layer_copy = processing.run("native:saveselectedfeatures", {'INPUT': layer, 'OUTPUT': 'memory:'})['OUTPUT']
# select Loliondo from WDPA
wdpa.selectByExpression('"WDPAID" IN (555623786)', 
    QgsVectorLayer.SetSelection)
loliondo = processing.run("native:saveselectedfeatures", {'INPUT': wdpa, 'OUTPUT': 'memory:'})['OUTPUT']
# merge
tmp2 = processing.run('native:union', {
  'INPUT': layer_copy,
  'OVERLAY': loliondo,
  'OUTPUT': "memory:"
  })
project.addMapLayer(tmp2['OUTPUT'])
# dissolve and set attributes
tmp2['OUTPUT'].selectAll()
eaf_01 = buffer_selection("EAF_01", layer = tmp2['OUTPUT'], buf = 0)

# EAF_02: Rift Valley WHS (Lake Bogoria, Lake Nakuru and Lake Elementaita) - Natron
KLC_name['EAF_02'] = "Rift Valley WHS - Natron"
# clear shift between WHS,  NP and RAMSAR (completely off!) limits: NP is too much to the south, but WHS is too much to the north, compared to Google imagery
# add Lake Navaisha? 103549
# select endorheic basins with the lakes + hyrdological? connection
# add NRT conservamcy Ruko 555555510
KLC_PA['EAF_02'] = (555542339, 103549, 900623, 555555510)
wdpa.selectByExpression('"WDPAID" IN (555542339, 103549, 900623, 555555510)', 
    QgsVectorLayer.SetSelection)
#tmp1 = buffer_selection("EAF_02_tmp1", buf = 10)
# still need to connect the 2 sections: Rob says that this is the whole point: trying to connect the Nothern lakes to Lake Natron
waterBodies.selectByExpression('"NAME_OF_WA" IN (\
        \'Natron\',\
        \'Magadi(Emugur)\',\
        \'Magadi\',\
        \'Naivasha\',\
        \'Elementeita\',\
        \'Nakuru\',\
        \'Bogoria\',\
        \'Baringo\'\
        )',
    QgsVectorLayer.SetSelection)
#tmp2 = buffer_selection("EAF_02_tmp2", layer = waterBodies, buf = 5)
# draw a line joining the centers of each lake
tmp1 = processing.run("native:centroids",{ 
    'ALL_PARTS' : True, 
    'INPUT' : QgsProcessingFeatureSourceDefinition(waterBodies.id(), True), 
    'OUTPUT' : 'memory:' 
    })
# add point in south part of Lake Natron
fet = QgsFeature()
fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(3599232, -316966)))
fet.setAttributes([NULL, NULL, NULL, NULL, "lake", NULL, NULL])
tmp1['OUTPUT'].dataProvider().addFeatures([fet])

# add field with y coordinate
res = tmp1['OUTPUT'].dataProvider().addAttributes([QgsField("Y", QVariant.Double)])
tmp1['OUTPUT'].updateFields()
editAttribute(tmp1['OUTPUT'], "Y", QgsExpression("$y")) # not working i don't know why!!!! Did it manually
project.addMapLayer(tmp1['OUTPUT'])
# !!!!!!!
tmp2= processing.run('qgis:pointstopath', {
    'INPUT': tmp1['OUTPUT'],
    'ORDER_FIELD': 'Y',
    'OUTPUT': 'memory:'
    }) 
#project.addMapLayer(tmp2['OUTPUT'])
# buffer line
tmp3 = processing.run('native:buffer', {
    'INPUT': tmp2['OUTPUT'],
    'DISTANCE': 5000,
    'OUTPUT': 'memory:'
    })
    
# union selected waterBodies and wdpa
tmp4 = processing.run('native:union', {
  'INPUT': QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
  'OVERLAY': QgsProcessingFeatureSourceDefinition(waterBodies.id(), True),
  'OUTPUT': "memory:"
  })
# delete fields. keep only geometry (make QGis crash on next step)
#tmp4['OUTPUT'].dataProvider().deleteAttributes(tmp4['OUTPUT'].attributeList())
# union buffered line with sites
tmp5 = processing.run('native:union', {
  'INPUT': tmp4['OUTPUT'],
  'OVERLAY': tmp3['OUTPUT'],
  'OUTPUT': "memory:"
  })
project.addMapLayer(tmp5['OUTPUT'])
tmp5['OUTPUT'].selectAll()
eaf_02 = buffer_selection("EAF_02", layer = tmp5['OUTPUT'], buf = 5)
# Difference with EAF_01
tmp = processing.run("native:difference", {
    #'INPUT': QgsVectorLayer('E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=EAF_02', "eaf_02", "ogr"),
    'INPUT': QgsVectorLayer('/Users/mela/JRCbox/BIOPAMA/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=EAF_02', "eaf_02", "ogr"),
    #'OVERLAY':  QgsVectorLayer('E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=EAF_01', "eaf_01", "ogr"),
    'OVERLAY':  QgsVectorLayer('Users/mela/JRCbox/BIOPAMA/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=EAF_01', "eaf_01", "ogr"),
    'OUTPUT' :  "memory:"
    })
# export to file
error = QgsVectorLayerExporter.exportLayer(tmp['OUTPUT'], 
   #"E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg",
   #'Users/mela/JRCbox/BIOPAMA/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg',
   'C:/Users/weyname/jrcbox/BIOPAMA/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg',
   "ogr", QgsCoordinateReferenceSystem("EPSG:54009"), False, {
   "update":True, "overwrite" : True, "driverName" : 'GPKG', "layerName":"EAF_02"})
if error[0] != QgsVectorLayerExporter.NoError:
   print("File not written!")    
KLC_comments['EAF_02'] = "We took a 5 km buffer around the lakes, including the Ruko Community Conservancy, and linked them through a 20 km wide corridor."

## Natron sink is HYBAS_ID 1000041020
#hybas.selectByExpression('"NEXT_SINK" IN (1000042480, 100004280, 1000082110, \
#    1000078370, 1000053010, 1000079700, 1000062340, 1000067860, 1000077050, \
#    1000081580, 1000047610, 1000057500, 1000044500, \
#    1000044180,\
#    1000072700,\
#    1000075320,\
#    1000082570,\
#    1000046470,\
#    1000076000,\
#    1000057390) \
#    ',
#    QgsVectorLayer.SetSelection)
##    1000044180 could be added to the east but goes too far east
## 1000041020 too much
#hybas.selectByExpression('"PFAF_7" IN (\
#    1152051,\
#    1152053,\
#    1152055) \
#    OR "PFAF_8" IN (11520521)\
#    OR "PFAF_9" IN (115205401)',
#    QgsVectorLayer.SetSelection)
## dissolve selected features
#tmp = processing.run("native:dissolve", {
#    'INPUT': QgsProcessingFeatureSourceDefinition(hybas.id(), True),
#    'OUTPUT':"memory:"
#    })
## remove/add attributes
#res = tmp['OUTPUT'].dataProvider().deleteAttributes(list(range(0, len(getFieldsNames(tmp['OUTPUT'])))))
#res = tmp['OUTPUT'].dataProvider().addAttributes([QgsField("KLC_ID", QVariant.String)])
#tmp['OUTPUT'].updateFields()
#editAttribute(tmp['OUTPUT'], "KLC_ID", QgsExpression("'EAF_02'"))
## export to file
#error = QgsVectorLayerExporter.exportLayer(tmp['OUTPUT'], 
#    "E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg",
#    "ogr", QgsCoordinateReferenceSystem("EPSG:54009"), False, {
#    "update":True, "overwrite" : True, "driverName" : 'GPKG', "layerName":"EAF_02"})
#if error[0] != QgsVectorLayerExporter.NoError:
#    print("File not written!")
## Problem Natron basin intersects with Ngorongoro...

# EAF_03: Greater Kilimanjaro
KLC_name['EAF_03'] = "Greater Kilimanjaro"
# according to KLC from DEVCO: Kilimanjaro NP, Enduimat WMA,Mkomazi NP , Tsavo West NP, Tsavo East, South Kitui
# I add Chyulu Hills NP 19563, Amboseli NP 758, Taita Hills WS 7408, Lumo 72309
# conservancies: Tawi 555555489, Nailepu 555555488, Osupuko 555555487, Kimana WS 555555481, Motikanju 555555486, Elerai 555555482
# Kilimanjaro: NP is larger than WHS
# Rob: include Taita, leave the small forest patches close to Mkomazi NP into Eastern arc
# TO DO buffer PAs but not Mkomazi (1402), then union it afterwards
KLC_PA['EAF_03'] = (922, 555549308, 19564, 752, 2590, 7408)
wdpa.selectByExpression('"WDPAID" IN (922, 555549308, 19564, 752, 2590,\
    19563, 758, 7408, 72309,\
    555555489, 555555488, 555555487, 555555481, 555555486, 555555482)', 
    QgsVectorLayer.SetSelection)
tmp = buffer_selection("EAF_03", buf = 15)
# union with wdpa = 1402
wdpa.selectByExpression('"WDPAID" IN (1402)', QgsVectorLayer.SetSelection)
tmp1 = processing.run("native:union", {
    'INPUT': tmp['OUTPUT'],
    'OVERLAY': QgsProcessingFeatureSourceDefinition(wdpa.id(), True), 
    'OUTPUT': "memory:"
    })

# dissolve
tmp2 = processing.run("native:dissolve", {
    'INPUT':tmp1['OUTPUT'],
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"EAF_03\" (geom) sql='
    })
# simplify: deleteVertex 488 to 468
eaf_03 = tmp2['OUTPUT']
eaf_03.startEditing()
iVertex = 488
while iVertex >= 468:
    eaf_03.deleteVertex(1,iVertex)
    iVertex = iVertex - 1

eaf_03.commitChanges()

KLC_comments['EAF_03'] = "We took a 15 km buffer around the target PAs, including community conservancies, except around Mkomazi NP, which orders KLC EAF_10 (Eastern Arc forests)."

# EAF_04: Niassa-Selous (WHS)
KLC_name['EAF_04'] = "Niassa-Selous"
# add Tunduru WMA and Nandembo FR to connect both areas
#Selous WHS/GR (TZ)
#• Niassa NR (MZ)
#• Mikumi NP (TZ)
#• Udzungwa NP (TZ)
#• Kilombero GCA (TZ)
#• + WMAs, conservancies and hunting blocks
KLC_PA['EAF_04'] = (5005, 555637447, 555549304, 303392)
#wdpa.selectByExpression('"WDPAID" IN (5005, 555637447, 555549304, 303392)', 
#    QgsVectorLayer.SetSelection)
#buffer_selection("EAF_04")
# original KLC is OK, just refine to make sure all PAs are inside.
# use Copernicus KLC
cop_klc.selectByExpression("\"klc_code\" = 'EAF_04'", QgsVectorLayer.SetSelection)
# save selection to Mollweide
tmp = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"EAF_04\" (geom) sql='
    })

KLC_comments['EAF_04'] = "For this KLC, we use the Copernicus Hotspot for which land cover has been mapped. "

# EAF_05: Simien Mountains
KLC_name['EAF_05'] = "Simien Mountains"
KLC_PA['EAF_05'] = (653)
wdpa.selectByExpression('"WDPAID" IN (653, 2006)', 
    QgsVectorLayer.SetSelection)
#buffer_selection("EAF_05")
# TO DO: select woreda touching the park (see ethiopiaworeda shp)
woreda = QgsVectorLayer("E:\weyname\BIOPAMA\GIS\data\Original\ethiopiaworeda\Eth_Woreda_2013.shp", "woreda","ogr")
# select by location
processing.run("native:selectbylocation", {
    'INPUT': woreda,
    'PREDICATE':0,
    'INTERSECT':QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'METHOD':0
    })
# reproject selection and dissolve
tmp1 =processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(woreda.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':"memory"
    })
eaf_05 = processing.run("native:dissolve", {
    'INPUT':tmp1['OUTPUT'],
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"EAF_05\" (geom) sql='
    })
# remove attributes and set KLC_ID
eaf_05['OUTPUT'].dataProvider().deleteAttributes(eaf_05['OUTPUT'].attributeList())
# add attributes
res = eaf_05['OUTPUT'].dataProvider().addAttributes([QgsField("KLC_ID", QVariant.String)])
eaf_05['OUTPUT'].updateFields()
editAttribute(eaf_05['OUTPUT'], "KLC_ID", QgsExpression("'EAF_05'"))
KLC_comments['EAF_05'] = "We delimited this KLC including all the municipalities (woreda) bordering the Simien National Park."

# EAF_06: Lake Turkana WHS
KLC_name['EAF_06'] = "Lake Turkana"
KLC_PA['EAF_06'] = (754, 7887, 7888)
wdpa.selectByExpression('"WDPAID" IN (145586)', 
    QgsVectorLayer.SetSelection)
#buffer_selection("EAF_06")
# Rob: do not include the whole lake. connect the three sites.
# TO DO: connect centroids, one side buffer
tmp = processing.run("native:centroids",{ 
    'ALL_PARTS' : True, 
    'INPUT' : QgsProcessingFeatureSourceDefinition(wdpa.id(), True), 
    'OUTPUT' : 'memory:' 
    })
res = tmp['OUTPUT'].dataProvider().addAttributes([QgsField("Y", QVariant.Double)])
tmp['OUTPUT'].updateFields()
editAttribute(tmp['OUTPUT'], "Y", QgsExpression("$y")) # not working i don't know why!!!! 
# !!!!!!
tmp1= processing.run('qgis:pointstopath', {
    'INPUT': tmp['OUTPUT'],
    'ORDER_FIELD': 'Y',
    'OUTPUT': 'memory:'
    }) 
#project.addMapLayer(tmp2['OUTPUT'])
# buffer line
tmp2 = processing.run('qgis:singlesidedbuffer', {
    'INPUT': tmp1['OUTPUT'],
    'DISTANCE': 10000,
    'SIDE': 1,
    'JOIN_STYLE':0,
    'OUTPUT': 'memory:'
    })
# union with wdpa selection
tmp3 = processing.run('native:union',{
    'INPUT':QgsProcessingFeatureSourceDefinition(wdpa.id(), True), 
    'OVERLAY': tmp2['OUTPUT'],
    'OUTPUT': "memory:"
    })
# buffer
project.addMapLayer(tmp3['OUTPUT'])
tmp3['OUTPUT'].selectAll()
buffer_selection("EAF_06", layer = tmp3['OUTPUT'], buf = 5)
KLC_comments['EAF_06'] = "We took a 5 km buffer around the three sites of the WHS and connected them through a 30 km wide corridor."

# EAF_07: Greater Mount Kenya (merge the NPs with the conservancies): Mount Kenya WHS, Aberdare NP, Ndotos Range FR, Mathews Range FR, Ol Pejeta, 
# Shaba NR, Mpus Kutuk Com Cons, Mpala Com Cons, Mukongo FR, Meibae ComCons, West Gate ComCons
#• Mt Kenya-Lewa Downs WHS 145585 /NR 555622007/FR 7661
#• Samburu NR 2298
#• Buffalo Springs NR 2295
#• Shaba NR 2427
#• Aberdare NP 756
#• + NRT Conservancies (nrt-kenya.org) should inlude all of them! + Kora, Meru etc.
KLC_name['EAF_07'] = "Greater Mount Kenya"
KLC_PA['EAF_07'] = (145585, 7661, 2298, 2295, 2427, 756,\
    33435, 7699, 17825, 7668, 33496)
# TO DO !!!
# GAUL2 Samburu
wdpa.selectByExpression('"WDPAID" IN (555555520, 555555504, 555555506, 555555496,\
    555555492, 555566903, 555566905, 555566906, 555555503, 555555508, 555555509, \
    555555519, 555555497, 555555522, 555555498, 555566899, 555555500, \
    555555511, 555566900, 555555490, 7649, 7668, 555555494, 555555495, 7663, 7683,\
    7685, 2295, 2298, 2427, 62221, 10751, 19565, 753)', 
    QgsVectorLayer.SetSelection)
# save selection
NRT = processing.run("native:saveselectedfeatures", {
    'INPUT': wdpa,
    'OUTPUT': "memory:"
    })
# Rest of Samburu county is county initiated conservancy
gaul2.selectByExpression('"ADM2_CODE" = 51389', QgsVectorLayer.SetSelection)
samburu = processing.run("native:reprojectlayer", {
    'INPUT': QgsProcessingFeatureSourceDefinition(gaul2.id(), True), 
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),
    'OUTPUT': "memory:"
    })
# NP
wdpa.selectByExpression('"WDPAID" IN (145585, 7661, 2298, 2295, 2427, 756,\
    33435, 7699, 17825, 7668, 33496)', 
    QgsVectorLayer.SetSelection)
# buffer selection without dissolve
tmp_wdpa = processing.run("native:buffer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'DISTANCE':5000, # meters
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':False,
    'OUTPUT':'memory:'
    })

# merge layers
tmp = processing.run("native:mergevectorlayers", {
    'LAYERS':[
        tmp_wdpa['OUTPUT'], # wdpa
        NRT['OUTPUT'], # NRT conservancies
        samburu['OUTPUT'] # samburu county
        ],
    'CRS': "EPSG:54009",
    'OUTPUT': "memory:"
    })
project.addMapLayer(tmp['OUTPUT'])
tmp['OUTPUT'].selectAll()

buffer_selection("EAF_07", buf = 0, layer=tmp['OUTPUT'])
KLC_comments['EAF_07'] = "We took a 5 km buffer around the main target PAs and included the NRT Community Conservancies surrounding them."

# EAF_08: Sudd-Badingilu-Gambella + Boma NP
KLC_name['EAF_08'] = "Sudd-Badingilu-Gambella"
#Zeraf GR (SS) 1368
# Shambe NP (SS) 1372
# Badingilu NP (SS) 2337, 
# Boma NP (SS) 1371
# Gambella NP (ET) 13704
# + other satellite PAs
# centroid etc.
# Main PAs
KLC_PA['EAF_08'] = (1368, 1372, 2337, 1371, 13704)
wdpa.selectByExpression('"WDPAID" IN (902886, 2337, 1371)', 
    QgsVectorLayer.SetSelection)
tmp = processing.run("native:centroids",{ 
    'ALL_PARTS' : True, 
    'INPUT' : QgsProcessingFeatureSourceDefinition(wdpa.id(), True), 
    'OUTPUT' : 'memory:' 
    })
res = tmp['OUTPUT'].dataProvider().addAttributes([QgsField("X", QVariant.Double)])
tmp['OUTPUT'].updateFields()
editAttribute(tmp['OUTPUT'], "X", QgsExpression("$x")) # not working i don't know why!!!! 
project.addMapLayer(tmp['OUTPUT'])
# !!!!!!
tmp1= processing.run('qgis:pointstopath', {
    'INPUT': tmp['OUTPUT'],
    'ORDER_FIELD': 'X',
    'OUTPUT': 'memory:'
    }) 
# buffer line
tmp2 = processing.run('native:buffer', {
    'INPUT': tmp1['OUTPUT'],
    'DISTANCE': 20000,
    'OUTPUT': 'memory:'
    })
project.addMapLayer(tmp2['OUTPUT'])
#  add triangle between Badingilo and Boma
tmp2['OUTPUT'].startEditing()
# insertVertex at 12
tmp2['OUTPUT'].insertVertex(3304885, 640945, 1, 12)
tmp2['OUTPUT'].insertVertex(3411981, 670537, 1, 12)
tmp2['OUTPUT'].insertVertex(3334477, 827658, 1, 1)
tmp2['OUTPUT'].commitChanges()

# union with wdpa selection
wdpa.selectByExpression('"WDPAID" IN (902886, 2337, 555583110, 13704, 1371, 1372, 555583108, 13755, 555583106, 1368)', 
    QgsVectorLayer.SetSelection)
tmp3 = processing.run('native:union',{
    'INPUT':QgsProcessingFeatureSourceDefinition(wdpa.id(), True), 
    'OVERLAY': tmp2['OUTPUT'],
    'OUTPUT': "memory:"
    })
# buffer
project.addMapLayer(tmp3['OUTPUT'])
tmp3['OUTPUT'].selectAll()
buffer_selection("EAF_08", layer = tmp3['OUTPUT'], buf = 10)
# OK + link manually, including the triangle between Badingilo and Boma.
#TO DO: triangle
KLC_comments['EAF_08'] = "We took a 10 km buffer around the main and satelite PAs \
and connected them with a 20 km wide corridor, including the a larger zone between Badingilo and Boma."

# EAF_09: Bale Mountains
KLC_name['EAF_09'] = "Bale Mountains"
KLC_PA['EAF_09'] = (2281)
# problem of Bale NP boundary relative to Wildliffe Res and Controlled Hunting Area
wdpa.selectByExpression('"WDPAID" IN (2281, 7961, 13759, 29119, 29120, 29118)', 
    QgsVectorLayer.SetSelection)    
buffer_selection("EAF_09", buf=1)
# OK
KLC_comments['EAF_09'] = "We took a 1 km buffer around the Bale Controlled Hunting Area, which buffers the Bale National Park."

# EAF_10: Eastern Arc Forests
KLC_name['EAF_10'] = "Eastern Arc Forests"
# Udzungwa NP (TZ) 19297 - already in Selous original KLC but NOT in Copernicus HS. Hence take it in.
# Usambara Mts FRs (TZ) all the NR close to the Kenyan border. e.g Shume Mangamba 301450, shagayu 301442, Mgambo 303462, Amani 127827
# Pare Mts FRs (TZ) # on Google seems to be north of Vumari FR 301428, edge of Mkomazi NP 1402 (Greater Kilimanjaro)
# Taita Hills FRs (KE) already in Greater Kilimanjaro
KLC_PA['EAF_10'] = (19297, 301450, 301442, 303462, 127827, 301428)
wdpa.selectByExpression('"NAME" LIKE \'Udzungwa Mountains National Park\'') # already in Selous
wdpa.selectByExpression('"WDPAID" IN (19297, 301450, 301442, 303462, 127827, 301428)', 
    QgsVectorLayer.SetSelection)
wdpa.selectByExpression('"WDPAID" IN (301528,303502,303509,351705,127827,303367, 303488, 301442, 19297)', 
    QgsVectorLayer.SetSelection)
# manually select all tiny polygons
wdpa.selectByExpression('"WDPAID" IN (301409, 301411, 301415, 301428, 301431, \
    301432, 301436, 301440, 301442, 301444, 301453, 301458, 301462, 301465, \
    301469, 301476, 301478, 301479, 301483, 301484, 301488, 301491, 301503, \
    301504, 301512, 301517, 301524, 301528, 301532, 301546, 301549, 301560, \
    301561, 301563, 301577, 301579, 350009, 303430, 303444, 303445, 303452, \
    303454, 303457, 303458, 303462, 303463, 303467, 303471, 303475, 303476, \
    303488, 303489, 303494, 303499, 303501, 303502, 303506, 478264, 478263, \
    303509, 303511, 303557, 351702, 351705, 351706, 354044, 354045, 354046, \
    301526, 301553, 350025, 301550, 301466, 301475, 301480, 301487, 301520, \
    301521, 301522, 301534, 301556, 301584, 301585, 303451, 303453, 303455, \
    303456, 303465, 303466, 303473, 303477, 303554, 303860, 350008, 350012, \
    350015, 350016, 350017, 351701, 351704, 303443, 301420, 555623849, \
    555623855, 555623857, 555624061, 555624065, 555624066, 555624067, \
    555624091, 555624100, 555624106, 555624107, 19297, 127827, 301450, \
    555556106, 303367)', 
    QgsVectorLayer.SetSelection)
# save selection
tmp_wdpa = processing.run("native:saveselectedfeatures", {
    'INPUT': wdpa,
    'OUTPUT': "memory:"
    })
# merge with EAF_10_sites
eaf_10_sites = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/KLC/EAF_10_EasternArcForests/EAF_10_sites.gpkg|layername=EAF_10_sites", "EAF_10_sites", "ogr")
# merge layers and dissolve
tmp = processing.run("native:mergevectorlayers", {
    'LAYERS':[tmp_wdpa['OUTPUT'],
        eaf_10_sites],
    'CRS': "EPSG:54009",
    'OUTPUT':"memory:"})
# remove all attributes and add KLC_ID
#if tmp['OUTPUT'].dataProvider().capabilities() & QgsVectorDataProvider.DeleteAttributes:
res = tmp['OUTPUT'].dataProvider().deleteAttributes(list(range(0, len(getFieldsNames(tmp['OUTPUT'])))))
res = tmp['OUTPUT'].dataProvider().addAttributes([QgsField("KLC_ID", QVariant.String)])
tmp['OUTPUT'].updateFields()
# buffer
tmp1 = processing.run("qgis:buffer", {
    'INPUT':tmp['OUTPUT'],
    'DISTANCE':15000, # meters
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':False,
    'OUTPUT':'memory:'
    })
project.addMapLayer(tmp1['OUTPUT'])
# dissolve
tmp2 = processing.run("native:dissolve", {
    'INPUT': tmp1['OUTPUT'],
    'OUTPUT': "memory:"})
editAttribute(tmp2['OUTPUT'], "KLC_ID", QgsExpression("'EAF_10'"))
# fill holes
tmp3 = processing.run("native:deleteholes", {
    'INPUT': tmp2['OUTPUT'],
    'MIN_AREA':0,
    'OUTPUT':"memory:"
    })
EAF_10_tmp = tmp3
# clip out adjacent KLCs: EAF_03 Kilimanjaro; EAF_04 Niassa-Selous
tmp = processing.run("native:union", {
    'INPUT':QgsVectorLayer('E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=EAF_03', "eaf_03", "ogr"),
    'OVERLAY':QgsVectorLayer('E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=EAF_04', "eaf_04", "ogr"),
    'OUTPUT':"memory:"
    })
tmp4 = processing.run("native:difference", {
    'INPUT': tmp3['OUTPUT'],
    'OVERLAY': tmp['OUTPUT'],
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"EAF_10\" (geom) sql='
    })
project.addMapLayer(tmp4['OUTPUT'])    
# clip out EAF_04 (Selous) and EAF_01 (Kilimanjaro). Done!
KLC_comments['EAF_10'] = "We took a 10 km buffer around all forest patches around the main target PAs. \
We clipped the landscape to the limits of other adjacent KLCs: EAF_01 and EAF_04."

# EAF_11 (page 191): Ruaha-Rungwa- Kitulo ?-Kipengere - Rungwe NR (301662) - Muhesi GR  + Mufundi Scarp + New Dabaga + Kinsinga Lugaro # 301638, 303531, 301601
# This includes the following PAs: 
#• Ruaha NP (917)
#• Muhezi GR (303338)
#• Kizigo GR (7883)
#• Rungwa GR (555623799)
#• Mbomipa WMA # Ask Rob: Mbomipa = Pawaga-Idodi WMA (DFID) (555549306)
#• Umemarua WMA # should be included in Pawaga-Idodi WMA
# https://www.stzelephants.org/download/human-elephant-conflict/Ruaha-HEC-Assessment-STEP-WC-Full-Report.pdf
#• Kitulo NP (350003)
#• Mpanga Kipengere GR (301661)?
#• Mt Rungwe NR (301662)
KLC_name['EAF_11'] = "Ruaha-Rungwa-Kitulo-Kipengere"
KLC_PA['EAF_11'] = (917, 555623799, 350003, 301661, 301662, 303338 , 555549306, 7883)
wdpa.selectByExpression('"WDPAID" IN (917, 555623799, 7883 , 350003, 301661, 301662, 303338 ,\
    555549306)', 
    QgsVectorLayer.SetSelection)
# TO DO??? Link North and South parts. Problem: mostly cropland
# create site to be added.
eaf_11_sites = QgsVectorLayer("Polygon?crs=epsg:54009&field=fid:int8&field=NAME::string(120)&index=yes",
    "eaf_11_sites", "memory")
# add features
# south
fet = QgsFeature()
fet.setGeometry(QgsGeometry.fromPolygonXY([[
        QgsPointXY(3417446, -1086938),
        QgsPointXY(3416988, -1079382),
        QgsPointXY(3417675, -1069652), 
        QgsPointXY(3418132, -1063814),
        QgsPointXY(3422368, -1063127),
        QgsPointXY(3420651, -1087968), 
        QgsPointXY(3417446, -1086938)]]))
fet.setAttributes([0, "link South"])
eaf_11_sites.dataProvider().addFeatures([fet])
project.addMapLayer(eaf_11_sites)
# merge with wdpa selection
tmp_wdpa = processing.run("native:saveselectedfeatures", {
    'INPUT':wdpa,
    'OUTPUT':"memory:"
    })
# delete attributes
res = tmp_wdpa['OUTPUT'].dataProvider().deleteAttributes(list(range(1, 5)) + list(range(6,len(getFieldsNames(tmp_wdpa['OUTPUT'])))))
tmp_wdpa['OUTPUT'].updateFields()
project.addMapLayer(tmp_wdpa['OUTPUT'])
tmp = processing.run("native:mergevectorlayers", {
    'LAYERS':[tmp_wdpa['OUTPUT'],
        eaf_11_sites],
    'CRS': "EPSG:54009",
    'OUTPUT':"memory:"})
project.addMapLayer(tmp['OUTPUT'])
tmp['OUTPUT'].selectAll()
buffer_selection("EAF_11", layer = tmp['OUTPUT'], buf = 20)

KLC_comments['EAF_11'] = "We took a 20 km buffer around the target PAs and connected the two blocks through a 40 km wide corridor."

# EAF_12 : Moyowosi-Kigosi
KLC_name['EAF_12'] = "Moyowosi-Kigosi"
KLC_PA['EAF_12'] = (7505, 555623782)
wdpa.selectByExpression('"WDPAID" IN (7505, 555623782)', 
    QgsVectorLayer.SetSelection)
# TO DO: include Gombe GCA
# got Kigosi GR polygon from http://africanelephantdatabase.org/population_submissions/68
mo19 = QgsVectorLayer("E:\weyname\BIOPAMA\GIS\data\Original\KLC\MO19_adminstrata\MO19_adminstrata.shp", 'mo_19', 'ogr')
mo19.selectByExpression('"admin" = \'Kigosi G.R\' ', QgsVectorLayer.SetSelection)
# union
tmp = processing.run("native:union",{
    'INPUT': QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'OVERLAY': QgsProcessingFeatureSourceDefinition(mo19.id(), True),
    'OUTPUT': "memory:"
    })
# buffer  
tmp['OUTPUT'].selectAll()
buffer_selection("EAF_12", layer = tmp['OUTPUT'], buf = 10)
KLC_comments['EAF_12'] = "We took a 10 km buffer around the target PAs, including the Kigosi Game Reserve, which is not in the WDPA. \
We retreived its boundary from the AfricanElephantDatabase.org website."
KLC_addLayers['EAF_12'] = ['QgsVectorLayer("E:\weyname\BIOPAMA\GIS\data\Original\KLC\MO19_adminstrata\MO19_adminstrata.shp", "mo_19", "ogr")']

# EAF_13: Nyungwe-Kibira
KLC_name['EAF_13'] = "Nyungwe-Kibira"
KLC_PA['EAF_13'] = (9148, 9161 )
wdpa.selectByExpression('"WDPAID" IN (9148, 9161 )', 
    QgsVectorLayer.SetSelection)
buffer_selection("EAF_13", buf=5) 
#OK
KLC_comments['EAF_13'] = "We took a 5 km buffer around the target PAs."

# EAF_14: Imatonga-Kidepo
KLC_name['EAF_14'] = "Imatonga-Kidepo"
KLC_PA['EAF_14'] = (958, 1369, 2998, 313107, 40602, 14089, 40463)
# Rob: include Imatong and Agaro; keep southern leg
wdpa.selectByExpression('"WDPAID" IN (958, 1369, 2998, 313107, 40602, 14089, 40463)', 
    QgsVectorLayer.SetSelection)
buffer_selection("EAF_14", buf=7)
# OK
KLC_comments['EAF_14'] = "We took a 7 km buffer around the target PAs."

################
# EAF_15: Lake Tanganyika
KLC_name['EAF_15'] = "Lake Tanganyika"
# Rob Olivier:
# Make sure to include iomportant PAs: Luama-Katanga (DRC) 555512065, Gombe NP 
# (TZ 926), Mahale Mts NP (TZ 7521), Kabobo Nat Reserve in DRC (not in WDPA, but between lake and Luama-Katanga) 
# Between the shore of Tanganyika and Luama NP (http://news.janegoodall.org/wp-content/uploads/2017/03/map-showing-borders-of-new-Kabobo-Natural-Reserve-396x512.jpg)
KLC_PA['EAF_15'] = (555512065, 926, 7521, 1092 )
waterBodies.selectByExpression('"NAME_OF_WA" LIKE \'Tanganyika\'', 
    QgsVectorLayer.SetSelection)
wdpa.selectByExpression('"WDPAID" IN (555512065, 926, 7521, 1092 )', 
    QgsVectorLayer.SetSelection)
# union
tmp = processing.run("native:union", {
    'INPUT':QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'OVERLAY': QgsProcessingFeatureSourceDefinition(waterBodies.id(), True),
    'OUTPUT': "memory:"
    })
tmp['OUTPUT'].selectAll()
project.addMapLayer(tmp['OUTPUT'])
buffer_selection("EAF_15", layer=tmp['OUTPUT'], buf = 15)
# clip off CAF_14: difference
tmp = processing.run("native:difference", {
    'INPUT':"E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=EAF_15",
    'OVERLAY':"E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=CAF_14",
    'OUTPUT': "memory:"
    })
# export    
error = QgsVectorLayerExporter.exportLayer(tmp['OUTPUT'], 
    "E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg",
    "ogr", QgsCoordinateReferenceSystem("EPSG:54009"), False, {
    "update":True, "overwrite" : True, "driverName" : 'GPKG', "layerName":"EAF_15"})

KLC_comments['EAF_15'] = "We took a 15 km buffer around the Lake Tanganyika and the surrounding target PAs. We clipped off the CAF_14 KLC."

# EAF_16
KLC_name['EAF_16'] = "Lake Malawi"
KLC_PA['EAF_16'] = (2317)
waterBodies.selectByExpression('"NAME_OF_WA" LIKE \'Malawi\'', 
    QgsVectorLayer.SetSelection)
buffer_selection("EAF_16", waterBodies, buf = 10)
# intersects with SAF_09/10
# clip out intersection
tmp = processing.run("native:difference", {
    'INPUT': "E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=EAF_16",
    'OVERLAY':"E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=SAF_09_10",
    'OUTPUT':"memory:"
    })
# save layer to "EAF_16"
error = QgsVectorLayerExporter.exportLayer(tmp['OUTPUT'], 
    "E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg",
    "ogr", QgsCoordinateReferenceSystem("EPSG:54009"), False, {
    "update":True, "overwrite" : True, "driverName" : 'GPKG', "layerName":"EAF_16"})

KLC_comments['EAF_16'] = "We took a 10 km buffer around Lake Malawi. We clipped off the intersection with KLC SAF_09_10."

# SAF (pages 88-90 of Larger than Elephants)
# use TFCA when available
def tfca_selection(klc, tfca):
    # extract tfca  
    tmp = processing.run("native:extractbyexpression", {
        'INPUT':'E:/weyname/BIOPAMA/GIS/data/Original/tfca/sadc_TFCA_Boundaries_2017.shp',
        'EXPRESSION':tfca,
        'OUTPUT':'TEMPORARY_OUTPUT'})
    # reproject to Mollweide
    tmp1 = processing.run("native:reprojectlayer", {
        'INPUT':tmp['OUTPUT'],
        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:54009'),
        'OUTPUT':'TEMPORARY_OUTPUT'
        })
    # drop attributes
    tmp2 = processing.run("qgis:deletecolumn", {
        'INPUT':tmp1['OUTPUT'],
        'COLUMN':['OBJECTID', 'ABBR', 'TFCA', 'TFCA2', 'STATUS', 'AREA_', 'PERIMETER', 'HECTARES', 'GlobalID', 'TreatyStat', 'PPF', 'Area_ha', 'Area_km2', 'Perimeter_', 'Core_Area', 'name_gis', 'Shape_Leng', 'Shape_Area', 'Area_km2_v', 'Area_ha_v2'],
        'OUTPUT':'TEMPORARY_OUTPUT'})
    # add attribute KLC ID
    tmp3 = processing.run("qgis:advancedpythonfieldcalculator", {
        'INPUT':tmp2['OUTPUT'],
        'FIELD_NAME':'KLC_ID',
        'FIELD_TYPE':2,
        'FIELD_LENGTH':13,
        'FIELD_PRECISION':0,
        'GLOBAL':'',
        'FORMULA':'value = \"' + klc + '\"',
        'OUTPUT':'TEMPORARY_OUTPUT'})
    # dissolve polygons
    tmp4 = processing.run("native:dissolve", {
        'INPUT': tmp3['OUTPUT'],
        'FIELD':['KLC_ID'],
        'OUTPUT':'TEMPORARY_OUTPUT'})
    # delete holes
    output = processing.run("native:deleteholes", {
        'INPUT':tmp4['OUTPUT'],
        'MIN_AREA':0,
        'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"' + klc + '\" (geom) sql='
        })
    return output

# SAF_01: Kavango Zambezi
KLC_name['SAF_01'] = "Kavango Zambezi"
KLC_PA['SAF_01'] = (1085, 1107, 1105, 1991, 600, 601, 7449, 555577555)
tfca_selection("SAF_01", '"ABBR" = \'KAZA TFCA\'') # OK
KLC_comments['SAF_01'] = "We took the limits of the KAZA TFCA."

# SAF_02: Great Limpopo: Limpopo NP, Kruger NP, Gonarezhou
KLC_name['SAF_02'] = "Great Limpopo"
KLC_PA['SAF_02'] = (20295, 873, 1104)
wdpa.selectByExpression('"WDPAID" IN (20295, 873, 1104)', 
    QgsVectorLayer.SetSelection)
tfca_selection("SAF_02", '"ABBR" = \'GLTP\'') # OK (also take in the TF Conservation area that was not included in the KLC)
KLC_comments['SAF_02'] = "We took the limits of the GLTP TFCA."

# SAF_03: Kgalagadi TFNP: Gemsbok, Kalahari Gemsbok
KLC_name['SAF_03'] = "Kgalagadi TFNP"
KLC_PA['SAF_03'] = (7508, 874)
wdpa.selectByExpression('"WDPAID" IN (7508, 874)', 
    QgsVectorLayer.SetSelection)
tfca_selection("SAF_03", '"ABBR" = \'KGTP\'') # ok
KLC_comments['SAF_03'] = "We took the limits of the KGTP TFCA."

# SAF_04: Lower Zambezi - Mana pools 
KLC_name['SAF_04'] = "Lower Zambezi - Mana pools"
KLC_PA['SAF_04'] = (555624126, 2525, 2526, 7962)
wdpa.selectByExpression('"WDPAID" IN (555624126, 2525, 2526, 7962)', 
    QgsVectorLayer.SetSelection)
tfca_selection("SAF_04", '"ABBR" = \'LZMP\'') # ok
KLC_comments['SAF_04'] = "We took the limits of the LZMP TFCA."

# SAF_05: Maloti-Drakensberg
KLC_name['SAF_05'] = "Maloti-Drakensberg"
KLC_PA['SAF_05'] = (7747, 145552)
wdpa.selectByExpression('"WDPAID" IN (7747, 145552)', 
    QgsVectorLayer.SetSelection)
tfca_selection("SAF_05", '"ABBR" = \'MDTFCDA\'') # ok
KLC_comments['SAF_05'] = "We took the limits of the MDTFCDA TFCA."

# SAF_06: Ais-Ais - Richtersveld
KLC_name['SAF_06'] = "Ais-Ais - Richtersveld"
KLC_PA['SAF_06'] = (8785,30851)
wdpa.selectByExpression('"WDPAID" IN (8785,30851)', 
    QgsVectorLayer.SetSelection)
tfca_selection("SAF_06", '"ABBR" = \'ARTP\' AND "TreatyStat" = \'Treaty Signed\'') # ok
KLC_comments['SAF_06'] = "We took the limits of the Nothern part of the ARTP TFCA."

# SAF_07: Lubombo TFCA
KLC_name['SAF_07'] = "Lubombo TFCA"
KLC_PA['SAF_07'] = (7444, 39758, 4652)
wdpa.selectByExpression('"WDPAID" IN (7444, 39758, 4652)', 
    QgsVectorLayer.SetSelection)
buffer_selection("SAF_07")
tfca_selection("SAF_07", tfca= '"ABBR" = \'LUTFCRA\' AND NOT regexp_match("TFCA2" ,\'Songimvelo\')')
# TO DO: keep the tfca without the little patch TFCA2 Songimvelo-Malolotja (OBJECTID 6)
KLC_comments['SAF_07'] = "We took the limits of the LUTFCRA TFCA, without its most Western part (Songimvelo)."


# SAF_08: Chimanimani (Chimanimani NR (MOZ) has no ploygon?)
KLC_name['SAF_08'] = "Chimanimani"
KLC_PA['SAF_08'] = (2532)
wdpa.selectByExpression('"WDPAID" IN (2532)', 
    QgsVectorLayer.SetSelection)
tfca_selection("SAF_08", '"ABBR" = \'CMTFCA\'') # OK
KLC_comments['SAF_08'] = "We took the limits of the CMTFCA TFCA."

# SAF_09: Malawi/Zambia TFCAs: Nyika NP, Vwaza and Marsh Wildlife Reserve (no wdpaid?)
KLC_name['SAF_09_10'] = "Malawi-Zambia TFCA"
KLC_PA['SAF_09_10'] = (34647, 1100, 1091, 780)
wdpa.selectByExpression('"NAME" LIKE \'Marsh\'', 
    QgsVectorLayer.SetSelection)
wdpa.selectByExpression('"WDPAID" IN (34647)', 
    QgsVectorLayer.SetSelection)
#buffer_selection("SAF_09")

tfca_selection("SAF_09_10", tfca = '"ABBR" = \'MZTFCA\'')
# KLC and TFCA very different.
# TO DO: merge with KLC SAF_09, SAF_14, SAF_15 + include GM areas

# SAF_10: Luambe-Lukusizi-Kusungu TFCA 
# Luambe 1100 (in Copernicus HS SAF_14_15)
# Lukusuzi 1091 (in TFCA MZTFCA)
# Kasungu 780 (in TFCA MZTFCA)
# There is however a Luangwa Forest Reserve
wdpa.selectByExpression('"NAME" LIKE \'Luambe\'', 
    QgsVectorLayer.SetSelection)
wdpa.selectByExpression('"WDPAID" IN (1100, 1091, 780)', 
    QgsVectorLayer.SetSelection)
#buffer_selection("SAF_10", buf=10)
# original KLC polygon merged for 9 and 10
# TO DO: include it in the merged MZTFCA, SAF_09, SAF_14, SAF_15
KLC_comments['SAF_09_10'] = "We merged SAF_09 and SAF_10 and took the limits of the MZTFCA."

# SAF_11: Maiombe
KLC_name['SAF_11'] = "Maiombe"
KLC_PA['SAF_11'] = (13694, 555512071, 37044)
wdpa.selectByExpression('"WDPAID" IN (13694, 555512071, 37044)', 
    QgsVectorLayer.SetSelection)
#buffer_selection("SAF_11")
# There is a TFCA on parts of SAF_11 and CAF_04, but NOT cntaining the Luki Biosphere Reserve
tfca_selection("SAF_11", '"ABBR" = \'Maiombe TFCA\'')
# TO DO: merge SAF_11 with CAF_04, including the TFCA. Take the TFCA, add Luki (both the National and MAB, with 1 km buffer) and DRC mangrove (link to TFCA through green patch), clip to the border.
KLC_comments['SAF_11'] = "We took the limits of the Maiombe TFCA."

# SAF_12: Iona-Skeleton coast: Iona NP (AGO), Skeleton Coast (NAM)
KLC_name['SAF_12'] = "Iona-Skeleton coast"
KLC_PA['SAF_12'] = (347, 885)
wdpa.selectByExpression('"WDPAID" IN (347, 885)', 
    QgsVectorLayer.SetSelection)
saf_12 = tfca_selection("SAF_12", tfca = '"ABBR" = \'ISTFCA\'')
# TO DO: include the community conservancies surrounding the TFCA. No buffer on the seaside
wdpa.selectByExpression('"WDPAID" IN (555555525, 555542908, 555555527,\
    555542963, 555542962, 555542943, 555542951, 555542916)', 
    QgsVectorLayer.SetSelection)
# save selection
tmp_wdpa = processing.run("native:saveselectedfeatures", {
    'INPUT':wdpa,
    'OUTPUT':"memory:"
    })
# merge and dissolve
tmp = processing.run("native:mergevectorlayers", {
    'LAYERS':[saf_12, tmp_wdpa['OUTPUT']],
    'CRS': "EPSG:54009",
    'OUTPUT':"memory:"})
project.addMapLayer(tmp['OUTPUT'])
tmp['OUTPUT'].selectAll()
buffer_selection("SAF_12", layer = tmp['OUTPUT'], buf=0)
# delete vertex
saf_12 = iface.addVectorLayer('E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=SAF_12','SAF_12', 'ogr')
saf_12.startEditing()
saf_12.deleteVertex(1,342)
saf_12.deleteVertex(1,341)
saf_12.deleteVertex(1,340)
for iVertex in range(1033,1049):
    saf_12.deleteVertex(1,iVertex)

saf_12.commitChanges()
KLC_comments['SAF_12'] = "We took the limits of the ISTFCA and added the surrounding community conservancies to the KLC."

# SAF_13: Etosha Pan NP
KLC_name['SAF_13'] = "Etosha Pan"
KLC_PA['SAF_13'] = (884)
# include no buffer to the east and south and community conservancies to the west and North
wdpa.selectByExpression('"WDPAID" IN (884, 555547906, 555542954, 555542928, 555542987)', 
    QgsVectorLayer.SetSelection)
buffer_selection("SAF_13", buf=0)
# No TFCA (within Namibia)
saf_13 = iface.addVectorLayer('E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=SAF_13','SAF_13', 'ogr')
saf_13.startEditing()
saf_13.deleteVertex(1,5)
saf_13.deleteVertex(1,4)
saf_13.commitChanges()

KLC_comments['SAF_13'] = "We included the community conservancies surrounding the Etosha National Park."

# SAF_14: North Luangwa NP
#wdpa.selectByExpression('"NAME" LIKE \'Luangwa\'', 
#    QgsVectorLayer.SetSelection)
#wdpa.selectByExpression('"WDPAID" IN (1088)', 
#    QgsVectorLayer.SetSelection)
#buffer_selection("SAF_14")
## TO DO: merge with KLC SAF_09 + include GM areas
#
# SAF_15: South Luangwa NP
#wdpa.selectByExpression('"WDPAID" IN (1086)', 
#    QgsVectorLayer.SetSelection)
#buffer_selection("SAF_15")
## TO DO: merge with KLC SAF_09 + include GM areas
#
# use cop_klc
KLC_name['SAF_14_15'] = "Luangwa"
cop_klc.selectByExpression('"klc_code" = \'SAF_14_15\'')
# fill holes
tmp = processing.run("native:deleteholes", {
    'INPUT': QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),
    'MIN_AREA':0,
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"SAF_14_15\" (geom) sql='
    })
KLC_PA['SAF_14_15'] = (1088, 1086)
KLC_comments['SAF_14_15'] = "For this KLC, we use the Copernicus Hotspot for which land cover has been mapped. "
# Merge SAF_09_10 and SAF_14_15
KLC_name['SAF_09_10_14_15'] = KLC_name['SAF_09_10'] + "-" + KLC_name['SAF_14_15']
tmp = processing.run("native:mergevectorlayers", {
    'LAYERS':[QgsVectorLayer('E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=SAF_09_10', 'SAF_09_10', 'ogr'),
        QgsVectorLayer('E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=SAF_14_15', 'SAF_14_15', 'ogr')],
    'CRS': "EPSG:54009",
    'OUTPUT':"memory:"})
project.addMapLayer(tmp['OUTPUT'])
tmp['OUTPUT'].selectAll()
buffer_selection("SAF_09_10_14_15", layer = tmp['OUTPUT'], buf=0)
KLC_PA['SAF_09_10_14_15'] = (1088, 1086, 34647, 1100, 1091, 780)
KLC_comments['SAF_09_10_14_15'] = "We propose to merge the four KLCs into one."

# SAF_16: Lake Malawi see EAF_16
## TO DO: talk to Rob Olivier. Otherwise, buffer the lake + include surrounding PAs
#waterBodies.selectByExpression('"NAME_OF_WA" LIKE \'Malawi\'', 
#    QgsVectorLayer.SetSelection)
## union
#tmp = processing.run("native:union", {
#    'INPUT':QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
#    'OVERLAY': QgsProcessingFeatureSourceDefinition(waterBodies.id(), True),
#    'OUTPUT': "memory:"
#    })
#tmp['OUTPUT'].selectAll()
#project.addMapLayer(tmp['OUTPUT'])
#buffer_selection("SAF_16", layer=tmp['OUTPUT'], buf = 15)
#

# SAF_17: central Kalahari (+ Khutse GR)
KLC_name['SAF_17'] = "central Kalahari"
KLC_PA['SAF_17'] = (7510, 7507)
wdpa.selectByExpression('"WDPAID" IN (7510, 7507)', 
    QgsVectorLayer.SetSelection)
buffer_selection("SAF_17", buf = 5) # take small buffer, BUT why is there a unexplained part protruding to the west of the KLC>
# No tfca
KLC_comments['SAF_17'] = 'We took a 5 km buffer around the target PAs.'

# SAF_18: Mountain Zebra
KLC_name['SAF_18'] = "Mountain Zebra"
KLC_PA['SAF_18'] = (877, 4035)
#wdpa.selectByExpression('"WDPAID" IN (877)', 
#    QgsVectorLayer.SetSelection)
#buffer_selection("SAF_18")
# all in SA. take in all buffer zone of Zebra and Camdebooo NP. see map fron SANParks
# I roughly digitized the buffer border (I didn't manage to georeference the map because no indication on the CRS)
saf_18 = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/KLC/SAF_18/CNP_MZNP_buffer_mela.gpkg|layername=CNP_MZNP_buffer_mela", "CNP_MZNP_buffer", "ogr")
# copy to SAF_18
saf_18.selectAll()
tmp = processing.run("native:saveselectedfeatures", {
    'INPUT':saf_18,
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"SAF_18\" (geom) sql='
    })
# set KLC_ID to 'SAF_18'
res = tmp['OUTPUT'].dataProvider().addAttributes([QgsField("KLC_ID", QVariant.String)])
tmp['OUTPUT'].updateFields()
editAttribute(tmp['OUTPUT'], "KLC_ID", QgsExpression("'SAF_18'"))
KLC_comments['SAF_18'] = "We considered all the buffer zone of Mount Zebra and Camdeboo National Parks as published on SANParks' website."

# SAF_19: Cangandala NP + Luando NR
KLC_name['SAF_19'] = "Cangandala-Luando"
KLC_PA['SAF_19'] = (351, 3066)
wdpa.selectByExpression('"WDPAID" IN (351, 3066)', 
    QgsVectorLayer.SetSelection)
buffer_selection("SAF_19", buf=20) #OK
# all in angola.
KLC_comments['SAF_19'] = "We took a 20 km buffer around the target PAs."

# SAF_20: Cape Floral
KLC_name['SAF_20'] = "Cape Floral"
# 8+ PAs including 
# Cape Peninsula NP ?? Cape Peninsula Nature Area (NR) 555563629
# De Hoop NR 4029 (not in original KLC)
# Cape Floral Region PAs as WHS 902347
# (MAB Gouritz 555570970)
# fill holes with 
# Walker Bay Whale Sanctuary Marine PA 555563467
# Langberg-Wes Mountain Catchment Area 351401
# Wagenboom NR 555570964
KLC_PA['SAF_20'] = (555563629, 4029, 902347)
wdpa.selectByExpression('"WDPAID" IN (902347, 4029, 555563629, 555563467, 351401, 555570964)', 
    QgsVectorLayer.SetSelection)
buffer_selection("SAF_20", buf=20)
# WHS is larger than original KLC
# OK
KLC_comments['SAF_20'] = "We took a 20 km buffer around target PAs."

# SAF_21: Madagascar forest: 16 PAs, 2 WHS, 
KLC_name['SAF_21'] = "Madagascar Forests"
KLC_PA['SAF_21'] = (303696, 2303, 2304, 2305, 2308, 5021, 20272, 26070, 354013, 303695, 20287, 352249, 903062)
wdpa.selectByExpression('"WDPAID" IN (303696, 2303, 2304, 2305, 2308, 5021, 20272, 26070, 354013, 303695, 20287, 352249,903062)', 
    QgsVectorLayer.SetSelection)
#buffer_selection("SAF_21")
# Copernicus HS
cop_klc.selectByExpression('"klc_code" = \'SAF_21\'')
# fill holes
tmp = processing.run("native:deleteholes", {
    'INPUT': QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),
    'MIN_AREA':0,
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"SAF_21\" (geom) sql='
    })
KLC_comments['SAF_21'] = "For this KLC, we use the Copernicus Hotspot for which land cover has been mapped."

####### 
# WAF: 21 KLCs...
# WAF_01: Niger-Chad-Algeria page 336 (# missing ahaggar)
KLC_name['WAF_01'] = "Desert Niger-Chad-Algeria"
# Termit & Tin Tourma (NER) 17367
# Air and Tenere (NER) 67727
# Addax Sanctuary (NER) 72350
# Ouadi Rimé-Ouadi (TCD) 1250
# Fada Archei (TCD) 9033
# Tassili-n-Ajjer (DZA) 20389
# Ahagghar (DZA) point wdpa. 633887 Km² concerne les communes de 
# Abalessa, In Amguel, Aine Guezzame, Tamanrasset, Tin Zaouatine, Tazrouk, Ideles, In Salah, In Ghar, Fougarta Azouaia
# source: http://www.ppca.dz/index.php/parcs-clulturels-algeriens/pc-du-touat-gourara-tidikelt-2/projet-en-generale
# park entries (postes de contrôle et de surveillance): Tamenghasset (22.2707752,4.554331)(23.0059774,5.6648396), In Salah (27.1955366,2.4753766), 
# Arak ? (24.2529466,2.9547351), Idelès (23.817483,5.9294199), In Azzou, Silet (22.657462,4.5696259),
# Tin Zaouatin (20.4281439,2.0909794), In Guezzam (20.3902377,5.3502117), Timiaouine (20.9286472,1.3568537),
# Tin Tarabine, Amguid (27.0755737,5.8708141) et Zazir
KLC_PA['WAF_01'] = (17367, 9024, 72350, 1250, 9033, 12352)
wdpa.selectByExpression('"WDPAID" IN (17367, 9024, 72350, 1250, 9033, 12352)', 
    QgsVectorLayer.SetSelection)
tmp1 = buffer_selection("WAF_01")

gaul2.selectByExpression('"ADM2_NAME" IN (\'Abalessa\', \'In Amguel\', \
    \'Aine Guezzame\', \'Tamanrasset\', \'Tazrouk\', \'Idles\', \'Fougarta Azouaia\',\'In Guezzam\',\
    \'Arlit\', \'Nokou\', \'Ntiona\', \'Salal\', \'Bilma\') \
     OR ADM2_CODE = 22556',
    QgsVectorLayer.SetSelection)
    #\'Tin Zaouatine\',\'In Salah\', \'In Ghar\',
    # 
# reproject selection
tmp2 = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(gaul2.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':'memory:'
    })
# merge
tmp3 = processing.run("native:mergevectorlayers", {
    'LAYERS':[tmp2['OUTPUT'], tmp1],
    'CRS': "EPSG:54009",
    'OUTPUT':"memory:"})
project.addMapLayer(tmp3['OUTPUT'])
tmp3['OUTPUT'].selectAll()
tmp4 = buffer_selection("WAF_01", buf = 0, layer = tmp3['OUTPUT'])
# clip off Lake Chad WAF 18
tmp = processing.run("native:difference", {
    'INPUT':"E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=WAF_01",
    'OVERLAY':"E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=WAF_18",
    'OUTPUT': "memory:"
    })
# export    
error = QgsVectorLayerExporter.exportLayer(tmp['OUTPUT'], 
    "E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg",
    "ogr", QgsCoordinateReferenceSystem("EPSG:54009"), False, {
    "update":True, "overwrite" : True, "driverName" : 'GPKG', "layerName":"WAF_01"})

KLC_comments['WAF_01'] = "We took a 50 km buffer around the target PAs and included the Level 2 adminitrative units surrounding them. \
We clipped off the intersection with KLC WAF_18 Lake Chad."

## create layer with points of park entrances
#vl = QgsVectorLayer("Point", "temporary_points", "memory")
## set CRS to epsg:4326
#vl.setCrs(QgsCoordinateReferenceSystem(4326))
#pr = vl.dataProvider()
#
## Enter editing mode
#vl.startEditing()
#
## add fields
#pr.addAttributes( [ QgsField("name", QVariant.String)] )
#
## add features
#entrances = {'Tamenghasset': (22.2707752,4.554331),
#            'In Salah': (27.1955366,2.4753766), 
#            'Arak ?': (24.2529466,2.9547351),
#            'Idelès': (23.817483,5.9294199),
#            #'In Azzou':(),
#            'Silet': (22.657462,4.5696259),
#            'Tin Zaouatin': (20.4281439,2.0909794), 
#            'In Guezzam': (20.3902377,5.3502117),
#            'Timiaouine': (20.9286472,1.3568537),
#            #'Tin Tarabine':(),
#            'Amguid': (27.0755737,5.8708141),
#            #'Zazir':()
#            }
#for k, v in entrances.items():
#    fet = QgsFeature()
#    fet.setGeometry( QgsGeometry.fromPointXY(QgsPointXY(v[1],v[0])) )
#    fet.setAttributes([k])
#    pr.addFeatures( [ fet ] )
#
## Commit changes
#vl.commitChanges()
#project.addMapLayer(vl)
# Need to join the areas, then OK

# WAF_02: Senegal delta page 337
KLC_name['WAF_02'] = "Senegal Delta"
KLC_PA['WAF_02'] = (95349, 68151, 352704, 5178, 352610)
wdpa.selectByExpression('"WDPAID" IN (95349, 68151, 352704, 5178, 352610)', 
    QgsVectorLayer.SetSelection)
buffer_selection("WAF_02_20", buf = 20)
# OK
KLC_comments['WAF_02'] = "We took a 20 km buffer around the target PAs."

# WAF_03: Banc d'arguin - Dakhla page 338
KLC_name['WAF_03'] = "Banc d'arguin - Dakhla"
KLC_PA['WAF_03'] = (797, 313473)
wdpa.selectByExpression('"WDPAID" IN (797, 313473)', 
    QgsVectorLayer.SetSelection)
buffer_selection("WAF_03")
# need simplification, then OK.
# edit WAF_03
canvas = qgis.utils.iface.mapCanvas()
waf_03 = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg|layername=WAF_03", "WAF_03", "ogr")
# delete points 253:267; 1:3
L = list()
for i in range(15):
    L.append(267 - i)

L.append(3)
L.append(2)
L.append(1)

waf_03.startEditing()
for iVertex in L:
    waf_03.deleteVertex(1,iVertex)

waf_03.commitChanges()
KLC_comments['WAF_03'] = "We took a 50 km buffer around the target PAs."


# WAF_04: WAPOK page 343 (WHS + buffer (see WHS map) + Togo)
KLC_name['WAF_04'] = "WAPOK (W, Arly, Pendjari, Oti Monduri-Keran"
KLC_PA['WAF_04'] = (124385, 3228, 2253, 3229, 9264, 2252, 2339)
wdpa.selectByExpression('"WDPAID" IN (124385, 3228, 2253, 3229, 9264, 2252, 2339)', 
    QgsVectorLayer.SetSelection)
# Copernicus HS
cop_klc.selectByExpression('"klc_code" = \'WAF_04\'')
# fill holes
tmp = processing.run("native:deleteholes", {
    'INPUT': QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),
    'MIN_AREA':0,
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"WAF_04\" (geom) sql='
    })
KLC_comments['WAF_04'] = "For this KLC, we use the Copernicus Hotspot for which land cover has been mapped. "

# WAF_05: Comoe-Mole
KLC_name['WAF_05'] = "Comoe-Mole"
KLC_PA['WAF_05'] = (7523, 669)
wdpa.selectByExpression('"WDPAID" IN (7523, 669)', 
    QgsVectorLayer.SetSelection)
# It doesn't make sense to connect Comoe with Mole. They are 100 km apart and in between there are a lot of people!
# TO DO: draw a corridor along the rivers + 15 km buffer. but full of people. Ecologically meaningful to put a corridor. Ask Carlo and Jean-Marc Froment (African Parks)
# Cop_klc
cop_klc.selectByExpression('"klc_code" = \'WAF_05\'')
# fill holes
tmp = processing.run("native:deleteholes", {
    'INPUT': QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),
    'MIN_AREA':0,
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"WAF_05\" (geom) sql='
    })
KLC_comments['WAF_05'] = "For this KLC, we use the Copernicus Hotspot for which land cover has been mapped."

# WAF_06: Niokolo-Badiar-Bafing-Baoulé-Faleme page 345
KLC_name['WAF_06'] = "Niokolo-Badiar-Bafing-Baoulé-Faleme"
# chimp area. see https://doi.org/10.1007/978-4-431-53921-6_41
# https://pure.mpg.de/rest/items/item_1555855/component/file_2083695/content.
# Chimps in Fouta Djalon in the forests: Nialama (317286), Fello Digué (29408), 
# Medina Lebere, Balayan-Souroumba (29425), Sincery Oursa (29426), and Bakoun Forest (29435)
# There is a proposal by the wild chimp. found. of a new PA in Guinea: Moyen-Bafing, covering the border with Senegal and Mali.
# Ask them for a polygon, maybe through Noelie Couthard. https://www.wildchimps.org/about-us/where-we-work.html
# Niokolo NP SEN 3045
# Badiar NP GIN 29069
# Bafing NP MLI 317194 (+ PN Wongo 317193 + PN Kouroufing 317195 + ZIC Flawa 317192)
# Boucle du Baoulé NP MLI (MAB 5086)
## used to fill holes WDPAID: 
# Gambie-Koulountou GIN Ramsar 902831
# Mt Loura CF GIN 29412
# Gambi CF GIN 29413
# Reserves de faune et ZIC MLI: 555556063, 555556064, 5555556057, 555556060, 2325, 
## KBAs SitRecID
# 31590
# Bafing MLI 6622
KLC_PA['WAF_06'] = (3045, 29069, 317194, 317193, 317195, 317192, 5086)
kba.selectByExpression('"SitRecId" IN (31590, 6622)', QgsVectorLayer.SetSelection)
# reproject selection
tmp1 = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(kba.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':"memory:"
    })
# delete attributes except 1
res = tmp1['OUTPUT'].dataProvider().deleteAttributes(list(range(1, len(getFieldsNames(tmp1['OUTPUT'])))))
tmp1['OUTPUT'].updateFields()
    
wdpa.selectByExpression('"WDPAID" IN (3045, 29069, 317194, 317193, 317195, 317192, 5086, \
    902831, 29412, 29413, 555556063, 555556064, 555556057, 555556060, 2325,\
    317286, 29435)',
    #29437, 29408, 29425, 29426)', 
    QgsVectorLayer.SetSelection)
# save selection
tmp2 = processing.run("native:saveselectedfeatures", {
    'INPUT':wdpa.id(),
    'OUTPUT':"memory:"
    })
# delete attributes except 1
res = tmp2['OUTPUT'].dataProvider().deleteAttributes(list(range(1, len(getFieldsNames(tmp2['OUTPUT'])))))
tmp2['OUTPUT'].updateFields()

# approximate WCF proposed Moyen-Bafing PA + fill sites
bafing = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/KLC/WAF_06/WCF_proposed_bafing.gpkg|layername=WCF_proposed_bafing", "WCF_proposed_bafing", "ogr")
# merge
tmp = processing.run("native:mergevectorlayers", {
    'LAYERS':[tmp1['OUTPUT'], # KBA
        tmp2['OUTPUT'], # wdpa
        bafing],
    'CRS': "EPSG:54009",
    'OUTPUT':"memory:"})
# buffer selection
tmp['OUTPUT'].selectAll()
project.addMapLayer(tmp['OUTPUT'])
waf06 = buffer_selection("WAF_06", buf=25, layer = tmp['OUTPUT'])
# I wonder what sense it has to connect Baoulé (savanah with Bafing)
# Do I need to include the Faleme river North of Guinea?
KLC_comments['WAF_06'] = "We took a 25 km buffer around the target PAs, including the Moyen-Bafing PA, proposed by the World Chimpanzee Foundation in Guinea."

# WAF_07: Gourma-Sahel-Inner Niger page 346
KLC_name['WAF_07'] = "Gourma-Sahel-Inner Niger"
# TO DO: from the elephants movements maps, draw the KLC (OK with 20 km buffer around Gourma and Sahel; see also report sent by Conrad, page 26.);
# (good example of community conservation)
# include 5 IBAs that are in the Niger inner Delta, near Timbuktu
# https://www.wild.org/mali-elephants/
KLC_PA['WAF_07'] = (2321, 3225)
wdpa.selectByExpression('"WDPAID" IN (2321, 3225)', 
    QgsVectorLayer.SetSelection)
tmp1 = buffer_selection("WAF_07_1", buf = 25) # OK but

# I digitized the ref points of the Ramsar site Niger inner Delta https://rsis.ramsar.org/ris/1365
rnid = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/KLC/WAF_07/ramsar_digitize.gpkg|layername=ramsar_digitize", "Niger delta ramsar", "ogr")
tmp =processing.run("native:reprojectlayer", {
    'INPUT':rnid,         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':"memory:"
    })
tmp['OUTPUT'].selectAll()    
project.addMapLayer(tmp['OUTPUT'])
tmp2 = buffer_selection("WAF_07_2", layer = tmp['OUTPUT'], buf = 5) # OK but

# Tombouctou KBA is missing from Ramsar site but is in the text
kba.selectByExpression('"SitRecID" IN (6607)', 
    QgsVectorLayer.SetSelection)
    # reproject selection
tmp =processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(kba.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':"memory:"
    })
tmp['OUTPUT'].selectAll()    
project.addMapLayer(tmp['OUTPUT'])
tmp3 = buffer_selection("WAF_07_3", layer = tmp['OUTPUT'], buf = 20) # OK but

# merge layers
# merge layers and dissolve
tmp = processing.run("native:mergevectorlayers", {
    'LAYERS':[tmp1['OUTPUT'],
        tmp2['OUTPUT'],
        tmp3['OUTPUT']],
    'CRS': "EPSG:54009",
    'OUTPUT':"memory:"})
# dissolve
tmp4 = processing.run("native:dissolve", {
    'INPUT': tmp['OUTPUT'],
    'OUTPUT': "memory:"})
editAttribute(tmp4['OUTPUT'], "KLC_ID", QgsExpression("'WAF_07'"))
# fill holes
tmp5 = processing.run("native:deleteholes", {
    'INPUT': tmp4['OUTPUT'],
    'MIN_AREA':0,
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"WAF_07\" (geom) sql='
    })
KLC_comments['WAF_07'] = "We took a 25 km buffer around the target PAs, and included a 5 km buffer around the Ramsar site of the Niger Inner Delta and a 20 km buffer around the Tombouctou Key Biodiversity Area."

# WAF_08: Lion KLC page 347
KLC_name['WAF_08'] = "Lion KLC"
KLC_PA['WAF_08'] = (819, 1332)
#wdpa.selectByExpression('"WDPAID" IN (819, 1332)', # NOT IN ORIGINAL klc: , 6955, 6956, 7957
#    QgsVectorLayer.SetSelection)
#buffer_selection("WAF_08", buf=10)
# with Conrad we said 10, but I increased to 20 to connect both parts of the Kiainji NP
# Benin part not in the original KLC but in the text, suggested as place to explore... Should it be included?
# select polygons from lion_areas from Riggio2013
lion_areas = QgsVectorLayer("E:/weyname/BIOPAMA/GIS/data/Original/lions/Lion_areas/lion_areas.shp", "lion_areas", "ogr")
lion_areas.selectByExpression('"ID" IN (7, 8)', # NOT IN ORIGINAL klc: 4
    QgsVectorLayer.SetSelection)
# reproject selection
tmp =processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(lion_areas.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':"memory:"
    })
tmp['OUTPUT'].selectAll()    
project.addMapLayer(tmp['OUTPUT'])
buffer_selection("WAF_08", layer = tmp['OUTPUT'], buf = 10)    
KLC_comments['WAF_08'] = "We took a 10 km buffer around the lion areas corresponding to the target PAs, as published by Riggio (2013)."

# WAF_09: Volta (connect WAPO with ComoeKLC) page 348
KLC_name['WAF_09'] = "Volta Trans-Boundary Ecosystem"
KLC_PA['WAF_09'] = (1049, 28556, 303940, 26544, 26443, 26501)
wdpa.selectByExpression('"WDPAID" IN (1049, 28556, 303940, 26544, 26443, 26501, \
    2342, 26535, 303938, 28535, 26528, 26536, 26547, 303941, 26546, 26551, 303942, \
    26552, 28555 )', 
    QgsVectorLayer.SetSelection)
tmp = processing.run("native:saveselectedfeatures", {
    'INPUT':wdpa.id(),
    'OUTPUT':"memory:"
    })
# delete attributes except 1
res = tmp['OUTPUT'].dataProvider().deleteAttributes(list(range(1, len(getFieldsNames(tmp['OUTPUT'])))))
tmp['OUTPUT'].updateFields()

# The Ranch Nazinga isn't in the WDPA, only the Sissili clas.forest. The ranch was is not included in the 2015 KLC!
# entrances of the ranch are here: https://goo.gl/maps/zZ9gytnh3hG2 and https://goo.gl/maps/6hrq7sfrJE92
# recent photo: https://www.google.it/maps/place/Ranch+de+Nazinga/@11.1577484,-1.6106495,3a,75y,90t/data=!3m8!1e2!3m6!1sAF1QipMjgS7r2wXZkLJgo2XjwhN1dliwF-EnHJUSGH6x!2e10!3e12!6shttps:%2F%2Flh5.googleusercontent.com%2Fp%2FAF1QipMjgS7r2wXZkLJgo2XjwhN1dliwF-EnHJUSGH6x%3Dw203-h152-k-no!7i4618!8i3464!4m5!3m4!1s0xe2cf1e27e7b30ed:0xf6e412a90ae8083!8m2!3d11.1577479!4d-1.6106504#
# TO DO: use the KBAs; buffer 15 km; connect to WAPOK and Comoe-Mole along the river (but it doesn't seem possible, full of people)
kba.selectByExpression('"SitRecID" IN (6028, 6340, 6337)', 
    QgsVectorLayer.SetSelection)
# reproject selection
tmp1 = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(kba.id(), True),# layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':"memory:"
    })
# delete attributes except 1
res = tmp1['OUTPUT'].dataProvider().deleteAttributes(list(range(1, len(getFieldsNames(tmp1['OUTPUT'])))))
tmp1['OUTPUT'].updateFields()

riv.selectByExpression('"ARCID" IN (350693, 350776, 350921, 351056, 351430,\
    351683, 352236, 352306, 352386, 352971, 353048, 353049, 353222, 360797, \
    361906, 362763, 363221, 363461, 363618, 364360, 364516, 365025, 344095, \
    344647, 344723, 344896, 345701, 345829, 347361, 347706, 347988, 348383, \
    348537, 348696, 350056, 356058)', 
    QgsVectorLayer.SetSelection)
# lines to polygon
tmp2 = processing.run("native:reprojectlayer", {
    'INPUT': QgsProcessingFeatureSourceDefinition(riv.id(), True),
    'TARGET_CRS': 'EPSG:54009',
    'OUTPUT': 'memory:'})
tmp3 = processing.run("qgis:buffer", {
    'INPUT':tmp2['OUTPUT'],
    'DISTANCE':500, # meters
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':False,
    'OUTPUT':'memory:'
    })
    
# merge
tmp4 = processing.run("native:mergevectorlayers", {
    'LAYERS':[
        tmp['OUTPUT'], # wdpa
        tmp1['OUTPUT'], # kba
        tmp3['OUTPUT'] # riv
        ],
    'CRS': "EPSG:54009",
    'OUTPUT': "memory:"
    })
project.addMapLayer(tmp4['OUTPUT'])
tmp4['OUTPUT'].selectAll()
tmp5 = buffer_selection("WAF_09", layer = tmp4['OUTPUT'], buf = 15)
tmp6 = processing.run("native:difference", {
    'INPUT': tmp5['OUTPUT'],
    'OVERLAY': cop_klc,
    'OUTPUT': "memory:"
    })
project.addMapLayer(tmp6['OUTPUT'])
# save layer to "WAF_09"
error = QgsVectorLayerExporter.exportLayer(tmp6['OUTPUT'], 
    "E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg",
    "ogr", QgsCoordinateReferenceSystem("EPSG:54009"), False, {
    "update":True, "overwrite" : True, "driverName" : 'GPKG', "layerName":"WAF_09"})

KLC_comments['WAF_09'] = "We took a 15 km  buffer around target PAs, \
including the Reanch Nazinga, which is not in the WDPA. \
This KLC is meant as a continuum between the WAPOK and Comoé-Molé complexes. \
Therefore we connect them through a 25 km wide corridor."

# WAF_10: Tai-Sapo page 354
KLC_name['WAF_10']="Tai-Sapo"
KLC_PA['WAF_10'] = (721, 9170, 7409)
wdpa.selectByExpression('"WDPAID" IN (721, 9170, 7409)', 
    QgsVectorLayer.SetSelection)
#buffer_selection("WAF_10", buf=10)
# TO DO:  add the krahn forest from Grebo-Krahn NP (2017) see waf_10_sites (from map of proposed Grebo-Krahn NP); draw corridor between Sapo and Grebo-Krahn.
cop_klc.selectByExpression('"klc_code" = \'WAF_10\'')
# fill holes
tmp = processing.run("native:deleteholes", {
    'INPUT': QgsProcessingFeatureSourceDefinition(cop_klc.id(), True),
    'MIN_AREA':0,
    'OUTPUT':'ogr:dbname=\'E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg\' table= \"WAF_10\" (geom) sql='
    })
#OK
KLC_comments['WAF_10'] = "For this KLC, we use the Copernicus Hotspot for which land cover has been mapped. "

# WAF_11: Gola-Lofa-Foya page 356 + WAF_xx: Mano-Wologizi-Wonegizi-Ziama page 356
KLC_name['WAF_11'] = "Gola-Lofa-Foya-Mano-Wologizi-Wonegizi-Ziama"
# Conrad suggests to have only one KLC for both areas.

# add Wologizi Mountain Range (8.11N, 9.9278W), not on WDPA??? see IBA polygon on birdlife.org
# big iron ore deposit
# There have already been two failed attempts to grant out the mountain range as a concession. The Government of Liberia, in 2013, tried to secretly award Wologizi to Jindal Steel & Power Limited, and the recent row to secretly award Wologizi to Sable Mining Company by changing Liberia's procurement law.
# Community members have succeeded in slowing down, delaying and in some instances holding back the monstrous pace of large-scale concessions development in Liberia.
# source https://www.liberianobserver.com/columns/women/the-challenges-of-navigating-centuries-of-taboos/
# listed as project on egcsouthafrica.com

# Fauna and Flora International have a USAID project ZWW Forest landscape conservation (see report)
KLC_PA['WAF_11'] = (555542335, 9171, 555512165, 7414, 29066)
wdpa.selectByExpression('"WDPAID" IN (555542335, 9171, 555512165,\
    7414, 29066)', 
    QgsVectorLayer.SetSelection)
# union with IBA Wologizi
iba.selectByExpression('"OBJECTID" = 3627', QgsVectorLayer.SetSelection)
tmp = processing.run("native:union", {
    'INPUT': QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'OVERLAY': QgsProcessingFeatureSourceDefinition(iba.id(), True),
    'OUTPUT': "memory:"
    })
project.addMapLayer(tmp['OUTPUT'])
tmp['OUTPUT'].selectAll()
tmp1 = buffer_selection("WAF_11", buf = 10, layer = tmp['OUTPUT'])
#OK
KLC_comments['WAF_11'] = "We merged the Gola-Lofa-Foya complex with the Mano-Wologizi-Wonegizi-Ziama landscape.\
We took a 10 km buffer around the target PAs, including the Wologizi mountains KBA, which is not in the WDPA."

# WAF_12: Outamba-Kilimi page 358
KLC_name['WAF_12'] = "Outamba-Kilimi"
KLC_PA['WAF_12'] = (7417, 555555549, 10733, 29378, 29376)
wdpa.selectByExpression('"WDPAID" IN (7417, 555555549, 10733, 29378, 29376)', 
    QgsVectorLayer.SetSelection)
buffer_selection("WAF_12", buf=15)
# OK!
KLC_comments['WAF_12'] = "We took a 15 km buffer around the target PAs."

# WAF_13: Ankasa-Bia-Nini Suhien page 359
KLC_name['WAF_13'] = "Ankasa-Bia-Nini Suhien"
# Ghana: most WDPA polygons are all shifted!!!
# Bia NP 672
# Nini-Suhien NP 5173, now Ankasa?
# copy Drw River to layer and shift polygon
KLC_PA['WAF_13'] = (5173,672, 40829)
wdpa.selectByExpression('"WDPAID" IN (5173,672, 40829)', 
    QgsVectorLayer.SetSelection)
# save selection to layer
tmp = processing.run("native:saveselectedfeatures", {
    'INPUT':wdpa.id(),
    'OUTPUT':"memory:"
    })
project.addMapLayer(tmp['OUTPUT'])
tmp['OUTPUT'].selectAll()
# manually shift feature.
buffer_selection("WAF_13", layer = tmp['OUTPUT'], buf=1)
# 2 blocks
# OK
KLC_comments['WAF_13'] = "We took a 1 km  buffer around the target PAs. These are key conservation areas in Ghana requiring high priority direct support."

# WAF_14:  rio cacheu-cufada-cantanhez-rio buba-iles tristao page 364
KLC_name['WAF_14'] = "Rio Cacheu-Bijagos"
KLC_PA['WAF_14'] = (33046, 33048, 317051, 33049, 11611, 67984)
# select listed IBAs:
iba.selectByExpression('"FinCode" IN (\'GW001\', \'GW004\', \'GW005\', \'GW008\', \'GN004\')', 
    QgsVectorLayer.SetSelection)
# Bijagos MAB 145507 /National 11611. Ither Pas cover the IBAs
wdpa.selectByExpression('"WDPAID" IN (33046, 33048, 317051, 33049, 11611, 67984)', 
    QgsVectorLayer.SetSelection)
# select mangrove KBAs (+ those correspong to the selected IBAs)
kba.selectByExpression('"SitRecID" IN (6363, 6383, 6384, 6386, 6387, 6388, 6390)',
    QgsVectorLayer.SetSelection)    
# reproject selection
tmp = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(kba.id(), True),# layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':"memory:"
    })
# delete attributes except 1
res = tmp['OUTPUT'].dataProvider().deleteAttributes(list(range(1, len(getFieldsNames(tmp['OUTPUT'])))))
tmp['OUTPUT'].updateFields()
# select more mangrove MANUALLY
tmp1 = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(gmw.id(), True),# layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':"memory:"
    })
res = tmp1['OUTPUT'].dataProvider().deleteAttributes(list(range(1, len(getFieldsNames(tmp1['OUTPUT'])))))
tmp1['OUTPUT'].updateFields()
project.addMapLayer(tmp1['OUTPUT'])
# buffer
tmp11 = processing.run("native:buffer",{
        'INPUT':QgsProcessingFeatureSourceDefinition(tmp1['OUTPUT'].id(), True),
        'DISTANCE':5*1000,
        'SEGMENTS':5,
        'END_CAP_STYLE':0,
        'JOIN_STYLE':0,
        'MITER_LIMIT':2,
        'DISSOLVE':True,
        'OUTPUT':'memory:'
        })
# save wdpa selelction to layer
tmp2 = processing.run("native:extractbyexpression", {
    'INPUT': wdpa,
    'EXPRESSION':'"WDPAID" IN (33046, 33048, 317051, 33049, 11611, 67984)',
    'OUTPUT': "memory:"
    })
res = tmp2['OUTPUT'].dataProvider().deleteAttributes(list(range(1, len(getFieldsNames(tmp2['OUTPUT'])))))
tmp2['OUTPUT'].updateFields()
# merge
tmp4 = processing.run("native:mergevectorlayers", {
    'LAYERS':[
        tmp['OUTPUT'], # kba
        tmp11['OUTPUT'], # gmw
        tmp2['OUTPUT'], # wdpa
        #tmp3['OUTPUT'] # seagrass
        ],
    'CRS': "EPSG:54009",
    'OUTPUT': "memory:"
    })
project.addMapLayer(tmp4['OUTPUT'])
tmp4['OUTPUT'].selectAll()
tmp5 = buffer_selection("WAF_14", layer = tmp4['OUTPUT'], buf = 5)
waf14 = tmp5['OUTPUT']

# add seagrass
seagr.selectByExpression('"ISO3" IN (\'GNB\')',
    QgsVectorLayer.SetSelection)    
# reproject selection
tmp3 = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(seagr.id(), True),# layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':"memory:"
    })
# delete attributes except 1
res = tmp3['OUTPUT'].dataProvider().deleteAttributes(list(range(1, len(getFieldsNames(tmp3['OUTPUT'])))))
tmp3['OUTPUT'].updateFields()
# merge with previous WAF_14
tmp6 = processing.run("native:mergevectorlayers", {
    'LAYERS':[
        waf14, # wdpa
        tmp3['OUTPUT'] # seagrass
        ],
    'CRS': "EPSG:54009",
    'OUTPUT': "memory:"
    })
project.addMapLayer(tmp6['OUTPUT'])
tmp6['OUTPUT'].selectAll()
buffer_selection("WAF_14", layer = tmp6['OUTPUT'], buf = 0)
KLC_comments['WAF_14'] = "We took a 5 km buffer around target PAs and KBA, and included mangrove and seagrass beds."
# TO DO: Link both areas (include mangroves and seagrass); clip to GIN border.

# WAF_15: Saloum page 365
KLC_name['WAF_15'] = "Saloum"
KLC_PA['WAF_15'] = (68153)
# IBA SN013 1800 km2
# add mangrove IBAs GMB003 and SN012
iba.selectByExpression('"FinCode" IN (\'SN013\', \'GM003\', \'SN012\')', 
    QgsVectorLayer.SetSelection)
# save selection
tmp = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(iba.id(), True),# layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':"memory:"
    })
wdpa.selectByExpression('"WDPAID" IN (68153)', # Delta Saloum Ramsar (probably not correct because crosses border)
    QgsVectorLayer.SetSelection)
# union
tmp1 = processing.run("native:union", {
    'INPUT':tmp['OUTPUT'],
    'OVERLAY':QgsProcessingFeatureSourceDefinition(wdpa.id(), True),
    'OUTPUT': "memory:"
    })
project.addMapLayer(tmp1['OUTPUT'])
tmp1['OUTPUT'].selectAll()
buffer_selection("WAF_15", layer = tmp1['OUTPUT'], buf = 5)
KLC_comments['WAF_15'] = "We took a 5 km buffer around the Saloum Delta KBA."

# WAF_16: Basse Casamance page 365
KLC_name['WAF_16'] = "Basse Casamance"
KLC_PA['WAF_16'] = (868)
wdpa.selectByExpression('"WDPAID" IN (868)', 
    QgsVectorLayer.SetSelection)
# Basse Casamance NP not completely in original KLC
# TO DO: include 2 KBAs + all the mangrove in the Delta
kba.selectByExpression('"OBJECTID" IN (2044,2045)', 
    QgsVectorLayer.SetSelection)
# gmw manual selection
# gmw.selectByExpression("ogc_fid" IN seq(78529, 80129)
# layer in epsg:4326
# save selection to Mollweide
tmp = processing.run("native:reprojectlayer", {
    'INPUT':QgsProcessingFeatureSourceDefinition(gmw.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':"memory:"
    })
project.addMapLayer(tmp['OUTPUT'])
tmp['OUTPUT'].selectAll()
buffer_selection("WAF_16", layer = tmp['OUTPUT'], buf = 5)
KLC_comments['WAF_16'] = "We took a 5 km buffer around the target KBAs, including the surrounding mangrove."

#####
# WAF_17: Keta Songor page 365
KLC_name['WAF_17'] = "Keta-Songor"
KLC_PA['WAF_17'] = (67970, 555547583)
wdpa.selectByExpression('"WDPAID" IN (67970, 555547583)', 
    QgsVectorLayer.SetSelection)
buffer_selection("WAF_17", buf = 7)
KLC_comments['WAF_17'] = "We took a 7 km buffer around the target PAs."
# took 7 instead of 7 to avoid manual joining of polygons

# WAF_18: Lake Chad (page 342)
KLC_name['WAF_18'] = "Lake Chad"
KLC_PA['WAF_18'] =  (555542689, 903113)
wdpa.selectByExpression('"WDPAID" IN (555542689, 903113)', 
    QgsVectorLayer.SetSelection)
#buffer_selection("WAF_18")
waterBodies.selectByExpression('"NAME_OF_WA" LIKE \'Chad\'', 
    QgsVectorLayer.SetSelection)
buffer_selection("WAF_18", waterBodies, buf=20)
# OK
KLC_comments['WAF_18'] = "We took a 20 km buffer around Lake Chad."

# WAF_19: Hadeja-Nguru (page????) KLC not on on the KBA Hadeja-Nguru Wetlands (FinCode = NG021)!!!!
KLC_name['WAF_19'] = "Hadeja-Nguru"
KLC_PA['WAF_19'] = (903105)
wdpa.selectByExpression('"WDPAID" IN (903105)', 
    QgsVectorLayer.SetSelection)
buffer_selection("WAF_19", buf=30)
# OK
KLC_comments['WAF_19'] = "We took a 30 km buffer around the target wetland."

# WAF_20: Sherbro and Turtle page 365 
KLC_name['WAF_20'] = "Sherbro and Turtle Islands"
# No PAs, no KBAs, no water body, selec the island manually?
KLC_PA['WAF_20'] = ()
wdpa.selectByExpression('"WDPAID" IN ()', 
    QgsVectorLayer.SetSelection)
# select gaul2 and break multipolygon
gaul2.selectByExpression('"ADM2_CODE" = 25415')
# save selected features and reproject
tmp = processing.run("native:reprojectlayer", {
    'INPUT': QgsProcessingFeatureSourceDefinition(gaul2.id(), True),         # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54009),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':"memory:"
    })
tmp1 = processing.run("native:multiparttosingleparts", {
    'INPUT':tmp['OUTPUT'],
    'OUTPUT':"memory:"
    })

project.addMapLayer(tmp1['OUTPUT'])
# Select manually
buffer_selection("WAF_20", tmp1['OUTPUT'], buf = 2)
# encompass mangrove, part seagrass beds. TO DO
KLC_comments['WAF_20'] = "We took a 2 km buffer around the Sherbro Island and the islets of the Turtle Bank."

# WAF_21: Mount Nimba page 355
KLC_name['WAF_21'] = "Mount Nimba"
KLC_PA['WAF_21'] = (1295, 29067, 20175, 9176)
wdpa.selectByExpression('"WDPAID" IN (1295, 29067, 20175, 9176)', 
    QgsVectorLayer.SetSelection)
buffer_selection("WAF_21", layer = wdpa, buf = 5)
# OK.
KLC_comments['WAF_21'] = "We took a 5 km buffer around the target Pas."

# save attributes dictionaries to json
import json
# write data
with open('../output/KLC_name.txt', 'w') as f:
    json.dump(KLC_name,f)

f.closed 

with open('../output/KLC_comments.txt', 'w') as f:
    json.dump(KLC_comments,f)

f.closed 

with open('../output/KLC_PA.txt', 'w') as f:
    json.dump(KLC_PA,f)

f.closed 


with open('../output/KLC_addLayers.txt', 'w') as f:
    json.dump(KLC_addLayers,f)

f.closed 



