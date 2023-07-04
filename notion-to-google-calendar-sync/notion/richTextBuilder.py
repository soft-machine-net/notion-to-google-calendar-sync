import json

class richTextBuilder:
    typeBlockBases = {
        'text': {
            'content': '',
            'link': None
        },
        'mention': {
            'type': '',
            
        },
        'equation': {
            'expression': ''
        },
    }
    colors = [
            "default",
            "blue","blue_background",
            "brown","brown_background",
            "gray","gray_background",
            "green","green_background",
            "orange","orange_background",
            "pink","pink_background",
            "purple","purple_background",
            "red","red_background",
            "yellow","yellow_background",
        ]
    def __init__(
            self,
            text = '',            
            type = 'text',
            annotations = {    
                'bold': False,
                'italic': False,
                'strikethrough': False,
                'underline': False,
                'code': False,
                'color': 'default'
            }
        ):
        self.richText = {
          "type": '',
          "annotations": {
            "bold": False,
            "italic": False,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": "default"
          },
          "plain_text": "",
          "href": None
        }
        self.setType(type)
        self.setText(text)
        self.setAnnotations()
    
    def setType(self, type):
        if type in self.typeBlockBases:
            print('type is' + type)
            self.richText[type] = self.typeBlockBases[type].copy()
            self.richText['type'] = type
        else:
            raise Exception('Type "' + type + '" is undefined')
    # テキストを追加
    def setText(self, text):
        self.richText['plain_text'] = text
        if self.richText['type'] == 'text':
            self.richText['text']['content'] = text
        elif self.richText['type'] == 'equition':
            self.richText['equition']['expression'] = text
            
    # Annotation設定
    def setAnnotations(self, bold = False, italic = False, strikethrough = False, underline = False, code = False):
        if not bold is None:
            self.richText['annotations']['bold'] = bold
        if not italic is None:
            self.richText['annotations']['italic'] = italic
        if not strikethrough is None:
            self.richText['annotations']['strikethrough'] = strikethrough
        if not underline is None:
            self.richText['annotations']['underline'] = underline
        if not code is None:
            self.richText['annotations']['code'] = code
        
    # テキストカラーを指定
    def setColor(self, color = 'default'):
        if color in self.colors:
            self.richText['annotations']['color'] = color
        else:
            print(color + ' is not supported')
    
    # URLの設定
    def setLink(self, url):
        self.richText['href'] = url
        if self.richText['type'] == 'mention' and self.richText['mention']['type'] == 'link_preview':
            self.richText['mention']['link_preview']['url'] = url
        elif self.richText['type'] == 'text':
            self.richText['text']['link']['url'] = url
    def getRichText(self):
        return self.richText

