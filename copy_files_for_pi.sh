#!/bin/bash
mkdir -p ../PI_scripts/scripts
mkdir -p ../PI_scripts/raw_data/PI_processed_files
mkdir -p ../PI_scripts/output/taxa/LIMS

cp scripts/taxa_stats.R ../PI_scripts/scripts
cp scripts/taxa_stats.Rmd ../PI_scripts/scripts/
cp raw_data/PI_processed_files/LIMS_Micropal_headers_PBDB_Taxonomy_notes_taxa_list_2021-07-28.csv  ../PI_scripts/raw_data/PI_processed_files
cp output/taxa/LIMS/taxa_stats_2021-08-16.csv  ../PI_scripts/output/taxa/LIMS
