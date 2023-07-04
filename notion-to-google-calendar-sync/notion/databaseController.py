import json
import http
import requests
from notion.base import base as base

class databaseController(base):
    # DBのID URLから確認
    dbid = ''
    
    def __init__(self, integrationSecret, dbid):
        super().__init__(integrationSecret)
        self.dbid = dbid

    def allPageProcessor(self, closure):
        requestBody = {}
        pagesList = []
        while True:
            response = self.apiRequestController('query', {'databaseId': self.dbid}, json.dumps(requestBody))
            body = json.loads(response.text)
            pagesList.extend(body['results'])
            for page in pagesList:
                closure(page)
            if body['next_cursor'] != None:
                requestBody = {'start_cursor': body['next_cursor'], 'page_size': 10}
            else:
                return

    def propertyToText(self,property):
        type = property['type']
        text = ""
        # print(property)
        if type == 'title' :
            for item in property[type]:
                text += item['plain_text']
        elif type == 'rich_text' :
            for item in property[type]:
                text += item['text']['content']
        elif type == 'date':
            text += property[type]["start"]
            if property[type]['end'] != None:
                text += "~" + property[type]['end']
        elif type == 'paragraph':
            for item in property[type]['text']:
                text += item['text']['content']
        elif type == 'relation':
            for item in property[type]:
                page = self.retrievePage(item['id'])
                # タイトルプロパティの絞り込み
                for key, property in page['properties'].items():
                    if property['id'] == 'title':
                        title = property
                        break
                text += self.propertyToText(title) + ', '
            # TODO: 他のパターンも対応する。
        return text
    
    def updatePage(self, pageId, properties):
        response = self.apiRequestController('updatePage', {'pageId':pageId}, json.dumps({"properties":properties}))
        print(response.text)
        return json.loads(response.text)
    
    # Authentication
    def createToken(self, data):
        response = self.apiRequestController('createToken', data=json.dumps(data))
        return json.loads(response.text)

    # Blocks
    def appendBlockChildren(self, blockId, data):
        response = self.apiRequestController('appendBlockChildren', params={'blockId': blockId}, data=json.dumps(data))
        return json.loads(response.text)

    def retrieveBlock(self, blockId):
        response = self.apiRequestController('retrieveBlock', params={'blockId': blockId})
        return json.loads(response.text)

    def retrieveBlockChildren(self, blockId):
        response = self.apiRequestController('retrieveBlockChildren', params={'blockId': blockId})
        return json.loads(response.text)

    def updateBlock(self, blockId, data):
        response = self.apiRequestController('updateBlock', params={'blockId': blockId}, data=json.dumps(data))
        return json.loads(response.text)

    def deleteBlock(self, blockId):
        response = self.apiRequestController('deleteBlock', params={'blockId': blockId})
        return response.status_code == 200

    # Pages
    def createPage(self, data):
        response = self.apiRequestController('createPage', data=json.dumps(data))
        return json.loads(response.text)

    def retrievePage(self, pageId):
        response = self.apiRequestController('retrievePage', params={'pageId': pageId})
        return json.loads(response.text)

    def retrievePageProperty(self, pageId, propertyId):
        response = self.apiRequestController('retrievePageProperty', params={'pageId': pageId, 'propertyId': propertyId})
        return json.loads(response.text)

    def updatePageProperties(self, pageId, properties):
        response = self.apiRequestController('updatePageProperties', params={'pageId': pageId}, data=json.dumps({"properties":properties}))
        return json.loads(response.text)

    def archivePage(self, pageId):
        response = self.apiRequestController('archivePage', params={'pageId': pageId})
        return json.loads(response.text)

    # Databases
    def createDatabase(self, data):
        response = self.apiRequestController('createDatabase', data=json.dumps(data))
        self.dbid = json.loads(response.text)['id']
        return json.loads(response.text)

    def queryDatabase(self, data):
        response = self.apiRequestController('queryDatabase', params={'databaseId': self.dbid}, data=json.dumps(data))
        return json.loads(response.text)
    
    def queryDatabaseAllPages(self, data):
        pagesList = []
        while True:
            response = self.apiRequestController('queryDatabase', params={'databaseId': self.dbid}, data=json.dumps(data))
            response = json.loads(response.text)
            pagesList.extend(response['results'])
            if response['has_more']:
                data = {'start_cursor': response['next_cursor'], 'page_size': 10}
            else:
                break
        return pagesList

    def retrieveDatabase(self):
        response = self.apiRequestController('retrieveDatabase', params={'databaseId': self.dbid})
        return json.loads(response.text)

    def updateDatabase(self, data):
        response = self.apiRequestController('updateDatabase', params={'databaseId': self.dbid}, data=json.dumps(data))
        return json.loads(response.text)
    
    # Users
    def listAllUsers(self):
        response = self.apiRequestController('listAllUsers')
        return json.loads(response.text)

    def retrieveUser(self, userId):
        response = self.apiRequestController('retrieveUser', params={'userId': userId})
        return json.loads(response.text)

    def retrieveBotUser(self):
        response = self.apiRequestController('retrieveBotUser')
        return json.loads(response.text)

    # Comments
    def createComment(self, data):
        response = self.apiRequestController('createComment', data=json.dumps(data))
        return json.loads(response.text)

    def retrieveComments(self, blockId):
        response = self.apiRequestController('retrieveComments', params={'blockId': blockId})
        return json.loads(response.text)

    # Search
    def searchByTitle(self, data):
        response = self.apiRequestController('searchByTitle', data=json.dumps(data))
        return json.loads(response.text)