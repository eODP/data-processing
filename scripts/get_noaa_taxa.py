
import csv
import os
import pandas as pd
import glob
import sys
import numpy as np
import re

data_path = 'notebooks/cleaned_data/odp_all_paleontology/range_tables/'
full_path = os.path.join(os.path.split(os.getcwd())[0], data_path)
raw_csvs = glob.glob(f"{full_path}/**/*.txt", recursive=True)

non_taxa_fields = ['Data', 'Age', 'From', '(oldest)', 'To', '(youngest)', 'Zone', '(bottom)', '(top)',
                'Leg', 'Site', 'H', 'Cor', 'T', 'Sc', 'Top(cm)', 'Depth', '(mbsf)',
                'Scientist', 'Fossil', 'Group', 'Group', 'Abundance', 'Group', 'Preservation',
                'Comment']


taxa_list = []
taxon_group_list = []
for file in raw_csvs:
    df = pd.read_csv(file, delimiter="\t")
    col_headers = list(df.columns.values)
    taxon_group = (os.path.splitext(os.path.split(file)[1])[0]).lower()
    for col in col_headers:
        column_split = col.split()
        non_taxa_bool = any(column in column_split for column in non_taxa_fields)
        if non_taxa_bool:
            next
        elif col in taxa_list:
            next
        else:
            taxa_list.append(col)
            taxon_group_list.append(taxon_group)
data = list(zip(taxa_list, taxon_group_list))
taxa_df = pd.DataFrame(data, columns=['verbatim_name', 'taxon_group'])
taxa_df['genera'] = taxa_df['verbatim_name'].str.extract('^([A-Z][a-z]+) [a-z]+')
taxa_df.head()
taxa_df.to_csv('noaa_taxa.csv', index=False)
