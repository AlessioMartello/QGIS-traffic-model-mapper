"""Methods used to extract Traffic Route from Strategic modelling data"""

import pandas as pd
import json
import pathlib


def load_data(strategic_data_file):
    """ Reads Excel data into Pandas DataFrames"""
    strategic_raw_data = pd.read_excel(strategic_data_file, header=0, sheet_name="AM_C_VisumPaths")
    return strategic_raw_data


def select_route_data(strategic_raw_data, ogv=None):
    """Obtain the relevant user class nodes"""
    ogv_index = min(strategic_raw_data[strategic_raw_data["UC"] == 9].index)

    strategic_data = strategic_raw_data[:ogv_index]
    volume_data = strategic_data[strategic_data.iloc[:, 0] != "route"]["Flow"].dropna().round(decimals=2)

    strategic_data = strategic_data[strategic_data.iloc[:, 0] == "route"]
    return strategic_data

def df_to_list(df):
    lst = df.to_string(header=False, index=False).split()
    return lst

def get_unique_codes(codes):
    # Create a list with unique code identifiers
    unique_codes = list(set(["_".join(codes[i:i+3]) for i in range(0, len(codes), 3)]))
    return unique_codes

def get_routes(links):
    nested_routes, nest_count =[], -1
    for i in range(len(links)):
        if links[i] == 'NaN':
            nested_routes.append([])
            nest_count +=1
            continue
        nested_routes[nest_count].append(links[i])
    return nested_routes

def group_nodes(nodes):
    """Create a nested list containing lists of nodes that make up each route. Use "route" string as separator."""

    nodes_grouped, count = [], -1  # todo change from -1
    for i in range(len(nodes)):
        if nodes[i] == "route":
            nodes_grouped.append([])
            count += 1
            continue
        if "+" in nodes[i]:
            nodes_grouped[count].append(float(nodes[i].replace("+", "")))  # Handle the extra characters
        else:
            nodes_grouped[count].append(float(nodes[i]))
    return nodes_grouped


def group_links(nodes_grouped):
    # Adjust the final element in each tuple that have been formatted as % in excel
    for count, node_group in enumerate(nodes_grouped):
        if len(str(node_group[-1])) < len(
                str(node_group[0])):  # Think of a more robust way, perhaps average the lengths of all but the last
            node_group[-1] = node_group[-1] * 100
        nodes_grouped[count] = list(map(int, node_group))

    # In the same nested list format, populate with the node to node combinations that make up the links
    links = []
    for i in range(len(nodes_grouped)):
        links.append([])
        for j in range(len(nodes_grouped[i]) - 1):
            links[i].append(f"{nodes_grouped[i][j]}>{nodes_grouped[i][j + 1]}")
    return links


def obtain_routes(links, qgis_table):
    # Extract the ID for each node to node combination, representing a link.
    # Obtain the link numbers for each node to node combination. Each list is a route composed of links.
    routes = []
    for i in range(len(links)):
        routes.append([])
        for link in links[i]:
            link_index = (qgis_table.index[qgis_table["AssBNode"] == link].tolist()[0])
            routes[i].append(qgis_table.at[link_index, "ID"])
    return routes


def unique_routes(routes, volume):
    """returns DataFrame containing unique routes and the total volume of each route"""
    volume = volume.tolist()
    routes_df = pd.DataFrame(pd.Series(list(map(str, routes))), columns=["Routes"])
    routes_df["Volumes"] = pd.Series(volume, index=routes_df.index)
    routes_df = routes_df.groupby("Routes", as_index=False).sum().round(decimals=2)
    return routes_df


def qgis_json_format(LINK_INPUT, LINK_OUTPUT, FAIL_OUTPUT, routes_df=pd.DataFrame([]), ogv=None,):
    """Format the sequence of links to be a list of dictionaries accepted by qgis"""
    unique_routes = [i.strip("[]").split(",") for i in routes_df["Routes"]]
    volumes = list(routes_df["Volumes"])

    def define_outputs(LINK_OUTPUT=LINK_OUTPUT, FAIL_OUTPUT=FAIL_OUTPUT):
        if not ogv:
            route_output = f"{LINK_OUTPUT}/{unique_routes[i][0]}_{i}_1_{volumes[i]}.gpkg"
            route_fail_output = f"{FAIL_OUTPUT}/{unique_routes[i][0]}_{i}_1_{volumes[i]}.gpkg"
        else:
            route_output = f"{LINK_OUTPUT}/{unique_routes[i][0]}_{i}_2_{volumes[i]}.gpkg"
            route_fail_output = f"{FAIL_OUTPUT}/{unique_routes[i][0]}_{i}_2_{volumes[i]}.gpkg"
        return route_output, route_fail_output

    qgis_route_list, route_ids = [], []
    for i in range(len(unique_routes)):
        route = {}
        route["PARAMETERS"] = {}
        route["PARAMETERS"]["INPUT"] = LINK_INPUT
        route["PARAMETERS"]["EXPRESSION"] = "' \\\"ID\\\"  = " + " or \\\"ID\\\"  = ".join(
            list(map(str, unique_routes[i]))) + "\\n'"
        route["OUTPUTS"] = {}
        route["OUTPUTS"]["OUTPUT"], route["OUTPUTS"]["FAIL_OUTPUT"] = define_outputs()
        route_ids.append(define_outputs()[0])
        qgis_route_list.append(route)
    return qgis_route_list, route_ids


def export_to_json(filename, data):
    file = f"{pathlib.Path.cwd()}/outputs/{filename}.json"
    with open(file, "w") as f:
        json.dump(data, f)


def prepare_excel_results(route_codes, all_routes_list, all_volumes, unique_routes_df, route_ids):
    def append(named_list, data):
        named_list.append(data)

    append(all_routes_list,
           unique_routes_df["Routes"])  # List of all routes, before dropping duplicates, used for volume results
    append(all_volumes, unique_routes_df["Volumes"])
    append(route_codes, [route_ids[i].split("/")[-1].strip(".gpkg") for i in range(len(route_ids))])


def create_volume_table(route_codes, unique_routes_list, all_volumes):
    for route_code, links, volumes, names in zip(route_codes, unique_routes_list, all_volumes,
                                                 ["Volumes", "OGV_Volumes"]):
        route_codes_id_df = pd.DataFrame(route_code).reset_index(drop=True)
        route_codes_id_df.columns = [f"Origin_Route-ID_UC_Volume"]
        links_df = links.reset_index(drop=True)
        volumes_df = volumes.reset_index(drop=True)
        volume_results = pd.concat([route_codes_id_df, links_df, volumes_df], axis=1)
        volume_results.to_excel(f"{pathlib.Path.cwd()}/outputs/{names}.xlsx", index=False)
