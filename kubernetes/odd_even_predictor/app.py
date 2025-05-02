from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/predict', methods=['GET'])
def predict():
    try:
        number = int(request.args.get('number', 0))
        result = "even" if number % 2 == 0 else "odd"
        message = os.environ.get('GREETING_MESSAGE', 'The number is')
        return jsonify({'input': number, 'prediction': result, 'message': message})
    except ValueError:
        return jsonify({'error': 'Please provide an integer number.'}), 400
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)