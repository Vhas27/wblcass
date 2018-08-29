#!/usr/Anaconda3/bin/python3
# ep_3results.py by Vaclav Hasik

import time
import os
import timeit
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
    # Show that the program started
    print('\n---START---')
    # Start timing the program execution
    start = timeit.default_timer()

    # ACCESSING E+ OUTPUT FILE DATA
    # Define path and extension of E+ output files to load
    xml_path = './Models/ss1_output'
    xml_extension = '.xml'
    atb0 = 'ss1_01'
    study_period = 30   # LCA study period in years

    # List all xml results file names in the specified directory
    xml_list = [f for f in os.listdir(xml_path) if f.endswith(xml_extension)]
    xml_list = sorted(xml_list)
    xml_count = len(xml_list)
    print('List of xml files: {}'.format(xml_list))
    print('Number of xml files: {}'.format(xml_count))

    # Analyze results from an xml output file
    # Setup xml reader
    tree = ET.parse('{}/{}'.format(xml_path, xml_list[0]))
    root = tree.getroot()

    # Preload all necessary databases
    df_con = pd.read_csv('./Data/data_constructions.csv')   # Load constructions spreadsheet
    df_con['Name'] = df_con['Name'].str.upper()             # Make all construction names uppercase for matching
    df_con.set_index('Name', inplace=True)                  # Set index
    df_mat = pd.read_csv('./Data/data_materials.csv')       # Load materials spreadsheet
    df_mat.set_index('Name', inplace=True)                  # Set index
    df_win = pd.read_csv('./Data/data_windows.csv')         # Load materials spreadsheet
    df_win.set_index('Name', inplace=True)                  # Set index
    df_if = pd.read_csv('./Data/data_impacts.csv')          # Load impact data spreadsheet
    df_if.set_index('LCI_name', inplace=True)               # Set index
    df_cost = pd.read_csv('./Data/data_costs.csv')          # Load cost data spreadsheet
    df_cost.set_index('Cost_name', inplace=True)            # Set index
    df_metadata = pd.read_csv('./Data/variable_metadata.csv')  # Load variable metadata
    df_metadata.set_index('Meta_name', inplace=True)        # Set index
    itemized_results = []                                   # This is where all results will be collected

    # Impact assessment methods and categories
    traci_2_1 = ['LCI_ODP', 'LCI_GWP', 'LCI_SFP', 'LCI_AP', 'LCI_EP', 'LCI_C', 'LCI_NC', 'LCI_RE', 'LCI_ETX', 'LCI_FFD']
    impact_categories = traci_2_1

    # Define energy disaggregation end use names
    enduse_names_array = ['Heating', 'Cooling', 'InteriorLighting', 'ExteriorLighting', 'InteriorEquipment',
                          'ExteriorEquipment', 'Fans', 'Pumps', 'HeatRejection', 'Humidification', 'HeatRecovery',
                          'WaterSystems', 'Refrigeration', 'Generators', 'TotalEndUses']

    # BUILDING ENERGY USE
    # Extract total site energy in kWh
    total_energy = root.findall('./AnnualBuildingUtilityPerformanceSummary/SiteAndSourceEnergy/TotalEnergy')[0].text
    total_energy = float(total_energy) * study_period
    print('Total annual energy use: {:.2f} kWh'.format(total_energy))

    # Identify energy source and lci name
    energy_source = 'Electricity, low voltage {RFC}| electricity production, photovoltaic, 3kWp slanted-roof ' \
                    'installation, multi-Si, panel, mounted | Alloc Def, S'
    print('Energy source:\n{}'.format(energy_source))

    # Calculate impacts due to energy
    energy_impacts = []
    for impact_category in impact_categories:
        lci_if = df_if[impact_category].loc[energy_source]          # Select impact factor for name and category
        impact_total = lci_if * total_energy
        energy_impacts.append(impact_total)

    # Accessing EIA grid electricity cost data via API
    # Make a get request to get the latest data
    response = requests.get('http://api.eia.gov/series/?api_key=c4aba82a2396b58e6fc44fd09d109160'
                            '&series_id=ELEC.PRICE.PA-ALL.A&out=xml')
    # Electric cost for last year in cents per kWh
    electric_cost = ET.fromstring(response.content).findall('./series/row/data/row/value')[0].text
    total_energy_cost = float(electric_cost)/100.00 * total_energy
    print('Total annual energy cost: ${:.2f}'.format(total_energy_cost))

    # Create a data frame from itemized results
    attributes = ['Building', 'Category', 'Scale', 'Source', 'System', 'Construction', 'Layer', 'Element',
                  'Ingredient', 'Stage']
    # atb0 = building
    # atb1 = category # Options: Energy, Water, Materials
    # atb2 = scale # Options: Grid, On-site, District, Purchased, n/a
    # atb3 = source # Options: Mix, Solar, Wind, Hydro, n/a
    # atb4 = system # Options: HVAC, Lights, Plug Loads, Roofs, Exterior Walls, Interior Walls, Floors, Openings
    # atb5 = construction # Specific to materials only
    # atb6 = layer # Specific to materials only
    # atb7 = element # Specific to materials only
    # atb8 = ingredient # Specific to materials only
    # atb9 = stage # Options: Manufacturing, Transport, Use, Maintenance, Repair, End-of-Life, Beyond
    atb1 = 'Energy'
    atb2 = 'Grid'
    atb3 = 'Solar'
    atb4 = 'HVAC & Lights & Plug Loads'
    atb5 = 'n/a'
    atb6 = 'n/a'
    atb7 = 'n/a'
    atb8 = 'n/a'
    atb9 = 'Use'

    attribute_values = [atb0, atb1, atb2, atb3, atb4, atb5, atb6, atb7, atb8, atb9]
    itemized_results.append(attribute_values + energy_impacts + [total_energy_cost])

    # Extract building floor area
    floor_area = root.findall('./AnnualBuildingUtilityPerformanceSummary/BuildingArea/TotalBuildingArea')[0].text
    # Convert the text from 'str' to 'float'
    floor_area = float(floor_area)
    print('Gross floor area: {} m2'.format(floor_area))

    # EXTRACTING SURFACE & MATERIAL DATA
    # Setup empty list for storing all surface data
    surfaces = []

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
    print('Envelope construction details exported.')

    # Sum areas for each construction and save as a new data frame
    df_ss = pd.DataFrame((df_sd.groupby('Construction').sum().reset_index()))
    df_ss.set_index('Construction', inplace=True)         # Make construction names the new index
    df_ss.to_csv('./Results/ss1_01_EnvelopeSummary.csv')
    constructions = df_ss.index.tolist()                  # List of constructions in the model
    print('Envelope construction summary exported.')
    print('Unique envelope constructions: {}'.format(len(constructions)))

    # WATER AND SEWAGE TREATMENT
    # Average annual precipitation in meters/year including rainfall and snowfall
    precipitation = 1.089 * df_ss['Area'].loc['ROOF A']         # Average annual precipitation in m
    water_demand = 15 * 0.0407458 * floor_area                  # Annual water use in 15 gal/sf converted to m3
    print('Total annual water demand: {:.2f} m3'.format(water_demand))
    print('Total annual wastewater discharge: {:.2f} m3'.format(water_demand))
    print('Total annual precipitation runoff: {:.2f} m3'.format(precipitation))

    water_source = 'Treatment plant, potable water'
    water_impacts = []
    for impact_category in impact_categories:
        lci_if = df_if[impact_category].loc[water_source]          # Select impact factor for name and category
        impact_total = lci_if * water_demand * study_period
        water_impacts.append(impact_total)

    atb1 = 'Water'
    atb2 = 'City'
    atb3 = 'River'
    atb4 = 'Potable Water'
    atb5 = 'n/a'
    atb6 = 'n/a'
    atb7 = 'n/a'
    atb8 = 'n/a'
    atb9 = 'Use'
    attribute_values = [atb0, atb1, atb2, atb3, atb4, atb5, atb6, atb7, atb8, atb9]
    itemized_results.append(attribute_values + water_impacts + [0.0])

    sewage_treatment = 'Treatment plant, wastewater'
    sewage_impacts = []
    for impact_category in impact_categories:
        lci_if = df_if[impact_category].loc[sewage_treatment]          # Select impact factor for name and category
        impact_total = lci_if * water_demand * study_period
        sewage_impacts.append(impact_total)

    atb1 = 'Water'
    atb2 = 'City'
    atb3 = 'n/a'
    atb4 = 'Wastewater'
    atb5 = 'n/a'
    atb6 = 'n/a'
    atb7 = 'n/a'
    atb8 = 'n/a'
    atb9 = 'Use'
    attribute_values = [atb0, atb1, atb2, atb3, atb4, atb5, atb6, atb7, atb8, atb9]
    itemized_results.append(attribute_values + sewage_impacts + [0.0])

    storm_treatment = 'Treatment plant, wastewater'
    storm_impacts = []
    for impact_category in impact_categories:
        lci_if = df_if[impact_category].loc[storm_treatment]  # Select impact factor for name and category
        impact_total = lci_if * precipitation * study_period
        storm_impacts.append(impact_total)

    atb1 = 'Water'
    atb2 = 'City'
    atb3 = 'n/a'
    atb4 = 'Stormwater Runoff'
    atb5 = 'n/a'
    atb6 = 'n/a'
    atb7 = 'n/a'
    atb8 = 'n/a'
    atb9 = 'Use'
    attribute_values = [atb0, atb1, atb2, atb3, atb4, atb5, atb6, atb7, atb8, atb9]
    itemized_results.append(attribute_values + storm_impacts + [0.0])

    # MATERIALS
    # Calculate environmental impact for the whole building

    print('Constructions present in this model:')
    for construction in constructions:
        print(construction)

    for construction in constructions:
        if 'WINDOW' not in construction:
            c_area = df_ss['Area'].loc[construction]            # Create area variable for use within this loop
            layers = df_con.loc[construction].dropna().tolist()  # Select construction, drop empty layers, save to list

            # for all layers in the selected construction, execute the following loop
            for layer in layers:
                lci_name = df_mat['LCI_name'].loc[layer]        # Find layer material in impact database
                lci_unit = df_if['LCI_unit'].loc[lci_name]      # Check unit for which impact factors are provided

                layer_impacts = []
                for impact_category in impact_categories:
                    lci_if = df_if[impact_category].loc[lci_name]   # Select impact factor for name and category
                    impact_total = calc_dv(construction, layer, lci_unit, lci_if, df_mat, df_ss)
                    layer_impacts.append(impact_total)

                cost_name = df_mat['Cost_name'].loc[layer]
                cost_unit = df_cost['Cost_unit'].loc[cost_name]
                cost_factor = df_cost['Cost_material'].loc[cost_name]
                layer_cost = calc_dv(construction, layer, cost_unit, cost_factor, df_mat, df_ss)

                atb1 = 'Materials'
                atb2 = 'n/a'
                atb3 = 'n/a'
                atb4 = assign_system(construction)
                atb5 = construction
                atb6 = layer
                atb7 = 'n/a'
                atb8 = 'n/a'
                atb9 = 'Manufacturing'
                attribute_values = [atb0, atb1, atb2, atb3, atb4, atb5, atb6, atb7, atb8, atb9]
                itemized_results.append(attribute_values + layer_impacts + [layer_cost])
        else:
            c_area = df_ss['Area'].loc[construction]              # Create area variable for use within this loop
            layers = df_con.loc[construction].dropna().tolist()   # Select construction, drop empty layers, save to list

            # for all layers in the selected construction, execute the following loop
            for layer in layers:
                lci_name = df_win['LCI_name'].loc[layer]    # Find window in impact database
                lci_unit = df_if['LCI_unit'].loc[lci_name]  # Check unit for which impact factors are provided

                layer_impacts = []
                for impact_category in impact_categories:
                    lci_if = df_if[impact_category].loc[lci_name]   # Select impact factor for name and category
                    impact_total = calc_dv(construction, layer, lci_unit, lci_if, df_win, df_ss)
                    layer_impacts.append(impact_total)

                cost_name = df_win['Cost_name'].loc[layer]
                cost_unit = df_cost['Cost_unit'].loc[cost_name]
                cost_factor = df_cost['Cost_material'].loc[cost_name]
                layer_cost = calc_dv(construction, layer, cost_unit, cost_factor, df_win, df_ss)

                atb1 = 'Materials'
                atb2 = 'n/a'
                atb3 = 'n/a'
                atb4 = assign_system(construction)
                atb5 = construction
                atb6 = layer
                atb7 = 'Glazing'
                atb8 = 'Glass'
                atb9 = 'Manufacturing'
                attribute_values = [atb0, atb1, atb2, atb3, atb4, atb5, atb6, atb7, atb8, atb9]
                itemized_results.append(attribute_values + layer_impacts + [layer_cost])

    print(itemized_results)
    # Summarize all surface impact results
    df_master = pd.DataFrame(itemized_results)              # Create a data frame from itemized results
    df_master.columns = attributes + impact_categories + ['Cost']      # Define headers
    print(df_master)                                        # Print itemized results
    df_master.to_csv('./Results/ss1_01_EnvelopeMaster.csv')  # Export itemized results to csv

    print(df_master.groupby('Category').sum().reset_index())

    # Print total program runtime
    print('\n Total run time:')
    stop = timeit.default_timer()
    print('{0:.4g} seconds'.format(stop - start))
    print('\n---END---')


'''
FUNCTIONS
'''


def extract_floor_area(path, file_name):
    # Open xml file with path and file name
    tree = ET.parse('{}/{}'.format(path, file_name))
    root = tree.getroot()

    # Find the specific results we are looking for
    floor_area = root.findall('./AnnualBuildingUtilityPerformanceSummary/BuildingArea/TotalBuildingArea')[0].text
    # Convert the text from 'str' to 'float'
    floor_area = float(floor_area)

    return floor_area


def extract_surface_areas(path, file_name):
    # Open xml file with path and file name
    tree = ET.parse('{}/{}'.format(path, file_name))
    root = tree.getroot()

    # Find the specific results we are looking for
    surface_area = root.findall('./EnvelopeSummary/OpaqueExterior')

    return surface_area


def extract_enduse_names(path, file_name):
    # Open xml file with path and file name
    tree = ET.parse('{}/{}'.format(path, file_name))
    root = tree.getroot()

    # find the specific results we are looking for
    enduse_names = root.findall('./AnnualBuildingUtilityPerformanceSummary/EndUses/name')
    enduse_names_array = []

    for enduse in enduse_names:
        enduse_names_array.append(enduse.text)

    return enduse_names_array


def extract_enduse_electricity(path, file_name):
    # open xml file with path and file name
    tree = ET.parse('{}/{}'.format(path, file_name))
    root = tree.getroot()

    # show instance information
    # building_name = root[0].text
    # location_file = root[2].text
    # location_city = location_file.split()
    # print('\n {} in {}'.format(building_name,location_city[0]))

    # find the specific results we are looking for
    enduse_electricity = root.findall('./AnnualBuildingUtilityPerformanceSummary/EndUses/Electricity')
    enduse_electricity_array = []

    for enduse in enduse_electricity:
        enduse_electricity_array.append(float(enduse.text))

    return enduse_electricity_array


def calc_dv(construction, material, unit, factor, df_data_materials, df_constructions_summary):
    thickness = df_data_materials['Thickness'].loc[material]
    density = df_data_materials['Density'].loc[material]
    area = df_constructions_summary['Area'].loc[construction]

    if unit in ('kg', 'lbs'):
        if unit in 'lbs':
            factor = factor * 2.2046
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


if __name__ == "__main__": main()