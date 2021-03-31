# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 10:37:57 2021

@author: julie
"""


from IPython import get_ipython
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import PySimpleGUI as sg
import math
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics

get_ipython().magic('reset -f')
get_ipython().magic('clear')

File = sg.popup_get_file('Please select the Day1.csv file for analyzing', keep_on_top = True)
Day1 = pd.read_csv(File, header = 0)

File = sg.popup_get_file('Please select the Day2.csv file for analyzing', keep_on_top = True)
Day2 = pd.read_csv(File, header = 0)

#Creating Maximum columns
Day1['Long_jump_max'] = Day1[['Long_jump_1 ', 'Long_jump_2 ', 'Long_jump_3 ']].max(axis=1) 
Day1['L_MVC_max'] = Day1[['L_MVC_1 ', 'L_MVC_2 ', 'L_MVC_3 ']].max(axis=1) 
Day1['R_MVC_max'] = Day1[['R_MVC_1 ', 'R_MVC_2 ', 'R_MVC_3 ']].max(axis=1) 
Day1['T_Test_max'] = Day1[['T_Test_1 ', 'T_Test_2 ']].max(axis=1)

#Creating New Data Frame with Variables of Interest
data = [Day1[['PCode', 'Sex ', 'Weight ', 'Long_jump_max', 'L_MVC_max', 'R_MVC_max', 'T_Test_max', 'Burpee_num']],
            Day2[['Obstacle_time_1 ', 'Obstacle_time_2 ', 'Obstacle_time_3 ', 'VO2 ']]]

data = pd.concat(data, axis=1)
data['Half_Weight'] = data['Weight ']*0.5

#Descriptive Stats for males and females 
Male_stats = pd.DataFrame()
Male_stats['mean'] = data[['Long_jump_max', 'L_MVC_max', 'R_MVC_max', 'T_Test_max',
                           'Burpee_num','Obstacle_time_1 ', 'Obstacle_time_2 ',
                           'Obstacle_time_3 ', 'VO2 ']][data['Sex '] == 1].apply(np.mean, axis = 0)
Male_stats['std'] = data[['Long_jump_max', 'L_MVC_max', 'R_MVC_max', 'T_Test_max',
                           'Burpee_num','Obstacle_time_1 ', 'Obstacle_time_2 ',
                           'Obstacle_time_3 ', 'VO2 ']][data['Sex '] == 1].apply(np.std, axis = 0)
ci95_hi = []
ci95_lo = []

for i in Male_stats.index:
    mean, std = Male_stats.loc[i]
    ci95_hi.append(mean + 1.95*std/math.sqrt(3))
    ci95_lo.append(mean - 1.95*std/math.sqrt(3))

Male_stats['Lower_CI'] = ci95_lo
Male_stats['Upper_CI'] = ci95_hi

Female_stats = pd.DataFrame()
Female_stats['mean'] = data[['Long_jump_max', 'L_MVC_max', 'R_MVC_max', 'T_Test_max',
                           'Burpee_num','Obstacle_time_1 ', 'Obstacle_time_2 ',
                           'Obstacle_time_3 ', 'VO2 ']][data['Sex '] == 0].apply(np.mean, axis = 0)
Female_stats['std'] = data[['Long_jump_max', 'L_MVC_max', 'R_MVC_max', 'T_Test_max',
                           'Burpee_num','Obstacle_time_1 ', 'Obstacle_time_2 ',
                           'Obstacle_time_3 ', 'VO2 ']][data['Sex '] == 0].apply(np.std, axis = 0)

Fci95_hi = []
Fci95_lo = []

for i in Female_stats.index:
    mean, std = Female_stats.loc[i]
    Fci95_hi.append(mean + 1.95*std/math.sqrt(3))
    Fci95_lo.append(mean - 1.95*std/math.sqrt(3))

Female_stats['Lower_CI'] = Fci95_lo
Female_stats['Upper_CI'] = Fci95_hi

# Saving Data
# selectfolder = sg.popup_get_folder('Select a folder to save descriptive stats', keep_on_top = True)

# with pd.ExcelWriter(selectfolder + '/Descriptive Stats.xlsx') as writer:
#     Male_stats.to_excel(writer, sheet_name = 'Male')
#     Female_stats.to_excel(writer, sheet_name = 'Female')

#Criterion Figures
def custom_plot(colname, title, ylabel, color1 = 'darkgreen', color2 = 'darkgoldenrod', *args, **kwargs):
    """Plotting test results for each participant. Males and Females are separated by colour"""
    Fig = plt.figure(figsize = (2,1), dpi=1200)
    ax = data.plot(x = 'PCode', y = colname,
              kind = "bar", title = title,
              legend = False, color=[color1, color1, color1, color2, color2, color2], 
              fontsize = 12, zorder = 2, rot = 45, *args, **kwargs)
    ax.set_xlabel('Participant', fontsize = 12)
    ax.set_ylabel(ylabel, fontsize = 12)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    return(ax)

#Long jump
fig1 = custom_plot('Long_jump_max', 'Long jump', 'Distance (cm)')
plt.axhline(y= 150, color='r', linestyle='-', zorder = 1)

#T-Test
fig2 = custom_plot('T_Test_max', 'T_Test', 'Time (s)')
plt.axhline(y= 9.5, color='darkgreen', linestyle='-', zorder = 1)
plt.axhline(y= 10.5, color='darkgoldenrod', linestyle='-', zorder = 1)

#Burpee
fig3 = custom_plot('Burpee_num', '30 sec Burpee', 'Number')
#Calculating 90th percentile for males and females
male_90 = np.percentile(data['Obstacle_time_1 '][data['Sex '] == 1], 90)
criterion_m = np.min(data['Burpee_num'][data['Sex '] == 1][data['Obstacle_time_1 '] < male_90])
female_90 = np.percentile(data['Obstacle_time_1 '][data['Sex '] == 0], 90)
criterion_f = np.min(data['Burpee_num'][data['Sex '] == 0][data['Obstacle_time_1 '] < female_90])
plt.axhline(y= criterion_m, color='darkgreen', linestyle='-', zorder = 1)
plt.axhline(y= criterion_f, color='darkgoldenrod', linestyle='-', zorder = 1)

#VO2 max
fig4 = custom_plot('VO2 ', 'VO2 max', 'VO2 (mL/kg*min)')
plt.axhline(y= 55.6, color='darkgreen', linestyle='-', zorder = 1)
plt.axhline(y= 47.2, color='darkgoldenrod', linestyle='-', zorder = 1)

#MVC
color1 = 'darkgreen'
color2 = 'darkgoldenrod'
colours = ('tab:red', 'tab:blue', 'tab:orange', 'tab:purple', 'tab:green', 'tab:pink')
fig5, axes = plt.subplots(2, figsize = (8,6), dpi = 300)
data.plot(x = 'PCode', y = 'L_MVC_max', kind = 'bar', title = 'Left MVC',
          legend = False, color = colours, fontsize = 12, ax = axes[0], zorder = 2, rot = 45)
axes[0].hlines(data['Half_Weight'], -1, 6, color= colours, linestyle='-', zorder = 1)
data.plot(x = 'PCode', y = 'R_MVC_max', kind = 'bar', title = 'Right MVC',
          legend = False, color = colours, fontsize = 12, ax = axes[1], zorder = 2, rot = 45)
axes[1].hlines(data['Half_Weight'], -1, 6, color= colours, linestyle='-', zorder = 1)
for ax in axes.flat:
    ax.set_ylabel('Weight (kg)', fontsize = 12)
    ax.set_xlabel('Participant', fontsize = 12)
    ax.set_ylim(0,55)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.title.set_size(12)
for ax in axes.flat:
    ax.label_outer()


#Obstacle Course
fig6, axes = plt.subplots(3, figsize =(8,6), dpi = 300)
fig6.suptitle('Obstacle Course', fontweight = "bold", size = 14)
data.plot(x = 'PCode', y = 'Obstacle_time_1 ', kind = "bar", title = 'Round 1',
          legend = False, color = [color1, color1, color1, color2, color2, color2],
          fontsize = 12, ax = axes[0], zorder = 2, rot = 45)
axes[0].axhline(y= 42.5, color='r', linestyle='-', zorder = 1)
data.plot(x = 'PCode', y = 'Obstacle_time_2 ', kind = "bar", title = 'Round 2',
          legend = False, color = [color1, color1, color1, color2, color2, color2],
          fontsize = 12, ax = axes[1], zorder = 2)
axes[1].axhline(y= 38, color='r', linestyle='-', zorder = 1)
data.plot(x = 'PCode', y = 'Obstacle_time_3 ', kind = "bar", title = 'Round 3',
          legend = False, color = [color1, color1, color1, color2, color2, color2],
          fontsize = 12, ax = axes[2], zorder = 2, rot = 45)
axes[2].axhline(y= 34.4, color='r', linestyle='-', zorder = 1)
for ax in axes.flat:
    ax.set_ylabel('Time (s)', fontsize = 12)
    ax.set_xlabel('Participant', fontsize = 12)
    ax.set_ylim(0,45)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.title.set_size(12)
for ax in axes.flat:
    ax.label_outer()


# selectfolder = sg.popup_get_folder('Select a folder to save all plots', keep_on_top = True)
# fig1.figure.savefig(selectfolder + '/Long jump.png', bbox_inches = 'tight', dpi = 300)
# fig2.figure.savefig(selectfolder + '/T Test.png',  bbox_inches='tight', dpi = 300)
# fig3.figure.savefig(selectfolder + '/Burpee.png', bbox_inches='tight', dpi = 300) 
# fig4.figure.savefig(selectfolder + '/VO2 max.png', bbox_inches = 'tight', dpi = 300)
# fig5.savefig(selectfolder + '/MVC.png',  bbox_inches='tight')
# fig6.savefig(selectfolder + '/Obstacle Course.png', bbox_inches='tight') 

#Linear Regression model for predicting obstacle run times based on binary input from 6 tests

#Setting binary pass/fail for each test
data['LJ_Crit'] = 0
data['TTest_Crit'] = 0
data['Burpee_Crit'] = 0
data['L_MVC_Crit'] = 0
data['R_MVC_Crit'] = 0
data['VO2_Crit'] = 0
for i in range(len(data)):
    if data['Long_jump_max'][i] > 150:
        data['LJ_Crit'][i] = 1
    else:
        data['LJ_Crit'][i] = 0   
    if data['T_Test_max'][i] <= 9.5 and data['Sex '][i] == 1:
        data['TTest_Crit'][i] = 1
    elif data['T_Test_max'][i] <= 10.5 and data['Sex '][i] == 0:
        data['TTest_Crit'][i] = 1
    else:
        data['TTest_Crit'][i] = 0
    if data['Burpee_num'][i] >= criterion_f and data['Sex '][i] == 0:
        data['Burpee_Crit'][i] = 1
    elif data['Burpee_num'][i] >= criterion_m and data['Sex '][i] == 1:
        data['Burpee_Crit'][i] = 1
    else:
        data['Burpee_Crit'][i] = 0
    if data['VO2 '][i] >= 55.6 and data['Sex '][i] == 1:
        data['VO2_Crit'][i] = 1
    elif data['VO2 '][i] >= 47.2 and data['Sex '][i] == 0:
        data['VO2_Crit'][i] = 1
    else:
        data['VO2_Crit'][i] = 0
    if data['L_MVC_max'][i] >= data['Half_Weight'][i]:
        data['L_MVC_Crit'][i] = 1
    else:
        data['L_MVC_Crit'][i] = 0
    if data['R_MVC_max'][i] >= data['Half_Weight'][i]:
        data['R_MVC_Crit'][i] = 1
    else:
        data['R_MVC_Crit'][i] = 0
        
x = data[['LJ_Crit', 'TTest_Crit', 'L_MVC_Crit','R_MVC_Crit', 'Burpee_Crit', 'VO2_Crit']]
y = data['Obstacle_time_1 ']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.1, random_state = 6)
regressor = LinearRegression()
regressor.fit(x_train, y_train)
y_pred = regressor.predict(x_test)
print('y_test:', y_test)
print('y_pred:', y_pred)
print("mae: {:.02f}".format(metrics.mean_absolute_error(y_test, y_pred)))
print("mse: {:.02f}".format(metrics.mean_squared_error(y_test, y_pred)))
print("rmse: {:.02f}".format(np.sqrt(metrics.mean_squared_error(y_test, y_pred))))
print("coef:", np.around(regressor.coef_, 2))
print("intercept: {:.02f}".format(regressor.intercept_))
    
        
        







