#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 09:57:21 2024

@author: zoeposner
"""

import numpy as np
import matplotlib.pyplot as plt
import random as random
import pandas as pd 



### -----GETTING VELOCITY DATA----- ###

file1 = 'DischargeData.csv'
CR_discharge = pd.read_csv(file1) # CR = Colorado River
discharge = CR_discharge['Discharge']

# Converting Discharge ft^3/s (cubic ft per second) to m^3/s (cubic meters per second)
discharge *= 0.0283168 # conversion rate, now discharge represented as m^3/s (cubic meters per second)

# Velocity = Discharge / Cross-Sectional Area
# Cross Sectional Area of Colorado River in Grand Canyon is 91m by 12m
velocity = discharge  / (91 * 12)
velocities = []

for i in range(30):
    random_velocity = random.choice(velocity)
    velocities.append(random_velocity)



### -----SETTING UP  MODEL OVER SPACE, DISTANCE (M)----- ###
dx = 1000
x = np.arange(0,446000,dx) # over 446km - distance of Colorado River in Grand Canyon
nodes = len(x)
dt = dx/np.max(velocity) 



### -----GETTING PHOSPHOROUS DATA NEAR LAKE POWELL----- ###
file2 = 'PhosphateData.csv'
CR_phosphate = pd.read_csv(file2)

# Filter for rows where 'Sediment' is 'Glen'
river_location = CR_phosphate[CR_phosphate['Sediment'] == 'Glen']
initial_concentration  = river_location['uM'].mean()

# Extract uM values for the filtered rows
p_concentration = river_location['uM'].dropna().tolist()  # Convert to a list and drop NaNs
p_concentration = [x for x in p_concentration if x > initial_concentration] 

# Supply of phosphorus
p_supply = np.array(river_location['nanomol/day'].dropna().tolist())
selected_indices = (x >= 1000) & (x <= 3000)
num_elements = np.sum(selected_indices)

s_min = np.min(p_supply)  # Minimum supply value
s_max = np.max(p_supply)  # Maximum supply value



### -----SETTING UP INITIAL PHOSPHORUS CONCENTRATION----- ###

# Parameters for initial concentration fluctuation
C_max = max(p_concentration)  # Max concentration for upstream levels
C_min = 0.03 # Min concentration for downstream levels
fluctuation_max = 2 # Max fluctuation upstream
fluctuation_min = 0.03 # Min fluctuation downstream

# Linear decay for mean concentration values
C_means = C_max * (1 - x / np.max(x)) + C_min

# Exponential decay for fluctuations
decay = 0.000004
fluctuations = fluctuation_max * np.exp(-decay * x) + fluctuation_min

# Creates initial concentration array
"""
Utilized linear decay and exponential decay functions here to make my plot more accurate to how phosphorus levels decrease over time
"""
C = np.array([np.random.normal(mean, fluc), for mean, fluc in zip(C_means, fluctuations)])

# Generate random supply values for the selected range
random_supply_values = np.random.uniform(s_min, s_max, num_elements)
C[selected_indices] += random_supply_values



### -----RUNNING THE MODEL THROUGH TIME----- ###

totaltime = 172800 # 48 hours in seconds

fig, ax, = plt.subplots(1, 1, figsize = (11, 5))
ax.plot(x / 1000, C, label = 'Initial Concentration', color = 'tab:blue')

time = 0

while time <= totaltime:
    
    # Creating A Matrix

    random_velocity = random.choice(velocities)  # Random velocity selection at each time step
    courant = dt * random_velocity / dx  # Recalculate courant for the new velocity  
    
    # Update matrix A with the new velocity and new courant
    A = np.zeros((nodes, nodes))
    for i in range(nodes - 1):
        A[i, i] = 1 - courant
        A[i, i - 1] = courant
    A[0, 0] = 1
    
    newC = np.dot(A, C)
    C[:] = newC * 1
    time += dt

ax.plot(x / 1000, C, label = 'Concentration After 48 Hours', color = 'tab:red', linewidth = 2.5)
ax.set_xlabel('Distance Throughout Grand Canyon (km)')
ax.set_ylabel('Concentration (u/M)')
ax.set_title('Phosphorus Concentration in the Colorado River Over Time', fontsize = 14)
ax.grid(True)
fig.legend(loc = 'upper right', fontsize=9)










