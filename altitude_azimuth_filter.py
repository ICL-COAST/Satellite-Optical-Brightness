import numpy as np
import pandas as pd

def satellite_to_observer_frame(i_xyz, o_xyz):
    # Normalize input vectors
    i_xyz = i_xyz / np.linalg.norm(i_xyz)
    o_xyz = o_xyz / np.linalg.norm(o_xyz)
    
    # Calculate z_s (points to geocenter)
    z_s = -o_xyz
    
    # Calculate y_s (handle parallel case)
    cross_product = np.cross(z_s, i_xyz)
    cross_norm = np.linalg.norm(cross_product)
    if cross_norm < 1e-10:
        y_s = np.array([0.0, 1.0, 0.0])
        y_s = y_s - np.dot(y_s, z_s) * z_s
        if np.linalg.norm(y_s) < 1e-10:
            y_s = np.array([1.0, 0.0, 0.0])
    else:
        y_s = cross_product / cross_norm
    
    # Calculate x_s (right-handed system)
    x_s = np.cross(y_s, z_s)
    x_s = x_s / np.linalg.norm(x_s)
    
    # Construct transformation matrix
    T = np.vstack([x_s, y_s, z_s]).T
    
    # Vector transformations
    v_sun_observer = T @ i_xyz
    v_sat_observer = T @ (-o_xyz)
    
    # Calculate altitude and azimuth
    def xyz_to_alt_az(v):
        x, y, z = v
        azimuth = np.arctan2(y, x) % (2 * np.pi)
        altitude = np.arcsin(z / np.linalg.norm(v))
        return np.degrees(altitude), np.degrees(azimuth)
    
    sun_alt, sun_az = xyz_to_alt_az(v_sun_observer)
    sat_alt, sat_az = xyz_to_alt_az(v_sat_observer)
    
    return sun_alt, sun_az, sat_alt, sat_az

# Load data
file_path = r"C:...\NewCode\filtered_angle_results.csv"
data = pd.read_csv(file_path)

# Process data
results = []
for _, row in data.iterrows():
    i_xyz = np.array([row['i_x'], row['i_y'], row['i_z']])
    o_xyz = np.array([row['o_x'], row['o_y'], row['o_z']])
    sun_alt, sun_az, sat_alt, sat_az = satellite_to_observer_frame(i_xyz, o_xyz)
    
    results.append({
        'sun_alt': sun_alt,
        'sun_az': sun_az,
        'sat_alt': sat_alt,
        'sat_az': sat_az,
        'phase_angle': row['phase_angle'],
        'A_eff_SA': row['A_eff_SA'],
        'A_eff_chassis': row['A_eff_chassis']
    })

# Convert to DataFrame and filter
results_df = pd.DataFrame(results)
sun_alt_condition = (results_df['sun_alt'] > -30) & (results_df['sun_alt'] < -10)
sat_alt_condition = (results_df['sat_alt'] > 20) & (results_df['sat_alt'] < 90)
filtered_df = results_df[sun_alt_condition & sat_alt_condition]
'''sun_alt_condition =  (results_df['sun_alt'] < -10)
sat_alt_condition = (results_df['sat_alt'] > 20) 
filtered_df = results_df[sun_alt_condition & sat_alt_condition]'''

# Save filtered results
output_path = r'...\NewCode\filtered_observer_frame_results.csv'
filtered_df.to_csv(output_path, index=False)
print(f"Conversion completed. Filtered results saved  records matching criteria).")