from saturn_routes import methods


def run_analysis(strategic_data_file, link_input, rounding=False):
    useful_sheet_list = list(filter(lambda x: "VisumPaths" in x, methods.load_data(strategic_data_file, None).keys()))
    for sheet in useful_sheet_list:
        strategic_raw_data = methods.load_data(strategic_data_file, sheet)
        od_codes = strategic_raw_data.iloc[:, 0:3].dropna()
        links = methods.df_to_list(strategic_raw_data.iloc[:, 4])
        codes = methods.df_to_list(od_codes)
        unique_codes = methods.get_unique_codes(codes)
        routes = methods.get_routes(links)
        volume_data = methods.load_data(strategic_data_file, sheet.replace("Paths", "Flows"))
        if rounding:
            volumes = methods.df_to_list(volume_data["VOL(AP)"].astype("float").round().astype("int"))
        else:
            volumes = methods.df_to_list(volume_data["VOL(AP)"])
        unique_volume_codes = [f"{i}_{j}" for i, j in zip(unique_codes, volumes)]
        directories = methods.create_route_directory(link_input, sheet)
        directories.insert(0, link_input)
        formatted_results = methods.qgis_json_format(*directories, unique_volume_codes, routes)
        methods.export_to_json(sheet, link_input, formatted_results)