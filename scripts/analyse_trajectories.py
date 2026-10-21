
# %% ============================================================
# 06 — ICHTHYOP PARTICLE TRAJECTORY ANALYSIS
# Experiment: EXP01 — Eastern Cape passive transport
# ================================================================

# %% 1. IMPORT LIBRARIES -----------------------------------------

from pathlib import Path
import xarray as xr


# %% 2. LOCATE SIMULATION OUTPUT ---------------------------------

project = Path.home() / "Research" / "Ichthyop-Workshop"

output_dir = project / "software" / "output"

nc_files = sorted(
    output_dir.glob("my-simulation_ichthyop-run*.nc"),
    key=lambda p: p.stat().st_mtime
)

if not nc_files:
    raise FileNotFoundError(
        f"No completed Ichthyop NetCDF files found in {output_dir}"
    )

nc_file = nc_files[-1]

print(f"\nOpening: {nc_file.name}")


# %% 3. OPEN PARTICLE TRAJECTORIES -------------------------------

ds = xr.open_dataset(nc_file)

print("\n--- SIMULATION OUTPUT ---")
print(ds)


# %% 4. LIST VARIABLES -------------------------------------------

print("\n--- AVAILABLE VARIABLES ---")

for name, variable in ds.variables.items():
    print(
        f"{name}: dimensions={variable.dims}, "
        f"shape={variable.shape}"
    )


# %% 5. GLOBAL ATTRIBUTES ----------------------------------------

print("\n--- SIMULATION METADATA ---")

for key, value in ds.attrs.items():
    print(f"{key}: {value}")


# %% 6. CLOSE DATASET --------------------------------------------

ds.close()

print("\nTrajectory inspection complete.")
