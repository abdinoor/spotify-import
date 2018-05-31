# Spotify Import

Migrates iTunes txt playlists to Spotify.

Forked from https://github.com/sepehr/xspfy.git

Should work with any txt file as long as the format follows:
- First line is column headings
- Tab separated
- Column 1 is track name
- Column 2 is artist name
- Column 4 is album name


### Usage
`import.py SPOTIFY_USERNAME PLAYLIST_FILE`

### Installation
    pip install requests spotipy
    git clone https://github.com/abdinoor/spotify-import.git
    python import.py
