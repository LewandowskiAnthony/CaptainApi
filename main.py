import json
import sys

from colorama import Fore
from colorama import Style
from datetime import datetime, timezone
import requests as requests

environment_json = open(sys.argv[1])

class Api:
    def __init__(self, url, key, env, test_data, name, field_to_check):
        self.url = url
        self.key = key
        self.env = env
        self.test_data = test_data
        self.name = name
        self.field_to_check = field_to_check


# Object containing API urls
class ApiUrls:
    def __init__(self, url, test_endpoint):
        self.url = url
        self.test_endpoint = test_endpoint


data = json.load(environment_json)
auth_information = data['authentication']
running_information = data['running_variable']
api_information = data['apis']

debug_mode = running_information['debug_mode']

# oAuth2 information
clientId = auth_information['clientId']
clientSecret = auth_information['client_secret']
oAuth2Url = auth_information['oAuth2Url']
auth_data = {
    'client_id': clientId,
    'client_secret': clientSecret,
}

apiList = []
for current_api_info in api_information:
    apiList.append(Api(ApiUrls(current_api_info["url"],
                               f'{current_api_info["url"]}{current_api_info["test_endpoint"]}{current_api_info["test_value"]}'),
                       current_api_info["x-api-key"], current_api_info["x-env"],
                       current_api_info["test_value"], current_api_info["api_name"], current_api_info["field_to_check"]))

# Is used to concert a string with a LocalDateTime to a python datetime format
def convert_utc_string_date_to_datetime(date_to_convert):
    date_to_convert = date_to_convert.replace('T', ' ')
    date_to_convert = date_to_convert.replace('Z', '')
    result = date_to_convert.split('.')
    return result[0]


# Get an access token from fedid using oAuth2 registration
def return_access_token(oAuth2Url, auth_data):
    if debug_mode:
        print(f'Authentication URL : {oAuth2Url}')
        print(f'Auth Datas : {auth_data}')
    # Get the access token
    response = requests.post(oAuth2Url, data=auth_data)
    return response.json()['access_token']


# Will check that the response of the api for the entity recovery is coherent
def api_response_test(api_call_response, field, api_name):
    if api_call_response.status_code == 200 and (
            field in api_call_response.json() or field in api_call_response.json()[0]):
        print(f'{Fore.GREEN} {api_name} API Responded correctly {Style.RESET_ALL}')
    else:
        print(f'{Fore.RED} Error in  {api_name} API Call, please, check your deployment {Style.RESET_ALL}')


# Will test the actuator/info endpoint of the API and will make a call to retrieve information
def test_api_and_return_entity(url, api_key, x_env, api_name, token, version="v1"):
    # Available Shipment Legacy validation
    print(f'{Fore.BLUE}\n -------------------- Testing : {api_name} API -------------------- {Style.RESET_ALL}')

    api_response = requests.get(f'{url.url}/actuator/info', headers={'Authorization': 'Bearer ' + token,
                                                                     'x-api-key': api_key,
                                                                     'x-env': x_env})
    if api_response.status_code != 200:
        api_response = requests.get(f'{url.url}/api/{version}/actuator/info', headers={'Authorization': 'Bearer ' + token,
                                                                         'x-api-key': api_key,
                                                                         'x-env': x_env})
    if debug_mode:
        print(api_response)
        print(api_response.json())
        print(f'API URL : {url.url}')
        print(f'Endpoint to test : {url.test_endpoint}')
        print(f'Token : {token}')
        print(f'Auth Datas : {auth_data}')

    if api_response.status_code == 200:
        currentTime = datetime.now()
        version = api_response.json()['app']['version']
        build_date = datetime.strptime(convert_utc_string_date_to_datetime(api_response.json()['app']['build']['date']),
                                       '%Y-%m-%d %H:%M:%S')
        print(f'{Fore.GREEN} Successfully retrieved {api_name} API information. {Style.RESET_ALL}')
        if (currentTime - build_date).days >= 1:
            print(
                f'{Fore.YELLOW} Warning : The version build date is not from today : {build_date} {Style.RESET_ALL}')

        api_response = requests.get(f'{url.test_endpoint}/',
                                    headers={'Authorization': 'Bearer ' + token,
                                             'x-api-key': api_key,
                                             'x-env': x_env})

        if debug_mode:
            print(json.dumps(api_response.json(), indent=2))

        return api_response

    else:
        print(
            f'{Fore.RED} Error, cannot contact  {api_name} API - Please check your deployment. {Style.RESET_ALL}')


# Main function
def main():
    access_token = return_access_token(oAuth2Url, auth_data)

    for current_api in apiList:
        response = test_api_and_return_entity(current_api.url, current_api.key, current_api.env, current_api.name,
                                              access_token)
        api_response_test(response, current_api.field_to_check, current_api.name)


if __name__ == "__main__":
    main()
