from flask import Flask, render_template, redirect, url_for, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/auth/<email>/<token>')
def auth(email, token):
    return email + ", " + token


@app.route('/api/unsubscribe/<email>/<token>')
def unsubscribe(email, token):
    return email + ", " + token


@app.route('/elements')
def elements():
    return render_template('elements.html')


@app.route('/stock/<fappa>')
def stock(fappa):
    return 'Stock: ' + fappa


@app.route('/json')
def json():
    data = { 'name' : 'Kappa', 'Family' : 'Ross' }
    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    