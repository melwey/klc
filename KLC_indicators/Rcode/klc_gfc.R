# klc_gfc: prepare data for ingestion into postgis database
library(tidyverse)
# import from google drive
library(googledrive)
downloaded_file <- drive_download("https://drive.google.com/file/d/104v33pqpPTS3VonetPq3JD9CsxB8UX_P/view?usp=sharing", overwrite = TRUE)

klc_gfc <- read_delim(downloaded_file$name, delim = ",") %>%
  # change names
  select(-`system:index`, -.geo) %>%
  rename_with(tolower) %>%
  # pivot longer: year to column
  pivot_longer(cols = `2001`:`2020_pa`, names_to = c("year", "pa"), names_sep = "_", values_to = "area") %>%
  # pa values as columns
  mutate(pa = if_else(is.na(pa), "total", "inside")) %>%
  pivot_wider(names_from = pa, values_from = area) %>%
  # get outside pa
  mutate(outside = total - inside) %>%
  # pa as column
  pivot_longer(cols = total:outside, names_to = "pa", values_to = "area_loss") %>%
  # year as numeric
  mutate(year = as.numeric(year))

# to get percentages, we need total area grouped by pa, klc_id from e.g. klc_gclc
klc_cglc <- read_csv( "../outputs/tables/klc_cglc.csv")
klc_pa_areas <- klc_cglc %>%
  rowwise() %>%
  mutate(total_area = sum(c_across(bare:water_seasonal))) %>%
  filter(year == 2019) %>%
  select(klc_id, pa, total_area)

klc_gfc_pc <- klc_gfc %>%
  left_join(klc_pa_areas) %>%
  group_by(pa, klc_id) %>%
  mutate(area_pc = area_loss/total_area*100)

ggplot(klc_gfc_pc %>% 
         filter(klc_id %in% c("CAF_01", "WAF_10", "WAF_11", "WAF_21")),
       aes(x = year, y = area_pc, colour = pa)) +
  geom_line() +
  facet_grid(klc_id~., scales = "free") +
  #scale_colour_manual(values = col_pa) + 
  ylab("Percentage of KLC area with forest loss") 

# ingest into biopama_api
# save to csv
write_csv(klc_gfc, "../outputs/tables/klc_gfc_pc.csv")

# verify that total areas do match
ggplot(klc_gfc_pc %>% 
         filter(pa == 'total' & area_km2 < 25000),
       aes(x=area_km2, y = total_area, label = klc_name, fill = total_area/area_km2)) + 
  geom_point() + 
  geom_label()
# they don't. but it seems to be just for marine and coastal KLCs

# clean
unlink(downloaded_file$name)
drive_rm(downloaded_file)
