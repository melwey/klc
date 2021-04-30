# load all layers from geopkg and merge/union them
# easier to create layer from selected features in various layers.

import re
from osgeo import ogr
import json
from datetime import date

# Get the project instance
project = QgsProject.instance()
project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))


# functions
def editAttribute(layer, fieldName, expression):
    index = layer.dataProvider().fieldNameIndex(fieldName)
    context = QgsExpressionContext()
    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
    layer.startEditing()
    for feature in layer.getFeatures():
        context.setFeature(feature)
        value = expression.evaluate(context)
        layer.changeAttributeValue(feature.id(), index, value)
        layer.updateFeature(feature)
    layer.commitChanges()

def area2Field(layer, fieldName):
    index = layer.dataProvider().fieldNameIndex(fieldName)
    layer.startEditing()
    for feature in layer.getFeatures():
        d = QgsDistanceArea()
        value = d.measurePolygon(feature.geometry().asPolygon()[0])
        layer.changeAttributeValue(feature.id(), index, value)
    layer.commitChanges()

def getFieldsNames(layer):
    fields = []
    for field in layer.fields():
      fields = fields + [field.name()]
    return(fields)

# find path
import os
print(os.path.dirname(os.path.realpath('__file__')))
# not working so set path manually
# set as working directory
#chdir(os.path.dirname(os.path.realpath('__file__')))
os.chdir("/Users/mela/JRCbox/BIOPAMA/KLC_Africa/pyCode")
os.getcwd()

# load layers
databasepath = r"../output/spatial_data/klc_buffer_wdpa_54009.gpkg" # r"E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_buffer_wdpa_54009.gpkg"
conn = ogr.Open(databasepath)
klc_new = dict()
for i in conn:
    name = i.GetName()
    if re.search("sites",name):
        continue
    else :
        if re.search("AF", name):
            klc_new[i.GetName()] = QgsVectorLayer(databasepath + "|layername=" + i.GetName(), i.GetName(), 'ogr')

klc_new_clean = dict()
for klc,layer in klc_new.items():
    # set crs
    crs = layer.crs()
    if not( crs.isValid()) :
        crs.createFromId(54009)
        layer.setCrs(crs)
    # select all
    layer.selectAll()
    # get features
    selected_ids = layer.selectedFeatureIds()
    memory_layer = layer.materialize(QgsFeatureRequest().setFilterFids(layer.selectedFeatureIds()))
    # delete attributes and set KLC_ID
    res = memory_layer.dataProvider().deleteAttributes(list(range(0, len(getFieldsNames(memory_layer)))))
    res = memory_layer.dataProvider().addAttributes([QgsField("KLC_ID", QVariant.String), QgsField("Area_km2", QVariant.Double)])
    memory_layer.updateFields()
    ###area2Field(memory_layer, "Area_km2")
    editAttribute(memory_layer, "KLC_ID", QgsExpression(klc))
    # put memory_layer in dict
    klc_new_clean[klc] = memory_layer

# changes to KLC to be documented!!!

# add feature to scratch layer
### try merge layers (hoping the attributes are OK)
tmp = processing.run("native:mergevectorlayers", {
    'LAYERS':list(dict.values(klc_new_clean)),
    'CRS': "EPSG:54009",
    'OUTPUT':"memory:"})
project.addMapLayer(tmp['OUTPUT'])

KLC_new = tmp['OUTPUT']
KLC_new.setName("KLC_new")
# delete attributes
#editAttribute(KLC_new, "KLC_ID", QgsExpression('@layer'))
# KLC_ID
with edit(KLC_new):
    for f in KLC_new.getFeatures():
        f['KLC_ID'] = f['layer']
        KLC_new.updateFeature(f)

# area
#"Area_km2" round($area*1e-6)
with edit(KLC_new):
    for f in KLC_new.getFeatures():
        d = QgsDistanceArea()
        value = d.measurePolygon(f.geometry().asPolygon()[0])
        f['Area_km2'] = value
        KLC_new.updateFeature(f)

# do manually since $area does not work with pyqgis
# delete fields
KLC_new.dataProvider().deleteAttributes([2,3])

# check geometries validity. All seems fine.
##
# save to gpkg
error = QgsVectorLayerExporter.exportLayer(KLC_new, 
    "../output/spatial_data/klc_buffer_wdpa_54009.gpkg",
    "ogr", QgsCoordinateReferenceSystem("EPSG:54009"), False, {
    "update":True, "overwrite" : True, "driverName" : 'GPKG', "layerName":"KLC_"+ date.today().strftime("%Y%m%d")})

# reproject to epsg:4326 and save to gpkg
tmp = processing.run("native:reprojectlayer", {
    'INPUT':KLC_new,# layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(4326),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':"../output/spatial_data/klc_" + date.today().strftime("%Y%m%d") + "_proposal.gpkg"
    })


# attached KLC_comments, KLC_name and KLC_PA to layer
klc_new = iface.addVectorLayer("../output/spatial_data/klc_" + date.today().strftime("%Y%m%d") + "_proposal.gpkg|layername=klc_" + date.today().strftime("%Y%m%d") +"_proposal", "KLC_today", "ogr")
with open('../output/KLC_comments.txt', 'r') as f:
    KLC_comments = json.load(f)

f.closed

with open('../output/KLC_PA.txt', 'r') as f:
    KLC_PA = json.load(f)

f.closed

with open('../output/KLC_name.txt', 'r') as f:
    KLC_name = json.load(f)

f.closed


# Edit
klc_new.startEditing()
# create new fields
res = klc_new.dataProvider().addAttributes([QgsField("KLC_name", QVariant.String),QgsField("Comments", QVariant.String), QgsField("target_PAs", QVariant.String), QgsField("fid_klc", QVariant.Int)])
klc_new.updateFields()
index_n = klc_new.dataProvider().fieldNameIndex("KLC_name")
index_c = klc_new.dataProvider().fieldNameIndex("Comments")
index_pa = klc_new.dataProvider().fieldNameIndex("target_PAs")
index_f = klc_new.dataProvider().fieldNameIndex("fid_klc")
def get_fid_klc(arg):
    switcher = {
        'C': '1',
        'E': '2',
        'S': '3',
        'W': '4'}
    return(int(switcher.get(arg[0],'0') + arg[4:6]))

for f in klc_new.getFeatures():
    klc = f["KLC_ID"]
    try:
        r=klc_new.changeAttributeValue(f.id(), index_n, KLC_name[klc])
        r=klc_new.changeAttributeValue(f.id(), index_c, KLC_comments[klc])
        r=klc_new.changeAttributeValue(f.id(), index_pa, format(KLC_PA[klc]))
        r=klc_new.changeAttributeValue(f.id(), index_f, get_fid_klc(klc))
    except:
        print("no KLC "+klc)
        pass
# i've manually deleted WAF_xx, which is the Mano-Wologizi-Wonegizi-Ziama landscape already in WAF_11, and all former KLCs that have been merged into bigger polygons

klc_new.commitChanges()

## manually exported to shp
#
## save as raster
## GDAL command:
## gdal_rasterize -l klc_201909_proposal -a fid_klc -ts 8280.0 7440.0 -a_nodata 0.0 -te -18.0 -34.99999999999997 50.99999999999997 27.0 -ot Int16 -of GTiff -co COMPRESS=PACKBITS E:/weyname/BIOPAMA/GIS/KLC_Africa/output/spatial_data/klc_201909_proposal.gpkg E:/weyname/BIOPAMA/GIS/data/Processed/KLC/Africa/klc_201909/klc_201909_30sec_Int16.tif
#
## WRITE report
## loop on KLC
## print layout with new and old
## comments from script comments?
#