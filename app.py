from flask import Flask, render_template, redirect, url_for, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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
    app.run()