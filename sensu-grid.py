import os
from flask import send_from_directory
from flask import Flask
from flask import render_template
import requests
import q

app = Flask(__name__)

data = {}

dcs = [{"name":"local", "url":"localhost"}]

def check_connection():
    r = requests.get('http://localhost:4567/results')
    if r:
        r.close()
        return True
    else:
        r.close()
        return False

@q
def get_data(dc):
    if check_connection():
        r = requests.get('http://'+dc['url']+':4567/results')
        data = r.json()
        r.close()
    return data


@app.route('/', methods=['GET'])
@q
def root():
    for dc in dcs:
        data[dc['name']] = get_data(dc)
        q(data)
    return render_template('data.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
