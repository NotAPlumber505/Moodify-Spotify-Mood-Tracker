import random
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import toml
import streamlit as st

def load_secrets():
    """Load secrets from Streamlit secrets or a local toml file."""
    if "st" in globals() and st.secrets:  # Check if running on Streamlit Cloud
        return st.secrets
    else:
        return toml.load("secrets.toml")  # Use secrets.toml for local development


class SpotifyBackend:
    def __init__(self, redirect_uri=None):
        # Load secrets from Streamlit secrets or local file
        secrets = load_secrets()

        self.sp = None
        self.client_id = secrets["SPOTIFY"]["CLIENT_ID"]
        self.client_secret = secrets["SPOTIFY"]["CLIENT_SECRET"]

        # Use provided redirect_uri or fall back to secrets
        self.redirect_uri = redirect_uri or secrets["SPOTIFY"]["REDIRECT_URI"]

        # Add a standard cache path for token storage (good for both local and cloud)
        self.cache_path = ".spotify_cache.json"

        # Prepare OAuth object using the cache path (this will be reused in other methods)
        self.oauth = SpotifyOAuth(
            self.client_id,
            self.client_secret,
            self.redirect_uri,
            # cache_path=self.cache_path
        )


    def ensure_token(self):
        """Ensure that a valid access token is available."""
        if not self.sp:
            # Already set in __init__, so you can skip re-instantiating
            token_info = self.oauth.get_cached_token()

            if token_info:
                # Check if token has expired
                if token_info['expires_at'] - int(time.time()) <= 0:
                    print("Token expired, refreshing...")
                    token_info = self.oauth.refresh_access_token(token_info["refresh_token"])
                    self.sp = spotipy.Spotify(auth=token_info["access_token"])
                    print("Token refreshed.")  # Debugging log
                else:
                    self.sp = spotipy.Spotify(auth=token_info["access_token"])
                    print("Token is valid.")  # Debugging log
            else:
                print("No cached token found. Please log in again.")
                return False  # Return False if no token is available

        if self.sp:  # If self.sp is initialized, token should be valid
            return True
        else:
            print("Error: Token is invalid or missing.")
            return False

    def request_token(self):
        """Force the user to log in again if the token is missing or expired."""
        auth_url = self.oauth.get_authorize_url()
        print(f"Please log in using this URL: {auth_url}")
        return auth_url

    def get_auth_url(self, scopes):
        """Generate Spotify authorization URL with the given scopes."""
        # Reuse existing self.oauth, update scope
        self.oauth.scope = scopes
        return self.oauth.get_authorize_url()

    def exchange_code_for_token(self, code):
        """Exchange the authorization code for an access token."""
        # Use the already-initialized OAuth object with stored credentials
        token_info = self.oauth.get_access_token(code, as_dict=True)

        if token_info and token_info.get("access_token"):
            # Store authenticated Spotify client for reuse
            self.sp = spotipy.Spotify(auth=token_info["access_token"])
            return token_info
        else:
            print("Token exchange failed.")  # Optional debug log
            return None

    def get_current_user(self):
        """Get the current user's Spotify profile."""
        if self.ensure_token():
            return self.sp.current_user()
        return None

    def get_token_info(self):
        """Return the current token information from the cache, if available."""
        return self.oauth.get_cached_token()

    def create_playlist(self, user_id, name, description="Mood-based playlist"):
        """Create a new playlist for the user."""
        try:
            playlist = self.sp.user_playlist_create(user_id, name, description=description, public=True)
            return playlist['id']  # Return the playlist ID
        except Exception as e:
            print(f"Error creating playlist: {e}")
            return None

    def add_tracks_to_playlist(self, playlist_id, track_uris, track_limit):
        """Add tracks to the playlist, respecting the track limit."""
        try:
            # Ensure track_uris does not exceed the track limit
            track_uris_to_add = track_uris[:track_limit]  # Limit the tracks to the specified track limit

            # Get current user ID automatically via current_user()
            user_id = self.sp.current_user()['id']

            # Now add the tracks to the playlist
            self.sp.user_playlist_add_tracks(user_id, playlist_id, track_uris_to_add)

            print(f"Successfully added {len(track_uris_to_add)} tracks to the playlist.")
        except Exception as e:
            print(f"Error adding tracks to playlist: {e}")

    def get_random_tracks_by_genre(self, mood, num_tracks=5):
        """Fetch multiple random tracks based on mood-related genre."""
        if not self.ensure_token():  # Ensure the token is valid before making the request
            print("Error: No valid token.")
            return [], []  # Return None if the token is invalid

        # Mapping moods to multiple genre combinations based on experiment
        mood_to_genres = {
            range(0, 2): ["ambient", "sad", "piano", "emo", "blues", "classical", "folk", "acoustic", "rainy-day"],
            range(2, 5): ["acoustic", "indie", "lo-fi", "folk", "punk", "punk-rock", "alternative", "indie-pop",
                          "country", "bluegrass"],
            range(5, 7): ["pop", "chill", "acoustic", "indie-pop", "rnb", "hip-hop", "soul", "jazz", "disco", "funk",
                          "latin"],
            range(7, 9): ["dance", "funk", "electro", "indie", "j-rock", "world-music", "edm", "house", "techno",
                          "electronic", "trance", "reggae"],
            range(9, 11): ["edm", "party", "hip-hop", "synth-pop", "j-pop", "rock-n-roll", "pop", "hard-rock", "club",
                           "metal", "drum-and-bass", "breakbeat", "hardstyle"],
        }

        genre_seeds = next((genres for r, genres in mood_to_genres.items() if mood in r), ["pop"])

        # Spotify supports these genre seeds. We're using a predefined list of known valid genres.
        valid_genres = [
            "pop", "rock", "hip-hop", "dance", "indie", "edm", "chill", "punk", "acoustic", "classical",
            "jazz", "blues", "ambient", "country", "lo-fi", "reggae", "metal", "funk", "soul", "r&b", "party",
            "sad", "piano", "electro", "indie-pop", "synth-pop", "folk"
        ]

        # Filter genre seeds to ensure only valid genres are included
        genre_seeds = [genre for genre in genre_seeds if genre in valid_genres]
        print(f"Valid Genre Seeds: {genre_seeds}")  # Debugging log

        try:
            recommended_tracks = []
            seen_tracks = set()  # Set to track unique songs by their Spotify URL

            # Try to fetch tracks for each genre seed
            for genre in genre_seeds:
                search_query = f"genre:{genre}"
                search_results = self.sp.search(q=search_query, type='track',
                                                limit=50)  # Fetch more tracks for better randomness

                if search_results and "tracks" in search_results and len(search_results["tracks"]["items"]) > 0:
                    # Pick `num_tracks` random tracks from the search results
                    tracks = search_results["tracks"]["items"]

                    # Filter out any tracks we've already seen (to avoid duplicates)
                    new_tracks = [track for track in tracks if track['external_urls']['spotify'] not in seen_tracks]

                    # Add these new tracks to the list of seen tracks
                    for track in new_tracks:
                        seen_tracks.add(track['external_urls']['spotify'])

                    # Randomly select tracks from the new list (if there are enough new tracks)
                    random_tracks = random.sample(new_tracks, min(num_tracks, len(new_tracks)))

                    for track in random_tracks:
                        track_data = {
                            "name": track["name"],
                            "artist": track["artists"][0]["name"],
                            "cover": track["album"]["images"][0]["url"],
                            "spotify_url": track["external_urls"]["spotify"],
                            "genre_seed": genre  # Adding the genre seed to the returned data
                        }
                        recommended_tracks.append(track_data)

            # If no tracks found for any of the genres, return None
            if recommended_tracks:
                track_uris = [track['spotify_url'] for track in recommended_tracks]
                return recommended_tracks, track_uris
            else:
                print("No tracks found for the provided genres.")
                st.warning("No recommendations available for the selected mood.")
                return [], []

        except Exception as e:
            print(f"Error while fetching tracks: {e}")
            return [], []  # Return None in case of error

    # Method to get recommendations from mood (valence and energy)
    def get_single_recommendation_by_mood(self, mood):
        """Fetch a single recommendation based on mood."""
        if not self.ensure_token():  # Ensure the token is valid before making the request
            print("Error: No valid token.")
            return None  # Return None if the token is invalid

        # Mapping moods to genres
        mood_to_genres = {
            range(0, 2): ["ambient", "sad", "piano", "emo"],
            range(2, 5): ["acoustic", "indie", "lo-fi", "folk", "punk", "punk-rock"],
            range(5, 7): ["pop", "chill", "acoustic", "indie-pop", "rnb", "hip-hop"],
            range(7, 9): ["dance", "funk", "electro", "indie", "j-rock", "world-music"],
            range(9, 11): ["edm", "party", "hip-hop", "synth-pop", "j-pop", "rock-n-roll"],
        }

        genre_seeds = next((genres for r, genres in mood_to_genres.items() if mood in r), ["pop"])

        # Spotify supports these genre seeds. We're using a predefined list of known valid genres.
        valid_genres = [
            "pop", "rock", "hip-hop", "dance", "indie", "edm", "chill", "punk", "acoustic", "classical",
            "jazz", "blues", "ambient", "country", "lo-fi", "reggae", "metal", "funk", "soul", "r&b", "party",
            "sad", "piano"
        ]

        # Filter genre seeds to ensure only valid genres are included
        genre_seeds = [genre for genre in genre_seeds if genre in valid_genres]
        print(f"Valid Genre Seeds: {genre_seeds}")  # Debugging log

        try:
            # Make the recommendations API call with valid token and limit set to 1
            recs = self.sp.recommendations(
                seed_genres=genre_seeds,  # Pass the list of genres directly
                limit=1  # Limit to a single track
            )

            print(f"Spotify Recommendations Response: {recs}")  # Debugging log

            if recs and "tracks" in recs and len(recs["tracks"]) > 0:
                track = recs["tracks"][0]  # Fetch only the first track from the list
                recommended_track = {
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "cover": track["album"]["images"][0]["url"],
                    "spotify_url": track["external_urls"]["spotify"]
                }

                return recommended_track
            else:
                print("No recommendations found.")
                return None  # Return None if no recommendations are found
        except Exception as e:
            print(f"Error while fetching recommendations: {e}")
            return None  # Return None in case of error

    def get_top_tracks_by_timeframe(self, interval):
        self.ensure_token()

        valid_intervals = ["None", "short_term", "medium_term", "long_term"]

        if interval not in valid_intervals:
            return None, f"Invalid interval: {interval}. Choose from {valid_intervals}."

        try:
            top_tracks = self.sp.current_user_top_tracks(limit=5, time_range=interval)
            if not top_tracks["items"]:
                return None, "No tracks available for the selected interval."

            data = []
            for track in top_tracks["items"]:
                data.append({
                    "Track": track["name"],
                    "Artist": track["artists"][0]["name"],
                    "Spotify Link": track["external_urls"]["spotify"],
                    "Popularity": track["popularity"],
                    "Cover Image": track["album"]["images"][0]["url"] if track["album"]["images"] else "No image available"
                })

            return pd.DataFrame(data), None  # Return DataFrame and no error message
        except Exception as e:
            return None, f"An error occurred: {str(e)}"

    def search_artist_top_tracks(self, artist_name):
        self.ensure_token()

        # Normalize the artist name to handle potential special characters or spaces
        artist_name_normalized = artist_name.strip().replace("/", "").replace(" ", "").lower()

        # Perform the search query with a normalized name, removing special characters
        result = self.sp.search(q=artist_name, type="artist", limit=5)  # Limit to top 5 matches

        if not result["artists"]["items"]:
            return [], []  # No artist found

        # Look through search results to find the best match
        best_match = None
        for artist in result["artists"]["items"]:
            artist_normalized = artist["name"].replace("/", "").replace(" ", "").lower()
            if artist_normalized == artist_name_normalized:
                best_match = artist
                break

        if not best_match:
            return [], []  # No exact match found

        # If a match is found, retrieve the artist's top tracks
        artist_id = best_match["id"]
        top_tracks = self.sp.artist_top_tracks(artist_id)

        # Get the top 5 tracks
        tracks = []
        for track in top_tracks["tracks"][:5]:
            track_data = {
                "Track": track["name"],
                "Artist": track["artists"][0]["name"],
                "Spotify Link": track["external_urls"]["spotify"],
                "Cover Image": track["album"]["images"][0]["url"] if track["album"]["images"] else "No image available",
                "Popularity": track["popularity"]  # Popularity score as a substitute for stream count
            }
            tracks.append(track_data)

        # Get the number of followers for the artist
        artist_followers = best_match["followers"]["total"]
        return tracks, artist_followers


# Example usage:
if __name__ == "__main__":
    backend = SpotifyBackend()
