# CaptainApi

## What is Captain API ?
Captain API is a small API tester which allows you to test if your API has been well deployed on you distant server.
It supports oAuth2 authentication using Client ID/Secret.
All the needed datas concerning your API must be filled inside the environment.json file
## How to start ?
### Install python3
First of all, the most important thing is to install you python environment on your engine.
This project has been made using Python 3, so we recommend you to install the latest Python 3 version : 
https://www.python.org/downloads/
### Install needed package
```
python3 -m pip install colorama requests datetime
```
### Fill the json environment file
#### Fields
The json environment file contain 3 different types of information : 

| Name             | Purpose                                                                                                                    | Example                                                                                                  |
|------------------|----------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| running_variable | All the variables that can affect the output display and behavior                                                          | The debug_mode variable allows you to enter in debug mode and shows you what is going on behind the code |
| authentication   | All the informations you'll need to authenticate to your API using oAuth2 authentication                                   | the client_id                                                                                            |
| apis             | This field in an array containing all your APIs informations. Captain API will check test every API mentioned in this part | url which is the URL of your API without the versioning                                                  |

#### Example
Here's an example to completion for an API test, admitting you want to test an api which follows this url : <br>
http://my-super-api/api/v1/clients/1000
Admitting this is the endpoint to test you'll have to fill the environment.json as : 
```
"apis": [
    {
      "url": "http:/my-super-api/",
      "test_endpoint": "api/v1/clients/",
      "x-api-key": "YOUR_API_KEY",
      "x-env": "YOU X-ENV",
      "test_value": 1000,
      "api_name": "My Super Api",
      "field_to_check": "a field of your DTO to check it returns the right entity"
    }
]
```
### Start the project
You can start the script using your command line : 
```
python3 main.py environment.json
```
![img.png](img/img.png)

