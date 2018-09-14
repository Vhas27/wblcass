#!/usr/Anaconda3/bin/python3
# ep_2run.py by Vaclav Hasik

from sys import platform
import os
import timeit
from eppy.modeleditor import IDF
import subprocess
import matplotlib.pyplot as plt
import time
import humanfriendly

plt.style.use('ggplot')

'''
MAIN BODY
Pseudo-code:
- Load idf file
- Run EnergyPlus
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
        print('Mac operating system identified.\nIDD path setup completed.')
        ep_path = '/Applications/EnergyPlus-8-8-0/energyplus'
        idd_path = '/Applications/EnergyPlus-8-8-0/Energy+.idd'
    elif platform == "win32":
        print('Windows operating system identified.')
        ep_path = 'C:/EnergyPlusV8-8-0/energyplus.exe'
        idd_path = 'C:/EnergyPlusV8-8-0/Energy+.idd'

    # Setup idd file
    IDF.setiddname(idd_path)
    print('IDD path setup completed.')
    # Specify weather file ==================================
    weather_path = './Data/Weather/'
    weather_file = 'PHL.epw'
    print('\nWeather file path: {}{}'.format(weather_path, weather_file))
    time.sleep(1)   # pause 1 second
    weather_locations = [weather_file]

    # Automating runs for multiple locations:
    '''
    weather_extension = '.epw'
    weather_files = [f for f in os.listdir(weather_path) if (f.endswith(weather_extension))]
    weather_count = len(weather_files)
    print('There are {} epw files in the "{}" directory.'.format(weather_count, weather_path))
    weather_locations = []
    for name in weather_files:
        split_name = name.split(".")
        weather_locations.append(split_name[0])
    '''

    # Specify idf file ======================================
    idf_group = 'ss2'

    idf_path = './Models/{}_idfs/'.format(idf_group)
    selection = select_run().lower()
    time.sleep(1)   # pause 1 second

    if selection in 'single':
        idf_design = 1
        idf_name = '{}_{:02d}'.format(idf_group, idf_design)
        print('\nInput file path: {}{}'.format(idf_path, idf_name))
        idf_list = [idf_name]
        idf_count = 1
    elif selection in 'batch':
        idf_extension = '.idf'
        idf_list = [f for f in os.listdir(idf_path) if f.endswith(idf_extension)]
        idf_count = len(idf_list)
        print('\nThere are {} idf files in the "{}" directory.'.format(idf_count, idf_path))
        for i in idf_list:
            print(i)
            time.sleep(.1)
    else:
        print('Invalid entry. Terminating.')

    # Specify output location ===============================
    output_path = './Models/{}_output/'.format(idf_group)
    time.sleep(1)   # pause 1 second

    # Run EnergyPlus simulations
    print('\nAccessing EnergyPlus')
    time.sleep(1)

    for location in weather_locations:
        for design in range(1, idf_count+1):
            print('\nSimulation of {}_{:02d} is beginning\n'.format(idf_group, design))
            time.sleep(2)  # pause 2 seconds
            idf_name = '{}_{:02d}'.format(idf_group, design)
            run_ep(ep_path, output_path, idf_path, idf_name, weather_path, location)
            print('\nSimulation of {}_{:02d} completed.\n=============================\n\n\n'.format(idf_group, design))

    print('\nTotal run time:')
    stop = timeit.default_timer()
    print(humanfriendly.format_timespan(stop - start))
    print('\n---END---')


'''
FUNCTIONS
'''


def run_ep(ep_path, output_path, idf_path, idf_name, weather_path, weather_file):
    subprocess.call([ep_path,
                     '-d', '{}'.format(output_path),
                     '-p', '{}'.format(idf_name),
                     '-s', 'C',
                     '-w', '{}{}'.format(weather_path, weather_file),
                     '-x', '{}{}.idf'.format(idf_path, idf_name)])

    # ENERGYPLUS SETTINGS
    # -a, --annual                 Force annual simulation
    # -d, --output-directory ARG   Output directory path (default: current
    #                              directory)
    # -D, --design-day             Force design-day-only simulation
    # -h, --help                   Display help information
    # -i, --idd ARG                Input data dictionary path (default: Energy+.idd
    #                              in executable directory)
    # -m, --epmacro                Run EPMacro prior to simulation
    # -p, --output-prefix ARG      Prefix for output file names (default: eplus)
    # -r, --readvars               Run ReadVarsESO after simulation
    # -s, --output-suffix ARG      Suffix style for output file names (default: L)
    #                                 L: Legacy (e.g., eplustbl.csv)
    #                                 C: Capital (e.g., eplusTable.csv)
    #                                 D: Dash (e.g., eplus-table.csv)
    # -v, --version                Display version information
    # -w, --weather ARG            Weather file path (default: in.epw in current
    #                              directory)
    # -x, --expandobjects          Run ExpandObjects prior to simulation


def select_run():
    i = 0
    while i < 1:
        selection = input('\nRun single file or a batch of files? (Options: Single | Batch)\n>> ')

        if selection.lower() in 'single':
            print('\nSINGLE file run selected.')
            i = 1
        elif selection.lower() in 'batch':
            print('\nBATCH file run selected.')
            i = 1
        else:
            print('\nInvalid entry. Try again.')

    return selection


if __name__ == "__main__": main()