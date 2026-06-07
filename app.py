from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Bet KG Admin Panel</h1>
    <p>Сайт иштеп жатат ✅</p>
    """
