import json
import os
import time


class CertImagesDB(object):

    def __init__(self, db_path='./data/db.json'):
        self.db_json_path = db_path
        pass

    def add(self, record):
        succ, msg, db_json = self.__load_db()
        if not succ:
            return succ, msg
        if db_json['data'] is None:
            db_json['data'] = []
        new_data = {
            'uk': str(time.time()),
            'name': record['name'],
            'category': record['category'],
            'images': record['images']
        }
        db_json['data'].append(new_data)
        succ, msg = self.__save_db(db_json)
        return succ, msg, new_data

    def delete(self, uk: str):
        if uk is None or len(uk) <= 0:
            return False, '删除目标不明确'
        succ, msg, db_json = self.__load_db()
        if not succ:
            return succ, msg
        if db_json is None or db_json['data'] is None or len(db_json['data']) <= 0:
            return False, '记录不存在'
        removed = False
        for record in db_json['data']:
            if record['uk'] is None:
                db_json['data'].remove(record)
            if (record['uk'] == uk):
                db_json['data'].remove(record)
                removed = True

        if not removed:
            return False, '记录不存在'

        succ, msg = self.__save_db(db_json)
        if succ:
            return True, '删除成功'
        else:
            return succ, msg

    def update(self, uk: str, record: dict):
        pass

    def query(self, keyword: str = None):
        succ, msg, db_json = self.__load_db()

        if not succ:
            return succ, msg, []

        data = db_json['data']

        if data is None:
            return succ, msg, []
        if keyword is None or len(keyword.strip()) <= 0:
            return True, '', data
        return True, '', [record for record in data if record['name'] and record['name'].find(keyword) >= 0]

    def query_by_uks(self, uks: list = None):
        if uks is None or len(uks) <= 0:
            return True, '', []

        succ, msg, db_json = self.__load_db()

        if not succ:
            return succ, msg, []

        data = db_json['data']

        if data is None:
            return succ, msg, []

        # a = uks.index('id1')

        return True, '', [record for record in data if record['uk'] and record['uk'] in uks]

    def __load_db(self) -> (bool, str, dict):
        if not os.path.exists(self.db_json_path):
            return False, '索引文件不存在', None
        with open(self.db_json_path, 'r') as db_json_file:
            try:
                db_json = json.load(db_json_file)
                return True, '', db_json
            except Exception as e:
                print(e)
                return False, '索引文件格式不正确', None

    def __save_db(self, db_json) -> (bool, str):
        if not os.path.exists(self.db_json_path):
            return False, '索引文件不存在'
        with open(self.db_json_path, 'w') as db_json_file:
            try:
                json.dump(db_json, db_json_file, indent=4)
                return True, '保存成功'
            except Exception as e:
                print(e)
                return False, '保存失败'
