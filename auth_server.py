from flask import Flask, request
import webbrowser

auth_code_holder = {"code": None}
app = Flask(__name__)

@app.route("/callback")
def callback():
    auth_code_holder["code"] = request.args.get("code")
    return "<h1>You can close this tab and return to the Streamlit app ✅</h1>"

def start_server():
    app.run(port=8080)

def open_browser(url):
    webbrowser.open(url)
