"""Methods used to extract Traffic Route from Strategic modelling data"""

import pandas as pd
import json
import pathlib


def load_data(strategic_data_file, sheet_name):
    """ Reads Excel data into Pandas DataFrames"""
    strategic_raw_data = pd.read_excel(strategic_data_file,dtype="object", header=4, sheet_name=sheet_name)
    return strategic_raw_data

def df_to_list(df):
    lst = df.to_string(header=False, index=False).split()
    return lst

def get_unique_codes(codes):
    # Create a list with unique code identifiers
    unique_codes_no_duplicates= []
    unique_codes = ["_".join(codes[i:i+3]) for i in range(0, len(codes), 3)]
    [unique_codes_no_duplicates.append(i) for i in unique_codes if i not in unique_codes_no_duplicates]
    return unique_codes_no_duplicates

def get_routes(links):
    nested_routes, nest_count =[], -1
    for i in range(len(links)):
        if links[i] == 'NaN':
            nested_routes.append([])
            nest_count +=1
            continue
        nested_routes[nest_count].append(links[i])
    return nested_routes

def qgis_json_format(LINK_INPUT, LINK_OUTPUT, FAIL_OUTPUT, unique_codes, routes):

    """Format the sequence of links to be a list of dictionaries accepted by qgis"""

    def define_filename(LINK_OUTPUT=LINK_OUTPUT, FAIL_OUTPUT=FAIL_OUTPUT):
        route_output = f"{LINK_OUTPUT}/{unique_codes[i]}.gpkg"
        route_fail_output = f"{FAIL_OUTPUT}/{unique_codes[i]}.gpkg"
        return route_output, route_fail_output

    qgis_route_list, route_ids = [], []
    for i in range(len(routes)):
        if unique_codes[i].endswith("_0"):
            continue
        route = {}
        route["PARAMETERS"] = {}
        route["PARAMETERS"]["INPUT"] = LINK_INPUT
        route["PARAMETERS"]["EXPRESSION"] = "' \\\"ID\\\"  = " + " or \\\"ID\\\"  = ".join(
            list(map(str, routes[i]))) + "\\n'"
        route["OUTPUTS"] = {}
        route["OUTPUTS"]["OUTPUT"], route["OUTPUTS"]["FAIL_OUTPUT"] = define_filename()
        route_ids.append(define_filename()[0])
        qgis_route_list.append(route)
    return qgis_route_list


def export_to_json(filename, data):
    file = f"{pathlib.Path.cwd()}/{filename}.json"
    with open(file, "w") as f:
        json.dump(data, f)
