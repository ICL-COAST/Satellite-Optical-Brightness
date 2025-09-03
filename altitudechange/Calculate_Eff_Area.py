import pandas as pd
import math
import os

# Constants
H = 8.1  # Height parameter
L = 1.3  # Length parameter

# File paths
input_path = r"...\sampling_results_27.csv"
output_path = r"...\effective_area_27.csv"

def calculate_effective_area(row):
    """
    Calculate effective area coefficients for SA and Chassis based on given conditions
    
    Args:
        row: DataFrame row containing angle values
    
    Returns:
        pd.Series: SA coefficient and Chassis coefficient
    """
    phi1 = row['phi_1 (deg)']
    phi_ob = row['phi_ob (deg)']
    phi_sun = row['phi_sun (deg)']
    
    # Calculate SA effective area coefficient
    if phi1 < 90:
        min_angle = min(phi_ob, phi_sun)
        # Compute 1 - (L/H)*cot(min_angle) where cot(x) = 1/tan(x)
        sa_coeff = 1 - (L / H) * (1 / math.tan(math.radians(min_angle))) if min_angle > 0 else 0
        sa_coeff = max(sa_coeff, 0)  # Ensure non-negative value
    else:
        sa_coeff = 0  # SA coefficient is 0 when phi1 >= 90
    
    # Calculate Chassis effective area coefficient
    chassis_coeff = 0 if phi_sun < 0 else 1  # 0 if phi_sun negative, else 1
    
    return pd.Series([sa_coeff, chassis_coeff])

# Main execution
try:
    # Read input CSV file
    df = pd.read_csv(input_path)
    
    # Rename columns from Greek letters to phi_ naming convention if needed
    column_mapping = {
        'φ1 (deg)': 'phi_1 (deg)',
        'φ2 (deg)': 'phi_2 (deg)',
        'φob (deg)': 'phi_ob (deg)',
        'φsun (deg)': 'phi_sun (deg)',
        'solarAngle (deg)': 'solarAngle (deg)'  # Keep solarAngle as is
    }
    df = df.rename(columns=column_mapping)
    
    # Verify required columns exist
    required_columns = ['phi_1 (deg)', 'phi_2 (deg)', 'phi_ob (deg)', 'phi_sun (deg)', 'solarAngle (deg)']
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        raise ValueError(f"Required columns missing in CSV file: {missing}")
    
    # Calculate effective area coefficients
    df[['SA_coeff', 'Chassis_coeff']] = df.apply(calculate_effective_area, axis=1)
    
    # Reorder columns for better readability
    output_columns = ['phi_1 (deg)', 'phi_2 (deg)', 'phi_ob (deg)', 'phi_sun (deg)', 
                     'solarAngle (deg)', 'SA_coeff', 'Chassis_coeff']
    df = df[output_columns]
    
    # Save results to new CSV file
    df.to_csv(output_path, index=False)
    print(f"Results successfully saved to: {output_path}")
    
except FileNotFoundError:
    print(f"Error: Input file not found at {input_path}")
except pd.errors.EmptyDataError:
    print("Error: The input file is empty")
except Exception as e:
    print(f"An error occurred during processing: {str(e)}")