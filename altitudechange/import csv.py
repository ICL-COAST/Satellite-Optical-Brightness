import csv
import os
import math

def calculate_angles(phi1, phi2, R, h):
    """Calculate phi_ob and phi_sun with arcsin modification and acute angle constraint"""
    if phi1 < 90:
        # Calculate sin(phi1 + 90) * R/(R+h), then take arcsin
        sin_phi_ob = math.sin(math.radians(phi1 + 90)) * R / (R + h)
        phi_ob = math.degrees(math.asin(sin_phi_ob))  # Result in [-90°, 90°]
        
        # Ensure phi_ob is acute (though asin already guarantees this)
        phi_ob = max(min(phi_ob, 90), -90)  # Clamp to [-90°, 90°]
        
        phi_sun = phi_ob + phi1 + phi2
    else:
        # Calculate sin(270 - phi1) * R/(R+h), then take arcsin
        sin_phi_ob = math.sin(math.radians(270 - phi1)) * R / (R + h)
        phi_ob = math.degrees(math.asin(sin_phi_ob))  # Result in [-90°, 90°]
        
        # Ensure phi_ob is acute
        phi_ob = max(min(phi_ob, 90), -90)  # Clamp to [-90°, 90°]
        
        phi_sun = -phi2 - phi1 + phi_ob + 90
    
    return phi_ob, phi_sun

def main():
    # Constant parameters
    phi2 = -27  # Example value, can be modified as needed
    R = 6378  # Earth radius in km
    h = 550   # Altitude in km
    
    # Generate phi1 values from 0 to 180 degrees with 5-degree steps
    phi1_values = range(0, 181, 5)
    
    # Prepare data for output
    data = []
    for phi1 in phi1_values:
        phi_ob, phi_sun = calculate_angles(phi1, phi2, R, h)
        solar_angle =  phi1 + phi2  # Calculate solar angle
        data.append([phi1, phi2, phi_ob, phi_sun, solar_angle])
    
    # Define the full output path
    output_dir = r"...\altitudechange"
    os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist
    filename = os.path.join(output_dir, "sampling_results_27.csv")
    
    # Write results to CSV file
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header with new column
        writer.writerow(['phi_1 (deg)', 'phi_2 (deg)', 'phi_ob (deg)', 'phi_sun (deg)', 'solarAngle (deg)'])
        writer.writerows(data)
    
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    main()