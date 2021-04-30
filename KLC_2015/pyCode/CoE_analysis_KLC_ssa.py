### replaced by WAD/convergence/pyCode/convergence_analysis_country_14.py with arguments continent = "ssa" and zone = "klc"
# Import arcpy module
import arcpy
from arcpy.sa import *
import numpy as np
from numpy import inf

# Set environment settings
arcpy.env.workspace = "E:\\weyname\\WAD\\convergence\\areaCalc_20170224.gdb"
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem="PROJCS['World_Goode_Homolosine_Land',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Goode_Homolosine'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Option',1.0],UNIT['Meter',1.0]]"
arcpy.env.cellSize = 1000
arcpy.env.extent = 'MAXOF'
# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")


sumCE_goode = "sumCE_goode"
# !!!! set sumCE as mask to be used in the zonal statistics !!!!!
arcpy.env.mask = sumCE_goode


f = open('E:/weyname/WAD/convergence/tables/keyOrder_14_20170428.txt','r') 
keyOrder = f.read()
f.close()
keys = keyOrder.split(', ')

keyData_goode = dict()
for k in keys:
    print str(k)
    keyData_goode[k] = k+"_goode"


# general zonal stats by KLC
# 2018-02-16: sumCE
# continents = "E:/weyname/BIOPAMA/GIS/data/Processed/KLC/Africa/klc_201508/klc_201508_gaul_2015_union.shp"
# arcpy.Project_management(
    # in_dataset = continents,
    # out_dataset = "klc_gaul_goode",
    # out_coor_system =  arcpy.env.outputCoordinateSystem)
continents_goode = "klc_gaul_goode"

# Zonal_sumCE_continents = TabulateArea(continents_goode, 'KLC_ADM0', sumCE_goode, 'Value', "Zonal_continents_sumCE",1000)
# export to txt
##
# continents_sumCE_arc = arcpy.da.TableToNumPyArray("Zonal_continents_sumCE","*")
# np.savetxt("E:/weyname/BIOPAMA/GIS/KLC_Africa/output/tables/ssa_klc_sumissues_areas.csv",
   # continents_sumCE_arc,
   # fmt = '%13d',
   # delimiter=",",
   # header = ",".join(["{:s}".format(i) for i in continents_sumCE_arc.dtype.names]),
   # comments = '')
	 
# 2018-07-17 single key issues
for k,v in keyData_goode.iteritems():
   print(str(k))
   Zonal = TabulateArea(continents_goode, 'KLC_ADM0', v,'Value', "Zonal_klc_ssa"+k, 1000)
# merge all result in a single table and export to txt
dt = [('KLC_AMD0', '|S20'),('key', '|S10'), ('area', '<f8')]
tmp1 = np.array([],dtype = dt)
for k in keyData_goode.iterkeys():
   tmp = arcpy.da.TableToNumPyArray("Zonal_klc_ssa"+k,"*")
   for i in range(0,7):
       tmp1 = np.append(tmp1 , np.array((tmp[i][1],k,tmp[i][3]),dtype=dt))
np.savetxt("E:/weyname/BIOPAMA/GIS/KLC_Africa/output/tables/ssa_klc_keyissues_areas.csv",
   tmp1,
   fmt = ['%s', '%s', '%15d'],
   delimiter=",",
   header = ",".join(["{:s}".format(i) for i in tmp1.dtype.names]),
   comments = '')
