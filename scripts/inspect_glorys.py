
# %% 1. IMPORT LIBRARIES -----------------------------------------

from pathlib import Path
import xarray as xr
import numpy as np

# %% 2. LOAD DATA ------------------------------------------------

project_dir = Path.home() / "Research" / "Ichthyop-Workshop"

nc_file = (
    project_dir / "software" / "input" / "sardinetrial.nc"
)

ds = xr.open_dataset(nc_file)

# %% 3. SPATIAL EXTENT -------------------------------------------

print("\n--- SPATIAL EXTENT ---")

print(f"Latitude min: {ds.latitude.min().item():.4f}")
print(f"Latitude max: {ds.latitude.max().item():.4f}")

print(f"Longitude min: {ds.longitude.min().item():.4f}")
print(f"Longitude max: {ds.longitude.max().item():.4f}")

print(f"Depth min: {ds.depth.min().item():.2f} m")
print(f"Depth max: {ds.depth.max().item():.2f} m")

# %% 4. TEMPORAL EXTENT ------------------------------------------

print("\n--- TEMPORAL COVERAGE ---")

print(f"Start: {ds.time.min().values}")
print(f"End: {ds.time.max().values}")

# %% 5. VARIABLES ------------------------------------------------

print("\n--- AVAILABLE VARIABLES ---")

for name, var in ds.data_vars.items():
    print(f"{name}: {var.dims}")

# %% 6. MISSING VELOCITY DATA ------------------------------------

print("\n--- MISSING DATA ---")

for name in ["uo", "vo", "thetao"]:
    missing = ds[name].isnull().mean().item() * 100
    print(f"{name}: {missing:.2f}% missing")

# %% 7. CLOSE DATASET --------------------------------------------

ds.close()
print("\nDataset inspection complete.")

#verify that the missing values correspond to land and seabed masking before using the dataset in Ichthyop.