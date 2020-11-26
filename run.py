import pathlib
import methods

def run_analysis(strategic_data_file, qgis_file):
    # strategic_data_file = pathlib.Path(strategic_data_file)
    # qgis_file = pathlib.Path(qgis_file)
    strategic_raw_data, qgis_table = methods.load_data(strategic_data_file, qgis_file)  # Load raw data

    volumes, nodes = methods.select_route_data(strategic_raw_data)
    ogv_volumes, ogv_nodes = methods.select_route_data(strategic_raw_data,
                                                       ogv=True)  # Extract routes for user class 9 (OGVs)

    data_sets = {"routes": nodes, "ogv_routes": ogv_nodes}
    volume_data_sets = {"volumes": volumes, "ogv_volumes": ogv_volumes}
    route_codes, all_routes_list, all_volumes = [], [], []
    for (user_class, data), (volume) in zip(data_sets.items(), volume_data_sets.values()):
        # Block executes code for JSON file to be imported into QGIS
        nodes = methods.to_list(data)
        nodes_grouped = methods.group_nodes(nodes)  # Group the node sequences that make up a route
        links = methods.group_links(nodes_grouped)  # From the node sequences create the links
        routes = methods.obtain_routes(links, qgis_table)  # For the links create the list of links that make up each route
        unique_routes_df = methods.unique_routes(routes, volume) # Group duplicate routes and sum the volumes
        qgis_routes, route_ids = methods.qgis_json_format(unique_routes_df) if user_class != "ogv_routes" else methods.qgis_json_format(unique_routes_df, ogv=True)  # Format results
        methods.export_to_json(user_class, qgis_routes)  # Export json files

        # Block executes code for the Excel table of results
        methods.prepare_excel_results(route_codes, all_routes_list, all_volumes, unique_routes_df, route_ids)

    methods.create_volume_table(route_codes, all_routes_list,
                                all_volumes=all_volumes)  # Create a table of routes and volumes and export it
