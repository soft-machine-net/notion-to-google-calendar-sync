import requests
import logging
import json

class base:
    # APIのベースURL
    apiUrl = "https://api.notion.com"
    # APIバージョン 今のとこ使用予定なし
    apiVersion = 'v1'
    # 各APIのリクエストURL
    apiEndpoints ={
        # Authentication
        'createToken':            { 'method': 'post'   , 'path': '/v1/oauth/token'}, 
        # Blocks
        'apopendBlockChildren':   { 'method': 'patch'  , 'path': '/v1/blocks/{blockId}/children',},
        'retrieveBlock':          { 'method': 'get'    , 'path': '/v1/blocks/{blockId}',},
        'retrieveBlockChildren':  { 'method': 'get'    , 'path': '/v1/blocks/{blockId}/children',},
        'updateBlock':            { 'method': 'patch'  , 'path': '/v1/blocks/{blockId}'},
        'deleteBlock':            { 'method': 'delete' , 'path': '/v1/blocks/{blockId}'},
        # Pages
        'createPage':             { 'method': 'post'  , 'path': '/v1/pages', },
        'retrievePage':           { 'method': 'get'   , 'path': '/v1/pages/{pageId}', },
        'regrievePageProperty':   { 'method': 'get'   , 'path': '/v1/pages/{pageId}/properties/{propertyId}', },
        'updatePageProperties':   { 'method': 'patch' , 'path': '/v1/pages/{pageId}'},
        'archivePage':            { 'method': 'patch' , 'path': '/v1/pages/{pageId}'},
        # Databases
        'createDatabase':         { 'method': 'post'  , 'path': '/v1/databases'},
        'queryDatabase':          { 'method': 'post'  , 'path': '/v1/databases/{databaseId}/query'},
        'retriveDatabase':        { 'method': 'get'   , 'path': '/v1/databases/{databaseId}'},
        'updateDatabase':         { 'method': 'patch' , 'path': '/v1/databases/{databaseId}'},
        # Users
        'listAllUsers':           { 'method': 'get'   , 'path': '/v1/users', },
        'retriveUser':            { 'method': 'get'   , 'path': '/v1/users{userId}', },
        'retriveBotUser':         { 'method': 'get'   , 'path': '/v1/users/me'},
        # Comments
        'createComment':          { 'method': 'post'  , 'path': '/v1/comments'},
        'retriveComments':        { 'method': 'get'   , 'path': '/v1/comments?block_id={blockId}', },
        # Search
        'searchByTitle':          { 'method': 'post'  , 'path': '/v1/search', },
    }
    # 共通のHTTPヘッダー
    headers = {
            'Authorization': 'Bearer {integrationSecret}',
            'Content-Type': 'application/json',
            'Notion-Version': '2021-08-16',
        }
    integrationSecret = ''
    def __init__(self, integrationSecret):
        self.integrationSecret = integrationSecret
        self.headers['Authorization'] = self.headers['Authorization'].format(integrationSecret=self.integrationSecret)
        
    def apiRequestController(self, apiName, params = {}, data = None):
        endpoint = self.apiEndpoints[apiName]
        if endpoint['method'] == 'get':
            response = requests.get(self.apiUrl + endpoint['path'].format(**params), headers = self.headers)
        elif endpoint['method'] == 'post':
            response = requests.post(self.apiUrl + endpoint['path'].format(**params), headers = self.headers, data = data)
        elif endpoint['method'] == 'patch':
            response = requests.patch(self.apiUrl + endpoint['path'].format(**params), headers = self.headers, data = data)
        elif endpoint['method'] == 'delete':
            response = requests.delete(self.apiUrl + endpoint['path'].format(**params), headers = self.headers, data = data)
        else:
            return None
        logging.info('RequestAPI: ' + apiName)
        # 200以外はとりあえず例外
        if response.status_code != 200:
            print(response.text)
            response.raise_for_status()
        return response
    
    def sampleApi(self, pageId):
        response = self.apiRequestController('getPage', {'pageId': pageId})
        print(response.text)
        return json.loads(response.text)