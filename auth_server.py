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
    # Run Flask server without specifying a port, allowing it to run on an available port
    app.run(debug=True, use_reloader=False)  # `use_reloader=False` ensures it runs only once

def open_browser(url):
    # If running locally, open the URL in the browser
    webbrowser.open(url)
