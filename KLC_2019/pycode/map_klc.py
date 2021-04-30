# map KLC old and new

import qgis.utils
from qgis.gui import *

import processing
import numpy as np
import os
import json

# set current directory
#os.chdir("E:/weyname/BIOPAMA/GIS/KLC_Africa/pyCode")
os.chdir("C:/Users/weyname/jrcbox/BIOPAMA/KLC_Africa/pyCode")
print(os.getcwd())

# Get the project instance
project = QgsProject.instance()
# set CRS to Mollweide to do the buffers
project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
# Draw layers with missing projection in project's CRS
settings = QSettings()
defaultProjValue = settings.value( "/Projections/defaultBehaviour", "prompt", type=str )
settings.setValue( "/Projections/defaultBehaviour", "useProject" )

project.write("../map_klc.qgz")

KLC_old = QgsVectorLayer("../data/KLC_201508/KLC_201508.shp", "KLC 2015", "ogr")
KLC_new = QgsVectorLayer("../output/spatial_data/klc_20200915_proposal.gpkg|klc_20200915_proposal", "KLC 2020", "ogr")

klc_old_names = {}
for f in KLC_old.getFeatures():
    v = f["klcname"]
    k = f["KLC_ID"]
    klc_old_names[k] = v

# save to json
with open('../output/KLC_old_name.txt', 'w') as f:
    json.dump(klc_old_names,f)

f.closed 

colours = {
    'KLC_old': '#f8b420',
    'KLC_new': '#e63825'
    }
layers = {'KLC_old':KLC_old,'KLC_new':KLC_new}
extent = NULL
# map background
uri = "url=http://basemaps.cartocdn.com/light_all/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&type=xyz"
mts_layer=QgsRasterLayer(uri,'Background: CartoDb Positron','wms')
backgr = project.addMapLayer(mts_layer)

# show PA 
#wdpa = QgsVectorLayer("dbname=\'d6biopamarest\' host=pgsql96-srv1.jrc.org port=5432 sslmode=disable authcfg=xky3xl0 key=\'wdpaid\' srid=4326 type=MultiPolygon table=\"geo\".\"mv_wdpa\" (geom) sql=", "WDPA May 2019 (WCMC/JRC/DOPA)", "postgres")
#project.addMapLayer(wdpa)
# (DOPA version of wdpa doesn't have the proposed PAs.)
wdpa_all = QgsVectorLayer("//ies-ud01/spatial_data//Original_Datasets/WDPA/uncompressed/WDPA_Sep2020_Public.gdb|layername=WDPA_poly_Sep2020", "WDPA Sep 2020", "ogr")#
project.addMapLayer(wdpa_all)
wdpa_all.setName("WDPA Sep 2020 (WCMC)")
iface.setActiveLayer(wdpa_all)
# run pa_legend.py
exec(open('./pa_legend_py3.py'.encode('utf-8')).read())
#renderer = regionPaLayer.renderer() #singleSymbol renderer
#symLayer = QgsSimpleFillSymbolLayer.create({'color':'255,255,255,100', 'outline_color': '#70b6d1'})
#renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0,symLayer)
#regionPaLayer.setRenderer(renderer)
#regionPaLayer.triggerRepaint()
#iface.layerTreeView().refreshLayerSymbology(regionPaLayer.id())
#

# show KLC
for name in colours.keys():
    try:
        layer = layers[name]
        project.addMapLayer(layer)
        renderer = layer.renderer() #singleSymbol renderer
        symLayer = QgsSimpleFillSymbolLayer.create({'color':'250,250,250,10', 'outline_color': colours[name]})
        renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0,symLayer)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(layer.id())
        # get extent and combine
        if extent.isNull():
            extent = layer.extent()
        else:
            extent.combineExtentWith(layer.extent())
    except:
        pass


# show wdpa to be filtered
iface.addVectorLayer(wdpa_all.source(), "Target protected areas", wdpa_all.providerType())#QgsVectorLayer("dbname=\'d6biopamarest\' host=pgsql96-srv1.jrc.org port=5432 sslmode=disable authcfg=xky3xl0 key=\'wdpaid\' srid=4326 type=MultiPolygon table=\"geo\".\"mv_wdpa\" (geom) sql=", "Target protected areas", "postgres")
wdpa1 = iface.activeLayer()
# no symbology
renderer = wdpa1.renderer() #singleSymbol renderer
symLayer = QgsSimpleFillSymbolLayer.create({'color':'255,255,255,0', 'outline_width':'0','outline_color': '#000000'})
renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0,symLayer)
wdpa1.setRenderer(renderer)
wdpa1.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(wdpa1.id())
# labels
label = QgsPalLayerSettings()
label.fieldName = 'name'
label.enabled = True
buffer = QgsTextBufferSettings()
buffer.setEnabled(True)
text_format = QgsTextFormat()
text_format.setBuffer(buffer)
label.setFormat(text_format)
labeler = QgsVectorLayerSimpleLabeling(label)
wdpa1.setLabelsEnabled(True)
wdpa1.setLabeling(labeler)
wdpa1.triggerRepaint()
wdpa1.setName("Target protected areas")

# create generic print layout to be customised for each KLC
# Set canvas extent
canvas = iface.mapCanvas()
# set CRS to WGS84
project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
# zoom to extent
canvas.setExtent(extent.buffered(0.08))
# # or zoom to single country
# eez.selectByExpression('"ISO_Ter1" = \'KEN\'', QgsVectorLayer.SetSelection)
# # zoom to selected features
# canvas.setExtent(eez.boundingBoxOfSelected().buffered(0.08))
# # deselect features
# eez.removeSelection()
# set CRS to native Mapbox (pseudo Mecator)
# project.setCrs(QgsCoordinateReferenceSystem("EPSG:3857"))

klc_extent = extent

# print layout
# get a reference to the layout manager
manager = project.layoutManager()
#make a new print layout object
layout = QgsPrintLayout(project)
#needs to call this according to API documentaiton
layout.initializeDefaults()
#cosmetic
layout.setName('map_africa_klc_pa')
#add layout to manager
manager.addLayout(layout)

#create a map item to add
itemMap = QgsLayoutItemMap.create(layout)
# lock layers
itemMap.setKeepLayerSet(False)
itemMap.setLayers([layers['KLC_new'], layers['KLC_old'], wdpa_all, backgr])
itemMap.setKeepLayerSet(True)

# add to layout
layout.addLayoutItem(itemMap)
# set size
itemMap.attemptResize(QgsLayoutSize(200, 200, QgsUnitTypes.LayoutMillimeters))
itemMap.attemptMove(QgsLayoutPoint(10,5,QgsUnitTypes.LayoutMillimeters))
itemMap.zoomToExtent(klc_extent.buffered(0.08))

# add grid linked to map
itemMap.grid().setName("graticule")
itemMap.grid().setEnabled(True)
itemMap.grid().setStyle(QgsLayoutItemMapGrid.FrameAnnotationsOnly)
itemMap.grid().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
itemMap.grid().setIntervalX(10)
itemMap.grid().setIntervalY(10)
itemMap.grid().setAnnotationEnabled(True)
itemMap.grid().setFrameStyle(QgsLayoutItemMapGrid.InteriorTicks)
itemMap.grid().setFramePenSize(0.5)
itemMap.grid().setAnnotationFormat(1) # DegreeMinuteSuffix
itemMap.grid().setAnnotationPrecision(0) # integer
#itemMap.grid().setBlendMode(QPainter.CompositionMode_SourceOver) # ?

# Legend
itemLegend = QgsLayoutItemLegend.create(layout)
itemLegend.setAutoUpdateModel(False)
itemLegend.setLinkedMap(itemMap)
itemLegend.setLegendFilterByMapEnabled(True)
itemLegend.setTitle("Key Landscapes _nfor Conservation _nin Sub-Saharan Africa")
itemLegend.setWrapString("_n")
itemLegend.setResizeToContents(False)
layout.addLayoutItem(itemLegend)
itemLegend.attemptResize(QgsLayoutSize(77, 150, QgsUnitTypes.LayoutMillimeters))
itemLegend.attemptMove(QgsLayoutPoint(220,0,QgsUnitTypes.LayoutMillimeters))

# text box
itemLabel = QgsLayoutItemLabel.create(layout)
itemLabel.setText("Coordinate Reference System: [% @project_crs %]")
#itemLabel.adjustSizeToText()
itemLabel.setFixedSize(QgsLayoutSize(100,25,QgsUnitTypes.LayoutMillimeters))
itemLabel.attemptMove(QgsLayoutPoint(220,200,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemLabel)

# North arrow
itemNorth = QgsLayoutItemPicture.create(layout)
itemNorth.setPicturePath("C:/PROGRA~1/QGIS3~1.2/apps/qgis/svg/arrows/NorthArrow_04.svg")
itemNorth.setFixedSize(QgsLayoutSize(10,10,QgsUnitTypes.LayoutMillimeters))
itemNorth.attemptMove(QgsLayoutPoint(200,190,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemNorth)

## BIOPAMA logo
#itemLogo = QgsLayoutItemPicture.create(layout)
#itemLogo.setPicturePath("E:/weyname/BIOPAMA/DOC/pen_biopama_logo_1.png")
#layout.addLayoutItem(itemLogo)
#itemLogo.setFixedSize(QgsLayoutSize(50,10,QgsUnitTypes.LayoutMillimeters))
#itemLogo.attemptMove(QgsLayoutPoint(230,190,QgsUnitTypes.LayoutMillimeters))
#
# resize layout to content
# ????
# layout.resizeToContents()

# print to png
export = QgsLayoutExporter(layout)
expSett = QgsLayoutExporter.ImageExportSettings()
expSett.dpi = 150
export.exportToImage("../output/maps/"  + layout.name() + ".png", expSett)

# for each KLC, create customized layout
# load KLC_PA
with open('../output/KLC_PA.txt', 'r') as f:
    KLC_PA = json.load(f)

f.closed

KLC_new_filter = iface.addVectorLayer(KLC_new.source(), KLC_new.name() + "_clone", KLC_new.providerType())
layers['KLC_new_filter'] = KLC_new_filter
colours['KLC_new_filter'] = colours['KLC_new']
colours['KLC_new'] = "#fb9a99"
# update KLC symbology so that 'outline_width':'0.5'
for name in layers.keys():
    try:
        layer = layers[name]
        renderer = layer.renderer() #singleSymbol renderer
        symLayer = QgsSimpleFillSymbolLayer.create({'outline_width':'0.5','color':'250,250,250,10', 'outline_color': colours[name]})
        renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0,symLayer)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(layer.id())
    except:
        pass


# KLC_new: add categories in symbology
#symbol = KLC_old.renderer().symbol().clone()
#symbol.symbolLayer(0).setStrokeColor(QColor(colours['KLC_new']))
#symbol.symbolLayer(0).setStrokeWidth(0.7)
#symbol1 = symbol.clone()
#symbol1.symbolLayer(0).setStrokeColor(QColor("#fb9a99"))
#symbol1.symbolLayer(0).setStrokeWidth(0.5)
#categories = [
#    QgsRendererCategory('KLC',symbol,'KLC'),
#    QgsRendererCategory('',symbol1,'all other values')
#    ]
#klc_rend = QgsCategorizedSymbolRenderer('KLC_ID', categories)
#KLC_new.setRenderer(klc_rend)
# copy renderer

# labels
label = QgsPalLayerSettings()
label.enabled = True
label.fieldName = 'KLC_ID'
label.placement = QgsPalLayerSettings.OverPoint  #??
#label.fontSizeInMapUnits = False
#label.textFont.setPointSize(4.6)  #results in 4 - seems to be integer only
#label.textColor = QColor(68,92,249) #this works
buffer = QgsTextBufferSettings()
buffer.setColor(QColor(colours['KLC_old']))
buffer.setEnabled(True)
text_format = QgsTextFormat()
text_format.setBuffer(buffer)
label.setFormat(text_format)
# draw text buffer
labeler = QgsVectorLayerSimpleLabeling(label)
KLC_old.setLabelsEnabled(True)
KLC_old.setLabeling(labeler)
KLC_old.triggerRepaint()

layouts = {}
for klc in ['CAF_05', 'SAF_21', 'WAF_04', 'WAF_05', 'WAF_10']:#KLC_PA.keys():#['CAF_07']:#['CAF_04_SAF_11','CAF_14','CAF_17', 'CAF_18']:#['SAF_17']:#
    extent = NULL
    # zoom to KLC
    KLC_new.selectByExpression('"KLC_ID" = \''+klc+'\'', QgsVectorLayer.SetSelection)    
    extent = KLC_new.boundingBoxOfSelected()
    KLC_new.removeSelection()
    KLC_old.selectByExpression('"KLC_ID" = \''+klc+'\'', QgsVectorLayer.SetSelection)
    extent.combineExtentWith(KLC_old.boundingBoxOfSelected())
    KLC_old.removeSelection()
#    canvas.setExtent(extent.buffered(0.08))
    # show target PAs
    try:
        wdpa1.setSubsetString('"wdpaid" IN ' + str(tuple(KLC_PA[klc])))
    except:
        wdpa1.setSubsetString('"wdpaid" = ' + str(KLC_PA[klc]))
    # show target KLC
    KLC_new_filter.setSubsetString('"KLC_ID" IN (\'' + klc +'\')')
    KLC_new_filter.setName("New " + klc)
#    # Change KLC_new symbology
#    klc_rend.updateCategoryValue(0, klc)
#    klc_rend.updateCategoryLabel(0, klc)
#    # update renderer
#    KLC_new.setRenderer(klc_rend)####
#    KLC_new.triggerRepaint()
#    iface.layerTreeView().refreshLayerSymbology(KLC_new.id())
    # create print layout
    layouts[klc] = manager.duplicateLayout(layout, 'KLC_'+klc)    
    for item in layouts[klc].items():
        # Map
        if item.type() == 65639:
            # zoom to extent
            item.zoomToExtent(extent.buffered(0.08))
            # refresh
            item.setKeepLayerSet(False)
            item.setLayers([wdpa1, KLC_new_filter, KLC_new, KLC_old,  wdpa_all, backgr])
            item.setKeepLayerSet(True)
            item.refresh()
            # update grid
            item.grid().setIntervalX(1)
            item.grid().setIntervalY(1)
#            # add scale bar
#            itemScaleBar = QgsLayoutItemScaleBar(layouts[klc])
#            itemScaleBar.applyDefaultSettings()
#            itemScaleBar.applyDefaultSize()
#            itemScaleBar.setStyle('Single Box') # optionally modify the style
#            itemScaleBar.setLinkedMap(item) # map is an instance of QgsLayoutItemMap
#            itemScaleBar.setNumberOfSegmentsLeft(0)
#            itemScaleBar.setNumberOfSegments (2)
#            itemScaleBar.setUnits(1)
#            itemScaleBar.setUnitLabel('km')
#            itemScaleBar.setSegmentSizeMode(01)
#            itemScaleBar.update()
#            itemScaleBar.setSegmentSizeMode(0)            
#            layouts[klc].addItem(itemScaleBar)
#            itemScaleBar.attemptMove(QgsLayoutPoint(220,170,QgsUnitTypes.LayoutMillimeters))
        # Legend
        if item.type() == 65642:
            item.setTitle(klc)
            item.setAutoUpdateModel(True)
    # print to png
    export = QgsLayoutExporter(layouts[klc])
    expSett = QgsLayoutExporter.ImageExportSettings()
    expSett.dpi = 150
    export.exportToImage("../output/maps/KLC_new/"  + layouts[klc].name() + ".png", expSett)

    
#    wdpa1.setSubsetString("")
    
