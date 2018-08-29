#!/usr/Anaconda3/bin/python3
# ep_1setup.py by Vaclav Hasik

from sys import platform
import os
import timeit
from eppy.modeleditor import IDF


'''
MAIN BODY
Pseudo-code:
- Modify and generate new idf files
- Select a specific output style for idf results
'''


def main():
    # Show that the program started
    print('\n---START---')
    # Start timing the program execution
    start = timeit.default_timer()

    # Check for operating system and setup appropriate energyplus path
    if platform == "linux" or platform == "linux2":
        print('Linux operating system identified... sorry, it is not supported.')
    elif platform == "darwin":
        print('Mac operating system identified.\nIDD path setup completed.\n')
        ep_path = '/Applications/EnergyPlus-8-8-0/energyplus'
        idd_path = '/Applications/EnergyPlus-8-8-0/Energy+.idd'
    elif platform == "win32":
        print('Windows operating system identified.\nIDD path setup completed.\n')
        ep_path = 'C:/EnergyPlusV8-8-0/energyplus.exe'
        idd_path = 'C:/EnergyPlusV8-8-0/Energy+.idd'

    # Setup idd file
    IDF.setiddname(idd_path)

    # Check for idf files
    # Define template file path
    idf_path = './Models/templates'
    # Define the file extension
    idf_extension = '.idf'
    # Put all of the files matching the above description in a list
    idf_files = [f for f in os.listdir(idf_path) if f.endswith(idf_extension)]
    # Count the number of files in the directory
    idf_count = len(idf_files)
    print('There are {} idf files in the "{}" directory.'.format(idf_count, idf_path))

    # Load individual template files
    idf_data = IDF('{}/{}.idf'.format(idf_path, 'skp_data'))  # Simulation setup
    idf_skp01 = IDF('{}/{}.idf'.format(idf_path, 'skp_01'))  # Geometry, glazing
    idf_skp05 = IDF('{}/{}.idf'.format(idf_path, 'skp_05'))  # Glazing
    idf_skp09 = IDF('{}/{}.idf'.format(idf_path, 'skp_09'))  # Geometry, glazing
    idf_skp13 = IDF('{}/{}.idf'.format(idf_path, 'skp_13'))  # Glazing

    save_path = './Models/ss1_idfs'
    idf_count = 16

    geometries = [idf_skp01, idf_skp09]
    glazings = [idf_skp01, idf_skp05, idf_skp09, idf_skp13]
    walls = ['Wall A', 'Wall B']
    windows = ['Window A', 'Window B']
    name_nos = ["%.2d" % i for i in range(idf_count)]

    generate_idf(save_path, idf_data, idf_skp01, idf_skp01, 'Wall A', 'Window A', 'ss1_01')
    generate_idf(save_path, idf_data, idf_skp01, idf_skp01, 'Wall B', 'Window A', 'ss1_02')
    generate_idf(save_path, idf_data, idf_skp01, idf_skp01, 'Wall A', 'Window B', 'ss1_03')
    generate_idf(save_path, idf_data, idf_skp01, idf_skp01, 'Wall B', 'Window B', 'ss1_04')

    generate_idf(save_path, idf_data, idf_skp01, idf_skp05, 'Wall A', 'Window A', 'ss1_05')
    generate_idf(save_path, idf_data, idf_skp01, idf_skp05, 'Wall B', 'Window A', 'ss1_06')
    generate_idf(save_path, idf_data, idf_skp01, idf_skp05, 'Wall A', 'Window B', 'ss1_07')
    generate_idf(save_path, idf_data, idf_skp01, idf_skp05, 'Wall B', 'Window B', 'ss1_08')

    generate_idf3(save_path, idf_data, idf_skp09, idf_skp09, 'Wall A', 'Window A', 'ss1_09')
    generate_idf3(save_path, idf_data, idf_skp09, idf_skp09, 'Wall B', 'Window A', 'ss1_10')
    generate_idf3(save_path, idf_data, idf_skp09, idf_skp09, 'Wall A', 'Window B', 'ss1_11')
    generate_idf3(save_path, idf_data, idf_skp09, idf_skp09, 'Wall B', 'Window B', 'ss1_12')

    generate_idf3(save_path, idf_data, idf_skp09, idf_skp13, 'Wall A', 'Window A', 'ss1_13')
    generate_idf3(save_path, idf_data, idf_skp09, idf_skp13, 'Wall B', 'Window A', 'ss1_14')
    generate_idf3(save_path, idf_data, idf_skp09, idf_skp13, 'Wall A', 'Window B', 'ss1_15')
    generate_idf3(save_path, idf_data, idf_skp09, idf_skp13, 'Wall B', 'Window B', 'ss1_16')

    idf_list = []
    for design in range(1, idf_count + 1):
        idf_file = modify_idf(design, idf_count, save_path)
        idf_list.append(idf_file)

    print(idf_list)

    # Specify save location for generated buildings
    output_path = './Models/ss1_input/'
    print('Model save location: {}'.format(output_path))

    print('\nAll buildings are now ready for EnergyPlus simulations. Proceed with execution of ep_1run.py')

    print('\n Total run time:')
    stop = timeit.default_timer()
    print('{0:.4g} seconds'.format(stop - start))
    print('\n---END---')


'''
FUNCTIONS
'''


def generate_idf(save_path, idf_data, idf_surfaces, idf_fenestration, wall_type, window_type, save_as):
    # Definitions
    mater = 'Material'
    glazi = 'WindowMaterial:SimpleGlazingSystem'
    const = 'Construction'
    surfa = 'BuildingSurface:Detailed'
    fenes = 'FenestrationSurface:Detailed'
    gen00 = 'Version'
    gen01 = 'SimulationControl'
    gen02 = 'RunPeriod'
    gen03 = 'Building'
    gen04 = 'Timestep'
    gen05 = 'SizingPeriod:WeatherFileDays'
    gen06 = 'RunPeriodControl:DaylightSavingTime'
    gen07 = 'Site:GroundTemperature:BuildingSurface'
    gen08 = 'GlobalGeometryRules'
    zon01 = 'ZoneVentilation:DesignFlowRate'
    zon02 = 'ZoneInfiltration:DesignFlowRate'
    zon03 = 'ZoneList'
    zon04 = 'Zone'
    lds01 = 'People'
    lds02 = 'Lights'
    lds03 = 'ElectricEquipment'
    sch01 = 'Schedule:Compact'
    sch02 = 'ScheduleTypeLimits'
    sch03 = 'Schedule:Day:Interval'
    sch04 = 'Schedule:Week:Daily'
    sch05 = 'Schedule:Year'
    sch06 = 'Schedule:Constant'
    hvc01 = 'HVACTemplate:Thermostat'
    hvc02 = 'HVACTemplate:Zone:VAV'
    hvc03 = 'HVACTemplate:System:PackagedVAV'
    out01 = 'Output:Surfaces:Drawing'
    out02 = 'OutputControl:Table:Style'
    out03 = 'Output:Table:SummaryReports'
    del_01 = 'LifeCycleCost:Parameters'
    del_02 = 'LifeCycleCost:UsePriceEscalation'
    del_03 = 'ZoneControl:Thermostat'
    del_04 = 'ThermostatSetpoint:DualSetpoint'
    del_05 = 'HVACTemplate:Zone:IdealLoadsAirSystem'
    del_06 = 'DesignSpecification:OutdoorAir'
    del_07 = 'Sizing:Parameters'
    del_08 = 'Material:AirGap'
    del_09 = 'WindowMaterial:Blind'
    del_10 = 'WindowMaterial:Glazing'
    del_11 = 'WindowProperty:FrameAndDivider'
    del_12 = 'WindowProperty:ShadingControl'
    del_13 = 'Site:Location'
    del_14 = 'Output:VariableDictionary'
    del_15 = 'Output:SQLite'
    del_16 = 'LifeCycleCost:NonrecurringCost'

    # Assignments
    gen00 = idf_data.idfobjects[gen00.upper()][0]
    gen01 = idf_data.idfobjects[gen01.upper()][0]
    gen02 = idf_data.idfobjects[gen02.upper()][0]
    gen03 = idf_data.idfobjects[gen03.upper()][0]
    gen04 = idf_data.idfobjects[gen04.upper()][0]
    gen05 = idf_data.idfobjects[gen05.upper()][0]
    gen06 = idf_data.idfobjects[gen06.upper()][0]
    gen07 = idf_data.idfobjects[gen07.upper()][0]
    gen08 = idf_data.idfobjects[gen08.upper()][0]
    zon01 = idf_data.idfobjects[zon01.upper()][0]
    zon02 = idf_data.idfobjects[zon02.upper()][0]
    zon03 = idf_data.idfobjects[zon03.upper()][0]
    zon04 = idf_data.idfobjects[zon04.upper()][0]
    lds01 = idf_data.idfobjects[lds01.upper()][0]
    lds02 = idf_data.idfobjects[lds02.upper()][0]
    lds03 = idf_data.idfobjects[lds03.upper()][0]
    sch01 = idf_data.idfobjects[sch01.upper()]
    sch02 = idf_data.idfobjects[sch02.upper()]
    sch03 = idf_data.idfobjects[sch03.upper()]
    sch04 = idf_data.idfobjects[sch04.upper()]
    sch05 = idf_data.idfobjects[sch05.upper()]
    sch06 = idf_data.idfobjects[sch06.upper()]
    hvc01 = idf_data.idfobjects[hvc01.upper()][0]
    hvc02 = idf_data.idfobjects[hvc02.upper()][0]
    hvc03 = idf_data.idfobjects[hvc03.upper()][0]
    out01 = idf_data.idfobjects[out01.upper()][0]
    out02 = idf_data.idfobjects[out02.upper()][0]
    out03 = idf_data.idfobjects[out03.upper()][0]

    # MATERIALS
    mater = idf_data.idfobjects[mater.upper()]
    glazi = idf_data.idfobjects[glazi.upper()]
    # CONSTRUCTION
    const = idf_data.idfobjects[const.upper()]
    # GEOMETRY
    surface_objects = idf_surfaces.idfobjects[surfa.upper()]
    fenestration_objects = idf_fenestration.idfobjects[fenes.upper()]

    # CREATE NEW IDF FILE
    # with common info and specific geometry
    idf2 = IDF()
    idf2.new()

    # copy over relevant info from source idfs
    source_objects = [gen00, gen01, gen02, gen03, gen04, gen05, gen06, gen07, gen08,
                      zon01, zon02, zon03, zon04,
                      lds01, lds02, lds03,
                      hvc01, hvc02, hvc03,
                      out01, out02, out03]
    for i in source_objects:
        idf2.copyidfobject(i)

    for i in sch01:
        idf2.copyidfobject(i)
    for i in sch02:
        idf2.copyidfobject(i)
    for i in sch03:
        idf2.copyidfobject(i)
    for i in sch04:
        idf2.copyidfobject(i)
    for i in sch05:
        idf2.copyidfobject(i)
    for i in sch06:
        idf2.copyidfobject(i)

    # MATERIALS
    for i in mater:
        idf2.copyidfobject(i)
    # GLAZING
    for i in glazi:
        idf2.copyidfobject(i)
    # CONSTRUCTIONS
    for i in const:
        idf2.copyidfobject(i)

    # Load geometry from a specific file.
    for i in surface_objects:
        idf2.copyidfobject(i)
    for i in fenestration_objects:
        idf2.copyidfobject(i)

    new_surface = idf2.idfobjects[surfa.upper()]
    new_subsurface = idf2.idfobjects[fenes.upper()]

    # Change the construction of each surface and glazing
    floor_type = 'Slab A'
    ceiling_type = 'Slab A'
    roof_type = 'Roof A'

    for surface in new_surface:
        if surface['Surface_Type'] == 'Floor':
            surface.Construction_Name = floor_type
        elif surface['Surface_Type'] == 'Ceiling':
            surface.Construction_Name = ceiling_type
        elif surface['Surface_Type'] == 'Roof':
            surface.Construction_Name = roof_type
        elif surface['Surface_Type'] == 'Wall':
            surface.Construction_Name = wall_type

    for subsurface in new_subsurface:
        if subsurface['Surface_Type'] == 'Window':
            subsurface.Construction_Name = window_type

    # Save to the disk and return to main
    idf2.saveas('{}/{}.idf'.format(save_path, save_as))
    idf_file = '{}/{}.idf'.format(save_path, save_as)

    return idf_file


def generate_idf3(save_path, idf_data, idf_surfaces, idf_fenestration, wall_type, window_type, save_as):
    mater = 'Material'  # All
    glazi = 'WindowMaterial:SimpleGlazingSystem'  # All
    const = 'Construction'  # All
    surfa = 'BuildingSurface:Detailed'  # For geometry
    fenes = 'FenestrationSurface:Detailed'  # For geometry
    gen00 = 'Version'  # All
    gen01 = 'SimulationControl'  # All
    gen02 = 'RunPeriod'  # All
    gen03 = 'Building'  # All
    gen04 = 'Timestep'  # All
    gen05 = 'SizingPeriod:WeatherFileDays'  # All
    gen06 = 'RunPeriodControl:DaylightSavingTime'  # All
    gen07 = 'Site:GroundTemperature:BuildingSurface'  # All
    gen08 = 'GlobalGeometryRules'  # All
    zon01 = 'ZoneVentilation:DesignFlowRate'  # For geometry
    zon02 = 'ZoneInfiltration:DesignFlowRate'  # For geometry
    zon03 = 'ZoneList'  # For geometry
    zon04 = 'Zone'  # For geometry
    lds01 = 'People'  # For geometry
    lds02 = 'Lights'  # For geometry
    lds03 = 'ElectricEquipment'  # For geometry
    sch01 = 'Schedule:Compact'
    sch02 = 'ScheduleTypeLimits'
    sch03 = 'Schedule:Day:Interval'
    sch04 = 'Schedule:Week:Daily'
    sch05 = 'Schedule:Year'
    sch06 = 'Schedule:Constant'
    hvc01 = 'HVACTemplate:Thermostat'  # All
    hvc02 = 'HVACTemplate:Zone:VAV'  # For geometry
    hvc03 = 'HVACTemplate:System:PackagedVAV'  # All
    out01 = 'Output:Surfaces:Drawing'
    out02 = 'OutputControl:Table:Style'
    out03 = 'Output:Table:SummaryReports'
    del_01 = 'LifeCycleCost:Parameters'
    del_02 = 'LifeCycleCost:UsePriceEscalation'
    del_03 = 'ZoneControl:Thermostat'
    del_04 = 'ThermostatSetpoint:DualSetpoint'
    del_05 = 'HVACTemplate:Zone:IdealLoadsAirSystem'
    del_06 = 'DesignSpecification:OutdoorAir'
    del_07 = 'Sizing:Parameters'
    del_08 = 'Material:AirGap'
    del_09 = 'WindowMaterial:Blind'
    del_10 = 'WindowMaterial:Glazing'
    del_11 = 'WindowProperty:FrameAndDivider'
    del_12 = 'WindowProperty:ShadingControl'
    del_13 = 'Site:Location'
    del_14 = 'Output:VariableDictionary'
    del_15 = 'Output:SQLite'
    del_16 = 'LifeCycleCost:NonrecurringCost'

    # Assignments
    gen00 = idf_data.idfobjects[gen00.upper()][0]
    gen01 = idf_data.idfobjects[gen01.upper()][0]
    gen02 = idf_data.idfobjects[gen02.upper()][0]
    gen03 = idf_data.idfobjects[gen03.upper()][0]
    gen04 = idf_data.idfobjects[gen04.upper()][0]
    gen05 = idf_data.idfobjects[gen05.upper()][0]
    gen06 = idf_data.idfobjects[gen06.upper()][0]
    gen07 = idf_data.idfobjects[gen07.upper()][0]
    gen08 = idf_data.idfobjects[gen08.upper()][0]
    zon01 = idf_surfaces.idfobjects[zon01.upper()][0]
    zon02 = idf_surfaces.idfobjects[zon02.upper()][0]
    zon03 = idf_surfaces.idfobjects[zon03.upper()][0]
    zon04 = idf_surfaces.idfobjects[zon04.upper()]
    lds01 = idf_surfaces.idfobjects[lds01.upper()][0]
    lds02 = idf_surfaces.idfobjects[lds02.upper()][0]
    lds03 = idf_surfaces.idfobjects[lds03.upper()][0]
    sch01 = idf_data.idfobjects[sch01.upper()]
    sch02 = idf_data.idfobjects[sch02.upper()]
    sch03 = idf_data.idfobjects[sch03.upper()]
    sch04 = idf_data.idfobjects[sch04.upper()]
    sch05 = idf_data.idfobjects[sch05.upper()]
    sch06 = idf_data.idfobjects[sch06.upper()]
    hvc01 = idf_data.idfobjects[hvc01.upper()][0]
    hvc02 = idf_surfaces.idfobjects[hvc02.upper()]
    hvc03 = idf_data.idfobjects[hvc03.upper()][0]
    out01 = idf_data.idfobjects[out01.upper()][0]
    out02 = idf_data.idfobjects[out02.upper()][0]
    out03 = idf_data.idfobjects[out03.upper()][0]

    # MATERIALS
    mater = idf_data.idfobjects[mater.upper()]
    glazi = idf_data.idfobjects[glazi.upper()]
    # CONSTRUCTION
    const = idf_data.idfobjects[const.upper()]
    # GEOMETRY
    surface_objects = idf_surfaces.idfobjects[surfa.upper()]
    fenestration_objects = idf_fenestration.idfobjects[fenes.upper()]

    # CREATE NEW IDF FILE
    # with common info and specific geometry
    idf2 = IDF()
    idf2.new()

    # copy over relevant info from source idfs
    # GENERAL
    idf2.copyidfobject(gen00)
    idf2.copyidfobject(gen01)
    idf2.copyidfobject(gen02)
    idf2.copyidfobject(gen03)
    idf2.copyidfobject(gen04)
    idf2.copyidfobject(gen05)
    idf2.copyidfobject(gen06)
    idf2.copyidfobject(gen07)
    idf2.copyidfobject(gen08)
    # ZONE
    idf2.copyidfobject(zon01)
    idf2.copyidfobject(zon02)
    idf2.copyidfobject(zon03)
    # idf2.copyidfobject(zon04)
    # LOADS
    idf2.copyidfobject(lds01)
    idf2.copyidfobject(lds02)
    idf2.copyidfobject(lds03)
    # HVAC
    idf2.copyidfobject(hvc01)
    # idf2.copyidfobject(hvc02)
    idf2.copyidfobject(hvc03)
    # OUTPUT
    idf2.copyidfobject(out01)
    idf2.copyidfobject(out02)
    idf2.copyidfobject(out03)
    # SCHEDULES
    for i in sch01:
        idf2.copyidfobject(i)
    for i in sch02:
        idf2.copyidfobject(i)
    for i in sch03:
        idf2.copyidfobject(i)
    for i in sch04:
        idf2.copyidfobject(i)
    for i in sch05:
        idf2.copyidfobject(i)
    for i in sch06:
        idf2.copyidfobject(i)

    for i in zon04:
        idf2.copyidfobject(i)
    for i in hvc02:
        idf2.copyidfobject(i)

    # MATERIALS
    for i in mater:
        idf2.copyidfobject(i)
    # GLAZING
    for i in glazi:
        idf2.copyidfobject(i)
    # CONSTRUCTIONS
    for i in const:
        idf2.copyidfobject(i)

    # Basic setup done
    # Now I need geometry from a specific file.
    # GEOMETRY
    for i in surface_objects:
        idf2.copyidfobject(i)
    for i in fenestration_objects:
        idf2.copyidfobject(i)

    new_surface = idf2.idfobjects[surfa.upper()]
    new_subsurface = idf2.idfobjects[fenes.upper()]

    # Now I want to change the construction of each surface and glazing.
    floor_type = 'Slab A'
    ceiling_type = 'Slab A'
    roof_type = 'Roof A'

    for surface in new_surface:
        if surface['Surface_Type'] == 'Floor':
            surface.Construction_Name = floor_type

    for surface in new_surface:
        if surface['Surface_Type'] == 'Ceiling':
            surface.Construction_Name = ceiling_type

    for surface in new_surface:
        if surface['Surface_Type'] == 'Roof':
            surface.Construction_Name = roof_type

    for surface in new_surface:
        if surface['Surface_Type'] == 'Wall':
            surface.Construction_Name = wall_type

    for subsurface in new_subsurface:
        if subsurface['Surface_Type'] == 'Window':
            subsurface.Construction_Name = window_type

    # Save it to the disk.
    idf2.saveas('{}/{}.idf'.format(save_path, save_as))
    idf_file = '{}/{}.idf'.format(save_path, save_as)

    return idf_file


def modify_idf(design, designs, idf_path):
    # Load idf file
    idf1 = IDF('./Models/ss1_idfs/ss1_{:02d}.idf'.format(design))

    # Setup fields to be changed
    building = 'Building'
    building = idf1.idfobjects[building.upper()][0]

    # Set object information
    building.Name = 'Building Design {:02d}/{:02d}'.format(design, designs)
    building.North_Axis = '0'

    print('IDF file setup for {} completed'.format(building.Name))

    idf_path = './Models/ss1_idfs'

    idf1.saveas('{}/ss1_{:02d}.idf'.format(idf_path, design))
    idf_file = '{}/ss1_{:02d}.idf'.format(idf_path, design)

    return idf_file


if __name__ == "__main__": main()