import pandas as pd
import numpy as np
from astropy.time import Time
import astropy.coordinates
import lumos.conversions
import lumos.calculator
from satellite_models.starlink_v1p5 import Surface
from lumos.brdf.library import BINOMIAL, PHONG

# Constants
OBSERVER_LOCATION = astropy.coordinates.EarthLocation(lat=32.4434, lon=-110.7881)
SATELLITE_HEIGHT = 550 * 1000  # Convert km to meters
SAT_AZ = 10  # Fixed satellite azimuth angle
SUN_AZ = 180  # Fixed sun azimuth angle

# Read input data
input_path = r"C:\Users\27549\Desktop\course_file\presonal_project\Satellite_Optical_Brightness_MSc_Project\altitudechange\effective_area_3_new.csv"
output_path = r"C:\Users\27549\Desktop\course_file\presonal_project\Satellite_Optical_Brightness_MSc_Project\altitudechange\abmag_3_new.csv"
df = pd.read_csv(input_path)

def prepare_surfaces(sa_coeff, chassis_coeff):
    """
    Prepare BRDF surfaces with effective area coefficients applied, using actual Starlink v1.5 BRDF models.
    
    Args:
        sa_coeff: Solar array effective area coefficient (0-1)
        chassis_coeff: Chassis effective area coefficient (0-1)
    
    Returns:
        Tuple of (adjusted_surfaces, original_surfaces) where:
        - adjusted_surfaces: List of Surface objects with adjusted areas
        - original_surfaces: List of Surface objects with base areas
    """
    # Base areas from Starlink v1.5 specifications
    BASE_SA_AREA = 22.68  # m² (solar array)
    BASE_CHASSIS_AREA = 3.65  # m² (chassis)
    
    # Apply effective area coefficients for adjusted surfaces
    solar_array_area = BASE_SA_AREA * sa_coeff  
    chassis_area = BASE_CHASSIS_AREA * chassis_coeff

    # Normal vectors for Starlink v1.5
    chassis_normal = np.array([0.353553, 0.353553, -0.866025])  # 更新后的底盘法向量
    solar_array_normal = np.array([0.933013, -0.066987, 0.353553])  # 更新后的太阳能电池板法向量
    
    # Lab-measured BRDF parameters for chassis (from Scatterworks measurements)
    B_chassis = np.array([[3.34, -98.085]])
    C_chassis = np.array([[-999.999, 867.538, 1000., 1000., -731.248, 618.552, 
                          -294.054, 269.248, -144.853, 75.196]])
    lab_chassis_brdf = BINOMIAL(B_chassis, C_chassis, d=3.0, l1=-5)
    
    # Lab-measured BRDF parameters for solar array (from Scatterworks measurements)
    B_solar = np.array([[0.534, -20.409]])
    C_solar = np.array([[-527.765, 1000., -676.579, 430.596, -175.806, 57.879]])
    lab_solar_array_brdf = BINOMIAL(B_solar, C_solar, d=3.0, l1=-3)
    
    # Create both adjusted and original surfaces
    adjusted_surfaces = [
        Surface(chassis_area, chassis_normal, lab_chassis_brdf),
        Surface(solar_array_area, solar_array_normal, lab_solar_array_brdf)
    ]
    
    original_surfaces = [
        Surface(BASE_CHASSIS_AREA, chassis_normal, lab_chassis_brdf),
        Surface(BASE_SA_AREA, solar_array_normal, lab_solar_array_brdf)
    ]
    
    return adjusted_surfaces, original_surfaces

# Calculate AB magnitudes for each observation
ab_mags = []
ab_mags_origin = []
for _, row in df.iterrows():
    phi_1 = row['phi_1 (deg)']  # Satellite altitude angle
    phi_2 = row['phi_2 (deg)']  # Sun altitude angle
    sa_coeff = row['SA_coeff']   # Solar array effective area coefficient
    chassis_coeff = row['Chassis_coeff']  # Chassis effective area coefficient
    
    # Prepare both adjusted and original surfaces
    adjusted_surfaces, original_surfaces = prepare_surfaces(sa_coeff, chassis_coeff)
    
    # Calculate observed intensity for adjusted surfaces
    intensity = lumos.calculator.get_intensity_observer_frame(
        adjusted_surfaces,
        SATELLITE_HEIGHT,
        phi_1,    # Satellite altitude angle (degrees)
        SAT_AZ,   # Satellite azimuth angle (degrees)
        phi_2,    # Sun altitude angle (degrees)
        SUN_AZ,   # Sun azimuth angle (degrees)
        include_earthshine=False
    )
    ab_mag = lumos.conversions.intensity_to_ab_mag(intensity)
    ab_mags.append(ab_mag)
    
    # Calculate observed intensity for original surfaces
    intensity_origin = lumos.calculator.get_intensity_observer_frame(
        original_surfaces,
        SATELLITE_HEIGHT,
        phi_1,
        SAT_AZ,
        phi_2,
        SUN_AZ,
        include_earthshine=False
    )
    ab_mag_origin = lumos.conversions.intensity_to_ab_mag(intensity_origin)
    ab_mags_origin.append(ab_mag_origin)

# Add results to DataFrame while preserving solarAngle column
df['ABmag'] = ab_mags
df['ABmag_Origin'] = ab_mags_origin

# Ensure solarAngle column exists in output (if it existed in input)
output_columns = ['phi_1 (deg)', 'phi_2 (deg)', 'solarAngle (deg)', 
                 'SA_coeff', 'Chassis_coeff', 'ABmag', 'ABmag_Origin']
df = df[output_columns]  # This will keep only specified columns in the output

# Save results
df.to_csv(output_path, index=False)
print(f"Results successfully saved to: {output_path}")