import argparse
from create_dsm import create_dsm_using_pyodm
from preprocessing_dsm import preprocess_dsm
from stats_extraction import extract_statistics
from pathlib import Path

# python3 run_pipeline.py filename arcticdem
# python3 run_pipeline.py filename odm --image_path=/image/location

parser = argparse.ArgumentParser(description = 'Extract statistics from existing ArcticDEM or from processing images using pyODM.')
parser.add_argument('filename', help='Name of the file to process.')
parser.add_argument('method', choices=['arcticdem','odm'], help = 'Use existing ArcticDEM file (arcticdem) or process raw images using pyODM (odm).')
parser.add_argument('--image_path', help = 'Path to the raw images that need processing using pyODM.')

args = parser.parse_args()

if args.method == 'odm':        
    #first check if the dsm already exists, otherwise make it and run the pyodm
    dsm_path = Path('./pyodm_dsm/' + args.filename + '/odm_dem/')
    if dsm_path.exists():
        print('Dsm already exists, cleaning now...')
    else:
        # if the image path was not given, throw error message
        if args.image_path is None:
            parser.error("--image_path is required when using ODM processing.")
        dsm_path = create_dsm(args.image_path)
    cleaned_dsm_path = preprocess_dsm(dsm_path, args.filename)
elif args.method == 'arcticdem':
    cleaned_dsm_path = Path('./arcticdem/' + args.filename + '.tif')
    if not cleaned_dsm_path.exists():
        print('Given ArcticDEM does not exist.')

extract_statistics(cleaned_dsm_path, args.filename, window_size=5)