import pandas as pd
import numpy as np

def calculate_angle_with_neg_z(data):
    """
    Calculate the angle between each vector (o_x, o_y, o_z) and the negative z-axis (0,0,-1)
    
    Args:
        data: DataFrame containing vector components o_x, o_y, o_z
        
    Returns:
        Series containing angles in degrees
    """
    # Calculate angle using arccos(-o_z/||o||)
    return np.degrees(
        np.arccos(
            -data['o_z'] / np.sqrt(data['o_x']**2 + data['o_y']**2 + data['o_z']**2)
        ))

def main():
    """
    Main function to process vector data and filter by angle with negative z-axis
    """
    # 1. Read input data
    input_path = r'C:...\NewCode\results.csv'
    data = pd.read_csv(input_path)
    
    # 2. Calculate angle with negative z-axis (0,0,-1)
    data['angle_with_z'] = calculate_angle_with_neg_z(data)
    
    # 3. Filter rows where angle < 66 degrees
    filtered_data = data[data['angle_with_z'] < 66]
    
    # 4. Save results to new CSV file
    output_path = r'C:...\NewCode\filtered_angle_results.csv'
    filtered_data.to_csv(output_path, index=False)
    
    print(f"Processing complete. Results saved to: {output_path}")
    print(f"Number of rows matching criteria: {len(filtered_data)}")

if __name__ == "__main__":
    main()