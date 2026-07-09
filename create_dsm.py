from pyodm import Node
from pathlib import Path

#flight_name = '30_03_2022_flight3'
#image_folder = Path('/media/chahes/ELIGHT1000/Drone/2022/30_03_2022_flight3')


def create_dsm_using_pyodm(image_folder, flight_name):
    image_files = sorted([str(f) for f in image_folder.glob("*.jpg")])

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
            print("Assets saved in ./pyodm_dsm/" + flight_name % os.listdir('./pyodm_dsm/' + flight_name))
            
            dsm_path = './pyodm_dsm/' + flight_name + '/odm_dem/'

            return dsm_path
                
        except exceptions.TaskFailedError as e:
            print("\n".join(task.output()))
    
    except exceptions.NodeConnectionError as e:
        print("Cannot connect: %s" % e)
    except exceptions.NodeResponseError as e:
        print("Error: %s" % e)