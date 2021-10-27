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

            if re.match('^" +IR.*?$', line):
                line = re.sub('^"(.*?)"$', r'\1', line)

            # split line into list of values using the header positions
            # https://stackoverflow.com/a/10851479
            values = [
                line[start:end].strip()
                for start, end in zip(header_positions, header_positions[1:] + [None])
            ]
            all_lines.append(values)

        df = pd.DataFrame(all_lines, index=None, columns=stripped_headers)

        return df
