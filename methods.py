"""Methods used to extract Traffic Route from Strategic modelling data"""

import pandas as pd
import json

from constants import LINK_INPUT, LINK_OUTPUT, FAIL_OUTPUT


def load_data(strategic_data_file, qgis_data_file):
    """ Reads Excel data into Pandas DataFrames"""
    strategic_raw_data = pd.read_excel(strategic_data_file, header=0, dtpe=object)
    qgis_table = pd.read_excel(qgis_data_file, header=0, usecols=["AssBNode", "ID"], index_col=None)
    return strategic_raw_data, qgis_table


def select_route_data(strategic_raw_data, ogv=None):
    """Obtain the relevant user class nodes"""
    ogv_index = min(strategic_raw_data[strategic_raw_data["UC"] == 9].index)
    if ogv:
        strategic_data = strategic_raw_data[ogv_index:]
        volume_data = strategic_data[strategic_data.iloc[:, 0] != "route"]["Flow"].dropna().round(decimals=2)
    else:
        strategic_data = strategic_raw_data[:ogv_index]
        volume_data = strategic_data[strategic_data.iloc[:, 0] != "route"]["Flow"].dropna().round(decimals=2)

    strategic_data = strategic_data[strategic_data.iloc[:, 0] == "route"]
    return volume_data, strategic_data


def to_list(strategic_data):
    # Create a list with all the nodes
    nodes = strategic_data.to_string(header=False, index=False).split()
    nodes = list(filter(lambda x: "NaN" not in x, nodes))
    return nodes


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
    # Adjust the final element in each uple that have been formatted as % in excel
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


def qgis_json_format(routes_df=pd.DataFrame([]), ogv=None, LINK_INPUT=LINK_INPUT):
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
    file = f"{filename}.json"
    with open(file, "w") as f:
        json.dump(data, f)


def create_volume_table(route_codes, unique_routes_df, all_volumes):
    for route_code, links, volumes, names in zip(route_codes, unique_routes_df, all_volumes,
                                                 ["Volumes", "OGV_Volumes"]):
        route_codes_id_df = pd.DataFrame(route_code).reset_index(drop=True)
        route_codes_id_df.columns = [f"Origin_Route-ID_UC_Volume"]
        links_df = links.reset_index(drop=True)
        volumes_df = volumes.reset_index(drop=True)
        volumes_df.columns = [f"Volume"]
        volume_results = pd.concat([route_codes_id_df, links_df, volumes_df], axis=1)
        volume_results.to_excel(f"{names}.xlsx", index=False)
