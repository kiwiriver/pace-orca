import re
import numpy as np
import xarray as xr

def extract_timestamp(filename):
    """
    Extracts the timestamp of the form YYYYMMDDTHHmmss from the given filename using pattern matching.

    Parameters:
        filename (str): The input filename.

    Returns:
        str: Extracted timestamp if found, otherwise None.
    """
    pattern = r"\.(\d{8}T\d{6})\."
    match = re.search(pattern, filename)
    if match:
        return match.group(1)
    return None

def filter_data(file1, iwv550 = 1, aot_min = 0.15,  criteria = (30, 20, 2.0)):
    """
    check the file, and output total number of pixels agree with the rules based on:
    aot, nv_ref, nv_dolp, chi2_max

    criteria = (nv_ref_min, nv_dolp_min, chi2_max)
    
    """

    nv_ref_min, nv_dolp_min, chi2_max = criteria
    
    datatree = xr.open_datatree(file1)
    dataset = xr.merge(datatree.to_dict().values())
    

    chi2 = dataset["chi2"].values
    aot = dataset["aot"].values
    data = aot[:, :, iwv550]
    #total non-nan data
    npixel_valid0 = np.sum(~np.isnan(data))

    try:
        nv_ref = dataset["nv_ref"].values
        nv_dolp = dataset["nv_dolp"].values
        filter1 = (aot[:, :, iwv550] >= aot_min) & (nv_ref>=nv_ref_min) & (nv_dolp>=nv_dolp_min) & (chi2 <=chi2_max)
        print("use nv_ref, nv_dolp, chi2")
    except:
        #when nv are not available
        filter1 = (aot[:, :, iwv550] >= aot_min) & (chi2 <=chi2_max)
        print("use chi2 only, nv_ref, nv_dolp not found")

    #total non-nan data after filtering
    data = np.where(filter1,data , np.nan)
    npixel_valid1 = np.sum(~np.isnan(data))

    return npixel_valid0, npixel_valid1, filter1