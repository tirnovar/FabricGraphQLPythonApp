from requests import request
import json2html
import tkinter as tk
import tkinter.ttk as ttk

def flatten(listOfLists):
    return [row for list in listOfLists for row in list]

def configReader(fileName):
    with open(fileName,"r") as config:
        configReader = config.read().split("\n")
        endpoint = configReader[0]
        tenantid = configReader[1]
        clientid = configReader[2]
        secret = configReader[3]
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

    def __send_request(self, method, url, headers={}, body={}, json={}):
        if body != {}:
            response = request(method, url, headers=headers, data=body)
        else:
            response = request(method, url, headers=headers, json=json)
        return self.__handle_response(response)
    
    def __send_autorized_request(self, method, url, body = {}):
        if self.__access_token == "": self.__get_access_token()

        headers = {
            "Authorization": self.__access_token,
            "Content-Type": "application/json"
        }

        response = self.__send_request(method, url, headers = headers, json=body)
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

query = """
query{
    obligatory_Exams{
        items{
            ExamCode
        }
    }
}"""

graph_ql_handler = GraphQLHandler(endpoint, tenantid, clientid, secret)
responseJson = graph_ql_handler.send_ql_query({"query":query})

root = tk.Tk()
root.title("GraphQL Data")


# Table
treeview = ttk.Treeview(root,show="headings",columns=("ExamCode"))
treeview.heading("#1", text="ExamCode")
treeview.grid(column=0, row=0,columnspan = 2)

print(responseJson)

for row in responseJson:
    treeview.insert("", "end", values=(row["ExamCode"]))

updateButton = tk.Button(root, text="Add", command=lambda: print("Add")).grid(column=0, row=1) 
delete = tk.Button(root, text="Delete", command=lambda: print("Delete")).grid(column=1, row=1)

root.mainloop()