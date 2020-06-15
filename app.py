import postman

# ------------------------------

import os.path
from appsettings import AlphaStockSettings


__settings_path = './alphastock_settings.json'
settings = AlphaStockSettings()
if not os.path.exists(__settings_path):
    print(f"새로운 설정 파일 생성, '{__settings_path}'")
    settings.create_settings(__settings_path)
    exit()
else:
    settings.load_settings(__settings_path)

# ------------------------------

import codecs


def build_auth_mail(email, token):
    message = __auth_message.replace('%email%', email).replace('%token%', token)
    return message


def build_welcome_mail(email, token):
    message = __welcome_message.replace('%email%', email).replace('%token%', token)


__auth_file_path = './auth.html'
__welcome_file_path = './welcome.html'
__auth_message = codecs.open(__auth_file_path, 'r', 'utf-8').read()
__welcome_message = codecs.open(__welcome_file_path, 'r', 'utf-8').read()

# ------------------------------

import requests


def check_recaptcha(user_response):
    payload = { 'secret': settings.recaptcha_secret, 'response': user_response }
    response = requests.post(__url, data = payload).json()
    return response['success']


__url = 'https://www.google.com/recaptcha/api/siteverify'

# ------------------------------

from flask import Flask, render_template, redirect, url_for, request, jsonify
from validate_email import validate_email


app = Flask(__name__)
project_nickname = '주가예측 알리미'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favorite/<email>/<token>')
def favorite(email, token):
    if email is None or email.isspace() or not validate_email(email):
        print('올바른 이메일의 형식이 아님', email)
        return 'Credential을 확인할 수 없습니다.'

    if token is None or token.isspace() or len(token) != 8:
        print('올바른 토큰의 형식이 아님', token)
        return 'Credential을 확인할 수 없습니다.'

    subscriber = postman.Subscriber(email)
    if token != subscriber.token:
        print('토큰이 일치하지 않음', token)
        return 'Credential을 확인할 수 없습니다.'

    if not postman.sub_manager.check_subscribe(email):
        print('구독중이 아닌 이메일', email)
        return '구독자만 이용할 수 있습니다.'

    # favorites = { 'data': postman.db_manager.select_favorite_stock_ids(subscriber) }
    favorites = postman.db_manager.select_favorite_stock_ids(subscriber)

    return render_template('favorite.html', email = email, token = token, stock_table = postman.stock_table, favorites = favorites)


@app.route('/api/favorite', methods = ['POST'])
def save_favorite():
    email = request.form['email']
    token = request.form['token']
    favorites = request.form.getlist('favorites[]')

    if email is None or email.isspace() or not validate_email(email):
        print('올바른 이메일의 형식이 아님', email)
        return 'Credential을 확인할 수 없습니다.'

    if token is None or token.isspace() or len(token) != 8:
        print('올바른 토큰의 형식이 아님', token)
        return 'Credential을 확인할 수 없습니다.'

    subscriber = postman.Subscriber(email)
    if token != subscriber.token:
        print('토큰이 일치하지 않음', token)
        return 'Credential을 확인할 수 없습니다.'

    if not postman.sub_manager.check_subscribe(email):
        print('구독중이 아닌 이메일', email)
        return '구독자만 이용할 수 있습니다.'

    postman.db_manager.delete_all_favorites(subscriber)
    postman.db_manager.insert_favorites(subscriber, favorites)

    return '저장되었습니다.'


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
    
    if postman.sub_manager.check_subscribe(email):
        print('이미 구독중인 이메일', email)
        return f"'{email}'\n이미 구독중인 이메일입니다."

    subscriber = postman.Subscriber(email)
    postman.sub_manager.add_to_auth(subscriber)
    subject = f'{project_nickname} 구독 인증 메일입니다'
    body = build_auth_mail(subscriber.email, subscriber.token)

    gmail_sender = postman.GmailSender(postman.settings.gmail_account, postman.settings.gmail_password, project_nickname)
    gmail_sender.send_mail([email], subject, body, True)
    
    return f"'{email}'\n구독을 위한 인증메일이 발송되었습니다.\n이메일을 확인해주세요."


@app.route('/api/unsubscribe/<email>/<token>')
def unsubscribe(email, token):
    if email is None or email.isspace() or not validate_email(email):
        print('올바른 이메일의 형식이 아님', email)
        return f"'{email}'\n올바른 형식의 이메일이 아닙니다."

    if token is None or token.isspace() or len(token) != 8:
        print('올바른 토큰의 형식이 아님', token)
        return '구독 해지 실패'

    if not postman.sub_manager.check_subscribe(email):
        print('구독중이 아닌 이메일 주소', email)
        return f"'{email}'\n구독중이 아닌 이메일입니다."

    postman.sub_manager.unsubscribe(email, token)
    
    return f"'{email}'\n구독 해지"


@app.route('/api/auth/<email>/<token>')
def auth(email, token):
    if email is None or email.isspace() or not validate_email(email):
        print('올바른 이메일의 형식이 아님', email)
        return '인증 실패'

    if token is None or token.isspace() or len(token) != 8:
        print('올바른 토큰의 형식이 아님', token)
        return '인증 실패'

    if postman.sub_manager.check_subscribe(email):
        print('이미 구독중인 이메일', email)
        return '인증 실패'

    if not postman.sub_manager.auth(email, token):
        print('인증 실패', email, token)
        return '인증 실패'
    
    postman.sub_manager.subscribe(email)
    subject = f'[{project_nickname}] 관심 종목을 선택해주세요'
    body = build_welcome_mail(email, token)

    gmail_sender = postman.GmailSender(postman.settings.gmail_account, postman.settings.gmail_password, project_nickname)
    gmail_sender.send_mail([email], subject, body, True)

    return '이메일 인증이 완료되었습니다.\n이메일을 확인해 주세요.'


@app.route('/elements')
def elements():
    return render_template('elements.html')

# ------------------------------

if __name__ == '__main__':
    app.run()
