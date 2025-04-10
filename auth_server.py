from flask import Flask, request
import webbrowser

auth_code_holder = {"code": None}
app = Flask(__name__)

@app.route("/callback")
def callback():
    # Get the authorization code from the query string and store it
    auth_code_holder["code"] = request.args.get("code")
    return "<h1>You can close this tab and return to the Streamlit app ✅</h1>"

def start_server():
    # Run Flask server on a different port (5001 or any available port)
    app.run(debug=True, use_reloader=False, port=5001)

def open_browser(url):
    # If running locally, open the URL in the browser
    webbrowser.open(url)
