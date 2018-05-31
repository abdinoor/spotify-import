#Spotify Import

Migrates iTunes txt playlists to Spotify.

Forked from https://github.com/sepehr/xspfy.git

Should work with any txt file as long as the format follows:
- First line is column headings
- tab separated
- column 0 is track name
- column 2 is artist name
- column 4 is album name


###Usage
`python xspfy.py SPOTIFY_USER_ID TXT_PATH `

###Installation
    pip install requests spotipy
    git clone https://github.com/abdinoor/spotify-import.git
    python import.py
