# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 14:58:24 2024

@author: vabuchar
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import seaborn as sns

import statsmodels.api as sm
from scipy import stats
from scipy.stats import norm

import warnings
warnings.simplefilter('ignore')

# FUNCTIONS
from fragility_function_CG import fragility_function_CG

#%%
# LOAD DATA

data_Stat = pd.read_excel('InputData.xlsx', sheet_name='Statics')
data_SolMech = pd.read_excel('InputData.xlsx', sheet_name='SolidMechanics')

#%% DISPERSION

# STATICS
fig1, ax1 = plt.subplots(figsize=(7,5))
ax1.plot(data_Stat['GPA'], data_Stat['CG'], marker = 'o', mfc = 'white', mec = 'black', linestyle='', markersize = 4, alpha = 0.7)
ax1.set_xlabel('GPA', size = 12)
ax1.set_ylabel('CG', size = 12)
ax1.set_title('Statics')
ax1.set_xlim(3,5)
ax1.set_ylim(-0.1,5.1)

# SOLID MECHANICS
fig2, ax2 = plt.subplots(figsize=(7,5))
ax2.plot(data_SolMech['GPA'], data_SolMech['CG'], marker = 'o', mfc = 'white', mec = 'black', linestyle='', markersize = 4, alpha = 0.7)
ax2.set_xlabel('GPA', size = 12)
ax2.set_ylabel('CG', size = 12)
ax2.set_title('Solid Mechanics')
ax2.set_xlim(3,5)
ax2.set_ylim(-0.1,5.1)

#%% FRAGILITY ESTIMATION

# Clean data
data_Stat = data_Stat[data_Stat['CG']>0]
data_Stat = data_Stat.reset_index(drop=True)
data_SolMech = data_SolMech [data_SolMech ['CG']>0]
data_SolMech = data_SolMech.reset_index(drop=True)

# Grades of interest (thresholds)
GOI = [3.0, 3.5, 4.0]

[param_Stat, data_plot_Stat, frag_Stat, All_data_Stat, count_Stat] = fragility_function_CG(data_Stat['GPA'], data_Stat['CG'], GOI)
[param_SolMech, data_plot_SolMech, frag_SolMech, All_data_SolMech, count_SolMech] = fragility_function_CG(data_SolMech['GPA'], data_SolMech['CG'], GOI)    

# Inputs for Curves
pos = 0 # Modificate according to the vector GOI
curr_GOI = GOI[pos] 

lim_inf = 3.3
lim_sup = 5.0

#%% BINNING

# STATICS
All_data_Stat_2 = All_data_Stat.copy()
All_data_Stat_2.drop(['IM'], axis = 1)
All_data_Stat_2['IM_bin'] = round(All_data_Stat_2['IM_bin'],1)
All_data_Stat_2['EDP'] = round(All_data_Stat_2['EDP'],1)
All_data_Stat_2 = All_data_Stat_2.groupby(by=['IM_bin', 'EDP']).count()
All_data_Stat_2.columns = ['Cantidad']

fig3, ax3 = plt.subplots(figsize=(7,4))
for i in range(len(All_data_Stat_2)):
    ax3.plot(All_data_Stat_2.index[i][0], All_data_Stat_2.index[i][1], marker = 'o', 
             mfc = 'gray', mec = 'black', linestyle='', markersize = (All_data_Stat_2.iloc[i,0])**0.6, alpha = 0.5)
    
ax3.set_xlabel('GPA$_{bin}$', size = 12)
ax3.set_ylabel('CG', size = 12)
ax3.set_title('Statics')
ax3.set_xlim(3,5)
ax3.set_ylim(-0.1,5.1)

# SOLID MECHANICS
All_data_SolMech_2 = All_data_SolMech.copy()
All_data_SolMech_2.drop(['IM'], axis = 1)
All_data_SolMech_2['IM_bin'] = round(All_data_SolMech_2['IM_bin'],1)
All_data_SolMech_2['EDP'] = round(All_data_SolMech_2['EDP'],1)
All_data_SolMech_2 = All_data_SolMech_2.groupby(by=['IM_bin', 'EDP']).count()
All_data_SolMech_2.columns = ['Cantidad']

fig4, ax4 = plt.subplots(figsize=(7,5))
for i in range(len(All_data_SolMech_2)):
    ax4.plot(All_data_SolMech_2.index[i][0], All_data_SolMech_2.index[i][1], marker = 'o', 
             mfc = 'gray', mec = 'black', linestyle='', markersize = (All_data_SolMech_2.iloc[i,0])**0.6, alpha = 0.5)
    
ax4.set_xlabel('GPA$_{bin}$', size = 12)
ax4.set_ylabel('CG', size = 12)
ax4.set_title('Solid Mechanics')
ax4.set_xlim(3,5)
ax4.set_ylim(-0.1,5.1)

#%% CASE 1: COMPARISON BETWEEN COURSES

# -----------------------------------------------
# P(CG >= GOI)
fig5, ax5 = plt.subplots(figsize=(7,5))

# Curves
ax5.plot(data_plot_Stat['IM'], data_plot_Stat['j = ' + str(curr_GOI)], color = 'black', linestyle = '-',
        label = 'Statics' +' - ' + r"$\theta$" +' = ' + str(round(param_Stat.iloc[pos,1],2)) + '  ' +
        r"$\beta$"+' = ' + str(round(param_Stat.iloc[pos,2],3)))

ax5.plot(data_plot_SolMech['IM'], data_plot_SolMech['j = ' + str(curr_GOI)], color = 'gray', linestyle = '--',
        label = 'Solid Mechanics' + ' - ' + r"$\theta$" +' = ' + str(round(param_SolMech.iloc[pos,1],2)) + '  ' +
        r"$\beta$"+' = ' + str(round(param_SolMech.iloc[pos,2],3)))

# Points
ax5.plot(frag_Stat['IM_bin'], frag_Stat['Zi - j = ' + str(curr_GOI)]/frag_Stat['N'], color = 'black', 
          marker = 'o', linestyle='', markersize = 3)

ax5.plot(frag_SolMech['IM_bin'], frag_SolMech['Zi - j = ' + str(curr_GOI)]/frag_SolMech['N'], color = 'gray', 
          marker = '^', linestyle='', markersize = 3)


ax5.set_xlim(lim_inf, lim_sup)
ax5.set_xlabel('GPA', size = 12)
ax5.set_ylabel('P(CG >= ' + str(curr_GOI) + ')', size = 12)
ax5.set_ylim(0, 1)
ax5.set_yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
ax5.tick_params(axis='both', labelsize=11) 

ax5.grid(which="both")
ax5.legend(fontsize=11)


# -----------------------------------------------
# P(CG < GOI)

fig6, ax6 = plt.subplots(figsize=(7,5))

# Curves
ax6.plot(data_plot_Stat['IM'], 1-data_plot_Stat['j = ' + str(curr_GOI)], color = 'black', linestyle = '-',
        label = 'Statics' +' - ' + r"$\theta$" +' = ' + str(round(param_Stat.iloc[pos,1],2)) + '  ' +
        r"$\beta$"+' = ' + str(round(param_Stat.iloc[pos,2],3)))

ax6.plot(data_plot_SolMech['IM'], 1-data_plot_SolMech['j = ' + str(curr_GOI)], color = 'gray', linestyle = '--',
        label = 'Solid Mechanics' + ' - ' + r"$\theta$" +' = ' + str(round(param_SolMech.iloc[pos,1],2)) + '  ' +
        r"$\beta$"+' = ' + str(round(param_SolMech.iloc[pos,2],3)))

# Points
ax6.plot(frag_Stat['IM_bin'], 1-frag_Stat['Zi - j = ' + str(curr_GOI)]/frag_Stat['N'], color = 'black', 
          marker = 'o', linestyle='', markersize = 3)

ax6.plot(frag_SolMech['IM_bin'], 1-frag_SolMech['Zi - j = ' + str(curr_GOI)]/frag_SolMech['N'], color = 'gray', 
          marker = '^', linestyle='', markersize = 3)


ax6.set_xlim(lim_inf, lim_sup)
ax6.set_xlabel('GPA', size = 12)
ax6.set_ylabel('P(CG < ' + str(curr_GOI) + ')', size = 12)
ax6.set_ylim(0, 1)
ax6.set_yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
ax6.tick_params(axis='both', labelsize=11) 

ax6.grid(which="both")
ax6.legend(fontsize=11)



#%% CASE 2: EVOLUTION OF STATICS

# Data
sub1 = data_Stat[(data_Stat['Subgroups']>=2009) & (data_Stat['Subgroups']<=2010)]
sub1 = sub1.reset_index(drop=True)
sub2 = data_Stat[(data_Stat['Subgroups']>=2011) & (data_Stat['Subgroups']<=2012)]
sub2 = sub2.reset_index(drop=True)
sub3 = data_Stat[(data_Stat['Subgroups']>=2013) & (data_Stat['Subgroups']<=2014)]
sub3 = sub3.reset_index(drop=True)
sub4 = data_Stat[(data_Stat['Subgroups']>=2015) & (data_Stat['Subgroups']<=2016)]
sub4 = sub4.reset_index(drop=True)

# Fragility
[param_S1, data_plot_S1, frag_S1, All_data_S1, count_S1] = fragility_function_CG(sub1['GPA'], sub1['CG'], GOI)
[param_S2, data_plot_S2, frag_S2, All_data_S2, count_S2] = fragility_function_CG(sub2['GPA'], sub2['CG'], GOI)
[param_S3, data_plot_S3, frag_S3, All_data_S3, count_S3] = fragility_function_CG(sub3['GPA'], sub3['CG'], GOI)
[param_S4, data_plot_S4, frag_S4, All_data_S4, count_S4] = fragility_function_CG(sub4['GPA'], sub4['CG'], GOI)

# --------------------------------------------------------------------
# Fragility curves
fig7, ax7 = plt.subplots(figsize=(7,5))

ax7.plot(data_plot_S1['IM'], 1-data_plot_S1['j = ' + str(curr_GOI)], color = 'black', linestyle = '-',
        label = 'Years 2009-2010' +' - ' + r"$\theta$" +' = ' + str(round(param_S1.iloc[pos,1],2)) + '  ' +
        r"$\beta$"+' = ' + str(round(param_S1.iloc[pos,2],3)))

ax7.plot(data_plot_S2['IM'], 1-data_plot_S2['j = ' + str(curr_GOI)], color = 'black', linestyle = '--',
        label = 'Years 2011-2012' +' - ' + r"$\theta$" +' = ' + str(round(param_S2.iloc[pos,1],2)) + '  ' +
        r"$\beta$"+' = ' + str(round(param_S2.iloc[pos,2],3)))

ax7.plot(data_plot_S3['IM'], 1-data_plot_S3['j = ' + str(curr_GOI)], color = 'gray', linestyle = ':',
        label = 'Years 2013-2014' +' - ' + r"$\theta$" +' = ' + str(round(param_S3.iloc[pos,1],2)) + '  ' +
        r"$\beta$"+' = ' + str(round(param_S3.iloc[pos,2],3)))

ax7.plot(data_plot_S4['IM'], 1-data_plot_S4['j = ' + str(curr_GOI)], color = 'gray', linestyle = '-.',
        label = 'Years 2015-2016' +' - ' + r"$\theta$" +' = ' + str(round(param_S4.iloc[pos,1],2)) + '  ' +
        r"$\beta$"+' = ' + str(round(param_S4.iloc[pos,2],3)))

ax7.set_xlim(lim_inf, lim_sup)
ax7.set_xlabel('GPA', size = 12)
ax7.set_ylabel('P(CG < ' + str(curr_GOI) + ')', size = 12)
ax7.set_ylim(0, 1)
ax7.set_yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
ax7.tick_params(axis='both', labelsize=11) 

ax7.grid(which="both")
ax7.legend(fontsize=11)

# --------------------------------------------------------------------
# Thetas and betas comparison 

thetas = [round(param_S1.iloc[pos,1],2), round(param_S2.iloc[pos,1],2), round(param_S3.iloc[pos,1],2), round(param_S4.iloc[pos,1],2)]
betas= [round(param_S1.iloc[pos,2],3), round(param_S2.iloc[pos,2],3), round(param_S3.iloc[pos,2],3), round(param_S4.iloc[pos,2],3)]
year = ["2009-2010", "2011-2012", "2013-2014", "2015-2016"]

fig8, ax8 = plt.subplots(figsize=(7,5))

color = 'black'
ax8.set_xlabel('Years', size = 12)
ax8.set_ylabel(r"$\theta$", color=color, size = 14)
ax8.plot(year, thetas, marker='o', color=color, linestyle='-', label=r"$\theta$", lw = 3)
ax8.tick_params(axis='y', labelcolor=color)
ax8.set_ylim(3,4)
ax8.tick_params(axis='both', labelsize=11)

ax9 = ax8.twinx()
ax9.set_ylabel(r"$\beta$", color=color, size = 14)
ax9.plot(year, betas, marker='o', color=color, linestyle='--', label=r"$\beta$", lw = 3)
ax9.tick_params(axis='y', labelcolor=color)
ax9.set_ylim(0.1,0.2)
ax9.tick_params(axis='both', labelsize=11)

ax8.legend(loc= 'upper left', bbox_to_anchor=(0.05, 1))
ax9.legend(loc= 'upper right', bbox_to_anchor=(0.95, 1))

# ax9.show()


#%% Other Figures
########################################
# P(CG < GOI)

fig66, ax66 = plt.subplots(figsize=(7,5))

pos = 0 # Modificate according to the vector GOI
curr_GOI = GOI[pos]


# Points
ax66.plot(frag_Stat['IM_bin'], 1-frag_Stat['Zi - j = ' + str(curr_GOI)]/frag_Stat['N'], mec= 'black', mfc = 'white', 
          marker = 'o', linestyle='', markersize = 7, label = 'Observations')

# Curves
ax66.plot(data_plot_Stat['IM'], 1-data_plot_Stat['j = ' + str(curr_GOI)], color = 'black', linestyle = '-',
          lw = 3, label = 'Fitted Fragility Function')

ax66.set_xlim(lim_inf, lim_sup)
ax66.set_xlabel('GPA', size = 12)
ax66.set_ylabel('P(CG < ' + str(curr_GOI) + ')', size = 12)
ax66.set_ylim(0, 1)
ax66.set_yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
ax66.tick_params(axis='both', labelsize=11) 

ax66.grid(which="both")
ax66.legend(fontsize=12)

########################################
# Crear una figura y un conjunto de subgráficos
fig, axs = plt.subplots(1, 3, figsize=(14, 4))  # 1 fila, 3 columnas

##
# Graficar en cada subgráfico
# Inputs for Curves
pos = 0 # Modificate according to the vector GOI
curr_GOI = GOI[pos]

# Points
axs[0].plot(frag_Stat['IM_bin'], 1-frag_Stat['Zi - j = ' + str(curr_GOI)]/frag_Stat['N'], mec= 'black', mfc = 'white', 
          marker = 'o', linestyle='', markersize = 5, label = 'Observations of Statics')

axs[0].plot(frag_SolMech['IM_bin'], 1-frag_SolMech['Zi - j = ' + str(curr_GOI)]/frag_SolMech['N'], mec= 'gray', mfc = 'white', 
          marker = 'o', linestyle='', markersize = 5, label = 'Observations of Solid Mechanics')

# Curves
axs[0].plot(data_plot_Stat['IM'], 1-data_plot_Stat['j = ' + str(curr_GOI)], color = 'black', linestyle = '-',
        lw = 3, label = 'Fragility Curve - Statics')

axs[0].plot(data_plot_SolMech['IM'], 1-data_plot_SolMech['j = ' + str(curr_GOI)], color = 'gray', linestyle = '--',
        lw = 3, label = 'Fragility Curve - Solid Mechanics')


axs[0].set_xlim(lim_inf, lim_sup)
axs[0].set_ylim(0, 1.05)
axs[0].set_xlabel('GPA', size = 12)
axs[0].set_ylabel('P(CG < ' + str(curr_GOI) + ')', size = 12)
axs[0].set_yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
axs[0].tick_params(axis='both', labelsize=11) 

axs[0].grid(which="both")
axs[0].legend(fontsize=8)

##
# Graficar en cada subgráfico
# Inputs for Curves
pos = 1 # Modificate according to the vector GOI
curr_GOI = GOI[pos]

# Points
axs[1].plot(frag_Stat['IM_bin'], frag_Stat['Zi - j = ' + str(curr_GOI)]/frag_Stat['N'], mec= 'black', mfc = 'white', 
          marker = 'o', linestyle='', markersize = 5, label = 'Observations')
# Curves
axs[1].plot(data_plot_Stat['IM'], data_plot_Stat['j = ' + str(curr_GOI)], color = 'black', linestyle = '-',
        lw = 3, label = 'Statics - P(CG >= 3.5)')

pos = 2 # Modificate according to the vector GOI
curr_GOI = GOI[pos]
axs[1].plot(data_plot_Stat['IM'], data_plot_Stat['j = ' + str(curr_GOI)], color = 'gray', linestyle = '--',
        lw = 3, label = 'Statics - P(CG >= 4.0)')

axs[1].set_xlim(lim_inf, lim_sup)
axs[1].set_ylim(0, 1.05)
axs[1].set_xlabel('GPA', size = 12)
axs[1].set_ylabel('Probability', size = 12)
axs[1].set_yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
axs[1].tick_params(axis='both', labelsize=11) 

axs[1].grid(which="both")
axs[1].legend(fontsize=8)

##
# Graficar en cada subgráfico
# Inputs for Curves
pos = 1 # Modificate according to the vector GOI
curr_GOI = GOI[pos]

# Points
axs[2].plot(frag_SolMech['IM_bin'], frag_SolMech['Zi - j = ' + str(curr_GOI)]/frag_SolMech['N'], mec= 'black', mfc = 'white', 
          marker = 'o', linestyle='', markersize = 5, label = 'Observations')
# Curves
axs[2].plot(data_plot_SolMech['IM'], data_plot_SolMech['j = ' + str(curr_GOI)], color = 'black', linestyle = '-',
        lw = 3, label = 'Solid Mechanics - P(CG >= 3.5)')

pos = 2 # Modificate according to the vector GOI
curr_GOI = GOI[pos]
axs[2].plot(data_plot_SolMech['IM'], data_plot_SolMech['j = ' + str(curr_GOI)], color = 'gray', linestyle = '--',
        lw = 3, label = 'Solid Mechanics - P(CG >= 4.0)')

axs[2].set_xlim(lim_inf, lim_sup)
axs[2].set_ylim(0, 1.05)
axs[2].set_xlabel('GPA', size = 12)
axs[2].set_ylabel('Probability', size = 12)
axs[2].set_yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
axs[2].tick_params(axis='both', labelsize=11) 

axs[2].grid(which="both")
axs[2].legend(fontsize=8)


