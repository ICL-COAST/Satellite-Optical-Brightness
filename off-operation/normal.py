import numpy as np
import pandas as pd
import math

def rotation_matrix(axis, theta):
    """
    Return rotation matrix for rotation around axis by theta radians
    Using Rodrigues' rotation formula
    """
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

def rotate_vector(vector, axis, angle_deg):
    """
    Rotate a vector around an axis by specified angle (degrees)
    """
    angle_rad = np.radians(angle_deg)
    rot_mat = rotation_matrix(axis, angle_rad)
    return np.dot(rot_mat, vector)

def main():
    # Initial vectors
    vector1 = np.array([0, 0, -1])
    vector2 = np.array([0, 1, 0])

    # Rotation axis
    rotation_axis = np.array([1, -1, 0])

    # Record rotation angles and results
    angles = list(range(0, 361, 5))  # From 0° to 360°, every 30°
    results = []

    for angle in angles:
        # Rotate vectors
        rotated_v1 = rotate_vector(vector1, rotation_axis, angle)
        rotated_v2 = rotate_vector(vector2, rotation_axis, angle)
        
        # Record results
        results.append({
            'rotation_angle_deg': angle,
            'vector1_x': rotated_v1[0],
            'vector1_y': rotated_v1[1],
            'vector1_z': rotated_v1[2],
            'vector2_x': rotated_v2[0],
            'vector2_y': rotated_v2[1],
            'vector2_z': rotated_v2[2]
        })

    # Create DataFrame and export to CSV
    df = pd.DataFrame(results)
    df.to_csv('rotated_vectors_record.csv', index=False, float_format='%.6f')

    print("Data exported to 'rotated_vectors_record_new.csv'")
    print("\nPreview of first few rows:")
    print(df.head())

    # Additional: Print some sample results for verification
    print("\nSample results:")
    for i in range(0, len(results), 4):  # Print every 4th result (since there are fewer angles now)
        result = results[i]
        print(f"Angle {result['rotation_angle_deg']}°: "
              f"Vector1 = [{result['vector1_x']:.3f}, {result['vector1_y']:.3f}, {result['vector1_z']:.3f}], "
              f"Vector2 = [{result['vector2_x']:.3f}, {result['vector2_y']:.3f}, {result['vector2_z']:.3f}]")


if __name__ == "__main__":
    main()