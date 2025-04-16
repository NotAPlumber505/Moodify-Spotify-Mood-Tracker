import streamlit as st
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from main import SpotifyBackend  # assumes your backend is in a separate module

# --- CONFIGURATION ---
st.set_page_config(page_title="Moodify", layout="wide")

client_id = st.secrets["SPOTIPY_CLIENT_ID"]
client_secret = st.secrets["SPOTIPY_CLIENT_SECRET"]
redirect_uri = st.secrets.get("SPOTIPY_REDIRECT_URI", "http://localhost:8501/callback")
scope = "user-library-read user-read-private user-top-read playlist-modify-public playlist-modify-private"

# --- AUTH ---
def get_oauth():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        show_dialog=True
    )

def get_sp():
    token_info = st.session_state.get("token_info")
    if token_info:
        oauth = get_oauth()
        if oauth.is_token_expired(token_info):
            token_info = oauth.refresh_access_token(token_info['refresh_token'])
            st.session_state["token_info"] = token_info
        return spotipy.Spotify(auth=token_info['access_token'])
    return None

def display_login():
    st.title("Moodify - Login")
    oauth = get_oauth()
    code = st.query_params.get("code")

    if st.button("Login with Spotify"):
        auth_url = oauth.get_authorize_url()
        st.markdown(f'<a href="{auth_url}" target="_blank">Click here to authorize Spotify</a>', unsafe_allow_html=True)
        st.info("After authorizing, return to this page.")

    if code:
        try:
            token_info = oauth.get_access_token(code)
            st.session_state["token_info"] = token_info
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")

def display_logout():
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# --- MAIN ---
def main():
    sp = get_sp()

    if not sp:
        display_login()
        return

    backend = SpotifyBackend(sp)
    user = sp.me()
    st.sidebar.success(f"Logged in as {user['display_name']}")
    display_logout()

    tab1, tab2, tab3 = st.tabs(["🎧 Moodify", "📊 Your Top Tracks", "🎤 Artist Explorer"])

    with tab1:
        st.header("Mood-Based Playlist")
        mood = st.slider("How are you feeling today?", 0, 10, 5, format="%d")
        if st.button("Get a Track!"):
            result = backend.get_single_recommendation_by_mood(mood)
            if result:
                st.image(result["cover"], width=200)
                st.markdown(f"**[{result['name']} by {result['artist']}]({result['spotify_url']})**")
                st.caption(f"Genre seed: {result['genre_seed']}")

    with tab2:
        st.header("Your Top Tracks")
        interval = st.radio("Time Range", ["short_term", "medium_term", "long_term"], format_func=lambda x: x.replace("_", " ").title())
        df, error = backend.get_top_tracks_by_timeframe(interval=interval)
        if error:
            st.error(error)
        elif df is not None:
            st.dataframe(df, use_container_width=True)

    with tab3:
        st.header("Search for an Artist")
        query = st.text_input("Enter artist name")
        if query:
            tracks, followers = backend.search_artist_top_tracks(query)
            if not tracks:
                st.warning("No matching artist found.")
            else:
                st.subheader(f"Top Tracks (Followers: {followers:,})")
                for i, track in enumerate(tracks):
                    st.image(track["Cover Image"], width=100)
                    st.markdown(f"{i+1}. [{track['Track']}]({track['Spotify Link']}) by {track['Artist']} - Popularity: {track['Popularity']}")

if __name__ == "__main__":
    main()