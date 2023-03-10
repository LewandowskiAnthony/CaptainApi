import json
import sys

from colorama import Fore
from colorama import Style
from datetime import datetime, timezone
import requests as requests

json_path = open(sys.argv[1])


class Api:
    def __init__(self, url, key, env, name, tests):
        self.url = url
        self.key = key
        self.env = env
        self.name = name
        self.tests = tests


# Object containing API tests
class ApiTests:
    def __init__(self, name, endpoint, value, must_be_present_field, http_method):
        self.name = name
        self.endpoint = endpoint
        self.value = value
        self.must_be_present_field = must_be_present_field
        self.http_method = http_method
        self.test_endpoint = "{}/{}".format(endpoint, value)


# Global variables definition
# Json fields
data = json.load(json_path)
auth_information = data['authentication']
running_information = data['running_variable']
api_information = data['apis']

# Debug mode to activate logs
debug_mode = running_information['debug_mode']

# oAuth2 information
clientId = auth_information['clientId']
clientSecret = auth_information['client_secret']
oAuth2Url = auth_information['oAuth2Url']
auth_data = {
    'client_id': clientId,
    'client_secret': clientSecret,
}

# Retrieve list of defined APIs
apiList = []
for current_api_info in api_information:
    apiTestsList = []

    # For each API, retrieve the list of test to execute
    for current_api_test in current_api_info["tests"]:
        apiTestsList.append(
            ApiTests(current_api_test["test_name"], current_api_test["test_endpoint"], current_api_test["test_value"],
                     current_api_test["field_to_check"], current_api_test["http_method"]))

    # Put every API inside a LIST of API Objects
    apiList.append(Api(current_api_info["url"],
                       current_api_info["x-api-key"], current_api_info["x-env"],
                       current_api_info["api_name"], apiTestsList))


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


# Will test the actuator/info endpoint of the API and will make a call to retrieve information
def test_api_health_endpoint(url, api_key, x_env, api_name, token, version="v1"):
    # Available Shipment Legacy validation
    print(f'{Fore.BLUE}\n -------------------- Testing : {api_name} API -------------------- {Style.RESET_ALL}')

    api_response = requests.get(f'{url}/actuator/info', headers={'Authorization': 'Bearer ' + token,
                                                                     'x-api-key': api_key,
                                                                     'x-env': x_env})
    if api_response.status_code != 200:
        api_response = requests.get(f'{url}/api/{version}/actuator/info',
                                    headers={'Authorization': 'Bearer ' + token,
                                             'x-api-key': api_key,
                                             'x-env': x_env})
    if debug_mode:
        print(api_response)
        print(api_response.json())
        print(f'API URL : {url}')
        print(f'Token : {token}')
        print(f'Auth Datas : {auth_data}')

    if api_response.status_code == 200:
        currentTime = datetime.now()
        version = api_response.json()['app']['version']
        build_date = datetime.strptime(convert_utc_string_date_to_datetime(api_response.json()['app']['build']['date']),
                                       '%Y-%m-%d %H:%M:%S')
        print(f'{Fore.GREEN} Successfully retrieved {api_name} API information {Style.RESET_ALL}')
        if (currentTime - build_date).days >= 1:
            print(
                f'{Fore.YELLOW} VERSION : {version}. \n Warning : The version build date is not from today : {build_date} {Style.RESET_ALL}')
        else:
            print(
                f'{Fore.WHITE} VERSION : {version}. \n The version build date has been built recently : {build_date} {Style.RESET_ALL}')

    else:
        print(
            f'{Fore.RED} Error, cannot contact  {api_name} API - Please check your deployment. {Style.RESET_ALL}')


# Test a real endpoint of the API and check if the given field is in the returned body
def test_real_endpoint(current_api, test, access_token):
    print(
                f'{Fore.LIGHTGREEN_EX} ---------- Launching test : {test.name} ---------- {Style.RESET_ALL}')
    api_response = requests.get(f'{current_api.url}/{test.test_endpoint}',
                                headers={'Authorization': 'Bearer ' + access_token,
                                         'x-api-key': current_api.key,
                                         'x-env': current_api.env})
    if debug_mode:
        print(json.dumps(api_response.json(), indent=2))

    if api_response.status_code == 200 and (
            test.must_be_present_field in api_response.json() or test.must_be_present_field in api_response.json()[0]):
        print(f'{Fore.GREEN} {current_api.name} - Test {test.name} executed successfully {Style.RESET_ALL}')
    else:
        print(f'{Fore.RED} Error in {current_api.name} - {test.name} API Call, please, check your deployment {Style.RESET_ALL}')

    return api_response


# Main function
def main():
    access_token = return_access_token(oAuth2Url, auth_data)

    for current_api in apiList:
        test_api_health_endpoint(current_api.url, current_api.key, current_api.env, current_api.name,
                                 access_token)

        for test in current_api.tests:
            test_real_endpoint(current_api, test, access_token)


if __name__ == "__main__":
    main()
