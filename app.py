import io

import streamlit as st
import plotly.express as px
import pandas as pd
import requests
import toml
from main import SpotifyBackend
from auth_server import start_server, open_browser, auth_code_holder
import threading
from geopy.geocoders import Nominatim

# Initialize Spotify backend
sb = SpotifyBackend()

# Set page config
st.set_page_config(page_title="Moodify", layout="wide", page_icon="favicon.ico")
st.title("🎵 Moodify: Your Spotify Mood Tracker and Browser")

# Start the Flask server in the background
if "flask_started" not in st.session_state:
    flask_thread = threading.Thread(target=start_server, daemon=True)
    flask_thread.start()
    st.session_state["flask_started"] = True

# Color picker for charts
chart_color = st.sidebar.color_picker("Pick a color for your charts", "#1f77b4")  # Default to blue

# Step 1: Generate and open Spotify auth URL with the correct scopes
if "token_exchanged" not in st.session_state or not st.session_state["token_exchanged"]:
    if st.button("🔐 Login with Spotify"):
        # Include 'user-top-read' scope for top track access
        scopes = "user-read-recently-played user-top-read playlist-modify-public playlist-modify-private"
        auth_url = sb.get_auth_url(scopes)
        open_browser(auth_url)
        st.info("A new tab has opened. Please authorize the app and return here. 🌐")
        st.info("When you finish authentication, please refresh the page. ♺")

# Step 2: Poll for the code from the Flask server and exchange it for a token
if auth_code_holder["code"] and "token_exchanged" not in st.session_state:
    print(f"Received auth code: {auth_code_holder['code']}")
    # Exchange the authorization code for the access token
    token_info = sb.exchange_code_for_token(auth_code_holder["code"])

    # Check if the token exchange was successful and update session state
    if token_info:
        st.session_state["token_exchanged"] = True
        st.success("✅ Authorized with Spotify! Now you can track your mood and songs.")
    else:
        st.error("❌ Failed to exchange code for token. Please try again.")

# Step 3: Check session state for token and display tabs
if "token_exchanged" in st.session_state and st.session_state["token_exchanged"]:
    print("User is logged in. Displaying tabs...")

    # Hide the login button once the user is logged in
    st.session_state["token_exchanged"] = True
    home_tab, mood_playlist_tab, top_songs_tab, artist_search_tab, artist_info_tab = st.tabs([
        "🏠 Home",
        "🎧 Mood Playlist",
        "📈 Top Songs Chart",
        "🔍 Artist Search",
        "📖 Artist Biographies",
    ])

    with home_tab:
        # Home tab content
        col1, col2 = st.columns([4, 1])  # Adjust the column ratio as per the layout
        with col1:
            st.header("Welcome to Moodify! 🎶")
            st.write("Moodify is a Spotify Mood Tracker that allows you to: ")
            st.markdown("""
                - Track your **mood** and generate music playlists that match your emotional state. 😊🎶
                - View your **top songs** over different time periods and explore music trends. 📊🎧
                - **Search for your favorite artists** and check out their top tracks and popularity. 🔍🎤
                - **Read artist biographies** to learn more about your favorite artists' backgrounds and journey in music. 📖🎤
                - **Customize your charts** using the sidebar color picker! 🎨 Change the colors of the charts in the "Top Songs" and "Artist Search" tabs to match your style and preferences. 🌈
            """)

            st.write("How does it work? 🤔")
            st.markdown("""
                - **Step 1**: Log in with Spotify and grant access to your account. 🔑
                - **Step 2**: Use the mood slider to set your emotional state and get a playlist recommendation. 🎚️🎶
                - **Step 3**: Explore your top songs, based on the time period you choose (short-term, medium-term, long-term). 📅🎵
                - **Step 4**: Search for any artist and see their top tracks, popularity, and followers! 🎤👀
                - **Step 5**: Want to know more about the artist? Check out their **biography** to get insights into their musical journey, background, and accomplishments! 📖🎶
            """)

            st.subheader("🎨 **Moodify's Vision:**")
            st.markdown("""
                <div style="background-color: #f0f0f5; padding: 20px; border-radius: 10px; text-align: center; font-size: 18px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin: 0 auto; width: 80%; ">
                    <strong>Vision of Moodify:</strong><br>
                    <em>"Moodify is here to enhance your listening experience, offering tailored playlists based on your emotional state. Whether you're feeling happy, sad, or somewhere in between, we aim to create the perfect soundtrack for your mood!"</em>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.image("C:\\Users\\Owner\\PycharmProjects\\Song_Browser_Project2HCI\\music_background.jpg", width=600)

    # Mood Playlist Tab
    with mood_playlist_tab:
        st.header("🎧 Mood-based Playlist Recommendation 🎶")

        st.info("""
            Curious about your listening habits? In this tab, you can:
            - 🎵 Get **mood-based** song recommendations
            - 📝 **Name** and **create** a playlist in your Spotify
            - 📥 **Download** song info as a **CSV** file
            - 🔄 **Refresh** your playlist to get a new set of mood-based recommendations without changing your current settings!
        """)

        # Mood slider with emojis and a legend
        mood = st.slider("How are you feeling today?", 0, 10, 5, format="%d",
                         help="0 = 😢 very sad, 5 = 🙂 neutral, 10 = 😄 very happy")
        st.write(f"Mood: {mood} - {['😢', '😔', '😟', '😐', '🙂', '😊', '😄'][mood // 2]}")
        st.info("Please use the slider above to reflect your mood. 😌")

        # Track limit input - User selects how many tracks they want (number input)
        track_limit = st.number_input("How many tracks would you like in your playlist?", min_value=1, max_value=50,
                                      value=5, step=1, help="Choose the number of tracks (maximum 50).")

        st.info("Please input a valid number between 1 and 50.")

        # Output the selected number of tracks
        st.write(f"Tracks in Playlist: {track_limit}")

        # Get recommendations based on mood
        recommended_tracks, track_uris = sb.get_random_tracks_by_genre(mood, num_tracks=track_limit)

        # Input for playlist name
        playlist_name = st.text_input("Enter a name for your playlist", f"Moodify Playlist - {mood}")
        st.info("Please input a valid name for the playlist before generating.")

        st.write("### Actions")

        # Create playlist button
        create_playlist_button = st.button("Create Playlist and Add Tracks")

        # Prepare track data for CSV download
        track_data = [{
            'Track Name': track['name'],
            'Artist': track['artist'],
            'Genre': track['genre_seed'].capitalize(),
            'Spotify URL': track['spotify_url'],
            'Cover Image': track['cover']
        } for track in recommended_tracks[:track_limit]]  # Ensure only the selected number of tracks

        # Convert to DataFrame
        df = pd.DataFrame(track_data)

        # Convert DataFrame to CSV (ensure correct encoding)
        csv = df.to_csv(index=False)

        # Convert the CSV to a downloadable object in memory
        csv_bytes = io.BytesIO()
        csv_bytes.write(csv.encode())
        csv_bytes.seek(0)

        # Display the "Download Playlist as CSV" button first (above the music)
        st.download_button(
            label="Download Playlist as CSV",
            data=csv_bytes,
            file_name="mood_playlist.csv",
            mime="text/csv",
            key=f"download_{mood}"  # Adding a unique key based on the mood
        )

        # Refresh button
        refresh_button = st.button("Refresh Playlist")

        if recommended_tracks:
            # Display the tracks in a grid format
            st.subheader("Your Personalized Playlist 🎶")

            # Show the music tracks after the download button
            if create_playlist_button:
                # Create a new playlist with custom or default name
                user_id = sb.sp.current_user()['id']  # Get the current user's ID
                playlist_id = sb.create_playlist(user_id, playlist_name)  # Create playlist with user-defined name
                if playlist_id:
                    try:
                        sb.add_tracks_to_playlist(playlist_id, track_uris, track_limit)
                        st.success(
                            f"✅ Playlist '{playlist_name}' created and {len(track_uris[:track_limit])} tracks added!")
                    except Exception as e:
                        st.error(f"An error occurred while adding tracks: {e}")
                else:
                    st.error("Error creating playlist. Please try again.")

            # Display tracks in a grid-like format (using columns)
            track_columns = st.columns(3)  # 3 columns for a grid layout
            for i, track in enumerate(
                    recommended_tracks[:track_limit]):  # Ensure only the selected number of tracks are displayed
                # Get the appropriate column for the track
                col = track_columns[i % 3]
                with col:
                    st.image(track['cover'], width=150)  # Display cover image
                    st.write(f"**{track['name']}** by {track['artist']}")
                    st.write(f"Genre: {track['genre_seed'].capitalize()}")
                    st.markdown(f"[Listen on Spotify]({track['spotify_url']})")

            # Refresh playlist
            if refresh_button:
                recommended_tracks, track_uris = sb.get_random_tracks_by_genre(mood, num_tracks=track_limit)
                st.session_state.recommended_tracks = recommended_tracks
                st.session_state.track_uris = track_uris
                st.success("Playlist refreshed with new recommendations!")

        else:
            st.error("Could not generate a playlist. Please try again later.")

    with top_songs_tab:
        st.header("🎵 Your Top Songs")
        st.info("""
            **📈 Track Your Top Songs! 🎶**

            Curious about your listening habits? In this tab, you can:
            - **View your top songs** from the past 30 days, 6 months, or since forever! 📅🎧
            - Explore your **popularity trends** with interactive charts. 📊
            - See which tracks are currently ruling your Spotify account! 🌟🎶
            - **Filter by time period** (short-term, medium-term, long-term) and track your listening journey over time! 🎶
            - **Save your top tracks** as a CSV file for easy access, tracking, and sharing!📥
        """)
        st.write("There are three time intervals you can choose from:")
        st.markdown("""        
                            - **short_term**: Past 30 Days --> 1 Month
                            - **medium_term**: Past 180 Days --> 6 Months
                            - **long_term**: All Time --> Since your Spotify account was created
                        """)

        interval = st.selectbox("Select Time Interval", ["None", "short_term", "medium_term", "long_term"])

        # Check if the interval is not 'None'
        if interval != "None":
            top_tracks, error_message = sb.get_top_tracks_by_timeframe(interval)

            if isinstance(top_tracks, pd.DataFrame):
                # Sort by popularity
                top_tracks_sorted = top_tracks.sort_values(by="Popularity", ascending=False).reset_index(drop=True)

                # Add Track # column
                top_tracks_sorted.insert(0, "Track No.", range(1, len(top_tracks_sorted) + 1))

                # Prepare track data for CSV download (after sorting the top tracks)
                track_data = [{
                    'Track No.': row['Track No.'],
                    'Track Name': row['Track'],
                    'Artist': row['Artist'],
                    'Popularity': row['Popularity'],
                    'Spotify Link': row['Spotify Link']
                } for _, row in top_tracks_sorted.iterrows()]  # Convert rows to a list of dicts

                # Convert to DataFrame
                df = pd.DataFrame(track_data)

                # Convert DataFrame to CSV (ensure correct encoding)
                csv = df.to_csv(index=False)

                # Convert the CSV to a downloadable object in memory
                csv_bytes = io.BytesIO()
                csv_bytes.write(csv.encode())
                csv_bytes.seek(0)

                # Display the "Download Top Tracks as CSV" button right after the select box
                st.download_button(
                    label="Download Top Tracks as CSV",
                    data=csv_bytes,
                    file_name=f"top_tracks_{interval}.csv",
                    mime="text/csv",
                    key=f"download_top_tracks_{interval}"  # Adding a unique key based on the interval
                )

                # Show dataframe
                st.subheader(f"🎶 Top Tracks ({interval.replace('_', ' ').title()})")
                st.dataframe(top_tracks_sorted[["Track No.", "Track", "Artist", "Popularity", "Spotify Link"]])

                # Plot popularity chart with selected color
                fig = px.bar(
                    top_tracks_sorted,
                    x="Track",
                    y="Popularity",
                    title="Track Popularity Comparison",
                    labels={"Track": "Track Name", "Popularity": "Popularity"},
                    hover_data=["Artist"],
                    height=500,
                    color_discrete_sequence=[chart_color]  # Apply selected color
                )
                fig.update_layout(xaxis_tickangle=360)
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.error(error_message or "Something went wrong retrieving top tracks.")
        else:
            st.info("Please select a time period to see your top songs.")

    # Artist Search Tab
    with artist_search_tab:

        # Initialize the artists_data in session state if it doesn't exist
        if "artists_data" not in st.session_state:
            st.session_state.artists_data = []

        st.header("🔍 Search for an Artist 🎤")
        st.info("""
                    **🔍 Find Your Favorite Artists 🎤**

                    Want to learn more about your favorite artists? This tab allows you to:
                    - **Search for any artist** and see their top tracks, popularity, and followers. 🎤✨
                    - Dive deep into **track popularity** and compare across multiple artists! 📊🎵
                    - Check out **album cover images** and **Spotify links** to listen instantly! 🔥🎶
                    - Keep track of your **favorite artists** and compare them to others with interactive charts! 📈
                """)
        artist_name = st.text_input("Enter artist name ✨")

        if artist_name == "":
            st.info("Please input an artist name. 🎵")

        if st.button("Search 🔍") and artist_name:
            # Search for the artist and retrieve top tracks and followers
            tracks_data, artist_followers = sb.search_artist_top_tracks(artist_name)

            if tracks_data:
                # Add the artist's name and follower count to the session state list
                st.session_state.artists_data.append({
                    "Artist": artist_name,
                    "Followers": artist_followers
                })

                st.subheader(f"Top 5 Tracks by {artist_name} 🎤")

                # Create the bar chart for multiple artists' followers with selected color
                followers_df = pd.DataFrame(st.session_state.artists_data)
                followers_fig = px.bar(followers_df, x="Artist", y="Followers",
                                       title="Artist Follower Count Comparison",
                                       labels={"Followers": "Number of Followers", "Artist": "Artist"},
                                       color_discrete_sequence=[chart_color])  # Apply selected color
                st.plotly_chart(followers_fig)

                # Prepare track data for the line chart (track popularity over tracks)
                track_popularity = [{"Track": track["Track"], "Popularity": track["Popularity"]} for track in
                                    tracks_data]
                popularity_df = pd.DataFrame(track_popularity)

                # Create a line chart for track popularity with selected color
                popularity_fig = px.line(popularity_df, x="Track", y="Popularity",
                                         title=f"{artist_name}'s Track Popularity 📊",
                                         labels={"Track": "Track Name", "Popularity": "Track Popularity"},
                                         line_shape="linear",
                                         color_discrete_sequence=[chart_color])  # Apply selected color
                st.plotly_chart(popularity_fig)

                # Add track numbers starting from 1 and make it the leftmost column
                for i, track in enumerate(tracks_data, 1):
                    track["Track Number"] = i  # Add a track number column starting from 1

                # Reorder the DataFrame to have 'Track Number' as the first column
                columns_order = ['Track Number'] + [col for col in tracks_data[0] if col != 'Track Number']
                tracks_data = [{col: track[col] for col in columns_order} for track in tracks_data]

                # Create a DataFrame for displaying in a table
                df = pd.DataFrame(tracks_data)
                st.dataframe(df)  # This creates the interactive table

                # Display each track's cover image and song previews in a grid with track numbers
                col_count = 3  # Define the number of columns in the grid (you can adjust this)
                for i in range(0, len(tracks_data), col_count):
                    cols = st.columns(col_count)  # Create columns for the grid
                    for j, track in enumerate(tracks_data[i:i + col_count]):
                        with cols[j]:
                            track_number = track["Track Number"]
                            cover_image_url = track["Cover Image"]
                            track_name = track["Track"]
                            spotify_link = track["Spotify Link"]

                            # Add track number to the preview caption
                            caption = f"{track_name} (No. {track_number})"

                            if cover_image_url != "No image available":
                                st.image(cover_image_url, caption=caption, width=150)
                            else:
                                st.write(f"No cover image available for {track['Track']}.")

                            st.markdown(f"[▶️ Open in Spotify]({spotify_link})")

            else:
                st.error("Artist not found or no tracks available. 🙁")


    # Function to get location from coordinates using Geopy
    def get_location_from_coordinates(lat, lon):
        geolocator = Nominatim(user_agent="artist-info-app")
        location = geolocator.reverse((lat, lon), language='en')

        # Extracting only city, postal code, and country from the full address
        if location:
            # Split the address into parts
            address_parts = location.address.split(",")

            # Assuming the address follows the format of "City, Postal Code, Country"
            if len(address_parts) >= 3:
                city = address_parts[-4].strip()  # 4th last item in the list (city)
                postal_code = address_parts[-3].strip()  # 3rd last item in the list (postal code)
                country = address_parts[-1].strip()  # Last item in the list (country)
                return f"{city}, {postal_code}, {country}"

        return "Location not available"

    # Artist Info Tab
    with artist_info_tab:

        st.header("🎤 Artist Info Finder")
        st.info("""
            **🎤 Artist Info Finder 🌍**

            Want to know more about an artist's roots and background? This tab is for you:
            - **Select any artist** and see their bio, hometown, and image! 🌍🎤
            - View the artist's **birthplace on the map** for a geographical perspective! 🗺️📍
            - Discover fun facts about **your favorite artists** and see where they grew up! 🏙️
            - Explore their genre, background, and learn about their journey to stardom! 🚀🎶
        """)

        # Sample data for artists with approximate birthplaces and coordinates
        artists_data = [
            {"artist": "Adele", "genre": "Pop", "lat": 51.5074, "lon": -0.1278},  # London (Adele's birthplace)
            {"artist": "Olivia Rodrigo", "genre": "Pop", "lat": 38.8833, "lon": -77.0167},  # Washington, D.C.
            {"artist": "Billie Eilish", "genre": "Pop", "lat": 34.0522, "lon": -118.2437},  # Los Angeles
            {"artist": "The Weeknd", "genre": "R&B", "lat": 43.65107, "lon": -79.347015},  # Toronto
            {"artist": "Lady Gaga", "genre": "Pop", "lat": 40.7447, "lon": -73.9947}  # New York City
        ]

        # Manually input artist images (URL or local file paths)
        artist_images = {
            "Adele": "C:\\Users\\Owner\\PycharmProjects\\Song_Browser_Project2HCI\\adele.jpg",
            "Olivia Rodrigo": "C:\\Users\\Owner\\PycharmProjects\\Song_Browser_Project2HCI\\olivia-rodrigo.jpg",
            "Billie Eilish": "C:\\Users\\Owner\\PycharmProjects\\Song_Browser_Project2HCI\\billie-eilish.jpg",
            "The Weeknd": "C:\\Users\\Owner\\PycharmProjects\\Song_Browser_Project2HCI\\the-weeknd.jpg",
            "Lady Gaga": "C:\\Users\\Owner\\PycharmProjects\\Song_Browser_Project2HCI\\lady-gaga.jpg"
        }

        # Convert data into pandas DataFrame for use with st.map
        df = pd.DataFrame(artists_data)

        # Default option: "Select an Artist"
        selected_artist = st.selectbox("Select an Artist", ["Select an Artist"] + list(df['artist']),
                                       key="artist_selectbox")

        # If the "Select an Artist" option is chosen, display a message and do nothing
        if selected_artist == "Select an Artist":
            st.info("Please select an artist from the dropdown to see their information. 🎤✨")
        else:
            def load_secrets():
                if "st" in globals() and st.secrets:  # Check if running on Streamlit Cloud
                    return st.secrets
                else:
                    return toml.load("secrets.toml")  # Use secrets.toml for local development


            def load_lastfm_api_key():
                secrets = load_secrets()
                return secrets["lastfm"]["api_key"]


            # Function to get artist information
            def get_artist_info(artist_name):
                API_KEY = load_lastfm_api_key()  # Load the API key securely
                url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={artist_name}&api_key={API_KEY}&format=json"
                response = requests.get(url)
                data = response.json()

                if 'artist' in data:
                    artist_info = data['artist']
                    biography = artist_info['bio']['content'] if 'content' in artist_info['bio'] else None
                    location = artist_info['bio']['published'] if 'published' in artist_info[
                        'bio'] else "Location not available"
                    image_url = artist_info['image'][2]['#text'] if 'image' in artist_info and len(
                        artist_info['image']) > 2 else None
                    return biography, location, image_url

                return None, None, None


            # Get artist info from Last.fm API
            biography, location, image_url = get_artist_info(selected_artist)

            # Use manually inputted image if available
            artist_image = artist_images.get(selected_artist, None)

            # Show map and artist details
            show_map = st.checkbox("Show Artist Hometown on Map")

            if show_map:
                artist_data = df[df['artist'] == selected_artist].iloc[0]
                artist_lat, artist_lon = artist_data['lat'], artist_data['lon']
                # Get simplified location
                simplified_location = get_location_from_coordinates(artist_lat, artist_lon)
                st.write(f"**Hometown**: {simplified_location}")  # Display simplified location
                st.map(pd.DataFrame({'lat': [artist_lat], 'lon': [artist_lon]}))  # Show artist's location on map

            # Use columns to lay out the biography and image side by side
            col1, col2 = st.columns([2, 1])  # Left column for text (biography), right column for image

            # Display artist information in the left column
            with col1:
                if biography:
                    st.subheader(f"Biography of {selected_artist}:")
                    st.write(biography)

            # Display the artist image in the right column
            with col2:
                if artist_image:
                    st.image(artist_image, caption=f"{selected_artist} Image", use_container_width=True)
                elif image_url:
                    st.image(image_url, caption=f"{selected_artist} Image", use_container_width=True)
                else:
                    st.write("No image available for this artist.")
else:
    st.warning("🔑 You need to log in to access the features.")
    print("User is not logged in. Please log in.")




