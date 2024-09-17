from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

@app.route('/api/data')
@app.route('/api/items', methods=['GET'])
def get_items():
    items = [
        {'name': 'Milk', 'shop': 'Woolies', 'price': 1.50},
        {'name': 'Bread', 'shop': 'Coles', 'price': 2.00},
        {'name': 'Apple', 'shop': 'Woolies', 'price': 0.70},
        {'name': 'Chicken', 'shop': 'Coles', 'price': 5.00},
    ]
    return jsonify(items)

@app.route('/api/submit', methods=['POST'])
def submit_data():
    data = request.json
    print('Received data:', data)
    return jsonify({'status': 'success', 'data': data})

if __name__ == '__main__':
    app.run()
