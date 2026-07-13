# melange_pipeline
Use run_pipeline.py to extract mélange statistics from raw images or an exisiting dem.
To run the file, the following arguments are needed:

filename = name of the drone flight or location, preferably including year and date
method = can be either 'odm', which indicates that raw images need to be processed to a dsm or that a dsm from images needs to be cleaned,
         or 'arcticdem', which indicates that a tif file from arcticdem exists that needs to be processed
--image_path = optional argument which is needed when using the odm method, points to the path with the images that need to be processed

## Example use
python3 run_pipeline.py filename arcticdem
python3 run_pipeline.py filename odm --image_path=/image/location

The arcticdem files need to be placed in a folder at the same location as the code, named 'arcicdem'. 
The dsm file that results from processing the images will be placed in a folder named 'pyodm_dsm'.
The cleaned dsm will be placed in 'cleaned_dsm'.

The results from the statistical extraction will be in the results folder, with the plots in the 'figures' folder, the stats file per map in the 'stats' folder and the packing fraction and iceberg detection results from each map will be added to the json file 'iceberg_stats' according to the filename.
