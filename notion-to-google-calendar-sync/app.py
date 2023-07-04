
from google.oauth2 import service_account
from googleapiclient import discovery
import notion
import os
import re
import json
import datetime
import pytz
from dateutil import parser
import logging

class NtGcMigrationController:
    metadataSeparater = "///////////////metadata///////////////"

    def __init__(self, integrationSecret, dbid, calendarId, reqProps = {}, optProps = {}, isAllSync = False):
        """初期化処理：対応するDB Controllerを作成、GoogleCalendar APIの承認情報周りの初期化"""
        self.dbController = notion.databaseController(integrationSecret, dbid)
        self.calendarId = calendarId
        self.reqProps = reqProps
        self.optProps = optProps
        self.isAllSync = isAllSync
        scopes = ["https://www.googleapis.com/auth/calendar"]
        self.credentials = service_account.Credentials.from_service_account_file(
            "token.json", scopes=scopes
        )  # jsonはgoogle cloud platformの鍵のダウンロードで落としたやつ
        self.service = discovery.build(
            "calendar", "v3", credentials=self.credentials, cache_discovery=False
        ) # cache_discovery=Falseにしてないとaws lambdaだとエラーが出るらしい
    
    def pageProcessor(self, page, title_key = None, description_key = None, datetime_key = 'datetime', properties = None):
        # GoogleCalendarAPIに渡すイベントオブジェクトに登録する辞書を作成
        event = {'summary': '', 'start': '', 'end': '', 'description': ''}
        # イベント：日付（開始日）
        event['start'], event['end'] = self.getDatetiime(page, datetime_key)
        # イベント：イベント名 設定がなければプロパティIDがtitleのプロパティを取得
        event['summary'] = self.getSummary(page, title_key)
        # イベント：説明
        event['description'] = self.getDescription(page, description_key)
        # イベント：イベントIDを取得(削除判定のため先に取得)
        event_id = self.getEventId(page)
        # イベントオプション項目
        # for key, propKey in self.optProps.items():
        #     event[key] = self.getProperty(page, propKey)
        # Googleカレンダーと同期 event_idが設定されていればアップデータト
        if event_id != '' :
            try:
                self.update_event(event_id, event)
                return
            except Exception as err:
                # 更新に失敗した場合はログ出して新規作成に移行する
                logging.error(err)

        # Googleカレンダーのイベントの作成
        event = self.add_event(event)
        # 作成したイベントをもとにNotionの対応するページのevent_idを設定する。
        self.update_notion_page_event_id(page['id'], event['id'])
                
    def add_event(self, event):
        """Googleカレンダーのイベントの作成"""
        event = ( 
            self.service.events()
            .insert(
                calendarId=self.calendarId,  # 設定>マイカレンダーの設定>カレンダーの等号>カレンダーID
                body=event,
            )
            .execute()
        )
        return event

    def update_event(self, event_id, event):
        """googlecカレンダーのイベントの更新"""
        event = ( 
            self.service.events()
            .update(
                calendarId=self.calendarId,  # 設定>マイカレンダーの設定>カレンダーの等号>カレンダーID
                eventId=event_id,
                body=event,
            )
            .execute()
        )
        return event
    
    def delete_event(self, event_id):
        """googlecカレンダーのイベントの更新"""
        event = ( 
            self.service.events()
            .delete(
                calendarId=self.calendarId,  # 設定>マイカレンダーの設定>カレンダーの等号>カレンダーID
                eventId=event_id
            )
            .execute()
        )
        return event

    def update_notion_page_event_id(self, page_id, event_id):
        """notionのDBにGoogleCalendarのevent_idを登録する登録する絡むはevent_id固定"""
        self.dbController.updatePageProperties(page_id, {"event_id":{'type':'rich_text','rich_text':[{'type':'text', 'text':{'content': event_id}}]}})

    def notionDbStructureCheck(self):
        """TODO: DB構造取得してチェックする処理,問題のあるプロパティを配列で返す"""
        return []
    
    def notionDbStructureMigrate(self):
        """TODO: NotionのDB構造を設定に合わせて更新する"""
        return False

    def migrate(self):
        """データベースとカレンダーのマイグレーション？の実行"""
        # DBに対応する絡むがちゃんとあるかを先にチェックする。合わせて対応しているタイプかどうかも確認する。
        # self.notionDbStructureCheck()
        # なければ自度的に作る
        # self.notionDbStructureMigrate()
        # DBにひもづくページを全て取得し１ページずつ処理する
        if self.isAllSync:
            pages = self.dbController.queryDatabaseAllPages({})
        else:
            interval_minutes = int(os.getenv('SYNC_INTERVAL_MINUTES'))
            timestamp = datetime.datetime.now() - datetime.timedelta(minutes=interval_minutes + 1)
            response  = self.dbController.queryDatabase({"filter": {
                    "timestamp": 'last_edited_time',
                    "last_edited_time": {
                        'on_or_after': timestamp.isoformat()
                    }
                }})
            pages = response['results']
            
        for page in pages:
            try:
                self.pageProcessor(page, self.reqProps['summary'], self.reqProps['description'], self.reqProps['datetime'])
            except Exception as err:
                logging.error(err)

    def is_within_minutes(self, timestamp_str, minutes):
        """入力されたtimestamp_strが現在からminutes以内に更新されたものかをチェックする"""
        # 現在の時刻を取得
        current_time = datetime.datetime.now(datetime.timezone.utc)

        # タイムスタンプをdatetimeオブジェクトに変換
        timestamp = parser.isoparse(timestamp_str)

        # 現在の時刻から指定された分数以内かどうかを判定
        diff = current_time - timestamp
        within_minutes = diff.total_seconds() <= (minutes * 60)

        return within_minutes
    
    def getDatetiime(self, page, key):
        datetime_texts = notion.utils.propertyToText(page['properties'][key]).rsplit('~')
        ### 日付の設定がない場合は例外スロー
        if datetime_texts == []:
            raise Exception('Date is empty ')
        
        ### 日付タイプの指定 終日:date 時間指定:dateTime
        date_type = 'date' if re.fullmatch(r'\d{4}\-\d{2}\-\d{2}', datetime_texts[0]) else 'dateTime'
        start = {date_type: datetime_texts[0], "timeZone": "Asia/Tokyo"}

        ### 終了日は設定がない場合は同じ日付が設定される。
        end_timestamp = datetime_texts[1] if len(datetime_texts) >= 2 else datetime_texts[0]
        end = {date_type: end_timestamp, "timeZone": "Asia/Tokyo"}
        return start, end

    def getDescription(self, page, key):
        metadata = self.createMetaData(page)
        if key == None:
            blocks = self.dbController.retrieveBlockChildren(page['id'])
            return notion.utils.blocksToText(blocks) + metadata
        else:
            return notion.utils.propertyToText(page['properties'][key]) + metadata
        
    def createMetaData(self, page):
        metadata = {
            'link': page['url'],
            'id': page['id'],
            'last_sync_time': datetime.datetime.now().isoformat()
        }
        return "\n\n\n"+self.metadataSeparater+"\n" + json.dumps(metadata)
    
    def getSummary(self, page, key):
        if key == None:
            for akey,property in page['properties'].items():
                print(property)
                if property['id'] == 'title':
                    title = property
        else:
            title = page['properties'][key]
        return self.dbController.propertyToText(title)
    
    def getEventId(self, page, key = 'event_id'):
        return notion.utils.propertyToText(page['properties'][key])
    
    def getProperty(self, page, key):
        return notion.utils.propertyToText(page['properties'][key])
    
    def geEvents(self):
        """Googleカレンダーのイベント一覧の取得"""
        page_token = None
        allEvents = []
        while True:
            events = self.service.events().list(calendarId=self.calendarId, pageToken=page_token).execute()
            allEvents += events['items']
            page_token = events.get('nextPageToken')
            if not page_token:
                break
        return allEvents
    
    def deleteSync(self):
        """
        NotionAPIに削除したページを取得する方法がない。
        GoogleCalendarのdescriptionの末尾にmetadataをjsonフォーマットで記載して、それをもとに処理。
        metadataの記載がないカレンダーは削除み対応
        GoogleCalendarのイベント一覧を取得→イベントのメタデータをもとにNotioAPI GetPage→archived=trueだったら削除
        """
        events = self.geEvents()
        for event in events:
            try:
                eventMeta = self.getEventMeta(event)
                notionPageId = eventMeta['id']
                page = self.dbController.retrievePage(notionPageId)
                if page['archived']:
                    self.delete_event(event['id'])
            except Exception as err:
                print(err)

    def getEventMeta(self, event):
        desc = event['description']
        # 区切り文字で文章を分割し、JSON部分を取得
        json_text = desc.split(self.metadataSeparater)[1].strip()
        return json.loads(json_text)
    
def lambda_handler(event,context):
    try:
        # Calendarのデータをeventから読み込み
        calendars = event["calendars"]
    except Exception as err:
        return {"statusCode": 500, "message": "CalendarData not found"}
    
    for calendar in calendars:
        # データベースごとにマイグレートを実行する
        migration = NtGcMigrationController(
                integrationSecret=calendar['integration_secret'], 
                dbid=calendar['dbid'], 
                calendarId=calendar['calendar_id'], 
                reqProps=calendar['req_props'], 
                optProps=calendar['opt_props'],
                isAllSync=calendar['is_all_sync']
            )
        migration.migrate()

        # 削除処理は重たいため３時間に１度だけ実行
        current_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        if current_time.hour % 3 == 0 and 0 <= current_time.minute <= 4:
            migration.deleteSync()
    
    return {'statusCode': 200, 'message': 'SyncComplete'}
