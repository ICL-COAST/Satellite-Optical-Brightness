import pandas as pd
import random

# File paths
input_path = r'...\NewCode\observer_frame_results.csv'
output_path = r'...\NewCode\observer_frame_results_night.csv'

# Read the original CSV file
df = pd.read_csv(input_path)

# Filter rows where sun_alt is negative
negative_sun_alt_df = df[df['sun_alt'] < 0]

# Calculate sample size (approximately 4% of remaining rows)
sample_size = len(negative_sun_alt_df) // 25

# Random sampling with fixed random_state for reproducibility
# Remove random_state parameter if you want different samples each time
sampled_df = negative_sun_alt_df.sample(n=sample_size, random_state=42)

# Save sampled data to new CSV file
sampled_df.to_csv(output_path, index=False)


print(f"Original dataset had {len(df)} rows, {len(negative_sun_alt_df)} had negative sun_alt")
print(f"Successfully sampled {sample_size} rows (~10%) from negative sun_alt data and saved to: {output_path}")