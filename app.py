from requests import request
import json2html
import tkinter as tk

def flatten(listOfLists):
    return [row for list in listOfLists for row in list]

def configReader(fileName):
    config = open(fileName,"r") 
    configReader = config.read().split("\n")
    endpoint = configReader[0]
    tenantid = configReader[1]
    clientid = configReader[2]
    secret = configReader[3]
    config.close()
    return endpoint, tenantid, clientid, secret

class GraphQLHandler:
    def __init__(self, url, tenant_id, client_id, client_secret):
        self.__url = url
        self.__tenant_id = tenant_id
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__access_token = ""

    def __handle_response(self, response):
        response.raise_for_status()
        body = None
        if ("json" in response.headers["Content-Type"]):
            try:
                body = response.json()
            except:
                body = response.text
        elif ("octet-stream" in response.headers["Content-Type"]):
            body = response.content
        elif ("text/plain" in response.headers["Content-Type"]):
            body = response.json()
        else:
            body = response.text

        return {
            'status_code': response.status_code,
            'headers': response.headers,
            'body': body
        }

    def __send_request(self, method, url, headers={}, body={}):
        response = request(method, url, headers=headers, data=body)
        return self.__handle_response(response)
    
    def __send_autorized_request(self, method, url, body = {}):
        if self.__access_token == "": self.__get_access_token()

        headers = {
            "Authorization": self.__access_token,
            "Content-Type": "application/json"
        }

        response = self.__send_request(method, url, headers = headers, body=body)
        return response
    
    def __get_access_token(self):
        url = f'https://login.microsoftonline.com/{self.__tenant_id}/oauth2/v2.0/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        scope = 'https://api.fabric.microsoft.com/.default'
        body = {
                "grant_type": "client_credentials",
                "client_id": self.__client_id,
                "client_secret": self.__client_secret,
                "scope": scope
            }
        response = self.__send_request("POST", url, headers, body)
        self.__access_token = "Bearer " + response["body"]["access_token"]
    
    def send_ql_query(self, query):
        response = self.__send_autorized_request("POST", self.__url, body = query)["body"]
        return response["data"]["obligatory_Exams"]["items"]


endpoint, tenantid, clientid, secret = configReader("config.txt")

query = '{"query":"query{obligatory_Exams{items{ExamCode}}}"}'

graph_ql_handler = GraphQLHandler(endpoint, tenantid, clientid, secret)
df = graph_ql_handler.send_ql_query(query)
print(df)