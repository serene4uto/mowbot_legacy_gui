import docker
import argparse
import os   
    
def main():
    parser = argparse.ArgumentParser(description="Start or stop a Docker container.")
    parser.add_argument(
        "--name",
        type=str,
        help="The name of the Docker container to start or stop."
    )
    
    docker_client = docker.from_env()
    
    container_running = False
    container_name = parser.parse_args().name
    
    # Get the host home directory from environment variables
    host_home = os.environ.get("HOST_HOME")
    
    
    # wait for input in terminal to start the container
    while True:
        if not container_running:
            user_input = input("Press Enter to start the container")
            # check if Enter was pressed
            if user_input == "":
                try:
                    container = docker_client.containers.run(
                        auto_remove=True,
                        remove=True,
                        detach=True,
                        privileged=True,
                        name=container_name,
                        network_mode="host",
                        environment={
                            "DISPLAY": ":0.0",
                        },
                        volumes={
                            f"{host_home}/mowbot_legacy_data": {"bind": "/mowbot_legacy_data", "mode": "rw"},
                            "/dev": {"bind": "/dev", "mode": "rw"},
                            "/tmp/.X11-unix": {"bind": "/tmp/.X11-unix", "mode": "rw"}
                        },
                        image="ghcr.io/serene4uto/mowbot-legacy-base",
                        command=[
                            "/bin/bash", 
                            "-c", 
                            ". /opt/mowbot_legacy/setup.bash && \
                            ros2 launch mowbot_legacy_launch gui_wp_localization.launch.py"
                        ],
                    )
                    
                    # wait for the container to start
                    while container.status != "running":
                        container.reload()
                        if container.status == "running":
                            break
                    
                    print(f"Container {container_name} started.")
                    container_running = True

                except docker.errors.NotFound:
                    print(f"Container {container_name} not found.")
                    break
                
        else:
            user_input = input("Press Enter to stop the container")
            # check if Enter was pressed
            if user_input == "":
                try:
                    container = docker_client.containers.get(container_name)
                    container.stop(
                        timeout=1
                    )
                    
                    while True:
                        try:
                            # Try to get the container - if it's removed, this will raise NotFound
                            container = docker_client.containers.get(container_name)
                            # time.sleep(0.5)
                        except docker.errors.NotFound:
                            # Container is fully removed
                            print(f"Container {container_name} has been stopped and removed.")
                            container_running = False
                            break
                        
                except docker.errors.NotFound:
                    print(f"Container {container_name} not found.")
                    break
                
            
    

if __name__ == "__main__":
    main()