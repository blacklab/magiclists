from datetime import datetime
from flask import Flask, render_template
import json
import requests
from spotify_api.api import SpotifyApi

app = Flask(__name__)

s_api = SpotifyApi()

LASTFM_API_KEY = "b9ba81a4f80bbff4fa3fcf7df609947e"
LASTFM_API_SECRET = "65f9cf1308e52e3369c5eeb992fa846a"

def getRecentTracks(user):

    url = "http://ws.audioscrobbler.com/2.0/"

    payload = {"api_key": LASTFM_API_KEY, 
              "method": "user.getrecenttracks",
              "user": user,
              "format": "json"}

    response = requests.get(url, params = payload)
    app.logger.debug(response.url)

    if response.status_code != 200:
        raise Exception("Panic! Cannot call lastfm user.getrecentracks!")

    #process response
    data = json.loads(response.text)

    return data['recenttracks']['track']

def isArtistOfAlbum(spotify_album, artist_name):
    for a in spotify_album.artists:
        if a.name == artist_name:
            return True

    return False

def getSpotifyLink(album_name, artist_name):
    """
    album_name: str
    artist_name: str
    """

    #TODO: Use advanced search
    #Search for albums in Spotify
    albums = s_api.albums.search(album_name)

    #Look in search results for best first fit
    for album in albums:
        if isArtistOfAlbum(album, artist_name):
            return album.href

    print "Unknown for: %s" % (album_name)
    return "Unknown"

@app.route("/<username>")
def index(username):

    #get recent tracks of user
    app.logger.debug("Get recent tracks from user... %d" % datetime.now().second)
    tracks = getRecentTracks(username)
       
    #get unique album names
    albums = dict()
    for track in tracks:
        try:
            albums[track['album']['#text']] = track['artist']['#text']
        except AttributeError:
            pass

    #Get Spotify links and collect data
    app.logger.debug("Look for Spotify links... %d" % datetime.now().second)
    album_data = [(album_name, getSpotifyLink(album_name, artist_name))
                  for album_name, artist_name 
                  in albums.items()]

    print album_data

    app.logger.debug("Render template... %d" % datetime.now().second)
    return render_template("index.html", albums = album_data)

if __name__=="__main__":
    app.run(debug = True)
