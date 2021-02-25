import urllib
import urllib.request
from urllib.error import URLError, HTTPError
import json
import math


def unskilledWorkerDaysPredict(year,month,volume):

    data =  {
            "Inputs": {
                    "input1":
                    {
                        "ColumnNames": ["dim_volume"],
                        "Values": [ [ str(volume) ]]
                    },        
                },
            "GlobalParameters": {}
    }

    body = str.encode(json.dumps(data))

    url = 'https://ussouthcentral.services.azureml.net/workspaces/9ca4a891224a4c69a511634dfae36a7d/services/29a92a77a0d8406192c0bfecb4252390/execute?api-version=2.0&details=true'
    api_key = 'TRniDcPijSRDHVLe5xd20FpONRRDEa8gO6zN0avCDDNGcdDQwL/lJlGbP7v7+WuCvnvm/fRjpBjg9TM5lsJzBw==' # Replace this with the API key for the web service
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers) 

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        json_results = json.loads(result)
        #print(json_results)

        return math.ceil(float(json_results['Results']['output1']['value']['Values'][0][-1]))
    except HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())

        print(json.loads(error.read()))
        return False

if __name__ == '__main__':
    answer = unskilledWorkerDaysPredict(12,1,0.2)
    print(answer, "days")