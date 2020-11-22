import json
import subprocess

# load json input for transformer
with open('req.json') as json_data:
    jsonReq = json.load(json_data)

# invoke transform service and pass parameters (in json)
subprocess.run(["./transformService.sh", json.dumps(jsonReq)])
