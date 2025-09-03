‘ABmag_SolarPhaseAngle_origin2 .ipynb’ and ‘MagnitudesCalculationOrigin2_Visible.csv’is for calculating brightness of observation sampling points with original area.
‘ABmag_SolarPhaseAngle_origin .ipynb’ and ‘MagnitudesCalculationOrigin_Visible.csv’is for calculating brightness of sphere sampling points with original area.
‘ABmag_SolarPhaseAngle .ipynb’ and ‘MagnitudesCalculation_Visible.csv’is for calculating brightness of sphere sampling points with effective area.

'Model_Correlation_EffectiveArea' is to, from sun and satellite altitude and azimuth in Ob_Frame, first calculate 2 vectors in Sat_Frame, then the effective area and brightness, and finally do correlation. 


altitude_azimuth2.py：This code filters nighttime rows (sun_alt < 0) from the dataset, then takes a random subset (4% remained) of those rows, and saves them into a new CSV for later use.

 Effective_Area_Calculation.py： calculate Effective area and visualise