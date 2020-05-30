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


def build_auth_mail(email, token):
    message = __auth_message.replace('%email%', email).replace('%token%', token)
    return message


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
__auth_message = codecs.open(__auth_file_path, 'r', 'utf-8').read()
__recaptcha_secret_key_path = 'recaptcha.secret'
__recaptcha_secret_key = codecs.open(__recaptcha_secret_key_path, 'r', 'utf-8').read()

# ------------------------------

import requests


__url = 'https://www.google.com/recaptcha/api/siteverify'


def check_recaptcha(user_response):
    payload = { 'secret': __recaptcha_secret_key, 'response': user_response }
    response = requests.post(__url, data = payload).json()
    return response['success']

# ------------------------------

from flask import Flask, render_template, redirect, url_for, request, jsonify


app = Flask(__name__)
project_nickname = '주가예측 알리미'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/subscribe', methods = ['POST'])
def subscribe():
    email = request.form['email']
    grecaptcha_response = request.form['grecaptcha_response']

    if grecaptcha_response is None or not check_recaptcha(grecaptcha_response):
        print('reCAPTCHA가 만료됨')
        return 'reCAPTCHA가 만료되었습니다.\n다시 시도해주세요.'

    if email is None or email.isspace() or not validate_email(email):
        print('올바른 이메일의 형식이 아님', email)
        return f"'{email}'\n올바른 형식의 이메일이 아닙니다."
    
    if __sub_manager.check_subscribe(email):
        print('이미 구독중인 이메일', email)
        return f"'{email}'\n이미 구독중인 이메일입니다."

    subscriber = Subscriber(email)
    __sub_manager.add_to_auth(subscriber)
    subject = f'{project_nickname} 구독 인증 메일입니다'
    body = build_auth_mail(subscriber.email, subscriber.token)

    gmail_sender = GmailSender(__gmail_account, __gmail_password, project_nickname)
    gmail_sender.send_mail([email], subject, body, True)
    
    return f"'{email}'\n구독을 위한 인증메일이 발송되었습니다.\n이메일을 확인해주세요."


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

if __name__ == '__main__':
    app.run()
