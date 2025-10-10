FROM continuumio/miniconda3

# Avoid interactive messages
ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_ENV_NAME=dockerguide_env

# Create working directory in the container and copy the current folder content there
WORKDIR /app
COPY . .

# Create conda environment
RUN conda env create -f environment.yml

# Activete conda environment when the container starts
SHELL ["conda", "run", "-n", "dockerguide_env", "/bin/bash", "-c"]

# Default command
ENTRYPOINT ["conda", "run", "-n", "dockerguide_env", "python", "main.py"]