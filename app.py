from flask import Flask
from spotify_api.api import SpotifyApi
import pylast

app = Flask(__name__)

s_api = SpotifyApi()

LASTFM_API_KEY = "b9ba81a4f80bbff4fa3fcf7df609947e"
LASTFM_API_SECRET = "65f9cf1308e52e3369c5eeb992fa846a"

network = pylast.LastFMNetwork(api_key = LASTFM_API_KEY, 
                               api_secret = LASTFM_API_SECRET)

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

def formatSpotifyLink(link):
    return '<iframe src="https://embed.spotify.com/?uri=%s" \
                    width="300" height="380" \
                    frameborder="0" \
                    allowtransparency="true"></iframe>' % (link)

@app.route("/")
def index():

    user = network.get_user("thesimius")

    #get recent tracks of user
    tracks = [played_track[0] for played_track in user.get_recent_tracks()]
   
    #get unique album names
    albums = dict()
    for track in tracks:
        albums[track.get_album().get_name()] = track.get_artist().get_name()

    album_links = [getSpotifyLink(album_name, artist_name) 
                   for album_name, artist_name 
                   in albums.items()]

    awesome_list = " ".join(formatSpotifyLink(a) for a in album_links)

    return "<h1>Magic Lists</h1>" + awesome_list

if __name__=="__main__":
    app.run(debug = True)
