import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
import astropy.coordinates
import lumos.conversions
import lumos.calculator
from satellite_models.starlink_v1p5 import Surface

# Constants
OBSERVER_LOCATION = astropy.coordinates.EarthLocation(lat=32.4434, lon=-110.7881)
SATELLITE_HEIGHT = 550 * 1000  # Convert km to meters
SAT_AZ = 0  # Fixed satellite azimuth angle
SUN_AZ = 180  # Fixed sun azimuth angle

# Read input data
input_path = r"...\effective_area_results.csv"
df = pd.read_csv(input_path)

def prepare_surfaces(sa_coeff, chassis_coeff):
    """
    Prepare BRDF surfaces with effective area coefficients applied
    
    Args:
        sa_coeff: Solar array effective area coefficient (0-1)
        chassis_coeff: Chassis effective area coefficient (0-1)
    
    Returns:
        List of Surface objects with adjusted areas
    """
    # Base areas (modify these with actual values)
    BASE_SA_AREA = 10.0  # m²
    BASE_CHASSIS_AREA = 5.0  # m²
    
    # Apply effective area coefficients
    solar_array_area = BASE_SA_AREA * sa_coeff  
    chassis_area = BASE_CHASSIS_AREA * chassis_coeff
    
    # Normal vectors (modify if needed)
    solar_array_normal = np.array([0, 0, 1])  # Z-axis normal
    chassis_normal = np.array([0, 1, 0])     # Y-axis normal
    
    # Placeholder BRDF functions - replace with actual implementations
    def lab_solar_array_brdf(theta_i, theta_o, phi_i, phi_o):
        """Placeholder for solar array BRDF function"""
        return 0.5  # Example isotropic BRDF value
    
    def lab_chassis_brdf(theta_i, theta_o, phi_i, phi_o):
        """Placeholder for chassis BRDF function"""
        return 0.3  # Example isotropic BRDF value
    
    return [
        Surface(chassis_area, chassis_normal, lab_chassis_brdf),
        Surface(solar_array_area, solar_array_normal, lab_solar_array_brdf)
    ]

# Calculate AB magnitude for each observation
ab_mags = []
for _, row in df.iterrows():
    phi_1 = row['phi_1 (deg)']  # Satellite altitude angle
    phi_2 = row['phi_2 (deg)']  # Sun altitude angle
    sa_coeff = row['SA_coeff']   # Solar array effective area coefficient
    chassis_coeff = row['Chassis_coeff']  # Chassis effective area coefficient
    
    # Prepare surfaces with effective area coefficients applied
    surfaces = prepare_surfaces(sa_coeff, chassis_coeff)
    
    # Calculate observed intensity
    intensity = lumos.calculator.get_intensity_observer_frame(
        surfaces,
        SATELLITE_HEIGHT,
        phi_1,    # Satellite altitude angle (degrees)
        SAT_AZ,   # Satellite azimuth angle (degrees)
        phi_2,    # Sun altitude angle (degrees)
        SUN_AZ,   # Sun azimuth angle (degrees)
        include_earthshine=False
    )
    
    # Convert intensity to AB magnitude
    ab_mag = lumos.conversions.intensity_to_ab_mag(intensity)
    ab_mags.append(ab_mag)

# Add results to DataFrame
df['ABmag'] = ab_mags

# Plot AB magnitude vs phi_1 (satellite altitude angle)
plt.figure(figsize=(10, 6))
plt.plot(df['phi_1 (deg)'], df['ABmag'], 'b-', linewidth=2, label='AB Magnitude')
plt.xlabel('Satellite Altitude Angle (phi_1) [deg]', fontsize=12)
plt.ylabel('AB Magnitude', fontsize=12)
plt.title('Satellite Brightness vs Observation Angle', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()

# Save results
output_path = r"...\abmag_results.csv"
df.to_csv(output_path, index=False)
print(f"Results successfully saved to: {output_path}")