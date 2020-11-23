import json
import subprocess
import boto3

CODESET = 'utf-8'


def extract_json(line):
    jsonStart = jsonStart = line.index("{")
    jsonEnd = len(line) - line[::-1].index("}")
    return json.loads(line[jsonStart:jsonEnd])


# load json input for transformer
with open('req.json') as json_data:
    jsonReq = json.load(json_data)

try:
    # invoke transform service and pass parameters (in json)
    output = subprocess.run(
        ["./transformService.sh", json.dumps(jsonReq)], capture_output=True, check=True)
except subprocess.CalledProcessError as e:
    # print errors
    print("An error occured while running the script, please review the following:")
    print("-- stdout: {}{}".format("\n", str(e.stdout, CODESET)))
    print("-- stderr: {}{}".format("\n", str(e.stderr, CODESET)))
else:
    # extract json response
    jsonResp = extract_json(str(output.stdout, CODESET))

    # get transformed object key
    outObjKey = jsonResp['outputNames'][0]

    # load s3 vars
    with open('s3vars.json') as json_data:
        s3vars = json.load(json_data)

    # get transformed object
    client = boto3.client('s3', aws_access_key_id=s3vars['aws_key_id'],
                          aws_secret_access_key=s3vars['aws_key_secret'])
    obj = client.get_object(Bucket=s3vars['aws_s3_bucket'], Key=outObjKey)
    body = obj['Body'].read()
    transformed = str(body, CODESET)

    # print result
    print('Item transformed successfully!')
    print('-- Output:')
    print(transformed)
