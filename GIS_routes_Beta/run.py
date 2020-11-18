import pathlib

import methods

strategic_data_file = pathlib.Path.cwd() / "Enfield Saturn Routes AM test.xlsx"
qgis_file = pathlib.Path.cwd() / "qgis_data.xlsx"
strategic_raw_data, qgis_table = methods.load_data(strategic_data_file, qgis_file) #Load raw data

volumes, nodes = methods.select_route_data(strategic_raw_data)
ogv_volumes, ogv_nodes = methods.select_route_data(strategic_raw_data, ogv=True) #Extract routes for user class 9 (OGVs)

data_sets = {"routes": nodes, "ogv_routes": ogv_nodes}
route_codes, all_routes_list=[],[]
for user_class, data in data_sets.items():
    nodes = methods.to_list(data)
    nodes_grouped = methods.group_nodes(nodes) # Group the node sequences that make up a route
    links = methods.group_links(nodes_grouped) # From the node sequences create the links
    routes = methods.obtain_routes(links, qgis_table) # For the links create the list of links that make up each route
    all_routes_list.append(routes) # List of all routes, before dropping duplicates, used for volume results
    qgis_routes, route_ids = methods.qgis_json_format(routes) if user_class != "ogv_routes" else methods.qgis_json_format(routes, ogv=True) # Format results
    route_codes.append([route_ids[i].split("/")[-1].strip(".gpkg") for i in range(len(routes))])
    methods.export_to_json(user_class, qgis_routes) # Export json files

methods.create_volume_table(route_codes, all_routes_list, all_volumes = [volumes, ogv_volumes]) # Create a table of routes and volumes and export it