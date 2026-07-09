import rasterio
import numpy as np
from rasterio.windows import Window
import matplotlib.pyplot as plt
from pathlib import Path  
import warnings
warnings.filterwarnings("ignore")


def plot_violins_all_new(data, file_name, plot_title, location_dict, packing_fraction, volume):
    # Remove rows/cols that are entirely nan
    valid_rows = ~np.all(np.isnan(data), axis=1)
    valid_cols = ~np.all(np.isnan(data), axis=0)

    data = data[valid_rows][:, valid_cols]

    n_rows, n_cols = data.shape

    # row distributions
    row_data = []

    for i in range(n_rows):

        vals = data[i, :]
        vals = vals[~np.isnan(vals)]

        if len(vals) > 1:
            row_data.append(vals)
        else:
            row_data.append(None)

    #column distributions
    col_data = []

    for j in range(n_cols):

        vals = data[:, j]
        vals = vals[~np.isnan(vals)]

        if len(vals) > 1:
            col_data.append(vals)
        else:
            col_data.append(None)

    # global distribition
    all_vals = data.flatten()
    all_vals = all_vals[~np.isnan(all_vals)]

    fig = plt.figure(figsize=(10, 11))

    gs = fig.add_gridspec(
        3, 2,
        width_ratios=[4, 1.5],
        height_ratios=[1.5, 4, 0.6],
        wspace=0.25,
        hspace=0.3
    )

    ax_top = fig.add_subplot(gs[0, 0])
    ax_main = fig.add_subplot(gs[1, 0])
    ax_right = fig.add_subplot(gs[1, 1])
    ax_global = fig.add_subplot(gs[0, 1])

    # Bottom statistics axis
    ax_stats = fig.add_subplot(gs[2, :])
    
    location = next((key for key, values in location_dict.items() if file_name in values), None)
    fig.suptitle(
        file_name + ' - ' + location,
        fontsize=18,
        fontweight='bold',
        y=0.95
    )

    im = ax_main.imshow(
        data,
        origin="upper",
        aspect="auto"
    )

    ax_main.set_title(plot_title)
    ax_main.set_xlabel("Column index")
    ax_main.set_ylabel("Row index")

    cbar = plt.colorbar(
        im,
        ax=ax_main,
        fraction=0.046,
        pad=0.02
    )

    cbar.set_label("Elevation (m)")

    # top column violins
    positions = np.arange(n_cols)

    for j, vals in enumerate(col_data):

        if vals is None:
            continue

        parts = ax_top.violinplot(
            [vals],
            positions=[j],
            widths=0.8,
            showmedians=True
        )

        for pc in parts['bodies']:
            pc.set_facecolor("#1f77b4")
            pc.set_edgecolor("black")
            pc.set_alpha(0.6)

        for key in ['cbars', 'cmins', 'cmaxes']:
            parts[key].set_color("black")

        parts['cmedians'].set_color("black")

    ax_top.set_xlim(-0.5, n_cols - 0.5)
    ax_top.set_ylabel("Elevation (m)")
    ax_top.set_title("Column distributions")

    ax_top.set_xticks([])

    # right row violins
    positions = np.arange(n_rows)

    for i, vals in enumerate(row_data):

        if vals is None:
            continue

        parts = ax_right.violinplot(
            [vals],
            positions=[i],
            widths=0.8,
            vert=False,
            showmedians=True
        )

        for pc in parts['bodies']:
            pc.set_facecolor("#1f77b4")
            pc.set_edgecolor("black")
            pc.set_alpha(0.6)

        for key in ['cbars', 'cmins', 'cmaxes']:
            parts[key].set_color("black")

        parts['cmedians'].set_color("black")

    ax_right.set_ylim(-0.5, n_rows - 0.5)
    ax_right.set_xlabel("Elevation (m)")
    ax_right.set_title("Row distributions")

    ax_right.set_yticks([])

    # global violin
    parts = ax_global.violinplot(
        [all_vals],
        showmedians=True
    )

    for pc in parts['bodies']:
        pc.set_facecolor("#1f77b4")
        pc.set_edgecolor("black")
        pc.set_alpha(0.6)

    for key in ['cbars', 'cmins', 'cmaxes', 'cmedians']:

        if key in parts:
            parts[key].set_color("black")

    ax_global.set_xticks([])
    ax_global.set_ylabel("Elevation (m)")
    ax_global.set_title("Global distribution")

    ax_top.set_xlim(ax_main.get_xlim())
    ax_right.set_ylim(ax_main.get_ylim())

    for ax in [ax_top, ax_right, ax_main]:

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # summary statistics
    stats_text = (
        f"Max: {np.nanmax(all_vals):.2f} m | "
        f"Mean elevation: {np.nanmean(all_vals):.2f} m | "
        f"Median: {np.nanmedian(all_vals):.2f} m | "
        f"Std: {np.nanstd(all_vals):.2f} m | "
        f"φ: {packing_fraction:.2f} | "
        f"Mean volume: {volume:.2f} m³ "
    )

    ax_stats.axis("off")

    ax_stats.text(
        0,
        0.75,   
        stats_text,
        transform=ax_stats.transAxes,
        fontsize=10,
        verticalalignment='center',
        horizontalalignment='left',
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor="white",
            edgecolor="black",
            alpha=0.9
        ),
        family='monospace'
    )

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    plt.savefig(
        './results/figures/' + file_name + '_violins.png',
        dpi=300,
        bbox_inches='tight'
    )

    plt.close()
    print('Saved figure')

    
def get_file_details(file, window_size):
    with rasterio.open(file) as src:
        data = src.read(1)
        pixel_size = src.res[0]
    
    window_pixels = int(window_size / (pixel_size )) 
    if window_pixels == 0:
        window_pixels = 1
    
    height, width = src.height, src.width
    
    n_rows = height // window_pixels
    n_cols = width // window_pixels
    
    return height, width, n_rows, n_cols, window_pixels

    
def iceberg_detection_simple(data):
    # taken from International Ice Patrol System.
    sea_ice_max = 0.5
    growler_min = 0.5
    growler_max = 1.5
    bergy_bit_min = 1.5
    bergy_bit_max = 5
    iceberg_min = 5
    
    sea_ice_mask = data < sea_ice_max
    growler_mask = (data >= growler_min) & (data < growler_max)
    bergy_mask = (data >= bergy_bit_min) & (data < bergy_bit_max)
    iceberg_mask = data > iceberg_min

    count_total = np.count_nonzero(~np.isnan(data))
    count_ice = np.sum(sea_ice_mask)
    count_growler = np.sum(growler_mask)
    count_bergy = np.sum(bergy_mask)
    count_iceberg = np.sum(iceberg_mask)

    ice = {
    'total_windows':count_total,
    "sea_ice": count_ice,
    "growler": count_growler,
    "bergy_bit": count_bergy,
    "iceberg": count_iceberg
    }

    
    large_elements = count_iceberg
    small_elements = count_ice + count_growler + count_bergy
    
    # large / small elements = size ratio rho
    if small_elements == 0:
        size_ratio = large_elements
        return ice, packing_fraction
    size_ratio = float((count_iceberg) / (count_ice + count_growler + count_bergy))

    # large / total elements = packing fraction phi
    packing_fraction = float(large_elements/count_total)
    
    return ice, size_ratio, packing_fraction

    
def calculate_volume(data, window_size):
    data = data.flatten()
    data = data[~np.isnan(data)]
    data = data[np.isfinite(data)]
    
    hydrostatic_eq = 10 #10 percent assumption
    freeboard_total = np.sum(data) # sum of mean values for all windows
    num_windows = np.count_nonzero(~np.isnan(data))
    
    total_volume = freeboard_total * hydrostatic_eq * window_size *  window_size
    total_area = num_windows * window_size * window_size
    volume_mean = total_volume / total_area
    return volume_mean, total_area

    
def get_window_stats(file, height, width, n_rows, n_cols, win_size, min_valid_fraction):
    min_grid = np.full((n_rows, n_cols), np.nan)
    max_grid = np.full((n_rows, n_cols), np.nan)
    median_grid = np.full((n_rows, n_cols), np.nan)
    mean_grid = np.full((n_rows, n_cols), np.nan)
    std_grid = np.full((n_rows, n_cols), np.nan)
    
    stats = {
    "min": min_grid,
    "max": max_grid,
    "median": median_grid,
    "mean": mean_grid,
    "std": std_grid,
    }
    
    with rasterio.open(file) as src:
        for i, row in enumerate(range(0, height - win_size + 1, win_size)):
            for j, col in enumerate(range(0, width - win_size + 1, win_size)):
    
                window = Window(col, row, win_size, win_size)
                data = src.read(1, window=window, masked=True)
            
                values = data.compressed()
    
                valid_count = len(values)
                total_pixels = win_size * win_size
    
                # Skip windows with too little valid data
                if valid_count / total_pixels < min_valid_fraction:
                    continue
    
                # extra safety for the violin plots
                values = values[np.isfinite(values)]
    
                if len(values) == 0:
                    continue
    
                #statistics
                stats['min'][i, j] = values.min()
                stats['max'][i, j] = values.max()
                stats['median'][i, j] = np.median(values)          
                stats['mean'][i, j] = values.mean()
                stats['std'][i, j] = values.std()
    return stats


    
def extract_statistics(cleaned_dsm_path, file_name, window_size):
    min_valid_fraction = 0.9  # filter windows with this fraction of nan values

    input_file = Path(cleaned_dsm_path)
    

    locations_dict = {
        'Melville':['25_03_2023_flight2','25_03_2023_flight1', '31_03_2022_flight3', 'A31_03_2022_flight3'],
        'Farquhar':['26_03_2023_flight1','31_03_2022_flight1', 'A31_03_2022_flight1'],
        'North Tracy':['26_03_2023_flight2','A26_03_2023_flight2'],
        'South Tracy':['13_04_2024_flight1','13_04_2024_flight2'],
        'North-west Tracy':['30_03_2022_flight3','30_03_2022_flight4','A30_03_2022_flight3','A30_03_2022_flight4' ],
        'South-west Tracy':['27_03_2023_flight1'],
        'Camp':['28_03_2023_flight1','27_03_2023_flight4', '27_03_2023_flight3', '27_03_2023_flight2', '31_03_2022_flight2','A31_03_2022_flight2'],
        'Denmark':['21_05_2026_flight1','21_05_2026_flight2']
    }

    height, width, n_rows, n_cols, window_pixels = get_file_details(input_file, window_size)
    stats = get_window_stats(input_file, height, width, n_rows, n_cols, window_pixels, min_valid_fraction)
    np.save('./results/stats/' + file_name + '.npy', stats)
  
    mean_grid = stats['mean']
    std_grid = stats['std']
    min_grid = stats['min']
    max_grid = stats['max']
    median_grid = stats['median']

    mean_ice_detected, size_ratio, packing_fraction = iceberg_detection_simple(mean_grid)
    #todo: check if the iceberg stats file exists, if not make it, if yes then update it
    #iceberg_stats.update({file_name:[packing_fraction, mean_ice_detected]})
    
    volume, area = calculate_volume(mean_grid, window_size)
    plot_violins_all_new(mean_grid, file_name, 
                         'Mean elevation (m) per window (' + str(window_size) + 'x' + str(window_size) +'m)', 
                         locations_dict, packing_fraction, volume)
    
    #file = open('./stats/iceberg_stats.txt','wt')
    #file.write(str(iceberg_stats))
    #file.close()