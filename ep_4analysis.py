#!/usr/Anaconda3/bin/python3
# ep_4analysis.py by Vaclav Hasik

import time
import os
import timeit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('ggplot')

'''
MAIN BODY
Pseudo-code:
- Open csv files
- Load them into a dataframe
- Plot design vs. decision variables scatter plot
- Plot systems by design bar chart
- Plot designs by decision variable scatter plot
'''


def main():
    # Show that the program started
    print('\n---START---')
    # Start timing the program execution
    start = timeit.default_timer()

    # STUDY SETUP
    idf_group = 'ss2'
    study_period = 30   # LCA study period in years

    print('Program beginning.\n\nIdf group selected: {}\nStudy period: {}'.format(idf_group, study_period))

    # DATABASE AND CONSTANT VARIABLE SETUP
    # Preload all necessary databases
    df_master = pd.read_csv('./Results/{}_summary__master.csv'.format(idf_group))   # Load master spreadsheet

    # Impact assessment methods and categories
    traci_2_1 = ['LCI_ODP', 'LCI_GWP', 'LCI_SFP', 'LCI_AP', 'LCI_EP', 'LCI_C', 'LCI_NC', 'LCI_RE', 'LCI_ETX', 'LCI_FFD']
    impact_categories = traci_2_1

    attributes = ['Number', 'Building', 'Category', 'Scale', 'Source', 'System', 'Construction', 'Layer', 'Element',
                  'Ingredient', 'Stage']

    # Attribute descriptions:
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

    # PLOTS
    df1 = pd.DataFrame((df_master.groupby('Building').sum().reset_index()))
    df1.to_csv('./Results/{}_summary_building.csv'.format(idf_group))
    print(df1)

    # Figure 1 multiple scatter plots
    fig = plt.figure(num=1, figsize=(7, 3), dpi=250)

    ax1 = fig.add_subplot(241)
    df1.plot.scatter(x='Cost', y='LCI_ODP', c='Number', colormap='rainbow',  ax=ax1)
    # plot settings
    ax1.tick_params(axis='x', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax1.tick_params(axis='y', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax1.set_xlabel('USD', fontsize=6, color='Black')
    ax1.set_ylabel('ODP', fontsize=6, color='Black')

    fig = plt.figure(num=1, figsize=(5, 4), dpi=250)
    ax2 = fig.add_subplot(242)
    df1.plot.scatter(x='Cost', y='LCI_GWP', c='DarkBlue', ax=ax2)
    # plot settings
    ax2.tick_params(axis='x', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax2.tick_params(axis='y', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax2.set_xlabel('Cost (2016 USD)', fontsize=6, color='Black')
    ax2.set_ylabel('GWP (kgCO2e', fontsize=6, color='Black')

    fig = plt.figure(num=1, figsize=(5, 4), dpi=250)
    ax3 = fig.add_subplot(243)
    df1.plot.scatter(x='Cost', y='LCI_SFP', c='DarkBlue', ax=ax3)
    # plot settings
    ax3.tick_params(axis='x', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax3.tick_params(axis='y', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax3.set_xlabel('USD', fontsize=6, color='Black')
    ax3.set_ylabel('SFP', fontsize=6, color='Black')

    fig = plt.figure(num=1, figsize=(5, 4), dpi=250)
    ax4 = fig.add_subplot(244)
    df1.plot.scatter(x='Cost', y='LCI_AP', c='DarkBlue', ax=ax4)
    # plot settings
    ax4.tick_params(axis='x', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax4.tick_params(axis='y', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax4.set_xlabel('USD', fontsize=6, color='Black')
    ax4.set_ylabel('AP', fontsize=6, color='Black')

    fig = plt.figure(num=1, figsize=(5, 4), dpi=250)
    ax5 = fig.add_subplot(245)
    df1.plot.scatter(x='Cost', y='LCI_EP', c='DarkBlue', ax=ax5)
    # plot settings
    ax5.tick_params(axis='x', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax5.tick_params(axis='y', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax5.set_xlabel('USD', fontsize=6, color='Black')
    ax5.set_ylabel('EP', fontsize=6, color='Black')

    fig = plt.figure(num=1, figsize=(5, 4), dpi=250)
    ax6 = fig.add_subplot(246)
    df1.plot.scatter(x='Cost', y='LCI_C', c='DarkBlue', ax=ax6)
    # plot settings
    ax6.tick_params(axis='x', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax6.tick_params(axis='y', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax6.set_xlabel('USD', fontsize=6, color='Black')
    ax6.set_ylabel('Carcinogenics', fontsize=6, color='Black')

    fig = plt.figure(num=1, figsize=(5, 4), dpi=250)
    ax7 = fig.add_subplot(247)
    df1.plot.scatter(x='Cost', y='LCI_NC', c='DarkBlue', ax=ax7)
    # plot settings
    ax7.tick_params(axis='x', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax7.tick_params(axis='y', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax7.set_xlabel('USD', fontsize=6, color='Black')
    ax7.set_ylabel('Non-carcinogenics', fontsize=6, color='Black')

    fig = plt.figure(num=1, figsize=(5, 4), dpi=250)
    ax8 = fig.add_subplot(248)
    df1.plot.scatter(x='Cost', y='LCI_FFD', c='DarkBlue', ax=ax8)
    # plot settings
    ax8.tick_params(axis='x', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax8.tick_params(axis='y', which='both', labelsize=4, color='Black', labelcolor='Black')
    ax8.set_xlabel('USD', fontsize=6, color='Black')
    ax8.set_ylabel('Fossil Fuel', fontsize=6, color='Black')

    '''
    # Figure 1 multiple scatter plots
    fig2 = plt.figure(num=2, figsize=(4, 3), dpi=250)

    bx1 = fig.add_subplot(111)
    df1.plot.scatter(x=[], y='Designs', ax=bx1)
    # plot settings
    bx1.tick_params(axis='x', which='both', labelsize=4, color='Black', labelcolor='Black')
    bx1.tick_params(axis='y', which='both', labelsize=4, color='Black', labelcolor='Black')
    bx1.set_xlabel('USD', fontsize=6, color='Black')
    bx1.set_ylabel('ODP', fontsize=6, color='Black')
    '''

    # End of plot settings
    fig.tight_layout()
    plt.show()

    fig_path = './Figures'
    fig.savefig('{}/fig_{}_{}.png'.format(fig_path, idf_group, 1))
    plt.close()

    # Print total program runtime
    print('\n Total run time:')
    stop = timeit.default_timer()
    print('{0:.4g} seconds'.format(stop - start))
    print('\n---END---')


'''
FUNCTIONS
'''


if __name__ == "__main__": main()