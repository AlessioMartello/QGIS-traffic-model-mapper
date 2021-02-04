import methods


def run_analysis():

    strategic_data_file = "C:/Users/Alessio/programming/Python/Visum_routes/HLN_FB_AM_Cordon_routing_info.xlsx"
    # link_input = "link_input"
    # link_output = "link_output"
    # fail_output = "fail_output"
    strategic_raw_data = methods.load_data(strategic_data_file)  # Load raw data
    od_codes = strategic_raw_data.iloc[4:,0:3].dropna()
    links = methods.df_to_list(strategic_raw_data.iloc[4:, 3])

    codes = methods.df_to_list(od_codes)
    unique_codes = methods.get_unique_codes(codes)

    routes = methods.get_routes(links)

    print(routes,"\n", unique_codes)
run_analysis()