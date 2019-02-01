from __future__ import unicode_literals

from flask import jsonify
from flask import Flask, request, abort

app = Flask(__name__)

@app.route('/keyboard')
def keyboard():
    return jsonify({'type': 'text'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9011)
