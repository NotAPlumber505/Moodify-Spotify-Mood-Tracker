# 🎧 Moodify: Your Spotify Mood Tracker and Browser App 🎶

A Streamlit-based application that tracks and recommends playlists based on mood, visualizes top songs, and provides artist search functionality. 🌟

## Features 🌟

1. **Mood-based Playlist Recommendations 🎶**  
   - Users can rate their mood using a slider (0-10) 🎚️ and receive playlist recommendations based on their mood 🎧.
   - Playlists are generated and stored on Spotify 🎵.

2. **Top Songs Visualization 📊**  
   - Displays a chart of the user's top songs with interactive time intervals (per month/year).
   - Songs are retrieved from Spotify API.

3. **Artist Search 🔍**  
   - Users can search for an artist 🎤 to see their top tracks, popularity, followers, and album covers 🖼️.
   - Includes links to Spotify 🔗 and song previews 🎶.

4. **Artist Info  🧑‍🎤**
   - Displays detailed information about the artist, including their top tracks, albums, and followers 👥.
   - Includes album covers 🎨, song previews 🎶, and direct links to Spotify 🔗.

## 🛠️ Setup Instructions

### 1. Clone the Repository

```
git clone https://github.com/NotAPlumber505/Moodify-Spotify-Mood-Tracker.git
cd Moodify-Spotify-Mood-Tracker
```

### 2. Create a Virtual Environment (Optional but Recommended) 🧑‍💻

To avoid dependency conflicts, it's a good practice to create a virtual environment for this project.

```
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies 📦

Install the required dependencies using `pip`:

```
pip install -r requirements.txt
```

### 4. Set Up Configuration ⚙️

Store your Spotify API credentials in a .toml file (e.g., config.toml) with the following format:
```
[spotify]
client_id = "your-client-id"
client_secret = "your-client-secret"
redirect_uri = "your-redirect-uri
Make sure to replace the placeholder values with your actual Spotify credentials.
```

### 5. Run the Application 🚀
Once the environment is set up and dependencies are installed, you can start the app by running:
streamlit run app.py

The app should open in your default web browser at http://localhost:8501

### Folder Structure

```
Moodify-Spotify-Mood-Tracker/
├── app.py                 # Main Streamlit app file
├── requirements.txt       # Project dependencies
├── config.toml            # Spotify API credentials
├── images/                # Folder to store artist images
└── README.md              # Project documentation
```

# Contributing
1. Fork the repository 🍴.
2.Create a new branch (git checkout -b feature-branch) 🌱.
3. Make your changes ✨.
4. Commit your changes (git commit -am 'Add new feature') 💡.
5. Push to the branch (git push origin feature-branch) 🚀.
6. Create a new pull request 🔀.

## 📜 License

MIT License

Copyright (c) 2025 Mario Casas 🎉

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


