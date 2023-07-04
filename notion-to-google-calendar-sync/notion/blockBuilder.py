import json

class blockBuilder:
    block = {
        'object': 'block',
    }
    def __init__(self, type: str):
        self.__setType(type)
    
    def __setType(self, type: str):
        self.block['type'] = type
        self.block[type] = {}
    
    def addRitchText(self, richText):
        try:
            self.block[self.block['type']]['rich_text'] += [richText]
            print('append')
        except :
            self.block[self.block['type']]['rich_text'] = [richText]
            print('add')
