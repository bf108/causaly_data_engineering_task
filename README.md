To create a Docker image and run a container from that image, follow these steps:

1. **Build the Docker Image**: Open a terminal in the directory containing the Dockerfile and run the following command:

```bash
docker build -t causaly-data-pipeline-app-v1 .
```

This command builds a Docker image using the instructions in the Dockerfile in the current directory (`.`). The `-t` option tags the image with the name `causaly-data-pipeline-app-v1`.

2. **Run the Docker Container**: After the image has been built, you can start a container from this image using the following command:

```bash
docker run -d -p 8000:80 causaly-data-pipeline-app-v1
```

This command starts a new Docker container from the `causaly-data-pipeline-app-v1` image. The `-d` option runs the container in detached mode (in the background). The `-p` option maps port 8000 on your local machine to port 80 on the Docker container.

After running this command, the application inside the Docker container should be accessible at `http://localhost:8000`.
