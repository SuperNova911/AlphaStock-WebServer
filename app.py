import sys


__postman_module_path = r'C:\Users\suwha\Documents\GitHub\Postman\Postman Python'
sys.path.append(__postman_module_path)

# ------------------------------

from subscriber import Subscriber
from subscribemanager import SubscribeManager
from dbmanager import DatabaseManager
from mailsender import GmailSender
from validate_email import validate_email


def load_gmail_credential(path):
    with open(path) as file:
        lines = [line.rstrip() for line in file]
    for line in lines:
        credential = line.split('/')
        if len(credential) != 2:
            print('잘못된 형식의 Credential', credential)
            continue

        id = credential[0]
        password = credential[1]
        if id.isspace() or password.isspace():
            print('아이디 또는 비밀번호가 빈 문자열', id, password)
            continue

        if not validate_email(id):
            print('올바른 이메일의 형식이 아님', id)

        return id, password
    return None, None


__db_path = 'PostmanDB.db'
__db_manager = DatabaseManager()
__db_manager.connect(__db_path)

__gmail_credential_path = 'GmailCredential.txt'
__gmail_account, __gmail_password = load_gmail_credential(__gmail_credential_path)
if __gmail_account is None or __gmail_password is None:
    print('Gmail Credential을 불러오지 못함')
    exit()

__sub_manager = SubscribeManager()

# ------------------------------

import codecs


__auth_file_path = 'auth.html'
__auth_file = codecs.open(__auth_file_path, 'r', 'utf-8')
__auth_message = __auth_file.read()

# ------------------------------

from flask import Flask, render_template, redirect, url_for, request, jsonify


app = Flask(__name__)
project_nickname = '주가예측 알리미'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/subscribe/<email>')
def subscribe(email):
    if email is None or email.isspace():
        print('유효하지 않은 이메일 주소')
        return
    
    if not validate_email(email):
        print('올바른 이메일의 형식이 아님', email)
        return
    
    if __sub_manager.check_subscribe(email):
        print('이미 구독중인 이메일', email)
        return

    subscriber = Subscriber(email)
    __sub_manager.add_to_auth(subscriber)
    subject = f'{project_nickname} 구독 인증 메일입니다'
    body = build_auth_mail(subscriber.email, subscriber.token)

    gmail_sender = GmailSender(__gmail_account, __gmail_password, project_nickname)
    gmail_sender.send_mail([email], subject, body, True)
    
    return email


@app.route('/api/unsubscribe/<email>/<token>')
def unsubscribe(email, token):
    if email is None or email.isspace():
        print('유효하지 않은 이메일 주소')
        return
    
    if not validate_email(email):
        print('올바른 이메일의 형식이 아님', email)
        return

    if token is None or token.isspace():
        print('유효하지 않은 토큰')
        return
    
    if len(token) != 8:
        print('올바른 토큰의 형식이 아님', token)
        return

    if not __sub_manager.check_subscribe(email):
        print('구독중이 아닌 이메일 주소', email)
        return

    __sub_manager.unsubscribe(email, token)
    
    return email + ", " + token


@app.route('/api/auth/<email>/<token>')
def auth(email, token):
    if email is None or email.isspace():
        print('유효하지 않은 이메일 주소')
        return
    
    if not validate_email(email):
        print('올바른 이메일의 형식이 아님', email)
        return

    if token is None or token.isspace():
        print('유효하지 않은 토큰')
        return
    
    if len(token) != 8:
        print('올바른 토큰의 형식이 아님', token)
        return

    if __sub_manager.check_subscribe(email):
        print('이미 구독중인 이메일', email)
        return

    if not __sub_manager.auth(email, token):
        print('인증 실패', email, token)
        return
    
    __sub_manager.subscribe(email)

    return email + ", " + token


@app.route('/elements')
def elements():
    return render_template('elements.html')

# ------------------------------

def build_auth_mail(email, token):
    message = __auth_message.replace('%email%', email).replace('%token%', token)
    return message

# ------------------------------

if __name__ == '__main__':
    app.run()
    