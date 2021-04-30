import pandas as pd
import re
import os


"""convert random space-separated txt file to tab delimited"""

"""this script works only for the problematic files from legs 180/181.
# the other files from legs 149,172,174,175 (6 total files) were organized
# differently (from legs 180/181 and from each other) so I wrote small
# scripts for each (6 total) and had to manually edit some."""


def get_headers(first_line):
    """getting a separate list of all headers"""
    header_list = re.findall("[A-Z][^A-Z]*", first_line)
    trigger_headers = [
        "From (oldest) ",
        "To (youngest) ",
        "From (bottom) ",
        "To  (top) ",
        "Group                                  ",
        "Abundance ",
        "Preservation ",
    ]
    for i in range(0, len(header_list)):
        if header_list[i] in trigger_headers:
            header_list[i - 1] = header_list[i - 1] + header_list[i]
            header_list[i] = " "
    return [i for i in header_list if i.strip()]


def get_csv(coord, dir_name):
    """converting txt file to tab delimited txt file"""
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
                    app = work[start : len(work)].strip()
                    if "," in app:
                        work_vals.append(app.strip(","))
                    else:
                        work_vals.append(app)
            reformat = [list(x) for x in zip(*[work_vals])]
            flattened = [val for sublist in reformat for val in sublist]
            all_lines.append(flattened)
        stripped_hl = [s.rstrip() for s in headers_list]
        df = pd.DataFrame(
            all_lines[1 : len(all_lines)], index=None, columns=stripped_hl
        )
        ext = coord.split("space_delim_original", 1)[1]
        # upload cleaned files to cleaned_data/...
        fix = os.path.join(
            dir_name, "notebooks/cleaned_data/odp_all_paleontology/range_tables" + ext
        )
        df.to_csv(fix, sep="\t", index=False)


""""--- main ---"""

problem_files = [
    "raw_data/odp_all_paleontology/range_tables/180/1109/HOLE_C/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1109/HOLE_C/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1109/HOLE_D/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1109/HOLE_D/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1110/HOLE_A/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1110/HOLE_A/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1110/HOLE_B/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1110/HOLE_B/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1111/HOLE_A/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1111/HOLE_A/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1112/HOLE_A/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1112/HOLE_A/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1114/HOLE_A/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1114/HOLE_A/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1115/HOLE_A/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1115/HOLE_A/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1115/HOLE_B/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1115/HOLE_B/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1115/HOLE_C/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1115/HOLE_C/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1116/HOLE_A/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1116/HOLE_A/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1117/HOLE_C/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1118/HOLE_A/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/180/1118/HOLE_A/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_A/Diatoms.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_A/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_A/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_A/Radiolarians.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_B/Benthic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_B/Diatoms.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_B/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_B/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_B/Radiolarians.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_C/Benthic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_C/Diatoms.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_C/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_C/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1119/HOLE_C/Radiolarians.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_A/Diatoms.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_A/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_A/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_A/Radiolarians.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_B/Benthic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_B/Diatoms.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_B/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_B/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_B/Radiolarians.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_C/Benthic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_C/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_D/Diatoms.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_D/Nannofossils.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_D/Planktonic_Foraminifers.txt",
    "raw_data/odp_all_paleontology/range_tables/181/1120/HOLE_D/Radiolarians.txt",
]

dir_name = os.path.split(os.path.dirname(__file__))[0]
for file in problem_files:
    add_ext = "notebooks/" + file
    filename = os.path.join(dir_name, add_ext)
    get_csv(filename, dir_name)
