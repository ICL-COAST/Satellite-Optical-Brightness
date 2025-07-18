import math
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

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
    
    def get_quadrant(self, phi_deg):
        """Determine which quadrant phi is in (1-4)"""
        phi = phi_deg % 360
        if 0 <= phi < 90:
            return 1
        elif 90 <= phi < 180:
            return 2
        elif 180 <= phi <= 270:
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
            cot_phi = 1 / math.tan(phi) if math.tan(phi) != 0 else float('inf')
            x_offset = self.L * cot_phi * math.sin(theta)
            y_offset = self.L * cot_phi * math.cos(theta)
            
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

    def calculate_effective_area(self, phi_i, theta_i, phi_o, theta_o):
        """Calculate effective area based on quadrant cases"""
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

    def create_solar_array(self):
        """Create solar array geometry"""
        return [
            (0, 0, self.H), (0, self.D, self.H),
            (0, self.D, 0), (0, 0, 0)
        ]
    
    def create_chassis(self):
        """Create chassis geometry"""
        return [
            (0, 0, 0), (self.L, 0, 0),
            (self.L, self.D, 0), (0, self.D, 0)
        ]
    
    def plot_scene_with_shadows(self, phi_i, theta_i, phi_o, theta_o):
        """Create 3D visualization with shadows based on input angles"""
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='3d')
        
        # Calculate effective area
        A_eff_SA, A_eff_chassis = self.calculate_effective_area(phi_i, theta_i, phi_o, theta_o)
        
        # Create solar array and chassis
        solar_array = self.create_solar_array()
        chassis = self.create_chassis()
        
        # Determine colors
        sa_color = 'blue' if A_eff_SA > 0 else 'gray'
        chassis_color = 'green' if A_eff_chassis > 0 else 'gray'
        
        # Plot solar array
        sa_poly = Poly3DCollection([solar_array], alpha=0.5, facecolors=sa_color, 
                                linewidths=1, edgecolors='navy')
        ax.add_collection3d(sa_poly)
        
        # Plot chassis
        ch_poly = Poly3DCollection([chassis], alpha=0.5, facecolors=chassis_color, 
                                linewidths=1, edgecolors='darkgreen')
        ax.add_collection3d(ch_poly)
        
        # Handle special cases (1-4 and 4-4)
        quad_i = self.get_quadrant(phi_i)
        quad_o = self.get_quadrant(phi_o)
        case_name = f"Case {quad_i}-{quad_o}"
        
        if (quad_i == 1 and quad_o == 4) or (quad_i == 4 and quad_o == 4):
            # Adjust angles according to the original special case logic
            if quad_i == 1 and quad_o == 4:
                # Case1-4: φ_i becomes 0, φ_o becomes φ_o-270
                phi_i_adj = 0
                phi_o_adj = phi_o - 270
            else:  # quad_i == 4 and quad_o == 4
                # Case4-4: both angles adjusted by -270
                phi_i_adj = phi_i - 270
                phi_o_adj = phi_o - 270
            
            # Get the combined shadow geometry
            _, combined_shadow = self.calculate_combined_non_shadow(
                phi_i_adj, theta_i,
                phi_o_adj, theta_o
            )
            
            # Convert to 3D coordinates (x=0 since it's on the YZ plane)
            def to_3d(polygon):
                if hasattr(polygon, 'geoms'):  # MultiPolygon case
                    return [[(0, x, y) for x, y in poly.exterior.coords] for poly in polygon.geoms]
                else:  # Single Polygon case
                    return [[(0, x, y) for x, y in polygon.exterior.coords]]
            
            if not combined_shadow.is_empty:
                shadow_3d = to_3d(combined_shadow)
                if isinstance(shadow_3d[0][0], tuple):  # Single polygon
                    shadow_poly = Poly3DCollection(shadow_3d, alpha=1,
                                                facecolors='black', linewidths=1,
                                                edgecolors='black')
                    ax.add_collection3d(shadow_poly)
                else:  # Multiple polygons
                    for poly in shadow_3d:
                        shadow_poly = Poly3DCollection([poly], alpha=1,
                                                    facecolors='black', linewidths=1,
                                                    edgecolors='black')
                        ax.add_collection3d(shadow_poly)
        
        # Set axis limits and labels
        max_dim = max(self.L, self.D, self.H)
        ax.set_xlim(0, max_dim )
        ax.set_ylim(0, max_dim )
        ax.set_zlim(0, max_dim )
        
        # Set equal aspect ratio
        ax.set_box_aspect([1, 1, 1])  # This makes the axes equally scaled
        
        # Create info text
        info_text = (
            f"{case_name}\n"
            f"φ_i={phi_i}°, θ_i={theta_i}°\n"
            f"φ_o={phi_o}°, θ_o={theta_o}°\n"
            f"SA Eff: {A_eff_SA:.2f} m²\n"
            f"Chassis Eff: {A_eff_chassis:.2f} m²"
        )
        # Remove all axis elements
        ax.set_axis_off()  # This removes all axes, ticks, labels, and the frame
        plt.subplots_adjust(left=0, right=0.5, bottom=0, top=1)
        # Set title (we'll use a text box instead of the default title)
        fig.text(0.7, 0.8, info_text, 
             ha='left', va='top', fontsize=10,
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))
        
        plt.tight_layout()
        plt.show()

def main():
    """Main function: calculates and prints the effective area"""
    calculator = ShadowCalculator()
    
    # Define 8 test cases (phi_i, theta_i, phi_o, theta_o)
    test_cases = [
        (45, -30, 200, 30),   # case 1-3
        (45, -30, 280, 30),    # case 1-4
        (135, 45, 200, -45),   # case 2-3 
        (135, 45, 300, -45),   # case 2-4
        (225, 0, 200, 60),     # case 3-3
        (225, 0, 300, -60),    # case 3-4
        (315, 60, 200, -30),   # case 4-3 
        (280, 15, 280, -30)     # case 4-4
]
    
    for i, (phi_i, theta_i, phi_o, theta_o) in enumerate(test_cases, 1):
        # Calculate the effective area
        A_eff_SA, A_eff_chassis = calculator.calculate_effective_area(phi_i, theta_i, phi_o, theta_o)
        
        print("=== Effective Area Calculation Results ===")
        print(f"Solar Array Effective Area: {A_eff_SA:.2f} m² (Original: {calculator.A_SA:.2f} m²)")
        print(f"Chassis Effective Area: {A_eff_chassis:.2f} m² (Original: {calculator.A_chassis:.2f} m²)")
        
        # Visualize the scene
        print("\nGenerating 3D visualization...")
        calculator.plot_scene_with_shadows(phi_i, theta_i, phi_o, theta_o)

if __name__ == "__main__":
    main()