import numpy as np
import pandas as pd

def fibonacci_sphere_sampling(samples=1000):
    """Generate evenly distributed points on a sphere using Fibonacci sampling."""
    points = []
    phi = np.pi * (3. - np.sqrt(5.))  # Golden angle in radians
    
    for i in range(samples):
        y = 1 - (i / float(samples - 1)) * 2  # y goes from 1 to -1
        radius = np.sqrt(1 - y * y)  # radius at y
        
        theta = phi * i  # Golden angle increment
        
        x = np.cos(theta) * radius
        z = np.sin(theta) * radius
        
        points.append([x, y, z])
    
    return np.array(points)

# Generate points on the sphere
samples = 1000
points = fibonacci_sphere_sampling(samples)

# Create all possible pairs where:
# - First point (i) can be any point on the sphere
# - Second point (o) must be in lower hemisphere (z < 0)
pairs = []
for i in range(samples):
    for o in range(samples):
        if points[o][2] < 0:  # Check if o is in lower hemisphere (z < 0)
            pairs.append((points[i], points[o]))

# Convert to numpy array for easier handling
pairs_array = np.array(pairs)

# Create a DataFrame to store the pairs
df_pairs = pd.DataFrame({
    'i_x': pairs_array[:, 0, 0],
    'i_y': pairs_array[:, 0, 1],
    'i_z': pairs_array[:, 0, 2],
    'o_x': pairs_array[:, 1, 0],
    'o_y': pairs_array[:, 1, 1],
    'o_z': pairs_array[:, 1, 2]
})

# Save to CSV
output_path = r'C:...\NewCode\viewing_sphere_pairs.csv'
df_pairs.to_csv(output_path, index=False)
df_pairs.to_csv(output_path, index=False)
print(f"Saved {len(pairs)} point pairs to {output_path}")
print(f"First point is arbitrary, second point is restricted to lower hemisphere (z < 0)")