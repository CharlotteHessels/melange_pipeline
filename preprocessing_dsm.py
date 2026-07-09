import numpy as np
import tifffile as tiff
import rasterio
from scipy.linalg import lstsq
from scipy.ndimage import distance_transform_edt
from pathlib import Path  

    
def open_file(file):
    with rasterio.open(file) as src:
        data = src.read(1)
        mask = src.read_masks(1)
        meta = src.meta.copy()
        pixel_size = src.res[0]

    data = data.astype('float32')
    data[mask == 0] = np.nan
    mask = ~np.isnan(data)
    return data, mask, meta, pixel_size


def fit_polynomial(x, y, z):
    A = np.c_[x**2, y**2, x*y, x, y, np.ones_like(x)]
    coeffs, *_ = np.linalg.lstsq(A, z, rcond=None)
    return coeffs
    

def correct_doming(data, mask):
    rows, cols = np.indices(data.shape)
    total_points = len(rows) * len(cols)
    sample_size = int(total_points * 0.00002)
    max_iterations = 4
    
    for _ in range(max_iterations):
        x_all = cols[mask]
        y_all = rows[mask]
        z_all = data[mask]
    
        # sampling
        sample_idc = np.random.choice(len(x_all), size=sample_size, replace=False)
        x = x_all[sample_idc]
        y = y_all[sample_idc]
        z = z_all[sample_idc]
        
        # Fit polynomial
        coeffs = fit_polynomial(x, y, z)        
    
        # Build fitted surface
        z_fit = (coeffs[0]*cols**2 +
                 coeffs[1]*rows**2 +
                 coeffs[2]*cols*rows +
                 coeffs[3]*cols +
                 coeffs[4]*rows +
                 coeffs[5])
    
        # calculate residuals between sample points and the fitted curve, remove the sample points that have high residuals
        residuals = data - z_fit
    
        # Keep only points with small residuals
        threshold = np.nanpercentile(np.abs(residuals[mask]), 90)
        new_mask = np.abs(residuals) < threshold
    
        mask = new_mask & (~np.isnan(data))
        
    # subtract the fitted curve from original dsm
    corrected = data - z_fit
    corrected[np.isnan(data)] = np.nan

    current_min = np.nanmin(corrected)
    current_max = np.nanmax(corrected)
    return corrected

    
def remove_artifacts(data, pixel_size, step_meters):
    # remove boundary in steps of 5 meters
    step_pixels = int(step_meters / pixel_size)

    # Bounds in between which the points need to be (meters)
    min_allowed = -0.8
    max_allowed = 100  

    max_iterations = 10  # remove max 50 meters from edges

    for i in range(max_iterations):
        valid_mask = ~np.isnan(data)

        # check if there is data left to remove
        if np.sum(valid_mask) == 0:
            break

        current_min = np.nanmin(data)
        current_max = np.nanmax(data)

        # Check if within bounds
        if (current_min >= min_allowed) and (current_max <= max_allowed):
            break

        # Compute distance to edge
        distance = distance_transform_edt(valid_mask)

        # Remove another 5 m band
        data[distance <= step_pixels] = np.nan

    global_min = np.nanmin(data)
    global_max = np.nanmax(data)
    
    return data


def remove_lower_outliers(data, k=1.5):
    valid = ~np.isnan(data)
    values = data[valid]

    if len(values) == 0:
        return data

    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    iqr = q3 - q1

    lower_bound = q1 - k * iqr

    # Only remove lower outliers
    data[data < lower_bound] = np.nan
    return data
    
    
def offset_data(data):
    # take global minimum as the new 0 level, after taking out lower outliers
    offset = np.nanmin(data)
    data = data - offset
    return data


def export_data(data, file_name, meta):
    meta.update(dtype=data.dtype)
    with rasterio.open('./cleaned_dsm/' + file_name + '.tif', 'w', **meta) as dst:
        dst.write(data, 1)
        

def preprocess_dsm(dsm_path, file_name):
    input_directory = Path(dsm_path)  
    file_dir = (file for file in input_directory.iterdir() if file.is_file())

    cleaned_path = Path('./cleaned_dsm/' + file_name + '.tif')
    if cleaned_path.exists():
        print('Dsm already cleaned, extracting statistics next...')
        return cleaned_path
    
    for file in file_dir:
        data, mask, meta, pixel_size = open_file(file)
        corrected_data = correct_doming(data, mask)
        no_artifacts_data = remove_artifacts(corrected_data, pixel_size, step_meters=5)
        cleaned_data = remove_lower_outliers(no_artifacts_data)
        adjusted_data = offset_data(cleaned_data)
        export_data(adjusted_data, file_name, meta)

    cleaned_path = './cleaned_dsm/' + file_name + '.tif'
    return cleaned_path