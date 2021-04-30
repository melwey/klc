# KLC region of Africa
library(dplyr);library(ggplot2); library(stringr)
library(showtext); font_add("EC", "PFSquareSansPro-Medium.otf");showtext_auto()

load('../output/spatial_data/klc_sf_54009.rdata')

plot_klc <- function(df, y, y_lab, fname, colour = "#90c04e"){
  df <- as.data.frame(df)
  df$var <- df[,y]/df[,'KLC_area']
  p <- ggplot(df) + 
    geom_bar(aes(x = klcname, y = var), stat = 'identity', fill = colour) + 
    scale_x_discrete(limits = df[order(df$var), "klcname"]) +
    coord_flip() +
    labs(
      y = y_lab,
      x = "Key Landscapes for Conservation (KLCs)"
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
         width=12,
         height=6,
         units="cm")
  return(p)
}

# loop on regions
regions <- c("SA", "EA", "WA", "CA")
for (region in regions){
# filter region only
sub_klc_sf <- klc_sf_54009 %>%
  filter(Region == paste0(region,"FR")) %>%
  mutate_at(vars("PA_area", matches("ghs")), funs(mkpc = .*1e2))
p <- plot_klc(df = sub_klc_sf, 
              y = "PA_area_mkpc", 
              y_lab = "Level of protection (WDPA polygons Jul. 2018) [%]",
              fname = paste0(region,"_KLC_PA.png"))
p <- plot_klc(df = sub_klc_sf, 
              y = "pop_count_2015", 
              y_lab = "Population density in KLC in 2015 [hab./km2]",
              fname = paste0(region,"_KLC_pop.png"), 
              colour = "#70b6d1")
p <- plot_klc(df = sub_klc_sf, 
              y = "pop_dif", 
              y_lab = "Change in population density in KLC between 2000 and 2015 [hab/km2]",
              fname = paste0(region,"_KLC_pop_dif.png"),
              colour = "#a8d0e3")
p <- plot_klc(df = sub_klc_sf,
              y = "ghs_2014",
              y_lab = "Percentage of built-up area in KLC in 2014 [%]",
              fname = paste0(region,"_KLC_ghs2014.png"),
              colour = "#cc775d")
p <- plot_klc(df = sub_klc_sf,
              y = "ghs_dif",
              y_lab = "Difference in built-up coverage in KLC between 2000 and 2014 [%]",
              fname = paste0(region,"_KLC_ghs_dif.png"),
              colour = "#a25a28")
}
