import pandas as pd
import matplotlib.pyplot as plt
import os

# Set the directory path
data_dir = r"...\altitudechange"

# List of files to import
file_names = ['abmag_27.csv', 'abmag_21.csv', 'abmag_15.csv', 'abmag_9.csv', 'abmag_3.csv']
altitudes = [27, 21, 15, 9, 3]  # Corresponding altitude values for legend

# Create figure
plt.figure(figsize=(10, 6))
ax = plt.gca()

# Define a color palette for different curves
colors = ['b', 'g', 'r', 'c', 'm']

# Read and plot each file
for file, alt, color in zip(file_names, altitudes, colors):
    file_path = os.path.join(data_dir, file)
    df = pd.read_csv(file_path)
    
    # Plot ABmag (solid line) vs phi_1 with altitude-specific label
    plt.plot(df['phi_1 (deg)'], df['ABmag'], 
             color=color, 
             linewidth=2,
             linestyle='--',
             alpha=0.6,
             label=f' -{alt}° (Effective Area)')
    
    # Plot ABmag_Origin (dashed line) with same color
    plt.plot(df['phi_1 (deg)'], df['ABmag_Origin'], 
             color=color, 
             linewidth=2,
             linestyle='-',
             alpha=0.4,
             label=f' -{alt}° (Original Area)')

# Configure y-axis (inverted magnitude scale)
ax.set_ylim(8.2, 3)  # Bright (3) at top, faint (10) at bottom
ax.set_yticks([ 8, 7, 6, 5, 4, 3])  # Specific magnitude ticks
ax.set_xlim(10, 170)

# Axis labels and title
plt.xlabel('Included Angle θ (°)', fontsize=12)
plt.ylabel('AB Magnitude', fontsize=12)
plt.title('Satellite Brightness', fontsize=14)

# Add grid and legend
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=8, title='Sun Altitude:', bbox_to_anchor=(0.05, 1), loc='upper left')
plt.tight_layout()
plt.show()