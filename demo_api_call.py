import urllib
from urllib.error import URLError, HTTPError
import urllib.request

import json 

def demoApiCall(grade,year,month,volume):
    data =  {

            "Inputs": {

                    "input1":
                    {
                        "ColumnNames": ["grade", "year", "month", "dim_volume"],
                        "Values": [ [ str(grade), str(year), str(month), str(volume) ] ]
                    },        },
                "GlobalParameters": {
    }
        }

    body = str.encode(json.dumps(data))

    url = 'https://ussouthcentral.services.azureml.net/workspaces/9ca4a891224a4c69a511634dfae36a7d/services/2c9855009faa4d1a9368ae8898c635a1/execute?api-version=2.0&details=true'
    api_key = 'kEx1VOC4iIIwr6tQcLP398fU88CieGiM6ewjOOeYBGqIgtKk/FLa8GlD5MfECMgETfOKE3Ng/D9gPz5olCUrTA==' # Replace this with the API key for the web service
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)

        # If you are using Python 3+, replace urllib2 with urllib.request in the above code:
        # req = urllib.request.Request(url, body, headers) 
        # response = urllib.request.urlopen(req)

        result = response.read()
        print(result)
        json_value = json.loads(result)

        return float(json_value['Results']['output1']['value']['Values'][0][-1])
    except HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())

        print(json.loads(error.read()))
        return False

if __name__ == '__main__':
    ans = demoApiCall(15,2020,3,9)
    print(ans,"LKR")