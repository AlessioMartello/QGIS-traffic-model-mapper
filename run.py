import pathlib
import pandas as pd
import methods

strategic_data_file = pathlib.Path.cwd() / "Enfield Saturn Routes AM test.xlsx"
qgis_file = pathlib.Path.cwd() / "qgis_data.xlsx"
strategic_raw_data, qgis_table = methods.load_data(strategic_data_file, qgis_file)  # Load raw data

volumes, nodes = methods.select_route_data(strategic_raw_data)
ogv_volumes, ogv_nodes = methods.select_route_data(strategic_raw_data,
                                                   ogv=True)  # Extract routes for user class 9 (OGVs)

data_sets = {"routes": nodes, "ogv_routes": ogv_nodes}
volume_data_sets = {"volumes": volumes, "ogv_volumes": ogv_volumes}
route_codes, all_routes_list = [], []
for (user_class, data), (volume) in zip(data_sets.items(), volume_data_sets.values()):
    # Block executes code for JSON file to be imported into QGIS
    volume = volume.tolist()
    nodes = methods.to_list(data)
    nodes_grouped = methods.group_nodes(nodes)  # Group the node sequences that make up a route
    links = methods.group_links(nodes_grouped)  # From the node sequences create the links
    routes = methods.obtain_routes(links, qgis_table)  # For the links create the list of links that make up each route
    routes_df = pd.DataFrame(pd.Series(list(map(str,routes))), columns=["Routes"])
    routes_df["Volumes"] = pd.Series(volume, index=routes_df.index)
    routes_df=routes_df.groupby("Routes").sum()
    routes_df.to_excel(f"{user_class}grouped volumes.xlsx")
    qgis_routes, route_ids = methods.qgis_json_format(routes,
                                                      volume) if user_class != "ogv_routes" else methods.qgis_json_format(
        routes, volume, ogv=True)  # Format results
    methods.export_to_json(user_class, qgis_routes)  # Export json files

    # Block executes code for the Excel table of results
    all_routes_list.append(routes)  # List of all routes, before dropping duplicates, used for volume results
    route_codes.append([route_ids[i].split("/")[-1].strip(".gpkg") + "_" + str(volume[i]) for i in range(len(routes))])

methods.create_volume_table(route_codes, all_routes_list,
                            all_volumes=[volumes, ogv_volumes])  # Create a table of routes and volumes and export it
