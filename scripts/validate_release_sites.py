
# %% ============================================================
# 04 — VALIDATE ICHTHYOP PARTICLE RELEASE LOCATIONS
# ================================================================
# Project: Sardine Run — Ichthyop
# Dataset: CMEMS GLORYS12V1
#
# Objectives:
# 1. Define candidate release locations
# 2. Match coordinates to nearest GLORYS grid cells
# 3. Check ocean validity across the simulation period
# 4. Extract local current and temperature statistics
# ================================================================


# %% 1. IMPORT LIBRARIES -----------------------------------------

from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr


# %% 2. FILE PATHS -----------------------------------------------

project_dir = Path.home() / "Research" / "Ichthyop-Workshop"

nc_file = (
    project_dir
    / "software"
    / "input"
    / "sardinetrial.nc"
)

output_dir = project_dir / "output"
output_dir.mkdir(parents=True, exist_ok=True)

ds = xr.open_dataset(nc_file)


# %% 3. DEFINE CANDIDATE RELEASE SITES ---------------------------

# Test coordinate from previous maximum velocity analysis.
# Replace with scientifically selected release sites later.

release_sites = {
    "Test_site_01": {
        "latitude": -33.666668,
        "longitude": 28.833345
    }
}

# Simulation period: inclusive daily records
start_date = "2023-05-01"
end_date = "2023-08-01"

simulation = ds.sel(
    time=slice(start_date, end_date)
)

if simulation.sizes["time"] == 0:
    raise ValueError("No forcing records in selected period.")


# %% 4. VALIDATE RELEASE SITES -----------------------------------

results = []

for name, site in release_sites.items():

    lat = site["latitude"]
    lon = site["longitude"]

    print(f"\n--- {name} ---")

    # Check spatial domain boundaries
    if not (
        float(ds.latitude.min()) <= lat <= float(ds.latitude.max())
        and float(ds.longitude.min()) <= lon <= float(ds.longitude.max())
    ):
        print("ERROR: Outside GLORYS domain")
        continue

    # Find nearest GLORYS grid cell
    cell = simulation.sel(
        latitude=lat,
        longitude=lon,
        method="nearest"
    )

    grid_lat = float(cell.latitude.item())
    grid_lon = float(cell.longitude.item())

    print(f"Requested: {lat:.5f}, {lon:.5f}")
    print(f"Grid cell: {grid_lat:.5f}, {grid_lon:.5f}")

    # Select surface layer
    u = cell["uo"].isel(depth=0)
    v = cell["vo"].isel(depth=0)
    temp = cell["thetao"].isel(depth=0)

    # Require all three variables to be valid
    valid = (
        np.isfinite(u.values)
        & np.isfinite(v.values)
        & np.isfinite(temp.values)
    )

    valid_days = int(np.count_nonzero(valid))
    total_days = len(valid)

    valid_percent = 100 * valid_days / total_days
    all_valid = bool(valid.all())

    print(f"Valid records: {valid_days}/{total_days}")
    print(f"Valid coverage: {valid_percent:.2f}%")

    if all_valid:
        print("PASS: Surface forcing available at all records")
    else:
        print("FAIL: Some surface forcing records are missing")

    # Current speed magnitude
    current_speed = np.hypot(u.values, v.values)

    if np.isfinite(current_speed).any():
        mean_speed = float(np.nanmean(current_speed))
        max_speed = float(np.nanmax(current_speed))
    else:
        mean_speed = np.nan
        max_speed = np.nan

    results.append({
        "site": name,
        "requested_lat": lat,
        "requested_lon": lon,
        "grid_lat": grid_lat,
        "grid_lon": grid_lon,
        "valid_records": valid_days,
        "total_records": total_days,
        "valid_percent": valid_percent,
        "all_valid": all_valid,
        "mean_speed_ms": mean_speed,
        "max_speed_ms": max_speed
    })


# %% 5. EXPORT VALIDATION RESULTS --------------------------------

results_df = pd.DataFrame(results)

print("\n--- RELEASE SITE VALIDATION SUMMARY ---")
print(results_df.to_string(index=False))

csv_file = output_dir / "release_site_validation.csv"

results_df.to_csv(csv_file, index=False)

print(f"\nSaved: {csv_file}")


# %% 6. CLOSE DATASET --------------------------------------------

ds.close()

print("\nRelease-site validation complete.")
