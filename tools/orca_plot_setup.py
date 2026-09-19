"""
Setup plot styles

"""
def load_dict1v(aot_max=1.0, nv_max=90):
    """
    Load plotting ranges and styles.

    Each dictionary entry contains:
        [[vmin, vmax], cmap, scale, cbar_extend]

    Parameters
    ----------
    aot_max : float, default=1.0
        Maximum AOD value used for plotting.

    nv_max : int, default=90
        Maximum number of valid viewing angles.
        Typically 90 for HARP2 and 170 for SPEXone.

    Returns
    -------
    dict
        Plotting configuration dictionary.
    """

    dict1v = {
        # Meteorological variables
        "ozone": [[150, 450], "Spectral_r", "linear", "both"],
        "surface_pressure": [[500, 1100], "Spectral_r", "linear", "both"],
        "height": [[0, 4000], "Spectral_r", "linear", "max"],

        # Aerosol optical properties
        "aot": [[0, aot_max], "YlOrRd", "linear", "max"],
        "aot_fine": [[0, aot_max], "YlOrRd", "linear", "max"],
        "aot_coarse": [[0, aot_max], "YlOrRd", "linear", "max"],
        "ssa": [[0.8, 1.0], "RdYlBu", "linear", "min"],
        "fvf": [[0, 1], "RdYlBu_r", "linear", None],
        "angstrom_440_670": [[0, 2], "RdYlBu_r", "linear", "both"],
        "angstrom_440_870": [[0, 2], "RdYlBu_r", "linear", "both"],
        "alh": [[0, 6], "Spectral_r", "linear", "max"],

        # Particle shape
        "sph": [[0, 1], "Spectral_r", "linear", None],
        "sph_fine": [[0, 1], "Spectral_r", "linear", None],
        "sph_coarse": [[0, 1], "Spectral_r", "linear", None],

        # Refractive index
        "mr": [[1.33, 1.55], "Spectral_r", "linear", "max"],
        "mi": [[0, 0.03], "Spectral_r", "linear", "max"],
        "mr_fine": [[1.33, 1.55], "Spectral_r", "linear", "max"],
        "mi_fine": [[0, 0.03], "Spectral_r", "linear", "max"],
        "mr_coarse": [[1.33, 1.55], "Spectral_r", "linear", "max"],
        "mi_coarse": [[0, 0.03], "Spectral_r", "linear", "max"],

        # Aerosol size
        "reff_fine": [[0, 1], "Spectral_r", "linear", "max"],
        "reff_coarse": [[1, 3], "Spectral_r", "linear", "max"],
        "veff_fine": [[0, 1], "Spectral_r", "linear", "max"],
        "veff_coarse": [[0, 1], "Spectral_r", "linear", "max"],

        # Lidar-related properties
        "aerosol_lidar_ratio": [
            [0, 100], "Spectral_r", "linear", "max"
        ],
        "aerosol_depol_ratio": [
            [0, 0.2], "Spectral_r", "linear", "max"
        ],

        # Ocean properties
        "wind_speed": [[0, 15], "RdYlBu_r", "linear", "max"],
        "chla": [[-2, 1], "viridis", "log10", "both"],

        # V3 Rrs variables
        "Rrs1_mean": [[-0.001, 0.015], "magma", "linear", "max"],
        "Rrs1": [[-0.001, 0.015], "magma", "linear", "max"],
        "Rrs2_mean": [[-0.001, 0.015], "magma", "linear", "max"],
        "Rrs2": [[-0.001, 0.015], "magma", "linear", "max"],

        # V4 Rrs variables
        "Rrs_angular_mean": [
            [-0.001, 0.015], "magma", "linear", "max"
        ],
        "Rrs_angular_std": [
            [0, 0.005], "magma", "linear", "max"
        ],
        "Rrs_nadir_mean": [
            [-0.001, 0.015], "magma", "linear", "max"
        ],
        "Rrs_nadir_std": [
            [0, 0.005], "magma", "linear", "max"
        ],

        # Land surface reflectance
        "rhos_angular_mean": [[0, 1], "magma", "linear", "max"],
        "rhos_angular_std": [[0, 1], "magma", "linear", "max"],
        "rhos_nadir_mean": [[0, 1], "magma", "linear", "max"],
        "rhos_nadir_std": [[0, 1], "magma", "linear", "max"],

        # Retrieval diagnostics
        "chi2": [[0, 2], "viridis", "linear", "max"],
        "chisqr_mapol": [[0, 2], "viridis", "linear", "max"],
        "timing": [[0, 2], "viridis", "linear", "max"],
        "nv_ref": [[0, nv_max], "viridis", "linear", None],
        "nv_rho": [[0, nv_max], "viridis", "linear", None],
        "nv_dolp": [[0, nv_max], "viridis", "linear", None],
        "quality_flag": [[0, 3], "viridis", "linear", "max"],
        "qual": [[0, 3], "viridis", "linear", "max"],

        # Land-model parameters
        "land_fiso": [[0, 1], "Spectral_r", "linear", None],
        "land_kvol": [[0, 1.5], "Spectral_r", "linear", "max"],
        "land_kgeo": [[0, 0.35], "Spectral_r", "linear", "max"],
        "land_fvol": [[0, 1.5], "Spectral_r", "linear", "max"],
        "land_fgeo": [[0, 0.35], "Spectral_r", "linear", "max"],
        "land_bpol": [[0, 10], "Spectral_r", "linear", "max"],
        "land_white_sky_albedo": [
            [0, 1], "Spectral_r", "linear", None
        ],
    }

    return dict1v