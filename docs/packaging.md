# Packaging

To package your extension and prepare it for deployment on Oloren Orchestrator you must satisfy the following criteria:

- Published to a repository on Github, it may be public or private.
- Contains a Dockerfile at the root, which launches the entrypoint file (the one which contains the {py:obj}`oloren.server.run` call). Here is a minimal Dockerfile example:

  ```dockerfile
  FROM python:3.10-slim-bullseye
  RUN pip install oloren
  COPY app.py .
  CMD python app.py
  ```

- Optionally, contains a `config.json` file. If specified the config.json file takes the following form:

  ```json
  {
    "cpu": 1024,
    "memory": 8192,
    "storage": 25
  }
  ```

  - The CPU refers to the number of CPU cores available.
  - The memory must be specified in units of MB.
  - The storage must be a value between 25 - 200, in units of GB
  - The following configurations are valid as defined in the [AWS Documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html#w354aac15c27c21b9b1b3c13):

    | CPU value      | Memory value                                |
    | -------------- | ------------------------------------------- |
    | 256 (.25 vCPU) | 512 MiB, 1 GB, 2 GB                         |
    | 512 (.5 vCPU)  | 1 GB, 2 GB, 3 GB, 4 GB                      |
    | 1024 (1 vCPU)  | 2 GB, 3 GB, 4 GB, 5 GB, 6 GB, 7 GB, 8 GB    |
    | 2048 (2 vCPU)  | Between 4 GB and 16 GB in 1 GB increments   |
    | 4096 (4 vCPU)  | Between 8 GB and 30 GB in 1 GB increments   |
    | 8192 (8 vCPU)  | Between 16 GB and 60 GB in 4 GB increments  |
    | 16384 (16vCPU) | Between 32 GB and 120 GB in 8 GB increments |
