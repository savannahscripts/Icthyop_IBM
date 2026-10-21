
# %% ============================================================
# 05 — UPSTREAM EASTERN CAPE PARTICLE RELEASE
# ================================================================
# Experiment: EXP01 — Passive transport towards Waterfall Bluff
# Forcing: CMEMS GLORYS12V1
# Release region: Offshore East London
# ================================================================

# %% 1. IMPORT LIBRARIES -----------------------------------------

from pathlib import Path
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt


# %% 2. DEFINE PATHS ---------------------------------------------

project = Path.home() / "Research" / "Ichthyop-Workshop"

nc_file = project / "software" / "input" / "sardinetrial.nc"

output_dir = project / "output" / "EXP01"
output_dir.mkdir(parents=True, exist_ok=True)

ds = xr.open_dataset(nc_file)


# %% 3. EXPERIMENT PARAMETERS ------------------------------------

start_date = "2023-06-01"
end_date = "2023-07-01"

# Approximate geographic search centre near East London.
# This is NOT yet a confirmed release location.

centre_lat = -33.0
centre_lon = 28.0

search_radius_km = 50

n_particles = 100
release_depth = -5.0  # Ichthyop: metres below surface

rng = np.random.default_rng(42)


# %% 4. SELECT SIMULATION PERIOD ---------------------------------

period = ds.sel(
    time=slice(start_date, end_date)
)

if period.sizes["time"] < 2:
    raise ValueError("Insufficient forcing records.")


# %% 5. IDENTIFY VALID OCEAN CELLS -------------------------------

# Valid surface velocity and temperature for every day.

u = period["uo"].isel(depth=0)
v = period["vo"].isel(depth=0)
temperature = period["thetao"].isel(depth=0)

valid = (
    u.notnull().all("time")
    & v.notnull().all("time")
    & temperature.notnull().all("time")
)

mask = valid.values

# Exclude grid edges and cells immediately adjacent
# to a masked cell using a 3x3 neighbourhood.

interior = np.zeros_like(mask, dtype=bool)

for j in range(1, mask.shape[0] - 1):
    for i in range(1, mask.shape[1] - 1):

        neighbourhood = mask[
            j-1:j+2,
            i-1:i+2
        ]

        interior[j, i] = neighbourhood.all()


# %% 6. FIND RELEASE CELLS NEAR EAST LONDON ----------------------

latitudes = ds.latitude.values
longitudes = ds.longitude.values

lon_grid, lat_grid = np.meshgrid(
    longitudes, latitudes
)

# Haversine distance from search centre

R = 6371.0  # Earth radius, km

phi1 = np.deg2rad(centre_lat)
phi2 = np.deg2rad(lat_grid)

dphi = phi2 - phi1
dlambda = np.deg2rad(lon_grid - centre_lon)

a = (
    np.sin(dphi / 2) ** 2
    + np.cos(phi1) * np.cos(phi2)
    * np.sin(dlambda / 2) ** 2
)

distance_km = 2 * R * np.arcsin(np.sqrt(a))

candidates = (
    interior
    & (distance_km <= search_radius_km)
)

candidate_indices = np.argwhere(candidates)

print("\n--- RELEASE AREA VALIDATION ---")
print(f"Eligible grid cells: {len(candidate_indices)}")

if len(candidate_indices) == 0:
    raise ValueError(
        "No eligible release cells found. "
        "Review the search radius and ocean mask."
    )


# %% 7. GENERATE PARTICLE POSITIONS ------------------------------

# Initial technical experiment:
# sample with replacement from valid grid-cell centres.
# Multiple particles may therefore share coordinates.

selected = rng.choice(
    len(candidate_indices),
    size=n_particles,
    replace=True
)

particle_indices = candidate_indices[selected]

particle_lat = latitudes[particle_indices[:, 0]]
particle_lon = longitudes[particle_indices[:, 1]]

print(f"Particles generated: {len(particle_lat)}")


# %% 8. EXPORT ICHTHYOP RELEASE FILE -----------------------------

release_file = output_dir / "upstream_release.txt"

with open(release_file, "w") as f:

    f.write("# longitude latitude depth\n")

    for lon, lat in zip(particle_lon, particle_lat):

        f.write(
            f"{lon:.6f} {lat:.6f} {release_depth:.1f}\n"
        )

print(f"Saved release file: {release_file}")


# %% 9. VISUALISE RELEASE LOCATIONS ------------------------------

fig, ax = plt.subplots(figsize=(9, 7))

# Background ocean mask
ax.pcolormesh(
    longitudes,
    latitudes,
    mask.astype(int),
    cmap="Blues",
    shading="auto"
)

# Candidate release locations
ax.scatter(
    lon_grid[candidates],
    lat_grid[candidates],
    s=15,
    color="orange",
    label="Eligible cells"
)

# Released particles
ax.scatter(
    particle_lon,
    particle_lat,
    s=12,
    color="red",
    label="Particle releases",
    alpha=0.7
)

ax.set_xlabel("Longitude (°E)")
ax.set_ylabel("Latitude (°N)")
ax.set_title("EXP01 — Eastern Cape Particle Releases")
ax.legend()

plt.tight_layout()

fig.savefig(
    output_dir / "release_locations.png",
    dpi=300
)

plt.show()


# %% 10. SUMMARY ------------------------------------------------

print("\n--- EXPERIMENT SUMMARY ---")
print(f"Start date: {start_date}")
print(f"End date: {end_date}")
print(f"Number of particles: {n_particles}")
print(f"Release depth: {release_depth} m")
print(f"Eligible release cells: {len(candidate_indices)}")
print(f"Release file: {release_file}")

ds.close()

print("\nRelease preparation complete.")
