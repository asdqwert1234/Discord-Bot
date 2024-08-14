'''
資料庫
'''
import psycopg2, datetime
from data.time_parameters import tz

class PostgreSQL:
    def __init__(self, dict):
        self.conn = psycopg2.connect(
            database = dict['database'],
            user = dict['user'],
            password=dict['password'],
            host=dict['host'],
            port=dict['port']
        )
        print('已經成功連結資料庫')
        self.cursor = self.conn.cursor()
    
    def save_data(self, data:dict):
        #dict -> SQL
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO user_info_1({columns}) VALUES({values})"
        self.cursor.execute(sql, tuple(data.values()))
        self.conn.commit()

    def search_data(self, user_id: int):
        # 執行查詢語句並取出結果
        self.cursor.execute(f"SELECT * FROM user_info_1 WHERE user_id = {user_id}")
        result = self.cursor.fetchone()
        if result:
            # 將結果轉成dict
            columns = [desc[0] for desc in self.cursor.description]
            data = dict(zip(columns, result))
            if not data["guild_roll_call"]== None:
                data["guild_roll_call"] = ((datetime.datetime.now().replace(tzinfo = tz)).date()-data["guild_roll_call"]).days
            del data["id"]
            return data
        else:
            return None
        
    def search_data_id(self, user_id: str):
        # 執行查詢語句並取出結果
        self.cursor.execute(f"SELECT * FROM user_info_1 WHERE maplestory_id = '{user_id}'")
        result = self.cursor.fetchone()
        if result:
            # 將結果轉成dict
            columns = [desc[0] for desc in self.cursor.description]
            data = dict(zip(columns, result))
            if not data["guild_roll_call"]== None:
                data["guild_roll_call"] = ((datetime.datetime.now().replace(tzinfo = tz)).date()-data["guild_roll_call"]).days
            del data["id"]
            return data
        else:
            return None

    def update_data(self, data: dict, user_id: int):
        # 將dict轉成SQL語句並執行
        set_statement = ', '.join([f"{key} = %s" for key in data])
        sql = f"UPDATE user_info_1 SET {set_statement} WHERE user_id = {user_id}"
        self.cursor.execute(sql, tuple(data.values()))
        self.conn.commit()
    
    def get_nick_list(self):
        # 執行查詢語句並取出結果
        self.cursor.execute("SELECT user_id, maplestory_id FROM user_info_1")
        results = self.cursor.fetchall()
        # 將結果集轉換為 tuple 的 list，並剔除 maplestory_id 為 None 的資料
        id_list = [(int(result[0]), result[1]) for result in results if result[1] is not None]
        return id_list

        
    def __del__(self):
        print('中斷與資料庫的連結')
        self.conn.close()


def data_check(data):
    # 移除空值
    for key in ['maplestory_id', 'maplestory_job', 'twitch', 'youtube']:
        if data[key] == '':
            del data[key]
    
    # 處理公會點名
    if data.get('guild_roll_call'):
        try:
            days = int(data['guild_roll_call'])
            if 0 <= days < 365:
                data['guild_roll_call'] = (datetime.datetime.now(tz).date() - datetime.timedelta(days=days)).date()
            else:
                del data['guild_roll_call']
        except ValueError:
            del data['guild_roll_call']
    
    return data