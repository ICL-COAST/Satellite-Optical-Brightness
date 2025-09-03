# Imports
import pandas as pd
import numpy as np

import lumos.calculator
import lumos.conversions

# Your existing satellite model (includes BRDF definitions)
import satellite_models.starlink_v1p5 as starlink_v1p5
from lumos.geometry import Surface  # Need to construct a per-row list of Surface objects

# ---------------- Fixed geometry parameters ----------------
satellite_heights = 1000 * 550  # m

# Angles (functions usually require radians; here we convert to radians.
# If your function uses degrees, remove np.deg2rad)
sat_alt = np.deg2rad(80)    # Satellite elevation 80°
sat_az  = np.deg2rad(10)    # Satellite azimuth 10°
sun_alt = np.deg2rad(-3)    # Sun elevation -3°
sun_az  = np.deg2rad(-180)  # Sun azimuth -180°

# ---------------- Constant areas (scaled by row-specific weights) ----------------
chassis_area = 3.65      # m^2
solar_array_area = 22.68 # m^2

# ---------------- Read CSV ----------------
csv_path = r"C:\Users\27549\Desktop\course_file\presonal_project\Satellite_Optical_Brightness_MSc_Project\codeinpython\off-operation\rotated_vectors_record_area.csv"
df = pd.read_csv(csv_path)

# Expected columns: vector1_x, vector1_y, vector1_z, vector2_x, vector2_y, vector2_z, Chassis, SA
required_cols = [
    "vector1_x", "vector1_y", "vector1_z",
    "vector2_x", "vector2_y", "vector2_z",
    "Chassis", "SA"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"CSV missing required columns: {missing}")

# ---------------- Get BRDF (predefined lab BRDFs from the module) ----------------
# Some versions expose variables as lab_chassis_brdf / lab_solar_array_brdf.
# If unavailable, extract brdf from SURFACES_LAB_BRDFS.
try:
    lab_chassis_brdf = starlink_v1p5.lab_chassis_brdf
    lab_solar_array_brdf = starlink_v1p5.lab_solar_array_brdf
except AttributeError:
    lab_chassis_brdf = starlink_v1p5.SURFACES_LAB_BRDFS[0].brdf
    lab_solar_array_brdf = starlink_v1p5.SURFACES_LAB_BRDFS[1].brdf

# ---------------- Utility function: normalize vector, avoid zero vector ----------------
def unit_vector(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    if n == 0:
        # If zero vector encountered, return a safe default to avoid numerical crash
        return np.array([0.0, 0.0, 1.0])
    return v / n

# ---------------- Row-wise calculation ----------------
N = len(df)
intensities = np.zeros(N, dtype=float)
magnitudes = np.zeros(N, dtype=float)

for i, row in df.iterrows():
    # 1) Row-specific surface normals (read from CSV and normalized)
    chassis_normal_row = unit_vector([row["vector1_x"], row["vector1_y"], row["vector1_z"]])
    solar_array_normal_row = unit_vector([row["vector2_x"], row["vector2_y"], row["vector2_z"]])

    # 2) Row-specific effective areas (scaled by weight columns)
    chassis_area_eff = chassis_area * float(row["Chassis"])
    solar_array_area_eff = solar_array_area * float(row["SA"])

    # 3) Construct row-specific SURFACES list
    surfaces_row = [
        Surface(chassis_area_eff, chassis_normal_row, lab_chassis_brdf),
        Surface(solar_array_area_eff, solar_array_normal_row, lab_solar_array_brdf),
    ]

    # 4) Call brightness calculation (exclude Earthshine)
    intensities[i] = lumos.calculator.get_intensity_observer_frame(
        surfaces_row,
        satellite_heights,  # sat_h
        sat_alt, sat_az,
        sun_alt, sun_az,
        include_earthshine=False
    )

# 5) Convert to AB magnitudes (using lumos.conversions)
magnitudes = lumos.conversions.intensity_to_ab_mag(intensities)

# (Optional) Write results back to df for export or analysis
df["intensity"] = intensities
df["ab_magnitude"] = magnitudes

# (Optional) Save results
out_csv = r"C:\Users\27549\Desktop\course_file\presonal_project\Satellite_Optical_Brightness_MSc_Project\codeinpython\off-operation\out_with_brightness.csv"
df.to_csv(out_csv, index=False)
print("Saved:", out_csv)
