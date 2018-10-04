#!/usr/Anaconda3/bin/python3
# ep_3results.py by Vaclav Hasik

from sys import platform
import timeit
import humanfriendly
import time
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import json
import requests

plt.style.use('ggplot')

'''
MAIN BODY
Pseudo-code:
- Open xml results file
- Extract the end use data
  - Start on line 29 column 2 end on line 55 column 6
  - Sum across rows and divide by floor area
  - Transpose and add to summary dataframe
- Export csv result summary
- Extract surface area for each construction (surfaces and sub-surfaces)
  - Find surface areas of opaque surfaces
  - Find surface areas of windows
  - Save that data in a csv file
'''


def main():
    print('---START---')                        # Show that the program started
    start_stopwatch = timeit.default_timer()    # Start timing the program execution
    check_os()                                  # Check for operating system
    #   #   #   #

    #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
    # STUDY SETUP
    idf_group = 'ss2'               # This is for archiving purposes, so one can save multiple runs and troubleshoot
    study_period = 60               # LCA study period in years
    city = 'Philadelphia'           # This should eventually be tied to selecting a weather file
    state = 'PA'                    # This should eventually be tied to selecting a weather file
    city_abbrv = 'PHL'              # This should eventually be obtained from a database based on above variables
    wind_loading = 'Low'            # Low, Moderate, High
    seismic_loading = 'None'        # None, Low, Moderate, High
    frame_type = 'Conventional'     # See SOM EA Tool

    print('Program beginning.\n\nIdf group selected: {}\nStudy period: {}'.format(idf_group, study_period))

    #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
    # DATABASE AND CONSTANT VARIABLE SETUP
    # Preload all necessary databases
    df_con = pd.read_csv('./Data/constructions_data.csv')       # Load constructions spreadsheet
    df_con['Name'] = df_con['Name'].str.upper()                 # Make all construction names uppercase for matching
    df_con.set_index('Name', inplace=True)                      # Set index
    df_mat = pd.read_csv('./Data/data_materials.csv')           # Load materials spreadsheet
    df_mat.set_index('Name', inplace=True)                      # Set index
    df_win = pd.read_csv('./Data/data_windows.csv')             # Load materials spreadsheet
    df_win.set_index('Name', inplace=True)                      # Set index
    df_imp_data = pd.read_csv('./Data/impact_data.csv')         # Load impact data spreadsheet
    df_imp_data.set_index('LCI_name', inplace=True)             # Set index
    df_imp_mtd = pd.read_csv('./Data/impact_method.csv')        # Load impact data spreadsheet
    df_imp_meta = pd.read_csv('./Data/impact_method_meta.csv')  # Load impact data spreadsheet
    df_cost = pd.read_csv('./Data/data_costs.csv')              # Load cost data spreadsheet
    df_cost.set_index('Cost_name', inplace=True)                # Set index
    df_metadata = pd.read_csv('./Data/variable_metadata.csv')   # Load variable metadata
    df_metadata.set_index('Meta_name', inplace=True)            # Set index
    df_pw_cost = pd.read_csv('./Data/data_water_costs.csv')     # Load potable water spreadsheet
    df_pw_cost.set_index('City name', inplace=True)             # Set index
    df_ww_cost = pd.read_csv('./Data/data_wastewater_costs.csv')  # Load wastewater spreadsheet
    df_ww_cost.set_index('City name', inplace=True)             # Set index
    df_str_data = pd.read_csv('./Data/structural_quantities_data.csv')  # Load structural data spreadsheet
    df_str_meta = pd.read_csv('./Data/structural_quantities_meta.csv')  # Load structural metadata spreadsheet
    df_str_meta.set_index('Key', inplace=True)                  # Set index
    itemized_results = []                                       # This is where all results will be collected

    # Impact assessment methods and categories
    traci_2_1 = ['LCI_ODP', 'LCI_GWP', 'LCI_SFP', 'LCI_AP', 'LCI_EP', 'LCI_C', 'LCI_NC', 'LCI_RE', 'LCI_ETX', 'LCI_FFD']
    impact_categories = traci_2_1

    # Define energy disaggregation end use names
    enduse_names_array = ['Heating', 'Cooling', 'InteriorLighting', 'ExteriorLighting', 'InteriorEquipment',
                          'ExteriorEquipment', 'Fans', 'Pumps', 'HeatRejection', 'Humidification', 'HeatRecovery',
                          'WaterSystems', 'Refrigeration', 'Generators', 'TotalEndUses']

    # Create a data frame from itemized results
    attributes_a = ['Stories', 'Wwr', 'Wall type', 'Window type', 'Structural Material', 'Structural system']
    attributes = ['Number', 'Building', 'Category', 'Scale', 'Source', 'System', 'Construction', 'Layer', 'Element',
                  'Ingredient', 'Stage']

    # Obtain information about idf files from which these results were generated
    idf_path = './Models/{}_idfs/'.format(idf_group)
    idf_extension = '.idf'
    idf_list = [f for f in os.listdir(idf_path) if f.endswith(idf_extension)]
    idf_count = len(idf_list)

    # Attribute descriptions:
    # ata1 = Number of stories
    # ata2 = Window-to-wall ratio
    # ata3 = Wall type
    # ata4 = Window type
    # ata5 = Structural material
    # ata6 = Structural system
    # atb0 = building # Design name
    # atb1 = category # Options: Energy, Water, Materials
    # atb2 = scale # Options: Grid, On-site, District, Purchased, n/a
    # atb3 = source # Options: Mix, Solar, Wind, Hydro, n/a
    # atb4 = system # Options: HVAC, Lights, Plug Loads, Roofs, Exterior Walls, Interior Walls, Floors, Openings
    # atb5 = construction # Specific to materials only
    # atb6 = layer # Specific to materials only
    # atb7 = element # Specific to materials only
    # atb8 = ingredient # Specific to materials only
    # atb9 = stage # Options: Manufacturing, Transport, Use, Maintenance, Repair, End-of-Life, Beyond

    # Generating attribute markers for each design combination
    stories = [1, 3]                        # Number of stories options
    wwrs = [0.2, 0.8]                       # Window-to-wall ratio options
    walls = ['Wall A', 'Wall B']            # Wall type options, see constructions_data.csv
    windows = ['Window A', 'Window B']      # Window type options, see data_windows.csv
    str_materials = ['Steel']               # Main structural material options, Steel/Concrete for now
    str_systems = ['Conventional']          # Structural system type options

    design = 1
    ata_list = []
    for str_material in str_materials:
        for str_system in str_systems:
            for story in stories:           # Everything beyond this is already defined based on the E+ model outputs
                for wwr in wwrs:
                    for window in windows:
                        for wall in walls:
                            list_item = ['{}_{:02d}'.format(idf_group, design),
                                         story, wwr, wall, window, str_material, str_system]
                            ata_list.append(list_item)
                            design = design + 1
    for i in range(16):
        print(ata_list[i])

    # This is the main processing for one design
    # iterated for each design from the design output file.
    # Substitute design variable by design list and make
    # sure it is compatible throughout the code, i.e.
    # check that all design names and attributes are consistent.

    # ACCESSING E+ OUTPUT FILE DATA
    # Define path and extension of E+ output files to load
    xml_path = './Models/{}_output'.format(idf_group)
    xml_extension = '.xml'
    # List all xml results file names in the specified directory
    xml_list = [f for f in os.listdir(xml_path) if f.endswith(xml_extension)]
    xml_list = sorted(xml_list)
    xml_count = len(xml_list)
    print('\nXML file count: {}'.format(xml_count))
    print('XML file list:')
    for item in xml_list:
        print('{}\t{}'.format(item[:-9], item))

    designs = range(1, idf_count + 1)       # Number of physical design combinations

    #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
    # ENERGY, WATER, AND MATERIAL CALCULATIONS FOR EACH BUILDING DESIGN
    # Physical designs are already predefined and this only calculates their environmental and economic costs.
    # Energy and water sourcing, as well as assignment of structural quantities happens here.
    for design in designs:
        atb00 = float(design)
        atb0 = '{}_{:02d}'.format(idf_group, design)
        print('\nCollecting results for {}\n======================='.format(atb0))

        # Prepare previously defined design attributes for use within this loop
        ata1 = ata_list[design - 1][1]
        ata5 = ata_list[design - 1][5]
        ata6 = ata_list[design - 1][6]

        # Analyze results from an xml output file
        # Setup xml reader
        tree = ET.parse('{}/{}Table.xml'.format(xml_path, atb0))
        root = tree.getroot()

        #   #   #   #   #   #   #   #   #   #
        # BUILDING ENERGY USE
        print('BUILDING ENERGY USE')
        # Extract total site energy in kWh
        total_energy = root.findall('./AnnualBuildingUtilityPerformanceSummary/SiteAndSourceEnergy/TotalEnergy')[0].text
        total_energy = float(total_energy) * study_period
        print(' Energy use: {:.2f} kWh/year'.format(total_energy))

        # Identify energy source and lci name
        energy_source = 'Electricity, low voltage {RFC}| electricity production, photovoltaic, 3kWp slanted-roof ' \
                        'installation, multi-Si, panel, mounted | Alloc Def, S'
        print(' Energy source: {}'.format(energy_source))

        # Calculate impacts due to energy
        energy_impacts = []
        for impact_category in impact_categories:
            lci_if = df_imp_data[impact_category].loc[energy_source]       # Select impact factor for name and category
            impact_total = lci_if * total_energy
            energy_impacts.append(impact_total)
        print(' Energy impacts calculated.')

        # Accessing EIA grid electricity cost data via API.
        # Make a get request to get the latest data.
        # Note that this accesses PA data specifically, and
        # will have to be updated to be able to access other locations.
        response = requests.get('http://api.eia.gov/series/?api_key=c4aba82a2396b58e6fc44fd09d109160'
                                '&series_id=ELEC.PRICE.PA-ALL.A&out=xml')
        # Electric cost for last year in cents per kWh
        electric_cost = ET.fromstring(response.content).findall('./series/row/data/row/value')[0].text
        electric_cost = float(electric_cost)
        total_energy_cost = electric_cost/100.00 * total_energy      # Calculation of total annual energy cost
        print(' Energy cost calculated.'.format(total_energy_cost, study_period))
        print(' Energy cost: ${:.2f}/kWh'.format(electric_cost/100))
        print(' Energy cost: ${:.2f}/{} years'.format(total_energy_cost, study_period))

        # Energy attributes
        atb1 = 'Energy'
        atb2 = 'Grid'
        atb3 = 'Solar'
        atb4 = 'HVAC&Lights&Loads'
        atb5 = '-'
        atb6 = '-'
        atb7 = '-'
        atb8 = '-'
        atb9 = 'Use'
        print(' Energy markers assigned.')

        attribute_values = [atb00, atb0, atb1, atb2, atb3, atb4, atb5, atb6, atb7, atb8, atb9]
        itemized_results.append(attribute_values + energy_impacts + [total_energy_cost])
        print(' Energy results filed.')

        #   #   #   #   #   #   #   #   #   #
        # EXTRACTING SURFACE & MATERIAL DATA
        print('SURFACES')
        # Setup empty list for storing all surface data
        surfaces = []

        # Extract building floor area
        floor_area = root.findall('./AnnualBuildingUtilityPerformanceSummary/BuildingArea/TotalBuildingArea')[0].text
        floor_area = float(floor_area)            # Convert the text from 'str' to 'float'
        print(' Gross floor area: {} m2'.format(floor_area))

        # Extract all opaque surface data from the xml
        opaque_areas = root.findall('./EnvelopeSummary/OpaqueExterior')
        for surface in opaque_areas:
            construction = surface.find('Construction').text
            area = float(surface.find('NetArea').text)
            surfaces.append([construction, area])

        # Extract all window surface data from the xml
        window_areas = root.findall('./EnvelopeSummary/ExteriorFenestration')
        # Drop the last three elements in the window area list (total and average rows in the csv)
        window_areas = window_areas[:-3]
        for window in window_areas:
            construction = window.find('Construction').text
            area = float(window.find('AreaOfMultipliedOpenings').text)
            surfaces.append([construction, area])

        # Create a data frame containing all of the extracted surface data
        # Create a new data frame consisting of data from the surface list
        df_sd = pd.DataFrame(surfaces)
        # Setup the data frame's column headers
        df_sd.columns = ['Construction', 'Area']
        # Make all construction names upper case - this is redundant since E+ already outputs
        # them in uppercase, it is done here just in case something changes in future E+ releases
        df_sd['Construction'] = df_sd['Construction'].str.upper()
        # Print and save the envelope construction summary
        df_sd.to_csv('./Results/ss1_01_EnvelopeSummaryDetailed.csv')
        print(' Envelope construction details exported.')

        # Sum areas for each construction and save as a new data frame
        df_ss = pd.DataFrame((df_sd.groupby('Construction').sum().reset_index()))
        df_ss.set_index('Construction', inplace=True)         # Make construction names the new index
        df_ss.to_csv('./Results/ss1_01_EnvelopeSummary.csv')
        constructions = df_ss.index.tolist()                  # List of constructions in the model
        print(' Envelope construction summary exported.')
        print(' Unique envelope constructions: {}'.format(len(constructions)))

        #   #   #   #   #   #   #   #   #   #
        # WATER AND WASTEWATER TREATMENT
        print('WATER & WASTEWATER')
        #   #   #   #   #   #   #
        # General location and building type specific data definitions
        precipitation_factor = 1.089    # Annual precipitation and snowfall for a location in [m]
        water_demand_factor = 15.0      # Annual potable and non-potable water demand for bldg. type in [gal/sf]
        sewage_prod_factor = 1.0    # Water demand to wastewater production ratio, dimensionless [-]
        # Wastewater production factor is a placeholder for potential future development and right now represents
        # one-to-one water demand to wastewater production ratio, i.e. water demand = wastewater production

        precipitation = precipitation_factor * df_ss['Area'].loc['ROOF A']  # Annual precipitation in [m3]
        water_demand = water_demand_factor * 0.0407458 * floor_area         # Annual water use converted to [m3]
        sewage_produced = sewage_prod_factor * water_demand         # Annual wastewater produced in [m3]

        print(' Annual water demand: {:.2f} m3/year'.format(water_demand))
        print(' Annual sewage discharge: {:.2f} m3/year'.format(sewage_produced))
        print(' Annual stormwater/snow runoff: {:.2f} m3/year'.format(precipitation))

        #   #   #   #   #   #   #
        # Water demand definitions and calculations
        print('Water demand')
        water_source = 'Treatment plant, potable water'
        print(' Water source/treatment: {}'.format(water_source))

        # Environmental impacts
        water_impacts = []
        for impact_category in impact_categories:
            lci_if = df_imp_data[impact_category].loc[water_source]    # Select impact factor for source and category
            impact_total = lci_if * water_demand * study_period  # Compute lifecycle impact
            water_impacts.append(impact_total)                   # Append results for a given impact category
        print(' Water impacts calculated')

        # Economic costs
        water_cost_unit = float(df_pw_cost['2016'].loc[city])    # Find unit cost for year and city in [$/kGal]
        water_cost = water_cost_unit * water_demand / 3.785 * study_period  # Lifecycle cost of water in [$/m3]
        print(' Water costs calculated.')
        print(' Water cost: ${:.2f}/kGal'.format(water_cost_unit))
        print(' Water cost: ${:.2f}/{} years'.format(water_cost, study_period))

        # Output attributes
        atb1 = 'Water'
        atb2 = 'City'
        atb3 = 'River'
        atb4 = 'Potable Water'
        atb5 = '-'
        atb6 = '-'
        atb7 = '-'
        atb8 = '-'
        atb9 = 'Use'
        attribute_values = [atb00, atb0, atb1, atb2, atb3, atb4, atb5, atb6, atb7, atb8, atb9]
        print(' Water markers assigned.')
        itemized_results.append(attribute_values + water_impacts + [water_cost])
        print(' Water results filed.')

        #   #   #   #   #   #   #
        # Sewage generation definitions and calculations
        print('Wastewater')
        #   Treated on-site or centrally?           Options: Central, On-site
        #   If -> Central
        #       What sewer type?                    Options: Combined, Separate
        sewage_treatment = 'Treatment plant, wastewater'
        print(' Wastewater treatment: {}'.format(sewage_treatment))

        # Environmental impacts
        sewage_impacts = []
        for impact_category in impact_categories:
            lci_if = df_imp_data[impact_category].loc[sewage_treatment]   # Select impact factor for type and category
            impact_total = lci_if * sewage_produced * study_period  # Compute lifecycle impact
            sewage_impacts.append(impact_total)                     # Append results for a given impact category
        print(' Wastewater impacts calculated.')

        # Economic costs
        sewage_cost_unit = float(df_ww_cost['2016'].loc[city])      # Find unit cost for year and city in [$/kGal]
        sewage_cost = sewage_cost_unit * sewage_produced / 3.785 * study_period  # Lifecycle cost of sewage in [$/m3]
        print(' Wastewater costs calculated.')
        print(' Wastewater cost: ${:.2f}/kGal'.format(sewage_cost_unit))
        print(' Wastewater cost: ${:.2f}/{} years'.format(sewage_cost, study_period))

        # Output attributes
        atb1 = 'Water'
        atb2 = 'City'
        atb3 = '-'
        atb4 = 'Wastewater'
        atb5 = '-'
        atb6 = '-'
        atb7 = '-'
        atb8 = '-'
        atb9 = 'Use'
        attribute_values = [atb00, atb0, atb1, atb2, atb3, atb4, atb5, atb6, atb7, atb8, atb9]
        print(' Wastewater markers assigned.')
        itemized_results.append(attribute_values + sewage_impacts + [sewage_cost])
        print(' Wastewater results filed.')

        #   #   #   #   #   #   #
        # Stormwater/snow runoff definitions and calculations
        print('Stormwater')
        # Is roof connected to sewer or not?            Options: Treated, Untreated
        #   If -> Treated
        #       Treated on-site or centrally?           Options: Central, On-site
        #       If -> Central
        #           What sewer type?                    Options: Combined, Separate
        storm_treatment = 'Treatment plant, wastewater'
        print(' Stormwater treatment: {}'.format(storm_treatment))

        # Environmental impacts
        # Options:
        #   Untreated
        #   Treated, On-site
        #   Treated, Central, Combined (equivalent to partial sewage treatment, partial overflow)
        #   Treated, Central, Separate (equivalent to sewage treatment impacts)
        storm_impacts = []
        for impact_category in impact_categories:
            lci_if = df_imp_data[impact_category].loc[storm_treatment]  # Select impact factor for type and category
            impact_total = lci_if * precipitation * study_period  # Compute lifecycle impact
            storm_impacts.append(impact_total)                    # Append results for a given impact category
        print(' Stormwater impacts calculated.')

        # Economic costs
        storm_cost_unit = float(df_ww_cost['2016'].loc[city])      # Find unit cost for year and city in [$/kGal]
        storm_cost = storm_cost_unit * precipitation / 3.785 * study_period  # Lifecycle cost of storm in [$/m3]
        print(' Stormwater costs calculated')
        print(' Stormwater cost: ${:.2f}/kGal'.format(storm_cost_unit))
        print(' Stormwater cost: ${:.2f}/{} years'.format(storm_cost, study_period))

        # Stormwater attributes
        atb1 = 'Water'
        atb2 = 'City'
        atb3 = '-'
        atb4 = 'Stormwater Runoff'
        atb5 = '-'
        atb6 = '-'
        atb7 = '-'
        atb8 = '-'
        atb9 = 'Use'
        attribute_values = [atb00, atb0, atb1, atb2, atb3, atb4, atb5, atb6, atb7, atb8, atb9]
        print(' Stormwater markers assigned.')
        itemized_results.append(attribute_values + storm_impacts + [storm_cost])
        print(' Stormwater results filed.')

        #   #   #   #   #   #   #   #   #   #   #   #
        # MATERIALS
        # Calculate environmental impact for the whole building

        print('STRUCTURE')
        # Obtain floor area, stories, main material, frame type, wind load, seismic load
        str_gfa = floor_area                # Gross floor area
        str_st_sup = ata1                   # Number of stories superstructure
        str_mat = ata5                      # Main structural material
        str_win_ld = wind_loading           # Wind loading
        str_sei_ld = seismic_loading        # Seismic loading
        str_sei_sys = frame_type            # Seismic force resisting system
        str_fa_sup = str_gfa/str_st_sup     # Area per floor superstructure, note that database has limited options

        # Filter out dataframe based on input specifications
        str_data_filtered = df_str_data[(df_str_data.ST_SUP == str_st_sup) &
                                        (df_str_data.FA_SUP == 1000) &          # Ref. str_fa_sup, database limitation
                                        (df_str_data.MAT == str_mat) &
                                        (df_str_data.WIN_LD == str_win_ld) &
                                        (df_str_data.SEI_LD == str_sei_ld) &
                                        (df_str_data.SEI_SYS == str_sei_sys)]
        str_data_filtered = str_data_filtered.reset_index()

        # Obtain variable names of structural materials
        str_mat_names = df_str_data.columns.tolist()[11:-1]  # Variable names for structural materials

        # Loop: for each structural material variable
        # Get total quantity for the whole building
        # Get impact & cost reference names
        # Loop: for each impact category, calculate total impacts
        # Calculate total cost
        # Define output attributes

        # for all layers in the selected construction, execute the following loop
        for material in str_mat_names:
            str_unit = df_str_meta['Units'].loc[material]       # Check unit used in structural data sheet
            lci_name = df_str_meta['Impact_ref'].loc[material]  # Get impact reference name for material
            lci_unit = df_imp_data['LCI_unit'].loc[lci_name]    # Check unit for which impact factors are provided
            check_units(str_unit, lci_unit)
            str_quant = str_data_filtered[material].loc[0]

            layer_impacts = []
            for impact_category in impact_categories:
                lci_if = df_imp_data[impact_category].loc[lci_name]  # Get impact factor for name and category
                impact_total = calc_dv2(lci_unit, lci_if) * str_quant * str_gfa
                layer_impacts.append(impact_total)
                print(' Structural {} impact calculated.'.format(impact_category))

            cost_name = df_str_meta['Cost_ref'].loc[material]   # Get cost reference name for material
            cost_unit = df_cost['Cost_unit'].loc[cost_name]     # Get unit from cost database
            cost_factor = df_cost['Cost_material'].loc[cost_name]
            layer_cost = calc_dv2(cost_unit, cost_factor) * str_quant * str_gfa
            print(' Structural cost calculated.')

            atb1 = 'Materials'
            atb2 = '-'
            atb3 = '-'
            atb4 = 'Structure'
            atb5 = 'Frame'
            atb6 = str_mat
            atb7 = df_str_meta['Material'].loc[material]
            atb8 = '-'
            atb9 = 'Manufacturing'
            attribute_values = [atb00, atb0, atb1, atb2, atb3, atb4, atb5, atb6, atb7, atb8, atb9]
            print(' Structural markers assigned.')
            itemized_results.append(attribute_values + layer_impacts + [layer_cost])
            print(' Structural results filed.')

        #   #   #   #   #   #
        # ENVELOPE MATERIALS
        print('ENVELOPE')
        print(' Constructions present in this model:')
        for construction in constructions:
            print(construction)

        for construction in constructions:
            if 'WINDOW' not in construction:
                c_area = df_ss['Area'].loc[construction]            # Create area variable for use within this loop
                layers = df_con.loc[construction].dropna().tolist()  # Select constr'n, drop empty layers, save list

                # for all layers in the selected construction, execute the following loop
                for layer in layers:
                    lci_name = df_mat['LCI_name'].loc[layer]        # Find layer material in impact database
                    lci_unit = df_imp_data['LCI_unit'].loc[lci_name]      # Check unit for which impact factors are provided

                    layer_impacts = []
                    for impact_category in impact_categories:
                        lci_if = df_imp_data[impact_category].loc[lci_name]   # Select impact factor for name and category
                        impact_total = calc_dv(construction, layer, lci_unit, lci_if, df_mat, df_ss)
                        layer_impacts.append(impact_total)

                    cost_name = df_mat['Cost_name'].loc[layer]
                    cost_unit = df_cost['Cost_unit'].loc[cost_name]
                    cost_factor = df_cost['Cost_material'].loc[cost_name]
                    layer_cost = calc_dv(construction, layer, cost_unit, cost_factor, df_mat, df_ss)

                    atb1 = 'Materials'
                    atb2 = '-'
                    atb3 = '-'
                    atb4 = assign_system(construction)
                    atb5 = construction
                    atb6 = layer
                    atb7 = '-'
                    atb8 = '-'
                    atb9 = 'Manufacturing'
                    attribute_values = [atb00, atb0, atb1, atb2, atb3, atb4, atb5, atb6, atb7, atb8, atb9]
                    itemized_results.append(attribute_values + layer_impacts + [layer_cost])
            else:
                c_area = df_ss['Area'].loc[construction]              # Create area variable for use within this loop
                layers = df_con.loc[construction].dropna().tolist()   # Select const'n, drop empty layers, save list

                # for all layers in the selected construction, execute the following loop
                for layer in layers:
                    lci_name = df_win['LCI_name'].loc[layer]    # Find window in impact database
                    lci_unit = df_imp_data['LCI_unit'].loc[lci_name]  # Check unit for which impact factors are provided

                    layer_impacts = []
                    for impact_category in impact_categories:
                        lci_if = df_imp_data[impact_category].loc[lci_name]   # Select impact factor for name and category
                        impact_total = calc_dv(construction, layer, lci_unit, lci_if, df_win, df_ss)
                        layer_impacts.append(impact_total)

                    cost_name = df_win['Cost_name'].loc[layer]
                    cost_unit = df_cost['Cost_unit'].loc[cost_name]
                    cost_factor = df_cost['Cost_material'].loc[cost_name]
                    layer_cost = calc_dv(construction, layer, cost_unit, cost_factor, df_win, df_ss)

                    atb1 = 'Materials'
                    atb2 = '-'
                    atb3 = '-'
                    atb4 = assign_system(construction)
                    atb5 = construction
                    atb6 = layer
                    atb7 = 'Glazing'
                    atb8 = 'Glass'
                    atb9 = 'Manufacturing'
                    attribute_values = [atb00, atb0, atb1, atb2, atb3, atb4, atb5, atb6, atb7, atb8, atb9]
                    itemized_results.append(attribute_values + layer_impacts + [layer_cost])
        print('{} completed'.format(atb0))

    # Back to main body, out of the big loop
    print(itemized_results)
    # Summarize all surface impact results
    df_master = pd.DataFrame(itemized_results)              # Create a data frame from itemized results
    df_master.columns = attributes + impact_categories + ['Cost']      # Define headers
    print(df_master)                                        # Print itemized results
    df_master.to_csv('./Results/{}_summary__master.csv'.format(idf_group))  # Export itemized results to csv

    # Print summary results
    print(df_master.groupby(['Building', 'Category']).sum().reset_index())
    # Sum areas for each construction and save as a new data frame
    df_design_category = pd.DataFrame((df_master.groupby(['Building', 'Category']).sum().reset_index()))
    df_design_category.to_csv('./Results/{}_summary_design-category.csv'.format(idf_group))

    #   #   #   #
    stop_stopwatch = timeit.default_timer()             # Stop timing the program execution
    show_stopwatch(start_stopwatch, stop_stopwatch)     # Show run time
    print('----END----')                                # Show that the program ended


'''
FUNCTIONS
'''


def show_stopwatch(start, stop):
    print('\nTotal run time:')
    print(humanfriendly.format_timespan(stop - start))


def check_os():
    # Check for operating system
    if platform == "linux" or platform == "linux2":
        print('Linux operating system identified... sorry, it is not supported.')
    elif platform == "darwin":
        print('Mac operating system identified.\n')
    elif platform == "win32":
        print('Windows operating system identified.\n')


def extract_floor_area(path, file_name):
    tree = ET.parse('{}/{}'.format(path, file_name))        # Open xml file with path and file name
    root = tree.getroot()                                   # Setup xml file root and find specific item in xml
    floor_area = root.findall('./AnnualBuildingUtilityPerformanceSummary/BuildingArea/TotalBuildingArea')[0].text
    floor_area = float(floor_area)                          # Convert the text from 'str' to 'float'
    return floor_area


def extract_surface_areas(path, file_name):
    tree = ET.parse('{}/{}'.format(path, file_name))        # Open xml file with path and file name
    root = tree.getroot()                                   # Setup xml file root and find specific item in xml
    surface_area = root.findall('./EnvelopeSummary/OpaqueExterior')  # Find item
    return surface_area


def extract_enduse_names(path, file_name):
    tree = ET.parse('{}/{}'.format(path, file_name))        # Open xml file with path and file name
    root = tree.getroot()                                   # Setup xml file root and find specific item in xml
    enduse_names = root.findall('./AnnualBuildingUtilityPerformanceSummary/EndUses/name')   # Find item
    enduse_names_array = []                                 # Prep empty array
    for enduse in enduse_names:
        enduse_names_array.append(enduse.text)              # Loop through all items satisfying the above cond's
    return enduse_names_array


def extract_enduse_electricity(path, file_name):
    tree = ET.parse('{}/{}'.format(path, file_name))        # open xml file with path and file name
    root = tree.getroot()                                   # Setup xml file root and find specific item in xml
    enduse_electricity = root.findall('./AnnualBuildingUtilityPerformanceSummary/EndUses/Electricity')  # Find item
    enduse_electricity_array = []                           # Prep empty array
    for enduse in enduse_electricity:
        enduse_electricity_array.append(float(enduse.text))  # Loop through all items satisfying the above cond's
    return enduse_electricity_array


def calc_dv(construction, material, unit, factor, df_data_materials, df_constructions_summary):
    thickness = df_data_materials['Thickness'].loc[material]    # Extract thickness datapoint
    density = df_data_materials['Density'].loc[material]        # Extract density datapoint
    area = df_constructions_summary['Area'].loc[construction]   # Extract Area datapoint
    # Check units and convert to the desired units given above data about thickness, density, and area
    if unit in ('kg', 'lbs', 'ton'):
        if unit in 'lbs':
            factor = factor * 2.2046
        if unit in 'ton':
            factor = factor * 0.0011
        total = factor * thickness * density * area
    elif unit in ('m3', 'ft3', 'yd3'):
        if unit in 'ft3':
            factor = factor * 35.3107
        elif unit in 'yd3':
            factor = factor * 1.3079
        total = factor * thickness * area
    elif unit in ('m2', 'ft2', 'yd2'):
        if unit in 'ft2':
            factor = factor * 10.7639
        elif unit in 'yd2':
            factor = factor * 1.1960
        total = factor * area
    else:
        total = 0
        print('Unknown units! Total for {}/{} set to 0!'.format(construction, material))
    return total


def check_units(model_units, database_units):
    if model_units in database_units:
        print(' Units checked & matching.')
    else:
        print(' Units checked & DO NOT MATCH!')
        print('  {} & {}'.format(model_units, database_units))


def calc_dv2(unit, factor):
    # Check units and convert to the desired units
    if unit in ('kg', 'lbs', 'ton'):
        if unit in 'lbs':
            factor = factor * 2.2046
        if unit in 'ton':
            factor = factor * 0.0011
        total = factor
    elif unit in ('m3', 'ft3', 'yd3'):
        if unit in 'ft3':
            factor = factor * 35.3107
        elif unit in 'yd3':
            factor = factor * 1.3079
        total = factor
    elif unit in ('m2', 'ft2', 'yd2'):
        if unit in 'ft2':
            factor = factor * 10.7639
        elif unit in 'yd2':
            factor = factor * 1.1960
        total = factor
    else:
        total = 0
        print('UNKNOWN UNITS!')
    return total


def assign_system(item):
    if 'ROOF' in item:
        return 'Roof'
    elif any(x in item for x in ['SLAB', 'FLOOR']):
        return 'Floor'
    elif 'WALL' in item:
        return 'Wall'
    elif any(x in item for x in ['WINDOW', 'DOOR']):
        return 'Opening'
    else:
        return 'n/a'


def intermission():
    i = 0
    while i < 1:
        selection = input('\nWould you like to continue? (Options: Yes | No)\n>> ')
        if selection.lower() in 'yes':
            print('\nContinuing...\n')
            i = 1
        elif selection.lower() in 'no':
            print('\nProgram terminated.')
            i = 2
        else:
            print('\nInvalid entry. Try again.')
    return i


if __name__ == "__main__": main()