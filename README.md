# dockerguide

# Get started

* Create a new virtual environment (in cmd)
```Bash 
conda create -n dockerguide_env python=3.11
```

* Activate environment (in cmd)
```Bash
conda activate dockerguide_env
```

* Install requirements
```Bash
conda install -c conda-forge cupy
pip install pybids
pip install ./cross_analytics-master
```

* Run code locally
```Bash
python main.py ../dati
```

* Build docker image
```Bash
docker build -t <dockerhubusername>/clinicianscode:latest <folderpath>
```





* Run docker image locally
```Bash
docker run --rm --gpus all -v ../dati:/dati <dockerhubusername>/clinicianscode /dati
```

* Pull the docker code from the repository
```Bash
docker pull <dockerhubusername>/clinicianscode