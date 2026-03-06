from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "HOME WORKING"

@app.route('/api/register/', methods=['POST'])
def register():
    return "REGISTER WORKING"

if __name__ == "__main__":
    app.run(debug=True)
