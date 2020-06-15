import sys


__postman_module_path = r'C:\Users\suwha\Documents\GitHub\Postman\PostmanPython'
sys.path.append(__postman_module_path)

# ------------------------------

import os.path
from subscriber import Subscriber
from subscribemanager import SubscribeManager
from dbmanager import DatabaseManager
from mailsender import GmailSender
from settings import PostmanSettings
from validate_email import validate_email


__settings_path = './postman_settings.json'
settings = PostmanSettings()
if not os.path.exists(__settings_path):
    print(f"새로운 설정 파일 생성, '{__settings_path}'")
    settings.create_settings(__settings_path)
    exit()
else:
    settings.load_settings(__settings_path)

__db_settings = settings.db_settings
db_manager = DatabaseManager()
db_manager.connect(__db_settings.mysql_server, __db_settings.database, __db_settings.user_id, __db_settings.password)

sub_manager = SubscribeManager()

stock_table = db_manager.select_all_stocks()