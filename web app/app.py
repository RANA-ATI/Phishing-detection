from flask import Flask, render_template, request
from models.URL_extraction import extract_features

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', prediction=None, error=None)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    url = request.form['url']
    
    try:
        prediction = extract_features(url)
        return render_template('index.html', prediction=prediction, error=None)
    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        return render_template('index.html', prediction=None, error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
