import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

plt.rcParams['axes.unicode_minus'] = False    

# Read Excel file - explicitly specify openpyxl engine
file_path = r'C:...\NewCode\off-operation\Toplot1.xlsx'

try:
    df = pd.read_excel(file_path, engine='openpyxl')
    print("File read successfully!")
    print(f"Data shape: {df.shape}")
    print("Columns:", df.columns.tolist())
    
except Exception as e:
    print(f"Error reading file: {e}")
    # Check if file exists
    import os
    if not os.path.exists(file_path):
        print("File does not exist, please check the path")
    exit()

# Extract required columns
try:
    rotation_angle = df['rotation_angle_deg']
    chassis = df['Chassis']
    abmag_eff = df['Abmag_eff']
    abmag_origin = df['Abmag_origin']
    print("Data extracted successfully!")
    
except KeyError as e:
    print(f"Column name error: {e}")
    print("Available columns:", df.columns.tolist())
    exit()

# Create figure and main axis
fig, ax1 = plt.subplots(figsize=(8, 6))

# Set x-axis range: 180 to 265
ax1.set_xlim(180, 265)

# Plot Abmag_eff and Abmag_origin curves (left Y-axis), store line objects
line1, = ax1.plot(rotation_angle, abmag_eff, 'b-', linewidth=2)
line2, = ax1.plot(rotation_angle, abmag_origin, 'r-', linewidth=2)

# Configure left Y-axis
ax1.set_xlabel('Rotation Angle (deg)', fontsize=16)
ax1.set_ylabel('AB magnitude', fontsize=16)
ax1.set_ylim(12, 4)  # 12 at bottom, 4 at top
ax1.set_yticks([12, 11, 10, 9, 8, 7, 6, 5, 4])  # Set ticks
ax1.grid(True, alpha=0.3)

# Create right Y-axis for Chassis coefficient
ax2 = ax1.twinx()

# Plot Chassis curve and fill the area below, store line object
line3, = ax2.plot(rotation_angle, chassis, 'g-', alpha=0.8, linewidth=1)
# Fill the area under the curve
fill = ax2.fill_between(rotation_angle, chassis, 0, color='green', alpha=0.2)

# Configure right Y-axis
ax2.set_ylabel('Chassis coefficient', fontsize=16)
ax2.set_ylim(0, 1)

# Create a unified legend including all lines and filled area
# Create a legend handle for the filled area
fill_patch = Patch(facecolor='green', alpha=0.2, label='Chassis coefficient')

blank_patch = Patch(facecolor='none', edgecolor='none', label='Solar Array coefficient = 1')

lines = [line1, line2, fill_patch, blank_patch]
labels = ['Effective Area', 'Original Area', 'Chassis coefficient', 'Solar Array coefficient = 1']
ax1.legend(lines, labels, loc='upper left', fontsize=12)

# Add title
plt.title('Optical Brightness Analysis', fontsize=24)

# Adjust layout
plt.tight_layout()

# Show figure
plt.show()
