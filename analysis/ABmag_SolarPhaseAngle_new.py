import math
import pandas as pd
from shapely.geometry import Polygon
from shapely.ops import unary_union


class ShadowCalculator:
    """A unified calculator for shadow properties and non-shadow areas"""
    
    CONFIG = {'L': 1.3, 'D': 2.8, 'H': 8.1}  # Default configuration
    
    def __init__(self, L=None, D=None, H=None):
        """Initialize with custom dimensions or use defaults"""
        self.L = L if L is not None else self.CONFIG['L']
        self.D = D if D is not None else self.CONFIG['D']
        self.H = H if H is not None else self.CONFIG['H']
        self.A_SA = self.D * self.H  # Solar array initial area
        self.A_chassis = self.L * self.D  # Chassis initial area
    
    def cartesian_to_spherical(self, x, y, z):
        """Convert Cartesian coordinates (x,y,z) to spherical coordinates (phi, theta) in degrees"""
        # Normalize the vector
        norm = math.sqrt(x**2 + y**2 + z**2)
        if norm == 0:
            return 0, 0
        x, y, z = x/norm, y/norm, z/norm
        
        # Calculate phi (elevation angle, 0-360 degrees)
        phi_rad = math.asin(z)  # z = sin(phi)
        phi_deg = math.degrees(phi_rad)
        
        # Determine the correct quadrant for phi
        # Since asin gives results between -90 and 90, we need to adjust
        if x > 0:
            # First or fourth quadrant
            phi_deg = phi_deg % 360
        else:
            # Second or third quadrant
            phi_deg = 180 - phi_deg
        
        # Calculate theta (azimuth angle, -90 to 90 degrees)
        # y = cos(phi)*sin(theta)
        if math.isclose(abs(phi_deg), 90, abs_tol=1e-9):
            # At poles, theta is undefined, set to 0
            theta_deg = 0
        else:
            sin_theta = y / math.cos(phi_rad)
            # Handle possible floating point errors
            sin_theta = max(-1, min(1, sin_theta))
            theta_rad = math.asin(sin_theta)
            theta_deg = math.degrees(theta_rad)
        
        return phi_deg % 360, theta_deg
    
    def get_quadrant(self, phi_deg):
        """Determine which quadrant phi is in (1-4)"""
        phi = phi_deg % 360
        if 0 <= phi < 90:
            return 1
        elif 90 <= phi < 180:
            return 2
        elif 180 <= phi < 270:
            return 3
        else:
            return 4
    
    def calculate_shadow(self, phi_deg, theta_deg):
        """Calculate shadow vertices as the intersection of the parallelogram and the solar array rectangle"""
        # Angle conversion
        phi = math.radians(phi_deg)
        theta = math.radians(theta_deg)
        
        # Handle vertical case (phi = 90°)
        if math.isclose(phi_deg % 180, 90, abs_tol=1e-9):
            # Vertical light source creates a rectangular shadow
            shadow_poly = Polygon([(0, 0), (self.D, 0), (self.D, self.L), (0, self.L)])
        else:
            # Trigonometric calculations
            # 在三角函数计算前限制数值范围
            cot_phi = 1 / max(1e-10, math.tan(phi))  # 避免除以零
            x_offset = self.L * cot_phi * math.sin(theta)
            y_offset = self.L * cot_phi * math.cos(theta)

            # 限制偏移量范围
            x_offset = max(-1e6, min(1e6, x_offset))
            y_offset = max(-1e6, min(1e6, y_offset))
            
            # Parallelogram vertices (unbounded shadow)
            shadow_poly = Polygon([
                (0, 0),
                (self.D, 0),
                (self.D - x_offset, y_offset),
                (-x_offset, y_offset)
            ])
        
        # Solar array rectangle (0,0) to (D, H)
        solar_array_rect = Polygon([(0, 0), (self.D, 0), (self.D, self.H), (0, self.H)])
        
        # Compute intersection (actual shadow shape)
        shadow_intersection = shadow_poly.intersection(solar_array_rect)
        
        # Extract vertices
        if shadow_intersection.is_empty:
            vertices = []
            area = 0
        else:
            # Get exterior coordinates (ignoring possible holes)
            vertices = list(shadow_intersection.exterior.coords)
            area = shadow_intersection.area
        
        return vertices, area
    
    def calculate_combined_non_shadow(self, phi_i, theta_i, phi_o, theta_o):
        """Calculate combined non-shadow area and shadow geometry for two light sources"""
        v_i, _ = self.calculate_shadow(phi_i, theta_i)
        v_o, _ = self.calculate_shadow(phi_o, theta_o)
        
        rect = Polygon([(0, 0), (self.D, 0), (self.D, self.H), (0, self.H)])
        combined = unary_union([Polygon(v_i), Polygon(v_o)])
        
        non_shadow = rect.difference(combined)
        non_shadow_area = non_shadow.area if hasattr(non_shadow, 'area') else self.D * self.H
        return non_shadow_area, combined
    
    def calculate_special_case(self, phi_i, theta_i, phi_o, theta_o):
        """Handle special case where φ_i is in Q1/Q4 and φ_o is in Q4"""
        quad_i = self.get_quadrant(phi_i)
        
        # Convert Q4 angles to their adjusted values
        phi_i_adj = 0 if quad_i == 1 else (phi_i - 270)
        phi_o_adj = phi_o - 270
        
        # Calculate non-shadow area using the polygon method
        non_shadow_area, _ = self.calculate_combined_non_shadow(
            phi_i_adj, theta_i, 
            phi_o_adj, theta_o
        )
        
        return non_shadow_area

    def calculate_effective_area(self, xi, yi, zi, xo, yo, zo):
        """Calculate effective area based on Cartesian coordinates"""
        # Convert Cartesian to spherical coordinates
        phi_i, theta_i = self.cartesian_to_spherical(xi, yi, zi)
        phi_o, theta_o = self.cartesian_to_spherical(xo, yo, zo)
        
        quad_i = self.get_quadrant(phi_i)
        quad_o = self.get_quadrant(phi_o)
        
        # Initialize both areas
        A_eff_SA = 0
        A_eff_chassis = 0
        
        # Case determination
        if quad_i == 1:
            if quad_o == 3:
                # Case 1-3: φ_i in Q1, φ_o in Q3
                A_eff_SA = 0
                A_eff_chassis = 0
            elif quad_o == 4:
                # Case1-4: Special case
                A_eff_SA = self.calculate_special_case(phi_i, theta_i, phi_o, theta_o)
                A_eff_chassis = 0
                
        elif quad_i == 2:
            if quad_o == 3:
                # Case2-3: φ_i in Q2, φ_o in Q3
                A_eff_SA = self.A_SA
                A_eff_chassis = 0
            elif quad_o == 4:
                # Case2-4: φ_i in Q2, φ_o in Q4
                A_eff_SA = 0
                A_eff_chassis = 0
        
        elif quad_i == 3:
            if quad_o == 3:
                # Case3-3: φ_i in Q3, φ_o in Q3
                A_eff_SA = self.A_SA
                A_eff_chassis = self.A_chassis
            elif quad_o == 4:
                # Case3-4: φ_i in Q3, φ_o in Q4
                A_eff_SA = 0
                A_eff_chassis = self.A_chassis
        
        elif quad_i == 4:
            if quad_o == 3:
                # Case4-3: φ_i in Q4, φ_o in Q3
                A_eff_SA = 0
                A_eff_chassis = self.A_chassis
            elif quad_o == 4:
                # Case4-4: Special case
                A_eff_SA = self.calculate_special_case(phi_i, theta_i, phi_o, theta_o)
                A_eff_chassis = self.A_chassis
                
        return A_eff_SA, A_eff_chassis


def calculate_solar_phase_angle(xi, yi, zi, xo, yo, zo):
    """Calculate the solar phase angle between two vectors in degrees"""
    # Normalize vectors
    norm_i = math.sqrt(xi**2 + yi**2 + zi**2)
    norm_o = math.sqrt(xo**2 + yo**2 + zo**2)
    
    if norm_i == 0 or norm_o == 0:
        return 0
    
    # Dot product
    dot_product = (xi * xo + yi * yo + zi * zo) / (norm_i * norm_o)
    
    # Handle possible floating point errors
    dot_product = max(-1, min(1, dot_product))
    
    # Calculate angle in radians and convert to degrees
    phase_angle_rad = math.acos(dot_product)
    return math.degrees(phase_angle_rad)


def process_vectors(input_path, output_path):
    df = pd.read_csv(input_path)
    print("Columns found:", df.columns.tolist())
    
    results = []
    calculator = ShadowCalculator()
    
    for _, row in df.iterrows():
        try:
            xi, yi, zi = row['i_x'], row['i_y'], row['i_z']
            xo, yo, zo = row['o_x'], row['o_y'], row['o_z']
            
            phase_angle = calculate_solar_phase_angle(xi, yi, zi, xo, yo, zo)
            A_eff_SA, A_eff_chassis = calculator.calculate_effective_area(xi, yi, zi, xo, yo, zo)
            
            results.append({
                'i_x': xi, 'i_y': yi, 'i_z': zi,
                'o_x': xo, 'o_y': yo, 'o_z': zo,
                'phase_angle': phase_angle,
                'A_eff_SA': A_eff_SA,
                'A_eff_chassis': A_eff_chassis
            })
        except Exception as e:
            print(f"Error processing row: {str(e)}")
            continue
    
    pd.DataFrame(results).to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")


# Example usage
if __name__ == "__main__":
    input_path = r'C:\Users\27549\Desktop\course_file\presonal_project\Satellite_Optical_Brightness_MSc_Project\codeinpython\viewing_sphere_pairs.csv'
    output_path = r'C:\Users\27549\Desktop\course_file\presonal_project\Satellite_Optical_Brightness_MSc_Project\codeinpython\results.csv'
    process_vectors(input_path, output_path)