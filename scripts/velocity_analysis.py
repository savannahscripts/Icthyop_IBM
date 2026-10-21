
# %% ============================================================
# 01 — MAXIMUM VELOCITY AND ICHTHYOP TIMESTEP
# ================================================================
# Project: Sardine Run — Ichthyop particle simulation
# Data: CMEMS GLORYS12V1
# Input: sardinetrial.nc

# %% 1. IMPORT LIBRARIES -----------------------------------------

from pathlib import Path
import numpy as np
import xarray as xr


# %% 2. DEFINE PROJECT PATHS -------------------------------------

project_dir = Path.home() / "Research" / "Ichthyop-Workshop"

nc_file = (
    project_dir
    / "software"
    / "input"
    / "sardinetrial.nc"
)

if not nc_file.is_file():
    raise FileNotFoundError(
        f"NetCDF file not found: {nc_file}"
    )

print(f"Input file: {nc_file}")


# %% 3. OPEN AND INSPECT NETCDF DATA -----------------------------

ds = xr.open_dataset(nc_file)

print("\n--- DATASET INFORMATION ---")
print(ds.sizes)

u = ds["uo"]
v = ds["vo"]

latitude = ds["latitude"].values
longitude = ds["longitude"].values


# %% 4. CALCULATE MAXIMUM CURRENT SPEED --------------------------

# Magnitude of horizontal velocity:
# V = sqrt(u^2 + v^2)

speed = np.hypot(u, v)

# Calculate maximum across all dimensions
max_speed = float(speed.max(skipna=True).item())

# Identify coordinates of maximum
idx = np.unravel_index(
    np.nanargmax(speed.values),
    speed.shape
)

max_coords = {
    dim: ds[dim].values[i]
    for dim, i in zip(speed.dims, idx)
}

print("\n--- MAXIMUM CURRENT VELOCITY ---")
print(f"Maximum: {max_speed:.4f} m/s")
print(f"Maximum: {max_speed * 100:.2f} cm/s")

print("\nLocation:")
for dim, value in max_coords.items():
    print(f"{dim}: {value}")


# %% 5. CALCULATE HORIZONTAL GRID SPACING ------------------------

# Approximate distances for a regular latitude-longitude
# grid, accounting for longitude convergence with latitude.

earth_radius = 6_371_000  # metres

# Angular distances between neighbouring grid points
dlat = np.abs(np.diff(latitude))
dlon = np.abs(np.diff(longitude))

# North-south spacing in metres
dy = earth_radius * np.deg2rad(dlat)

# East-west spacing depends on latitude
dx = (
    earth_radius
    * np.cos(np.deg2rad(latitude[:, None]))
    * np.deg2rad(dlon[None, :])
)

# Conservative grid spacing across entire domain
min_dx = float(np.min(dx))
min_dy = float(np.min(dy))

min_grid_spacing = min(min_dx, min_dy)

print("\n--- HORIZONTAL GRID RESOLUTION ---")
print(f"Minimum east-west spacing: {min_dx:.1f} m")
print(f"Minimum north-south spacing: {min_dy:.1f} m")
print(f"Minimum grid spacing: {min_grid_spacing:.1f} m")


# %% 6. CALCULATE CFL TIMESTEP ----------------------------

# CFL condition:
# C = V_max * dt / dx <= 1

# Theoretical maximum timestep
dt_max = min_grid_spacing / max_speed

# Proposed Ichthyop integration timestep (seconds)
dt_selected = 1800

# Calculate Courant number
courant = max_speed * dt_selected / min_grid_spacing

print("\n--- CFL TIMESTEP ---")
print(f"Maximum permissible dt: {dt_max:.2f} s")
print(f"Selected timestep: {dt_selected} s")
print(f"Selected timestep: {dt_selected / 60:.1f} min")
print(f"Courant number: {courant:.3f}")

assert courant <= 1, "CFL condition exceeded"


# %% 7. CHECK NETCDF TEMPORAL RESOLUTION -------------------------

# Determine time intervals in the forcing data
time_values = ds["time"].values

intervals = (
    np.diff(time_values)
    / np.timedelta64(1, "s")
)

unique_intervals = np.unique(intervals)

print("\n--- HYDRODYNAMIC DATA TIME INTERVAL ---")

print(f"Number of time records: {len(time_values)}")
print(f"Unique time intervals (seconds): {unique_intervals}")
print(f"Median interval: {np.median(intervals):.0f} s")
print(f"Median interval: {np.median(intervals) / 3600:.2f} h")


# %% 8. SUMMARY -------------------------------------------------

print("\n====================================")
print("ICHTHYOP CONFIGURATION SUMMARY")
print("====================================")

print(f"Maximum velocity: {max_speed:.4f} m/s")
print(f"Minimum grid spacing: {min_grid_spacing:.1f} m")
print(f"CFL maximum timestep: {dt_max:.2f} s")
print(f"Selected timestep: {dt_selected} s")
print(f"Selected timestep: {dt_selected / 60:.2f} min")
print(f"Courant number: {courant:.3f}")

print("\nAnalysis complete.")

ds.close()

git status
git add scripts/velocity_analysis.py
git commit -m "Calculate GLORYS maximum velocity and CFL timestep"
git push