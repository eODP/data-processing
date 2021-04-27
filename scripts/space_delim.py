# convert random space-separated txt file to tab delimited

import pandas as pd
import csv,re,os
import numpy as np

def split(word):
    return [char for char in word]


def getindices(s):
    return [i for i, c in enumerate(s) if c.isupper()]


def get_headers(first_line):
    # --- getting a separate list of all headers ---
    header_list = re.findall('[A-Z][^A-Z]*', first_line)
    trigger_headers = ["From (oldest) ", "To (youngest) ", "From (bottom) ", "To  (top) ",
                       "Group                                  ", "Abundance ", "Preservation "]
    for i in range(0, len(header_list)):
        if header_list[i] in trigger_headers:
            header_list[i - 1] = header_list[i - 1] + header_list[i]
            header_list[i] = ' '
    header_list = [i for i in header_list if i.strip()]
    # header_list = [s.rstrip() for s in header_list]
    return header_list


def get_csv(coord):
    # --- converting txt file to tab delimited txt file ---
    with open(coord) as infile:
        first_line = infile.readline()
        headers_list = get_headers(first_line)
        head_loc = []
        for i in range(0, len(headers_list)):
            head_loc.append(first_line.index(headers_list[i]))
        file = infile.readlines()
        all_lines = []
        for k in range(0, len(file)):
            work_vals = []
            work = file[k]
            for j in range(0, len(headers_list)):
                start = head_loc[j]
                if int(j) != len(headers_list) - 1:
                    end = head_loc[j + 1]
                    app = work[start:end].strip()
                    if "," in app:
                        work_vals.append(app.strip(","))
                    else:
                        work_vals.append(app)
                else:
                    app = work[start:len(work)].strip()
                    if "," in app:
                        work_vals.append(app.strip(","))
                    else:
                        work_vals.append(app)
            reformat = [list(x) for x in zip(*[work_vals])]
            flattened = [val for sublist in reformat for val in sublist]
            all_lines.append(flattened)
        stripped_hl = [s.rstrip() for s in headers_list]
        df = pd.DataFrame(all_lines[1:len(all_lines)], index=None, columns=stripped_hl)
        ext = coord.split("space_delim_check",1)[1]
        fix = "/Users/morga/PycharmProjects/clean_up/space_delim" + ext
        df.to_csv(fix, sep='\t', index=False)
        # return fix --- for testing


# --- main ---

# I saved a local copy of all of the original problematic space_delim files
# Traversing the directory to get to the txt files
root_dir = "/Users/morga/PycharmProjects/clean_up/space_delim_check/175"
site_list = os.listdir(root_dir)
for site in site_list:
    site_path = os.path.join(root_dir, str(site))
    hole_list = os.listdir(site_path)
    for hole in hole_list:
        hole_path = os.path.join(site_path, hole)
        data_list = os.listdir(hole_path)
        for data in data_list:
            data_path = os.path.join(hole_path, data)
            fixed_path = get_csv(data_path)
            # --- to test the file ouput in csv form ---
            # test_df = pd.read_csv(fixed_path,sep='\t')
            # curr_dir = os.path.splitext(fixed_path)
            # test_df.to_csv(curr_dir[0] + ".csv", index=False)
