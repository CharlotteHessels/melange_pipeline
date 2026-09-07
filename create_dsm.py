from pyodm import Node, exceptions
from pathlib import Path
import os, shutil


def apply_mask(image_folder, mask_template_path):
    """Copy a single mask template to a _mask.png file for every photo in image_folder."""
    image_folder = Path(image_folder)
    mask_template_path = Path(mask_template_path)

    photo_exts = ("*.jpg", "*.JPG", "*.jpeg", "*.JPEG")
    photos = [f for ext in photo_exts for f in image_folder.glob(ext)]

    print(f"Applying mask template to {len(photos)} images...")
    for photo in photos:
        dest = image_folder / f"{photo.stem}_mask.png"
        shutil.copy(mask_template_path, dest)
        

def create_dsm_using_pyodm(image_folder, flight_name, mask=None):
    image_folder = Path(image_folder)

    if mask is not None:
        apply_mask(image_folder, mask)
        
    photo_exts = ("*.jpg", "*.JPG", "*.jpeg", "*.JPEG")
    photos = [f for ext in photo_exts for f in image_folder.glob(ext)]
    masks = image_folder.glob("*_mask.png")
    image_files = sorted([str(f) for f in list(photos) + list(masks)])

    node = Node('localhost', 3000)
    
    try:
        # Start a task
        print("Uploading images...")
        task = node.create_task(
            image_files,
            {"dsm": True},
        )
        print(task.info())
    
        try:
            # Block until the task is finished
            task.wait_for_completion()
    
            print("Task completed, downloading results...")
            task.download_assets("./pyodm_dsm/" + flight_name)
            print("Assets saved in ./pyodm_dsm/" + flight_name)
            
            dsm_path = './pyodm_dsm/' + flight_name + '/odm_dem/'

            return dsm_path
                
        except exceptions.TaskFailedError as e:
            print("\n".join(task.output()))
    
    except exceptions.NodeConnectionError as e:
        print("Cannot connect: %s" % e)
    except exceptions.NodeResponseError as e:
        print("Error: %s" % e)