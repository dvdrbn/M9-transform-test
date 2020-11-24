import json
import subprocess
import boto3

CODESET = 'utf-8'


def extract_json(line):
    """Return a json object if it exists in a string"""
    jsonObj = None

    if '{' in line and '}' in line:
        jsonStart = line.find("{")
        jsonEnd = len(line) - line[::-1].find("}")
        jsonObj = json.loads(line[jsonStart:jsonEnd])
    return jsonObj


def stream_print(streamName, streamOut):
    """
    Print stream output returned from script execution. 
    If JSON reponse was received, print it first for better clearance.
    """

    # if stream contained any output
    if streamOut:
        print('{} {}'.format(streamName, '-'*65))
        jResp = extract_json(streamOut)

        # if json response was part of the stream
        if jResp:
            print("Status: {}".format(jResp['status']))
            print("Log:\n{}\n".format("\n".join(jResp['log'])))
        else:
            # service maybe offline if response is empty
            print(
                'No response received from server, it maybe offline. Please try again in a few minutes.')

        # print full stream output
        print('Full {} output:{}{}{}{}'.format(
            streamName, '\n', '-'*19, '\n', streamOut))
    else:
        print('{} had no output'.format(streamName))


# load json input for transformer
with open('request.json') as json_data:
    jsonReq = json.load(json_data)

try:
    # invoke transform service and pass parameters (in json)
    output = subprocess.run(
        ["./transformService.sh", json.dumps(jsonReq)], capture_output=True, check=True)
except subprocess.CalledProcessError as e:
    # print errors
    print("An error occured while running the script, please review the following:")
    stream_print('stdout', str(e.stdout, CODESET))
    stream_print('stderr', str(e.stderr, CODESET))
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
