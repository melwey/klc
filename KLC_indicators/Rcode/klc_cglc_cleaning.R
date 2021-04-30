# klc_cglc: prepare data for ingestion into postgis database
library(tidyverse)
# import from google drive
library(googledrive)
downloaded_file <- drive_download("https://drive.google.com/file/d/1yV78jVnZmyZzlrO_vtbAti9Eiblr1VfY/view?usp=sharing", overwrite = TRUE)

klc_cglc <- read_delim(downloaded_file$name, delim = ",") %>%
  # change names
  select(-`system:index`, -.geo) %>%
  rename_with(~gsub("-coverfraction","", .x, fixed = TRUE)) %>%
  rename_with(~gsub("-", "_",.x, fixed = TRUE)) %>%
  rename_with(tolower) %>%
  # transform PA=false into (area where pa=false) - (area where pa = true)
  pivot_longer(bare:water_seasonal, names_to = "lc", values_to = "area") %>%
  pivot_wider(names_from = pa, values_from = area) %>%
  rename(total = `FALSE`) %>%
  mutate('outside' = total - `TRUE`) %>%
  rename('inside' = `TRUE`) %>%
  # reshape
  pivot_longer(c(total, outside, inside), names_to = "pa", values_to = "area") %>%
  pivot_wider(names_from = lc, values_from = area) %>%
  select(klc_id, pa, year, bare:water_seasonal)

# ingest into biopama_api
# save to csv
write_csv(klc_cglc, "../outputs/tables/klc_cglc.csv")

# clean
unlink(downloaded_file$name)
drive_rm(downloaded_file)
