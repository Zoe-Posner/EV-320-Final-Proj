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

# CR = Colorado River
file1 = 'DischargeData.csv'
CR_discharge = pd.read_csv(file1)

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

# Initial concentration of phosphorous
C_array = []
for each in range(nodes):
    concentration = random.choice(p_concentration)
    C_array.append(concentration)

C = np.ones(nodes)*C_array


# Supply of phosphorus
p_supply = np.array(river_location['umol/day'].dropna().tolist())
selected_indices = (x >= 1000) & (x <= 3000)
num_elements = np.sum(selected_indices)

s_min = np.min(p_supply)  # Minimum supply value
s_max = np.max(p_supply)  # Maximum supply value

# Generate random supply values for the selected range
random_supply_values = np.random.uniform(s_min, s_max, num_elements)
C[selected_indices] += random_supply_values



### -----RUNNING THE MODEL THROUGH TIME----- ###

totaltime = 100000

fig, ax, = plt.subplots(1, 1, figsize = (11, 5))
ax.plot(x, C, label = 'Initial Concentration', color = 'tab:blue')

time = 0

while time <= totaltime:
    
    # ----CREATING A MATRIX----

    random_velocity = random.choice(velocities)  # Random velocity selection at each time step or spatial interval
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

ax.plot(x, C, label = 'Concentration After X', color = 'tab:red', linewidth = 2)
ax.set_xlabel('Distance (m)')
ax.set_ylabel('Concentration (u/M)')
ax.set_title('Phosphorus Concentration Over Time', fontsize = 14)
ax.grid(True)
fig.legend(loc = 'upper right', fontsize=12)










