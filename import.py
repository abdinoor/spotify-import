#!/usr/bin/env python

import spotipy
import spotipy.util
import codecs
import urllib
import glob
import sys
import os

SPOTIFY_CLIENT_ID     = '6508015df04044ffa68efaa4cc4ac8c3'
SPOTIFY_CLIENT_SECRET = '6186195c2bf34bd6a2caf05d76f157fc'
SPOTIFY_AUTH_SCOPE    = 'playlist-modify-public playlist-modify-private'
SPOTIFY_REDIRECT_URI  = 'https://sepehr.github.io/laspotipy'

def spotify_uri(token, artist, track, album = False):
    '''
    Returns spotify uri by artist and track names using Spotify Web API.
    '''
    spotify = spotipy.Spotify(token)

    if album:
        query = 'artist:"%s" album:"%s" %s' % (artist, album, track)
    else:
        query = 'artist:"%s" %s' % (artist, track)

    try:
        response = spotify.search(q = query, type = 'track', offset = 0, limit = 1)

        if len(response['tracks']['items']) > 0:
            return response['tracks']['items'][0]['uri']

        return False
    except Exception as ex:
        print ex
        return False


def spotify_playlist_create(token, username, name, public = True):
    '''
    Creates a public Spotify playlist using its API and returns its ID.
    '''
    spotify  = spotipy.Spotify(token)

    try:
        response = spotify.user_playlist_create(username, name, public = public)

        if not response or not response['id']:
            return False

        return response['id']
    except Exception as ex:
        print ex
        return False


def spotify_playlist_add(token, username, playlist_id, tracks):
    '''
    Adds passed track URIs to the playlist specified.
    '''
    spotify = spotipy.Spotify(token)

    # Add the first 100 tracks
    try:
        response = spotify.user_playlist_add_tracks(username, playlist_id, tracks[:100])

        if not response['snapshot_id']:
            return False

        # A maximum of 100 tracks can be added per request, so:
        if len(tracks) > 100:
            response = spotify_playlist_add(token, username, playlist_id, tracks[100:])

        return response.get('snapshot_id', False)
    except:
        return False


def spotify_auth_token(username, auth_scope, client_key, client_secret, redirect_uri):
    '''
    Grabs passed scope permissions for a Spotify user.
    '''
    return spotipy.util.prompt_for_user_token(username, auth_scope, client_key, client_secret, redirect_uri)


class Playlist(object):
    '''
    its a playlist
    '''


class Track(object):
    '''
    its a track in a playlist
    '''


def txt_parse(path):
    '''
    Parse a text file into a playlist object
    '''
    playlist = Playlist()
    playlist.title = '.'.join(path.split('/')[-1].split('.')[:-1])  # filename cleaned
    playlist.track = []
    with codecs.open(path, encoding='utf-8') as f:
        lines = f.read().splitlines()
        for line in lines[1:]:
            try:
                fields = line.split('\t')
                track = Track()
                track.title   = clean_track_name(fields[0])
                track.creator = clean_artist(fields[1])
                track.album   = fields[3]
                playlist.track.append(track)
            except IndexError as ex:
                print line, ex
                continue
            except Exception as ex:
                print line, ex
                raise ex

    return playlist


def clean_bad_chars(input):
    clean = input.lower()
    clean = clean.replace('(', '')
    clean = clean.replace(')', '')
    clean = clean.replace('[', '')
    clean = clean.replace(']', '')
    clean = clean.replace('&', ', ')
    return clean


def consolidate_spaces(clean):
    return ' '.join(clean.split())


def clean_features(input):
    clean = input
    clean = clean.replace('ft.', 'feat.')
    if 'feat.' in clean:
        clean = clean.split('feat.')[0]
    return clean


def clean_track_name(track_name):
    clean = clean_bad_chars(track_name)
    clean = clean_features(clean)
    clean = consolidate_spaces(clean)
    return clean


def clean_artist(artist):
    clean = clean_bad_chars(artist)
    clean = clean_features(clean)
    if ',' in clean:
        clean = clean.split(',')[0]
    clean = consolidate_spaces(clean)
    return clean


def main():
    # -------------------------------------------------------------------------
    # Check args, init
    # -------------------------------------------------------------------------
    if len(sys.argv) < 3:
        sys.exit('\nUSAGE: spotify_import.py SPOTIFY_USERNAME FILE_PATH\n')
    else:
        filepath    = sys.argv[2]
        spotify_user = sys.argv[1].lower()

    print '\nConnecting to Spotify API endpoint, authorizing as "%s"...' % spotify_user
    token = spotify_auth_token(spotify_user, SPOTIFY_AUTH_SCOPE, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI)

    process(filepath, token, spotify_user)


def process(filepath, token, spotify_user):
    print '\nProcessing "%s"...' % filepath

    pl = txt_parse(filepath)

    failed = count = 0
    pl_len = len(pl.track)
    spotify_pl = {
        'title':  pl.title,
        'tracks': []
    }

    print 'Found %d tracks in the playlist:' % pl_len

    spotify_pls = []

    for track in pl.track:
        uri = spotify_uri(token, track.creator, track.title)

        count += 1
        print '\t%d/%d: "%s - %s"' % (count, pl_len, track.creator[:40], track.title[:40])

        if uri:
            print '\t[FOUND] %s\n' % uri
            spotify_pl['tracks'].extend([uri])

        else:
            print '\t[FAILED]\n'
            failed += 1

    spotify_pls.extend([spotify_pl])

    print '%d tracks not found on Spotify.' % failed

    print 'Creating Spotify playlist with %d found tracks: "%s"' % (len(spotify_pl['tracks']), spotify_pl['title'])

    pl_id = spotify_playlist_create(token, spotify_user, spotify_pl['title'])
    if not pl_id:
        print '[ERROR] Could not create Spotify playlist. Skipping...'
        return

    success = spotify_playlist_add(token, spotify_user, pl_id, spotify_pl['tracks'])
    if not success:
        print '[ERROR] Could not add tracks to the playlist. Please make sure to REMOVE the playlist manually.'
        return

    print '[SUCCESS] Enjoy!'


if __name__ == '__main__':
    main()
