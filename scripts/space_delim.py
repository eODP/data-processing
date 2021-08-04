import re
import os

import fire
import pandas as pd


"""convert random space-separated txt file to tab delimited"""


def is_standard_header(header1, header2):
    headers = [
        {"a": "Age", "b": "From (oldest)"},
        {"a": "Age", "b": "To (youngest)"},
        {"a": "Zone", "b": "From (bottom)"},
        {"a": "Zone", "b": "To (top)"},
        {"a": "Fossil", "b": "Group"},
        {"a": "Group", "b": "Abundance"},
        {"a": "Group", "b": "Preservation"},
    ]
    header1 = re.sub(" +", " ", header1).strip()
    header2 = re.sub(" +", " ", header2).strip()

    match = False
    for header in headers:
        if header1 == header["a"] and header2 == header["b"]:
            match = True
    return match


def get_headers(first_line):
    """take a string, and form a list of headers"""
    headers = re.findall("[A-Z][^A-Z]*", first_line)

    for i in range(0, len(headers)):
        # merges 2 headers when there are standard headers
        # 'Age ', 'From (oldest) ' -> 'Age From (oldest) '
        if i < len(headers) - 1 and is_standard_header(headers[i], headers[i + 1]):
            headers[i] = headers[i] + headers[i + 1]
            headers[i + 1] = " "

        # megers multiple headers when there are parathensis
        # 'header1 (', 'Text', 'More) text' -> 'header1 (Text More) text'
        elif re.search("\(", headers[i]) and not re.search("\)", headers[i]):
            indexes = []
            updated_header = ""
            for j in range(i, len(headers)):
                updated_header += headers[j]
                indexes.append(j)
                if re.search("\)", headers[j]):
                    break

            for index in indexes:
                headers[index] = ""
            headers[i] = updated_header

        # merges 2 headers into 1 header when there are species modifier
        # 'Genus sp. ', 'A ' -> 'Genus sp. A '
        # 'Genus sp. ', 'G. species ' -> 'Genus sp. G. species '
        elif re.search(" sp.|aff.|cf. +$", headers[i]) and re.match(
            "([A-Z]|[A-Z]\. [a-z]+) ?$", headers[i + 1]
        ):
            headers[i] = headers[i] + headers[i + 1]
            headers[i + 1] = " "

        # # merges 2 headers into 1 header
        # # 'header1 ', 'A ' -> 'header1 A'
        # elif re.match("^[A-Z] +$", headers[i]) and not re.match(
        #     "(Cor|Site) +$", headers[i - 1]
        # ):
        #     headers[i - 1] = headers[i - 1] + headers[i]
        #     headers[i] = " "

        # merges 3 headers into 1 header when 'Xxxx Form X'
        # 'Genus ', 'Form ', 'A ' -> 'Genus Form A '
        elif re.search("^Form +$", headers[i]) and re.match("[A-Z] +$", headers[i + 1]):
            headers[i - 1] = headers[i - 1] + headers[i] + headers[i + 1]
            headers[i] = " "
            headers[i + 1] = " "

    return [i for i in headers if i.strip()]


def convert_space_delim_file(filename):
    """converting space delimited txt file to tab delimited txt file"""
    with open(filename) as infile:
        # iterate over lines until we reach the header line
        for line in infile:
            if line.startswith("Abbreviated View --ALL"):
                continue
            elif line == '""\n':
                continue
            elif line == "\n":
                continue
            else:
                first_line = line
                break

        headers_list = get_headers(first_line)
        stripped_headers = [header.strip() for header in headers_list]

        # keep track of the start position for each header
        header_positions = []
        start_position = 0
        for i in range(0, len(headers_list)):
            header_positions.append(start_position)
            start_position = start_position + len(headers_list[i])

        all_lines = []
        for line in infile.readlines():
            if line == '\n':
                continue
            elif line == '""\n':
                continue

            # split line into list of values using the header positions
            # https://stackoverflow.com/a/10851479
            values = [
                line[start:end].strip()
                for start, end in zip(header_positions, header_positions[1:] + [None])
            ]
            all_lines.append(values)

        df = pd.DataFrame(all_lines, index=None, columns=stripped_headers)

        return df


odp_base_path = "odp_all_paleontology|range_tables|"
# convert files by script
space_delim_files_odp_1 = [
    "149|897|HOLE_C|Nannofossils.txt",
    "174|1071|HOLE_B|Benthic_Foraminifers.txt",
    "175|1085|HOLE_A|Planktonic_Foraminifers.txt",
    "180|1109|HOLE_C|Nannofossils.txt",
    "180|1109|HOLE_C|Planktonic_Foraminifers.txt",
    "180|1109|HOLE_D|Nannofossils.txt",
    "180|1109|HOLE_D|Planktonic_Foraminifers.txt",
    "180|1110|HOLE_A|Nannofossils.txt",
    "180|1110|HOLE_A|Planktonic_Foraminifers.txt",
    "180|1110|HOLE_B|Nannofossils.txt",
    "180|1110|HOLE_B|Planktonic_Foraminifers.txt",
    "180|1111|HOLE_A|Nannofossils.txt",
    "180|1111|HOLE_A|Planktonic_Foraminifers.txt",
    "180|1112|HOLE_A|Nannofossils.txt",
    "180|1112|HOLE_A|Planktonic_Foraminifers.txt",
    "180|1114|HOLE_A|Nannofossils.txt",
    "180|1114|HOLE_A|Planktonic_Foraminifers.txt",
    "180|1115|HOLE_A|Nannofossils.txt",
    "180|1115|HOLE_A|Planktonic_Foraminifers.txt",
    "180|1115|HOLE_B|Nannofossils.txt",
    "180|1115|HOLE_B|Planktonic_Foraminifers.txt",
    "180|1115|HOLE_C|Nannofossils.txt",
    "180|1115|HOLE_C|Planktonic_Foraminifers.txt",
    "180|1116|HOLE_A|Nannofossils.txt",
    "180|1116|HOLE_A|Planktonic_Foraminifers.txt",
    "180|1117|HOLE_C|Nannofossils.txt",
    "180|1118|HOLE_A|Nannofossils.txt",
    "180|1118|HOLE_A|Planktonic_Foraminifers.txt",
    "181|1119|HOLE_A|Diatoms.txt",
    "181|1119|HOLE_A|Nannofossils.txt",
    "181|1119|HOLE_A|Planktonic_Foraminifers.txt",
    "181|1119|HOLE_A|Radiolarians.txt",
    "181|1119|HOLE_B|Benthic_Foraminifers.txt",
    "181|1119|HOLE_B|Diatoms.txt",
    "181|1119|HOLE_B|Nannofossils.txt",
    "181|1119|HOLE_B|Planktonic_Foraminifers.txt",
    "181|1119|HOLE_B|Radiolarians.txt",
    "181|1119|HOLE_C|Benthic_Foraminifers.txt",
    "181|1119|HOLE_C|Diatoms.txt",
    "181|1119|HOLE_C|Nannofossils.txt",
    "181|1119|HOLE_C|Planktonic_Foraminifers.txt",
    "181|1119|HOLE_C|Radiolarians.txt",
    "181|1120|HOLE_A|Diatoms.txt",
    "181|1120|HOLE_A|Nannofossils.txt",
    "181|1120|HOLE_A|Planktonic_Foraminifers.txt",
    "181|1120|HOLE_A|Radiolarians.txt",
    "181|1120|HOLE_B|Benthic_Foraminifers.txt",
    "181|1120|HOLE_B|Diatoms.txt",
    "181|1120|HOLE_B|Nannofossils.txt",
    "181|1120|HOLE_B|Planktonic_Foraminifers.txt",
    "181|1120|HOLE_B|Radiolarians.txt",
    "181|1120|HOLE_C|Benthic_Foraminifers.txt",
    "181|1120|HOLE_C|Planktonic_Foraminifers.txt",
    "181|1120|HOLE_D|Diatoms.txt",
    "181|1120|HOLE_D|Nannofossils.txt",
    "181|1120|HOLE_D|Planktonic_Foraminifers.txt",
    "181|1120|HOLE_D|Radiolarians.txt",
]

# manually edit files first, then convert files by script
space_delim_files_odp_2 = [
    "172|1056|HOLE_C|Nannofossils.txt",
    "175|1081|HOLE_A|Planktonic_Foraminifers.txt",
]

# manually edit files
space_delim_files_odp_3 = [
    "174|1071|HOLE_B|Planktonic_Foraminifers.txt",
    "175|1077|HOLE_A|Diatoms.txt",
]

janus_base_path = "NOAA_csv|JanusIODP_paleo_agemodel|paleontology|range_tables|"
# convert files by script
space_delim_files_janus_iodp_1 = [
    "149|897|HOLE_C|Nannofossils.csv",
    "174|1071|HOLE_B|Benthic_Foraminifers.csv",
    "175|1085|HOLE_A|Planktonic_Foraminifers.csv",
    "180|1114|HOLE_A|Nannofossils.csv",
    "180|1114|HOLE_A|Planktonic_Foraminifers.csv",
    "180|1112|HOLE_A|Nannofossils.csv",
    "180|1112|HOLE_A|Planktonic_Foraminifers.csv",
    "180|1115|HOLE_B|Nannofossils.csv",
    "180|1115|HOLE_B|Planktonic_Foraminifers.csv",
    "180|1115|HOLE_C|Nannofossils.csv",
    "180|1115|HOLE_C|Planktonic_Foraminifers.csv",
    "180|1115|HOLE_A|Nannofossils.csv",
    "180|1115|HOLE_A|Planktonic_Foraminifers.csv",
    "180|1109|HOLE_C|Nannofossils.csv",
    "180|1109|HOLE_C|Planktonic_Foraminifers.csv",
    "180|1109|HOLE_D|Nannofossils.csv",
    "180|1109|HOLE_D|Planktonic_Foraminifers.csv",
    "180|1110|HOLE_B|Nannofossils.csv",
    "180|1110|HOLE_B|Planktonic_Foraminifers.csv",
    "180|1110|HOLE_A|Nannofossils.csv",
    "180|1110|HOLE_A|Planktonic_Foraminifers.csv",
    "180|1117|HOLE_C|Nannofossils.csv",
    "180|1116|HOLE_A|Nannofossils.csv",
    "180|1116|HOLE_A|Planktonic_Foraminifers.csv",
    "180|1111|HOLE_A|Nannofossils.csv",
    "180|1111|HOLE_A|Planktonic_Foraminifers.csv",
    "180|1118|HOLE_A|Nannofossils.csv",
    "180|1118|HOLE_A|Planktonic_Foraminifers.csv",
    "181|1119|HOLE_B|Diatoms.csv",
    "181|1119|HOLE_B|Nannofossils.csv",
    "181|1119|HOLE_B|Benthic_Foraminifers.csv",
    "181|1119|HOLE_B|Radiolarians.csv",
    "181|1119|HOLE_B|Planktonic_Foraminifers.csv",
    "181|1119|HOLE_C|Diatoms.csv",
    "181|1119|HOLE_C|Nannofossils.csv",
    "181|1119|HOLE_C|Benthic_Foraminifers.csv",
    "181|1119|HOLE_C|Radiolarians.csv",
    "181|1119|HOLE_C|Planktonic_Foraminifers.csv",
    "181|1119|HOLE_A|Diatoms.csv",
    "181|1119|HOLE_A|Nannofossils.csv",
    "181|1119|HOLE_A|Radiolarians.csv",
    "181|1119|HOLE_A|Planktonic_Foraminifers.csv",
    "181|1120|HOLE_B|Diatoms.csv",
    "181|1120|HOLE_B|Nannofossils.csv",
    "181|1120|HOLE_B|Benthic_Foraminifers.csv",
    "181|1120|HOLE_B|Radiolarians.csv",
    "181|1120|HOLE_B|Planktonic_Foraminifers.csv",
    "181|1120|HOLE_C|Benthic_Foraminifers.csv",
    "181|1120|HOLE_C|Planktonic_Foraminifers.csv",
    "181|1120|HOLE_D|Diatoms.csv",
    "181|1120|HOLE_D|Nannofossils.csv",
    "181|1120|HOLE_D|Radiolarians.csv",
    "181|1120|HOLE_D|Planktonic_Foraminifers.csv",
    "181|1120|HOLE_A|Diatoms.csv",
    "181|1120|HOLE_A|Nannofossils.csv",
    "181|1120|HOLE_A|Radiolarians.csv",
    "181|1120|HOLE_A|Planktonic_Foraminifers.csv",
]

# manually edit files first, then convert files by script
space_delim_files_janus_iodp_2 = [
    "172|1056|HOLE_C|Nannofossils.csv",
    "174|1071|HOLE_B|Planktonic_Foraminifers.csv",
]

# manually edit files
space_delim_files_janus_iodp_3 = [
    "175|1077|HOLE_A|Diatoms.csv",
]



class Space_Delim(object):
    def fix_odp_paleo(self):
        for file in space_delim_files_odp_1:
            path = ("notebooks|raw_data|" + odp_base_path + file).split("|")
            filename = os.path.join(*path)
            df = convert_space_delim_file(filename)
            path = filename.replace("raw_data", "cleaned_data")
            df.to_csv(path, index=False, sep="\t")

    def fix_odp_paleo_hybrid(self):
        """Manually edit the files first, then run script"""
        for file in space_delim_files_odp_2:
            path = ("notebooks|cleaned_data|" + odp_base_path + file).split("|")
            filename = os.path.join(*path)
            df = convert_space_delim_file(filename)
            df.to_csv(filename, index=False, sep="\t")

    def fix_janus_iodp_paleo(self):
        for file in space_delim_files_janus_iodp_1:
            path = ("notebooks|raw_data|" + janus_base_path + file).split("|")
            filename = os.path.join(*path)
            df = convert_space_delim_file(filename)
            path = filename.replace("raw_data", "cleaned_data")
            df.to_csv(path, index=False)

    def fix_janus_iodp_paleo_hybrid(self):
        """Manually edit the files first, then run script"""
        for file in space_delim_files_janus_iodp_2:
            path = ("notebooks|cleaned_data|" + janus_base_path + file).split("|")
            filename = os.path.join(*path)
            df = convert_space_delim_file(filename)
            df.to_csv(filename, index=False)


if __name__ == "__main__":
    fire.Fire(Space_Delim)
