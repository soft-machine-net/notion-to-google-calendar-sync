def propertyToText(property):
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
    # elif type == 'relation':
    #     for item in property[type]
    #         page = 
        # TODO: 他のパターンも対応する。
    return text 

def blocksToText(blocks):
    text = ""
    for block in blocks['results']:
        type = block['type']
        if type in ['title', 'rich_text', 'date', 'paragraph']:
            text += propertyToText(block) + "\n"
    return text



# {
#     "object":"block",
#     "id":"3f779820-6176-498e-ab1c-6a3253f39fb3",
#     "parent":{"type":"page_id","page_id":"eadf8821-6a7c-4c86-95db-2bb6878009e9"},
#     "created_time":"2023-05-15T12:27:00.000Z",
#     "last_edited_time":"2023-05-15T12:28:00.000Z",
#     "created_by":{"object":"user","id":"1a79eb1a-cb54-4cfb-8d76-f76cab8f0541"},
#     "last_edited_by":{"object":"user","id":"1a79eb1a-cb54-4cfb-8d76-f76cab8f0541"},
#     "has_children":false,
#     "archived":false,
#     "type":"paragraph",
#     "paragraph":{
#         "color":"default",
#         "text":[
#             {
#                 "type":"text",
#                 "text":{
#                     "content":"新しいダブルベッドが届いた。",
#                     "link":null
#                 },
#                 "annotations":{
#                     "bold":false,
#                     "italic":false,"strikethrough":false,"underline":false,"code":false,"color":"default"
#                 },
#                 "plain_text":"新しいダブルベッドが届いた。",
#                 "href":null
#             }
#         ]
#     }
# }