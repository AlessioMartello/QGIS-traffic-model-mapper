import pandas as pd
import json
from constants import LINK_INPUT, LINK_OUTPUT, FAIL_OUTPUT


def load_data(strategic_data_file, qgis_data_file):
    """ Reads Excel data into Pandas DataFrames"""
    strategic_raw_data = pd.read_excel(strategic_data_file, header=0, dtpe=object)
    qgis_table = pd.read_excel(qgis_data_file, sheet_name=1, header=0, usecols=["AssANode","AssBNode", "ID"], index_col=None)
    return strategic_raw_data, qgis_table

def select_route_data(strategic_raw_data, ogv=None):
    """Obtain the relevant user class nodes"""
    ogv_index=min(strategic_raw_data[strategic_raw_data["UC"] == 9].index)
    if ogv:
        strategic_data=strategic_raw_data[ogv_index:]
    else:
        strategic_data=strategic_raw_data[:ogv_index]
    strategic_data=strategic_data[strategic_data.iloc[:,0] == "route"]

    # Create a list with all the nodes
    nodes = strategic_data.to_string(header=False, index=False).split()
    nodes=list(filter(lambda x: "NaN" not in x, nodes))
    return nodes

def select_volume_data(strategic_raw_data):
    """Obtain the relevant user class traffic flow data"""
    volume_data=strategic_raw_data[strategic_raw_data.iloc[:,0] != "route"]["Flow"]

    # Create a list with all the volumes
    nodes = volume_data.to_string(header=False, index=False).split()
    nodes=list(filter(lambda x: "NaN" not in x, nodes))
    return nodes

def group_nodes(nodes):
    """Create a nested list containing lists of nodes that make up each route. Use "route" string as separator."""
    
    nodes_grouped, count = [], -1 # todo change from -1
    for i in range(len(nodes)):
        if nodes[i] == "route":
            nodes_grouped.append([])
            count+=1
            continue
        if "+" in nodes[i]:
            nodes_grouped[count].append(float(nodes[i].replace("+",""))) # Handle the extra characters
        else:
            nodes_grouped[count].append(float(nodes[i]))
    return nodes_grouped

def group_links(nodes_grouped):
    # Adjust the final element in each uple that have been formatted as % in excel
    for count, node_group in enumerate(nodes_grouped):
        if len(str(node_group[-1])) < len(str(node_group[0])): # Think of a more robust way, perhaps average the lengths of all but the last
            node_group[-1] = node_group[-1]*100
        nodes_grouped[count] = list(map(int,node_group))

    # In the same nested list format, populate with the node to node combinations that make up the links
    links=[]
    for i in range(len(nodes_grouped)):
        links.append([])
        for j in range(len(nodes_grouped[i])-1):
            links[i].append(f"{nodes_grouped[i][j]}>{nodes_grouped[i][j+1]}")
    return links

def obtain_routes(links, qgis_table):
    # Extract the ID for each node to node combination, representing a link.
    # Obtain the link numbers for each node to node combination. Each list is a route composed of links.
    routes=[]
    for i in range(len(links)):
        routes.append([])
        for link in links[i]:
            link_index = (qgis_table.index[qgis_table["AssBNode"] == link].tolist()[0])
            routes[i].append(qgis_table.at[link_index, "ID"])
    return routes

def routes_volume_join(routes, volumes):
    """ Join the Routes for every user class to the respective traffic volumes"""
    lst=[]
    res ={}
    for i,route, volume in zip(range(len(routes)), routes, volumes):
        res={}
        res["Route"] = route
        lst.append(res)
    return lst

def drop_duplicates(lst):
    """Remove any duplicate routes"""
    unique_routes=[]
    unique_routes = [list(i.values())[0] for i in lst if list(i.values())[0] not in unique_routes]
    return unique_routes

def qgis_json_format(unique_routes, ogv=None, LINK_INPUT=LINK_INPUT, LINK_OUTPUT=LINK_OUTPUT, FAIL_OUTPUT=FAIL_OUTPUT):
    """Format the sequence of links to be a list of dictionaries accepted by qgis"""
    def define_outputs():
        if not ogv:
            route_output = f"{LINK_OUTPUT}/{i}_1.gpkg"
            route_fail_output = f"{FAIL_OUTPUT}/{i}_1.gpkg"
        else:
            route_output = f"{LINK_OUTPUT}/{i}_2.gpkg"
            route_fail_output = f"{FAIL_OUTPUT}/{i}_2.gpkg"
        return route_output, route_fail_output

    qgis_route_list = []
    for i in range(len(unique_routes)):
        route={}
        route["PARAMETERS"] ={}
        route["PARAMETERS"]["INPUT"] = LINK_INPUT
        route["PARAMETERS"]["EXPRESSION"] = "' \\\"NO\\\"  = " + " or \\\"NO\\\"  = ".join(list(map(str,unique_routes[i]))) + "\\n'"
        route["OUTPUTS"] = {}
        route["OUTPUTS"]["OUTPUT"], route["OUTPUTS"]["FAIL_OUTPUT"] = define_outputs()
        qgis_route_list.append(route)
    return qgis_route_list

def export_to_json(filename, data):
    file = f"{filename}.json"
    with open(file, "w") as f:
        json.dump(data, f)