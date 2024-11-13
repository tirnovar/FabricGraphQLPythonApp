from requests import request
from graphql_query import Operation, Query, Field
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
        print("Data requested...")
        response = self.__send_request(method, url, headers = headers, json=body)
        print("Data received...")
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
        print("Access token requested...")
        self.__access_token = "Bearer " + response["body"]["access_token"]
        print("Access token received.")
    
    def send_ql_query(self, query, tableName):
        response = self.__send_autorized_request("POST", self.__url, body = query)["body"]
        return response["data"][tableName]["items"]

class UIBuilder:
    def __init__(self, receivedData = [{"Data": "Loading..."}]):
        self.__root = tk.Tk()
        self.__data = receivedData

    def __run(self):
        print("App loading...")
        self.__root.mainloop()
        print("App closed.")

    def __build_menu(self):
        menu = tk.Menu(self.__root)
        self.__root.config(menu=menu)
        filemenu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=lambda: print("New"))
        filemenu.add_command(label="Open...", command=lambda: print("Open"))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.__root.quit)

        helpmenu = tk.Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=lambda: print("About"))


    def __build_table(self, data):
        columns = list(data[0].keys())
        __treeview = ttk.Treeview(self.__root,show="headings",columns=columns)

        id = 0
        for column in columns:
            id += 1
            __treeview.heading(f"#{id}", text=column)
            
        __treeview.grid(column=0, row=0,columnspan = 2 if id < 2 else id)

        for row in data:
            __treeview.insert("", "end", values=list(row.values()))

        return __treeview
    
    def __build_buttons(self, title, position_col, position_row):
        return tk.Button(self.__root, text=title, command=lambda: print(title)).grid(column=position_col, row=position_row) 

    def build_app(self, title):
        graph_ql_handler = GraphQLHandler(endpoint, tenantid, clientid, secret)
        self.__data = graph_ql_handler.send_ql_query({"query":query},tableName)
        self.table_with_values = self.__build_table(self.__data)

        print("Building app:")
        self.__root.title(title)
        self.table_with_values = self.__build_table(self.__data)
        print(" Table created...")
        self.update_button = self.__build_buttons("Update", 0, 1)
        self.delete_button = self.__build_buttons("Delete", 1, 1)
        print(" Buttons created...")
        self.__run()


endpoint, tenantid, clientid, secret = configReader("config.txt")

tableName = "certification_Mappings"
fields = ["certificationUid", "examCode"]

querySetup = Query(name=tableName, fields=[Field(name="items", fields=fields)])
query = Operation(type='query', queries=[querySetup]).render()
print("Query prepared for execution.")

ui_builder = UIBuilder()
ui_builder.build_app("GraphQL Data")