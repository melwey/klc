# Overlay of spatial data on KLCs and statistics extraction in EPSG:54009
# BIOPAMA, 2018
# Melanie Weynants

# load packages
# data processing
library(foreign)
library(tidyverse)
library(wesanderson)
# spatial
library(raster)
library(rasterVis)
library(sf)
library(gdalUtils)
# change fonts to EC official
require(showtext); font_add("EC", "PFSquareSansPro-Medium.otf");showtext_auto()

# ?? Q ?? how much of the KLCs is protected?

KLCfile <- "../../data/Processed/KLC/Africa/klc_201508/klc_201508.shp"
# st_read creates an sf by adding a geometry column
klc_sf <- st_read(KLCfile)
# add crs
st_crs(klc_sf) <- 4326
# reproject in Mollweide EPSG:54009
klc_sf_54009 <- st_transform(klc_sf, 54009)
# save to disk
st_write(klc_sf_54009, "../../data/Processed/KLC/Africa/klc_201508/klc_201508_54009.shp")

# 1/ Rasterize klc using GDAL

# # get crs and resolution from wdpa
larger_extent_4326 <- sapply(st_bbox(klc_sf), function(x){ifelse(x > 0, ceiling(x), floor(x))})
# wdpa <- raster("../../data/Original/WDPA/wdpa_flat_grassexport_201710_1km_1bit.tif")
# dir.create("../../data/Processed/WDPA")
# wdpaAfrica <- crop(wdpa, larger_extent[c(1, 3, 2, 4)], filename = "../../data/Processed/WDPA/wdpa_flat_201710_1km_1bit_crop_klc.tif")

# get crs and resolution from ghs_54009
ghs2014 <- raster("../../data/Original/GHS/GHS_BUILT_LDS2014_GLOBE_R2016A_54009_1k_v1_0/GHS_BUILT_LDS2014_GLOBE_R2016A_54009_1k_v1_0.tif")
larger_extent_54009 <- st_bbox(klc_sf_54009)
larger_extent_54009[c(1,3)] <- sapply(st_bbox(klc_sf_54009)[c(1,3)], 
  function(x, r){ifelse(x > 0, ceiling(x/1000)*1000+extent(r)@xmax%%res(r)[1], floor(x/1000)*1000+extent(r)@xmin%%res(r)[1])},
  r = ghs2014)
larger_extent_54009[c(2,4)] <- sapply(st_bbox(klc_sf_54009)[c(2,4)],
  function(x, r){ifelse(x > 0, ceiling(x/1000)*1000+extent(r)@ymax%%res(r)[2], floor(x/1000)*1000+extent(r)@ymin%%res(r)[2])},
  r = ghs2014)
# rasterize
klc_54009_r <- gdal_rasterize(
  src_datasource = "../../data/Processed/KLC/Africa/klc_201508/klc_201508_54009.shp",
  dst_filename = "../../data/Processed/KLC/Africa/klc_201508/klc_201508_54009_1km_1byte.tif",
  # field to be burned
  a = "OID",
  # layer name
  l = "klc_201508_54009",
  a_srs = crs(ghs2014),
  # set no data value
  a_nodata = 0,
  # extent in Mollweide in Mollweide units (meter)
  te = larger_extent_54009,
  # resolution in Mollweide units (meter)
  tr = res(ghs2014),
  # output type
  ot = "Byte",
  verbose = TRUE,
  output_Raster = TRUE
)

# 2/ rasterize wdpa
pa_sf <- sf::read_sf("//ies-ud01/spatial_data/Original_Datasets/WDPA/uncompressed/WDPA_Jul2018_Public.gdb", layer = "WDPA_poly_Jul2018")
# which types of geometries?
print(unique(st_geometry_type(st_geometry(pa_sf))))
# pa_sf contains MULTISURFACE. Need to be converted to MULTIPOLYGON with cast
pa_sf <- sf::st_cast(pa_sf, "MULTIPOLYGON") # takes again some time...
# save result
st_write(pa_sf, "../../data/Processed/WDPA/pa_Jul2018.shp")
# reproject (takes some time)
pa_sf_54009 <- st_transform(pa_sf, 54009)
rm(pa_sf)
# save to disk
st_write(pa_sf_54009, "../../data/Processed/WDPA/pa_Jul2018_54009.shp", delete_dsn = TRUE)
# keep as R data
save(pa_sf_54009, file = "../output/spatial_data/pa_Jul2018_sf_54009.rdata")
# rasterize
system.time(
wdpa_54009_africa_r <- gdal_rasterize(
  src_datasource = "../../data/Processed/WDPA/pa_Jul2018_54009.shp",
  dst_filename = "../../data/Processed/WDPA/pa_Jul2018_54009_africa_1km_flat.tif",
  # field to be burned
  a = "PA_DEF",
  # layer name
  l = "pa_Jul2018_54009",
  a_srs = crs(ghs2014),
  # set no data value
  a_nodata = 0,
  # extent in Mollweide in Mollweide units (meter)
  te = larger_extent_54009,
  # resolution in Mollweide units (meter)
  tr = res(ghs2014),
  # output type
  ot = "Byte",
  verbose = TRUE,
  output_Raster = TRUE
)
)

# 2/ Tabulate
# For each KLC, sum area of pixels in PA
# combine KLC and PA with raster calc
klc_pa_54009_r <- mask(klc_54009_r, mask = wdpa_54009_africa_r, filename = "../../data/Processed/KLC/Africa/klc_paJul2018_54009.tif")
# zonal sum
# ! # klc_pa_zonal <- zonal(wdpa_54009_africa_r, klc_54009_r, fun = "sum", na.rm = TRUE) # ERROR!
## for simple case of tabulate area
# sum cell areaes by indexes stored in raster
klc_pa_tabulate <- tapply(wdpa_54009_africa_r, klc_pa_54009_r[], FUN = sum, na.rm=TRUE)
klc_pa_tabulate_df <- data.frame(OID = as.numeric(names(klc_pa_tabulate)), PA_area = as.numeric(klc_pa_tabulate))
save(klc_pa_tabulate_df, file = "klc_pa_Jul2018_54009_tabulate_df.rdata")
load("klc_pa_Jul2018_54009_tabulate_df.rdata")
# add result to klc attribute table
klc_sf_54009 <- left_join(klc_sf_54009[,-grep('geom$', names(klc_sf_54009))], klc_pa_tabulate_df) 
rm(klc_pa_tabulate, klc_pa_54009_r, klc_pa_tabulate_df)
# KLC area
# klc_tabulate <- tapply(rep(1, ncell(klc_54009_r)), klc_54009_r[], FUN = sum, na.rm = TRUE)
# klc_tabulate_df <- data.frame(OID = as.numeric(names(klc_tabulate)), KLC_area = as.numeric(klc_tabulate))
# save(klc_tabulate_df, file = "klc_54009_tabulate_df.rdata")
load("klc_54009_tabulate_df.rdata")
# add result to klc attribute table
klc_sf_54009 <- klc_sf_54009 %>% left_join(klc_tabulate_df)
rm(klc_tabulate, klc_tabulate_df)

# 3/ plot
plot_klc <- function(df, y, y_lab, fname){
  df <- as.data.frame(df)
  df$var <- df[,y]/df[,'KLC_area']
  p <- ggplot(df) + 
    geom_bar(aes(x = klcname, y = var, fill = Region), stat = 'identity') + 
    scale_x_discrete(limits = df[order(df$var), "klcname"]) +
    coord_flip() +
    labs(
      y = y_lab,
      x = "Key Landscapes for Conservation (KLCs)"
    ) +
    scale_fill_manual(labels = c('CAFR' = 'Central Africa', 
                                 'EAFR' = 'Eastern Africa', 
                                 'SAFR' = 'Southern Africa', 
                                 'WAFR' = 'Western Africa'),
                      values = c("#0E3D59", "#88A61B", "#F29F05", "#F25C05")
    ) + 
    theme(
      plot.background = element_rect(fill = "transparent"),
      panel.background = element_rect(fill = "transparent"),
      panel.grid.major.x = element_line(colour = "dark grey"),
      aspect.ratio = 1/.6
    )
  ggsave(fname, 
         p + theme(text = element_text(size = 24)),
         path = "../output/graphs/", 
         width=20,
         height=18,
         units="cm")
  return(p)
}
p <- plot_klc(df = klc_sf_54009, 
              y = "PA_area", 
              y_lab = "Proportion of KLC under any form of protection (polygon WDPA Juy 2018)",
              fname = "KLC_PA_Jul2018_54009_area_pc.png")

# Calculate KLC and PA areas directly on sf
klc_sf_54009 <- klc_sf_54009 %>%
  mutate(KLC_AREA_sf = st_area(klc_sf_54009))

# dissolve/union PA to create flat layer (not working with sf::st_union; try with QGIS dissolve using RQGIS)
# library(RQGIS)
# # crop pa to extent of interset
# pa_sf_africa <- pa_sf %>% 
#   st_intersection(
#     st_set_crs(
#       st_as_sf(
#         as(
#           raster::extent(larger_extent_4326[c(1,3,2,4)]), 
#           "SpatialPolygons"
#           )
#         ), 
#       st_crs(pa_sf)
#       )
#   )
# 
# pa_sf_africa_54009 <- pa_sf_africa %>% st_transform(54009)
# # save to disk
# st_write(pa_sf_africa_54009, "../../data/Processed/WDPA/pa_Fed2018_Africa_54009.shp", delete_dsn = TRUE)
# 
# system.time(
#   pa_africa_flat_sf_54009 <- run_qgis(alg = 'qgis:dissolve', INPUT = pa_sf_africa_54009, DISSOLVE_ALL = TRUE, FIELD = "PA_DEF", OUTPUT = "../../data/Processed/WDPA/pa_africa_flat_sf_54009.shp", load_output = TRUE)
# ) # careful: takes ages. just for sub-saharan africa (ssa), time elapsed only 8 minutes!
# ##### !!!!! DO NEXT WHEN dissolve IS DONE !!!!!! 
# # pa_flat_sf_54009 <- st_read("../../data/Processed/pa_Fed2018_flat_54009.shp")
# # intersect flat pa with klc
# system.time(
# klc_pa_sf_54009 <-  klc_sf_54009 %>%
#   st_intersection(pa_africa_flat_sf_54009) %>%
#   # 3. calculate area
#   mutate(PA_AREA_sf = st_area())
# )
klc_sf_54009 <- klc_sf_54009 %>% mutate(PA_AREA_sf = NA)
#### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ###################
# Which KLC area to use for the other calculations?
  
# ?? Q ?? What are the pressures on the KLCs
# population count by KLC/area -> average population density
# population data are in epsg:4326. Work with that.
klc_4326_r <- raster("../../data/Processed/KLC/Africa/klc_201508/klc_201508_1km_1byte.tif")
dir.create("../../data/Processed/gpw-v4")
pop_count <- raster("../../data/Original/gpw-v4/gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals_2015.tif")
pop_count_afr <- crop(pop_count, larger_extent_4326[c(1, 3, 2, 4)], filename = "../../data/Processed/gpw-v4/pop_count_2015_crop_klc.tif")
klc_pop_tabulate <- tapply(pop_count_afr, klc_4326_r[], FUN = sum, na.rm=TRUE)
klc_pop_tabulate_df <- data.frame(OID = as.numeric(names(klc_pop_tabulate)), pop_count = as.numeric(klc_pop_tabulate))
save(klc_pop_tabulate_df, file = "../output/tables/klc_pop_tabulate_df.rdata")
load("../output/tables/klc_pop_tabulate_df.rdata")
# add result to klc attribute table
klc_sf_54009 <- klc_sf_54009 %>%
  left_join(klc_pop_tabulate_df) %>%
  rename(pop_count_2015 = pop_count)
rm(pop_count, pop_count_afr, klc_pop_tabulate, klc_pop_tabulate_df)
# ! CAUTION ! population count|KLC is calculated on the basis of 4326, while KLC_area based on 54009 !
# would be more coherent to used KLC_area_4326
# plot
p <- plot_klc(df = klc_sf_54009, 
              y = "pop_count_2015", 
              y_lab = "Population density in KLC in 2015 [hab./km2]",
              fname = "KLC_pop.png")


# ! population density above or below threshold -> area under high population pressure
# ! How to define threshold? by eco-region? Try it in another script

# change in population count (t2 - t1) / area -> average population change
pop_count_2000 <- raster("../../data/Original/gpw-v4/gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals_2000.tif")
pop_count_2000_afr <- crop(pop_count_2000, larger_extent_4326[c(1, 3, 2, 4)], filename = "../../data/Processed/gpw-v4/pop_count_2000_crop_klc.tif")
klc_pop_2000_tabulate <- tapply(pop_count_2000_afr, klc_4326_r[], FUN = sum, na.rm=TRUE)
klc_pop_2000_tabulate_df <- data.frame(OID = as.numeric(names(klc_pop_2000_tabulate)), pop_count_2000 = as.numeric(klc_pop_2000_tabulate))
save(klc_pop_2000_tabulate_df, file = "../output/tables/klc_pop_2000_tabulate_df.rdata")
load("../output/tables/klc_pop_2000_tabulate_df.rdata")
# add result to klc attribute table
klc_sf_54009 <- klc_sf_54009 %>%
  left_join(klc_pop_2000_tabulate_df) %>%
  mutate(pop_dif = pop_count_2015 - pop_count_2000)
rm(pop_count_2000, pop_count_2000_afr, klc_pop_2000_tabulate, klc_pop_2000_tabulate_df)
# plot
p <- plot_klc(df = klc_sf_54009, 
              y = "pop_dif", 
              y_lab = "Change in population density in KLC between 2000 and 2015 [hab/km2]",
              fname = "KLC_pop_dif.png")

# ! absolute population change by pixel classified in 4 quantiles by eco-region?

# built-up coverage -> average on KLC
# 2014  GHS_BUILT_LDS2014_GLOBE_R2016A_54009_1k_v1_0
ghs2014_afr <- crop(ghs2014, larger_extent_54009[c(1, 3, 2, 4)], filename = "../../data/Processed/GHS/GHS_BUILT_2014_54009_1km_cropKLC.tif")
klc_ghs2014_tabulate_df <- raster::zonal(ghs2014_afr, subset(klc_54009_r, 1), fun = 'sum', na.rm = TRUE) %>%
  as.data.frame() %>%
  rename(OID = zone, ghs_2014 = sum) %>%
  mutate(ghs_2014 = ghs_2014)
# klc_ghs2014_tabulate <- tapply(ghs2014_afr, klc_54009_r[], FUN = sum, na.rm = TRUE)
# klc_ghs2014_tabulate_df <- data.frame(OID = as.numeric(names(klc_ghs2014_tabulate)), ghs2014 = as.numeric(klc_ghs2014_tabulate)*1e4)
save(klc_ghs2014_tabulate_df, file = "../output/tables/klc_ghs2014_tabulate_df.rdata")
load("../output/tables/klc_ghs2014_tabulate_df.rdata")
# add result to klc attribute table and divide by area
klc_sf_54009 <- klc_sf_54009 %>%
  left_join(klc_ghs2014_tabulate_df)
rm(klc_ghs2014_tabulate_df)
p <- plot_klc(df = klc_sf_54009,
              y = "ghs_2014",
              y_lab = "Proportion of built-up area in KLC in 2014 [proportion]",
              fname = "KLC_ghs2014.png")
p

# 2000 
ghs2000_afr <- crop(raster("../../data/Original/GHS/GHS_BUILT_LDS2000_GLOBE_R2016A_54009_1k_v1_0/GHS_BUILT_LDS2000_GLOBE_R2016A_54009_1k_v1_0.tif"),
                    larger_extent_54009[c(1, 3, 2, 4)], filename = "../../data/Processed/GHS/GHS_BUILT_2000_54009_1km_cropKLC.tif")
klc_ghs2000_tabulate_df <- raster::zonal(ghs2000_afr, subset(klc_54009_r, 1), fun = 'sum', na.rm = TRUE) %>%
  as.data.frame() %>%
  rename(OID = zone, ghs_2000 = sum) %>%
  mutate(ghs_2000 = ghs_2000)
save(klc_ghs2000_tabulate_df, file = "../output/tables/klc_ghs2000_tabulate_df.rdata")
load("../output/tables/klc_ghs2000_tabulate_df.rdata")
# add result to klc attribute table and divide by area
klc_sf_54009 <- klc_sf_54009 %>%
  left_join(klc_ghs2000_tabulate_df) %>%
  mutate(ghs_dif = ghs_2014 - ghs_2000) 
rm(klc_ghs2000_tabulate_df)
p <- plot_klc(df = klc_sf_54009,
              y = "ghs_dif",
              y_lab = "Difference in built-up coverage in KLC between 2000 and 2014 [proportion of area]",
              fname = "KLC_ghs_dif.png")

# ! change in built-up -> proportion of KLC that saw an increase in built-up of more than threshold

# tree covered (in 2000)
# tree covered (in 2016)

# GLWD level 3 (12 classes of water and wetland data)
# surface water change
# groundwater change ? (data available?)

# same with indicators inside PAs
# ghs 2000
klc_pa_ghs2014_tabulate_df <- raster::zonal(ghs2014_afr, klc_54009_r, fun = 'sum', na.rm = TRUE) %>%
  as.data.frame() %>%
  rename(OID = zone, pa_ghs_2014 = sum) %>%
  mutate(pa_ghs_2014 = pa_ghs_2014)
save(klc_pa_ghs2014_tabulate_df, file = "../output/tables/klc_paJul18_ghs2014_tabulate_df.rdata")
load("../output/tables/klc_paJul18_ghs2014_tabulate_df.rdata")
# add result to klc attribute table and divide by area
klc_sf_54009 <- klc_sf_54009 %>%
  left_join(klc_ghs2014_tabulate_df)
# ghs 2014
klc_pa_ghs2014_tabulate_df <- raster::zonal(ghs2014_afr, klc_54009_r, fun = 'sum', na.rm = TRUE) %>%
  as.data.frame() %>%
  rename(OID = zone, pa_ghs_2014 = sum) %>%
  mutate(pa_ghs_2014 = pa_ghs_2014)
save(klc_pa_ghs2014_tabulate_df, file = "../output/tables/klc_paJul18_ghs2014_tabulate_df.rdata")
load("../output/tables/klc_paJul18_ghs2014_tabulate_df.rdata")
# add result to klc attribute table and divide by area
klc_sf_54009 <- klc_sf_54009 %>%
  left_join(klc_ghs2014_tabulate_df)
#### CONTINUE FROM HERE #####
klc_pa_54009_r
##################
save(klc_sf_54009, file = "../output/spatial_data/klc_sf_54009.rdata") # rdata seems to have a good compression rate!
# export to shp
st_write(klc_sf_54009, "../output/spatial_data/klc_sf_54009.shp")
# export to csv (remove spatial features first)
klc_sf_54009 %>%
  # remove geometry
  st_set_geometry(NULL) %>%
  dplyr::select(-POLY_AREA,-Longitude, -Latitude, -Ecosystem)%>%
  # export to csv
  write.csv(file = "../output/tables/klc_stats_Jul2018.csv")




# ?? Q ?? country intersect KLC
gaul_file <- "E:/weyname/epscAfrica/africa_boundaries/africa_gaul2015.shp"
dir.create("../../data/Processed/GAUL")
# rasterize adm0_code to 4326
gdal_rasterize(
  src_datasource = gaul_file,
  dst_filename = "../../data/Processed/GAUL/gaul_Africa_2015_30sec.tif",
  # field to be burned
  a = "adm0_code",
  # layer name
  l = "africa_gaul2015",
  a_srs = "+proj=longlat +datum=WGS84 +no_defs",
  # set no data value
  a_nodata = 0,
  # extent
  te = larger_extent_4326,
  # resolution
  tr = rep(1/60/2,2),
  # output type
  ot = "Int32",
  verbose = TRUE
)
gaul_r_4326 <- raster("../../data/Processed/GAUL/gaul_Africa_2015_30sec.tif")

# rasterize adm0_code to 54009
gaul_sf_4326 <- read_sf(gaul_file)
gaul_sf_54009 <- st_transform(gaul_sf_4326, 54009)
st_write(gaul_sf_54009, "../../data/Processed/GAUL/gaul_Africa_2015_54009.shp")
rm(gaul_sf_4326)
gaul_54009_r <- gdal_rasterize(
  src_datasource = "../../data/Processed/GAUL/gaul_Africa_2015_54009.shp",
  dst_filename = "../../data/Processed/GAUL/gaul_Africa_2015_54009_1km.tif",
  # field to be burned
  a = "adm0_code",
  # layer name
  l = "gaul_Africa_2015_54009",
  a_srs = crs(ghs2014),
  # set no data value
  a_nodata = 0,
  # extent in Mollweide in Mollweide units (meter)
  te = larger_extent_54009,
  # resolution in Mollweide units (meter)
  tr = res(ghs2014),
  # output type
  ot = "Int32",
  verbose = TRUE,
  output_Raster = TRUE
)

# combine gaul and klc to compute areas
# # gaul adm_0 Africa min: 4, max: 61013
# # klc min: 1, max = 76
klc_gaul_r_54009 <- overlay(klc_54009_r, 
                            gaul_54009_r, 
                            fun = function(x1,x2){x1*1e5 + x2}, 
                            filename = "../../data/Processed/KLC/Africa/klc_x1e5_gaul_54009_1km.tif", 
                            overwrite = TRUE)
# tabulate area
klc_gaul_54009_tabulate_df <- raster::zonal(klc_gaul_r_54009, klc_gaul_r_54009, fun = 'count', na.rm = TRUE) %>%
  as.data.frame() %>%
  rename(ID_KLC_gaul = zone, KLC_gaul_area = count) %>%
  mutate(ID_KLC = floor(ID_KLC_gaul * 1e-5)) %>%
  mutate(ID_gaul = ID_KLC_gaul - ID_KLC * 1e5)
save(klc_gaul_54009_tabulate_df, file = "../output/tables/klc_gaul_54009_tabulate_df.rdata")
load("../output/tables/klc_gaul_54009_tabulate_df.rdata")

# create new sf by intersecting KLCs and countries
klc_gaul_sf_54009 <- klc_sf_54009 %>%
  select(OID, KLC_ID, klcname, Region, KLC_area,KLC_AREA_sf) %>%
  st_intersection(
    select(.data = gaul_sf_54009, ogc_fid, adm0_code, adm0_name, iso3, fao, un_m49)
  ) %>%
  mutate(adm0_code = as.numeric(adm0_code))
# calculate polygon area
klc_gaul_sf_54009$KLC_gaul_AREA_sf <- st_area(klc_gaul_sf_54009)

# attach area to sf
klc_gaul_sf_54009 <- klc_gaul_sf_54009 %>%
  left_join(klc_gaul_54009_tabulate_df, by = c("OID" = "ID_KLC", "adm0_code" = "ID_gaul")) %>%
  # add column
  mutate(KLC_gaul_area_pc = KLC_gaul_area/KLC_area*100) %>%
  mutate(KLC_gaul_AREA_sf_pc = as.numeric(KLC_gaul_AREA_sf/KLC_AREA_sf*100))
save(klc_gaul_sf_54009, file = "klc_gaul_sf_54009.rdata")
st_write(klc_gaul_sf_54009, "../output/spatial_data/KLC_gaul_54009.shp", delete_dsn=TRUE)

# intersect klc_gaul with teow from dopa
#st_read(dsn = "http://lrm-maps.jrc.ec.europa.eu/geoserver/dopa_explorer_2/wfs?", layer = "dopa_explorer_2:terrestrial_ecoregion_2014")
teow_sf <- read_sf("../../data/Original/TEOW/wwf_terr_ecos.shp")
teow_sf_54009 <- st_transform(teow_sf, 54009)
dir.create("../../data/Processed/TEOW")
st_write(teow_sf_54009, "../../data/Processed/TEOW/wwf_terr_ecos_54009.shp")
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# intersect 
klc_gaul_teow_sf_54009 <- klc_gaul_sf_54009 %>%
  select(ID_KLC_gaul) %>%
  st_intersection(teow_sf_54009[, c('ECO_ID', 'ECO_NAME')])
st_write(klc_gaul_sf_54009, "../output/spatial_data/klc_gaul_teow_sf_54009.shp", delete_dsn=TRUE)
# save in R format
save(klc_gaul_sf_54009, file = "../output/tables/klc_gaul_teow_sf_54009.rdata")


# instersect klc_gaul with pa_code  ! Maybe too big ! Takes some time but seems to work. Detach when done
# # problem: invalid geometries in pa_sf_54009
# system.time(
# klc_gaul_pa_sf_54009 <- klc_gaul_sf_54009 %>%
#   select(ID_KLC_gaul) %>%
#   st_intersection(pa_sf_africa_54009[, c('WDPAID','WDPA_PI', 'NAME', 'DESIG_E', 'IUCN_CA', 'MARINE', 'STATUS', 'ISO3', 'PARENT_')])
# )
###################################
# 4326
pa_sf_4326 <- sf::read_sf("//ies-ud01/spatial_data/Original_Datasets/WDPA/uncompressed/WDPA_Jul2018_Public.gdb", layer = "WDPA_poly_Jul2018")
load("klc_gaul_sf_tmp.rdata") # from klc_overlay_stats.r (4326)
system.time(
  klc_gaul_pa_sf <- st_sf(klc_gaul_sf_tmp) %>%
    select(ID_KLC_gaul, KLC_ID, klcname, Region, iso3) %>%
    st_intersection(pa_sf_4326[, c('WDPAID','WDPA_PID', 'NAME', 'DESIG_ENG', 'IUCN_CAT', 'MARINE', 'GIS_M_AREA', 'GIS_AREA', 'STATUS', 'ISO3', 'PARENT_ISO3')])
)
rm(pa_sf_4326)

# remove PAs that are not in the correct country
klc_gaul_pa_sf <- klc_gaul_pa_sf %>%
  filter(iso3 == ISO3)
# check geometry
print(unique(st_geometry_type(st_geometry(klc_gaul_pa_sf)))) # OK
st_write(klc_gaul_pa_sf, "../output/spatial_data/klc_gaul_pa_Jul2018.shp")
# save to R data
save(klc_gaul_pa_sf, file ="../output/tables/klc_gaul_pa_Jul2018.rdata")


# add info
klcAddInfo <- function(id, isf){
  return(paste(isf[isf$ID_KLC_gaul == id, grepl('NAME$', names(isf))], collapse = ', '))
}
klc_gaul_teow_pa_sf_54009 <- klc_gaul_sf_54009 %>%
  # list other countries also in KLC
  mutate(other_countries = unlist(sapply(ID_KLC_gaul, FUN = function(x){paste(adm0_name[OID == floor(x*1e-5) & ID_KLC_gaul != x], collapse = ', ')}))) %>%
  # list PAs intersecting with KLC and country
  mutate(pa_klc_country = unlist(sapply(ID_KLC_gaul, FUN = klcAddInfo, as.data.frame(klc_gaul_pa_sf)))) %>%
  # list TEOW intersecting with KLC and country
  mutate(teow_klc_country = unlist(sapply(ID_KLC_gaul, FUN = klcAddInfo, as.data.frame(klc_gaul_teow_sf_54009))))
st_write(klc_gaul_teow_pa_sf_54009, "../output/spatial_data/klc_gaul_teow_pa_Jul2018_54009.shp", delete_dsn = TRUE)
# save to rdata
save(klc_gaul_teow_pa_sf_54009, file = "../output/tables/klc_gaul_teow_pa_Jul2018_54009.rdata")


# example of data display
show_country_klc <- function(klc_gaul_teow_pa_sf, country = NULL, country_code = NULL, klc_name = NULL, klc_id = NULL){
  if (is.null(country) & is.null(country_code) & is.null(klc_name)){stop("You have to specify at least one argument")}
  if (!is.null(country)){
    # check that country name exists
    if (any(grepl(country, klc_gaul_teow_pa_sf$adm0_name))){
      output <- klc_gaul_teow_pa_sf %>%
        filter(grepl(country, adm0_name)) %>%
        select(adm0_name, klcname, Region, KLC_area, KLC_gaul_area, KLC_gaul_area_pc, pa_klc_country, teow_klc_country, other_countries)
    } else {stop("Unvalid country name")}
  } else {
    if (!is.null(country_code)){
      # check that country code is valid
      if(country_code %in% klc_gaul_teow_pa_sf$adm0_code){
        output <- klc_gaul_teow_pa_sf %>%
          filter(adm0_code == country_code) %>%
          select(klcname, Region, KLC_area, KLC_gaul_area, KLC_gaul_area_pc, pa_klc_country, teow_klc_country, other_countries)
        } else {
          stop("country_code must be a valid gaul adm0_code")
          }
      } else {
        output <- klc_gaul_teow_pa_sf
      }
    }
  if (!is.null(klc_name)){
    # check that klc_name exists in data set
    if (any(grepl(klc_name, klc_gaul_teow_pa_sf$klcname))){
      output <- output %>%
        filter(grepl(klc_name, klcname)) %>%
        select(klcname, adm0_name, Region, KLC_area, KLC_gaul_area, KLC_gaul_area_pc, pa_klc_country, teow_klc_country, other_countries)
    } else {
      stop('klc_name is not valid')
    }
  } else {
    if (! is.null(klc_id)){
      # check that klc code is valid
      if (klc_id %in% klc_gaul_teow_pa_sf$KLC_ID){
        output <- output %>%
          filter(klc_id %in% KLC_ID) %>%
          select(klcname, adm0_name, Region, KLC_area, KLC_gaul_area, KLC_gaul_area_pc, pa_klc_country, teow_klc_country, other_countries)
      } else {
        stop("klc_id is not valid. It should be of the form [[:upper:]]{3}_[[:digit:]]{2}")
      }
    }
  }
  return(output)
}
  
# test it
names(klc_gaul_teow_pa_sf_54009) <- c(names(klc_gaul_sf_54009)[-18], "other_countries", "pa_klc_country", "teow_klc_country", "geometry")
tmp <-
  show_country_klc(klc_gaul_teow_pa_sf_54009, klc_name = "Arc")
# seems to be some mismatch with the countries and the wdpa: need to do a cleaner insersection
show_country_klc(klc_gaul_teow_pa_sf_54009, klc_name = "Vir")
