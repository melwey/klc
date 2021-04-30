# CoE KLC U SSA countries
# Statistics of bws, tree loss and lpd inside and outside KLCs, w/o mask

#system("C:/Python27/ArcGIS10.5/python.exe ../pyCode/CoE_analysis_KLC_ssa.py")
# did not work as expected. Export as csv badly written. 
# I exported tables to dbf from ArcCatalog

library(foreign)
library(dplyr)

klc_ssa <- function(tbl){
		tbl %>%
			mutate_at(vars(starts_with("VALUE")), funs(.*1e-9)) %>%
			mutate(KLC = matrix(unlist(strsplit(KLC_ADM0, ';', fixed = TRUE)), ncol = 2, byrow = TRUE)[,1]) %>%
				mutate(ADM0 = matrix(unlist(strsplit(KLC_ADM0, ';', fixed = TRUE)), ncol = 2, byrow = TRUE)[,2]) %>%
				mutate(IN_KLC = ifelse(nchar(KLC) > 0, "IN", "OUT"))
}


klc_sum <- function(tbl){
	total <- sum(tbl %>% dplyr::select(starts_with("VALUE")))
	tbl %>%
		group_by(IN_KLC) %>%
		summarize_at(c("VALUE_0", "VALUE_1"), sum, na.rm = TRUE)%>%
		mutate(rel = round(VALUE_1/(VALUE_0  + VALUE_1) *100)) %>%
		mutate(rel_total = round(VALUE_1/total *100))
}

bws <- klc_ssa(read.dbf("../output/tables/ssa_klc_bws_areas.dbf", as.is = TRUE))
bws_g <- klc_sum(bws)
print(bws_g)

frstL <- klc_ssa(read.dbf("../output/tables/ssa_klc_frstL_areas.dbf", as.is = TRUE))
frstL_g <- klc_sum(frstL)
print(frstL_g)

lpd <- klc_ssa(read.dbf("../output/tables/ssa_klc_LPD_areas.dbf", as.is = TRUE))
lpd_g <- klc_sum(lpd)
print(lpd_g)


