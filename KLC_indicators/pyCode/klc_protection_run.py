wdpa_poly = QgsVectorLayer("/Users/mela/Documents/JRC/BIOPAMA/data/WDPA_Apr2021_Public/WDPA_Apr2021_Public.gdb|layername=WDPA_poly_Apr2021", "wdpa_poly", "ogr")
if not wdpa_poly.isValid():
  print("Layer failed to load!")

wdpa_point = QgsVectorLayer("/Users/mela/Documents/JRC/BIOPAMA/data/WDPA_Apr2021_Public/WDPA_Apr2021_Public.gdb|layername=WDPA_point_Apr2021", "wdpa_point", "ogr")
if not wdpa_point.isValid():
  print("Layer failed to load!")

klc = QgsVectorLayer("/Users/mela/JRCbox/BIOPAMA/KLC_Africa/output/spatial_data/klc_20200921_proposal.gpkg|layername=klc_20200921_proposal", "klc", "ogr")
if not klc.isValid():
  print("Layer failed to load!")


params = {
    'inputzones': klc,
    'zone_id':"KLC_ID", # default KLC_ID
    'inputwdpapoints':wdpa_point,
    'inputwdpapolygons':wdpa_poly,
    #'Result':, # default: create temporary layer
    'APIComment':"Protection level of KLCs, based on WDPA May 2021",
    'wdpaversionperc':"api_klc_protection_21_05"
}

tmp = processing.run('wdpa:Wdpa_ zone_processing', params)