import json

class pageBuilder:
    page = {
        'properties': {
            # PageTitle
            'title': {
                'title': [
                    {
                        'text': {
                            'content': ''
                        }
                    }
                ]
            },
        },
        'children': []
    }
    
    def __init__(self, title = 'EmptyPage'):
        self.setTitle(title)


    def __str__():
        return json.dumps(self.page)
            
    def setTitle(self, title):
        self.page['properties']['title']['title'][0]['text']['content'] = title
        
    def getTitle(self):
        return self.page['properties']['title']['title'][0]['text']['content']
    
    def setDescription(self, text):
        self.page['properties']['Description'] = {'rich_text': [{'text':{'content': text}}]}
        
    def addBlock(self, block):
        self.page['children'].append(block)

    def setIcon(self, img):
        pass

    def setCover(self, img):
        pass

    def setProperty(self, name, value):
        pass

    def getProperty(self, propertyName, value):
        self.page['properties'][propertyName]['title'][0]['text']['content'] = value

    def setProperties(self, properties):
        pass

    def getProperties(self, propertyName):
        return self.page[propertyName]

    def getDescription(self):
        self.page['properties']['Description']['rich_text'][0]['text']['content']

    def setUrl(self, propertyName, url):
        self.page['properties'][propertyName] = {'url':url}
        # self.page['properties'][propertyName]['url'] = url
    
    def setSelect(self, propertyName, value):
        self.page['properties'][propertyName] = {'select':{'name':value}}
