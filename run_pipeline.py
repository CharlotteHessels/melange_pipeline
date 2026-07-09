import argparse
from create_dsm import create_dsm_using_pyodm
from preprocessing_dsm import preprocess_dsm
from stats_extraction import extract_statistics
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("image_folder")
parser.add_argument("flight_name")

args = parser.parse_args()

#first check if the dsm already exists, otherwise make it and run the pyodm
dsm_path = Path('./pyodm_dsm/' + args.flight_name + '/odm_dem/')
if dsm_path.exists():
    print('Dsm already exists, cleaning now...')
else:
    dsm_path = create_dsm(args.image_folder)
cleaned_dsm_path = preprocess_dsm(dsm_path, args.flight_name)
extract_statistics(cleaned_dsm_path, args.flight_name, window_size=5)