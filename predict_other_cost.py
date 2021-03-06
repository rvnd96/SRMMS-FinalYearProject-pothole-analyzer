import urllib
import urllib.request
from urllib.error import URLError, HTTPError
import json


def otherCostPredict(grade,year,month,dim_volume):

    data =  {

        "Inputs": {

                "input1":
                {
                    "ColumnNames": ["grade", "year", "month", "dim_volume"],
                    "Values": [ [ str(grade), str(year), str(month), str(dim_volume) ] ]
                },        },
            "GlobalParameters": {}
    }

    body = str.encode(json.dumps(data))

    url = 'https://ussouthcentral.services.azureml.net/workspaces/9ca4a891224a4c69a511634dfae36a7d/services/72fc319635b742609909555ea44aa2a5/execute?api-version=2.0&details=true'
    api_key = 'FRyQs/tYsEXZZOG/dBwdoLhcuJZG61RyRUvHxqHqHC79klJXXNIdg32GKNXKtT6IZrJ+QmD8Po390rV4lzcI3w==' # Replace this with the API key for the web service
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers) 

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        json_results = json.loads(result)
        print(json_results)

        return float(json_results['Results']['output1']['value']['Values'][0][-1])
    except HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())

        print(json.loads(error.read()))
        return False

if __name__ == '__main__':
    answer = otherCostPredict(25,2020,1,9)
    print(answer, "LKR")