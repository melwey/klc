load("../output/tables/klc_gaul_pa_Jul2018.rdata")
load("../output/spatial_data/pa_Jul2018_sf_54009.rdata")

tmp <- as.data.frame(pa_sf_54009) %>% 
  filter(WDPAID %in% klc_gaul_pa_sf$WDPAID) %>%
  select(WDPAID, GIS_M_AREA, GIS_AREA) %>%
  left_join(as.data.frame(klc_gaul_pa_sf)) %>%
  select(- geometry)

# display duplicates:
tmp[tmp$WDPAID %in% tmp$WDPAID[duplicated(tmp$WDPAID)],c("WDPAID","NAME","DESIG_ENG", "IUCN_CAT", "ISO3", "KLC_ID", "klcname")]
# remove duplicate wdpa (a PA should be in only one klc)
# some PAs removed:
wdpa_rm <- c(555558303, 555623781, 555623786, 4101, 27010)
tmp <- tmp[!tmp$WDPAID %in% wdpa_rm,]
# some attributed to one KLC
tmp <- tmp %>%
  filter(! (WDPAID == 301440 & KLC_ID == 'EAF_10')) %>%
  filter(! (WDPAID == 301442 & KLC_ID == 'EAF_03')) %>%
  filter(! (WDPAID == 303451 & KLC_ID == 'EAF_10')) %>%
  filter(! (WDPAID == 555624100 & KLC_ID == 'EAF_10')) %>%
  filter(! (WDPAID == 555623785 & (KLC_ID == 'EAF_01'| KLC_ID == 'EAF_03'))) %>%
  filter(! (WDPAID == 2524 & KLC_ID == 'SAF_04')) %>%
  filter(! (WDPAID == 2527 & KLC_ID == 'SAF_01'))

area_class <- function(x){
  y <- rep(NA, length(x))
  y[x > 0 & x < 50] <- 'low'
  y[x >= 50 & x < 150] <- 'medium'
  y[x >= 150] <- 'high'
  y[is.na(y)] <- 'unknown'
  return(y)
}

tmp1 <- data.frame(WDPA_ID) %>% 
  left_join(tmp, by = c("WDPA_ID" = "WDPAID")) %>%
  mutate(GIS_total = GIS_AREA + GIS_M_AREA) %>%
  mutate(Surface_area = area_class(GIS_total))

write.csv(tmp1, file = "pa_klc.csv")
