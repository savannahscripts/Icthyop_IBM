
# %% 1. IMPORT LIBRARIES -----------------------------------------

from pathlib import Path
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt


# %% 2. LOAD DATA ------------------------------------------------

project_dir = Path.home() / "Research" / "Ichthyop-Workshop"

nc_file = (
    project_dir / "software" / "input" / "sardinetrial.nc"
)

ds = xr.open_dataset(nc_file)


# %% 3. EXAMINE SURFACE DATA -------------------------------------

# Select shallowest depth level
u_surface = ds["uo"].isel(depth=0)

# Calculate valid and missing fractions across time
surface_missing = u_surface.isnull().mean().item() * 100

print("\n--- SURFACE DATA COVERAGE ---")
print(f"Missing surface data: {surface_missing:.2f}%")
print(f"Valid surface data: {100 - surface_missing:.2f}%")


# %% 4. IDENTIFY VALID OCEAN CELLS -------------------------------

# Grid cells with at least one valid surface observation
ocean_mask = u_surface.notnull().any(dim="time")

print("\n--- OCEAN MASK ---")
print(f"Valid ocean cells: {int(ocean_mask.sum().item())}")
print(f"Total grid cells: {ocean_mask.size}")


# %% 5. PLOT OCEAN MASK ------------------------------------------

from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

fig, ax = plt.subplots(figsize=(10, 7))

cmap = ListedColormap(["#eeeeee", "#173c70"])

ocean_mask.astype(int).plot(
    ax=ax,
    cmap=cmap,
    vmin=0,
    vmax=1,
    add_colorbar=False
)

ax.legend(
    handles=[
        Patch(facecolor="#eeeeee", label="Land / masked"),
        Patch(facecolor="#173c70", label="Valid ocean")
    ],
    loc="lower left"
)

ax.set_title("GLORYS Surface Ocean Mask")
ax.set_xlabel("Longitude (°E)")
ax.set_ylabel("Latitude (°N)")

plt.tight_layout()

output_dir = project_dir / "figures"
output_dir.mkdir(parents=True, exist_ok=True)

fig.savefig(
    output_dir / "glorys_ocean_mask.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# %% 6. CLOSE DATASET --------------------------------------------

ds.close()

print("\nOcean mask analysis complete.")
