import os
import sys
import json
import webbrowser
from json.decoder import JSONDecodeError

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

import networkx as nx
import matplotlib.pyplot as plt

from math import log

import plotly.graph_objects as go

# Create spotify object with security token
username = 1221250460
token = util.prompt_for_user_token(username)
spotifyObject = spotipy.Spotify(auth=token)

# Get and display current user playlists
results = spotifyObject.current_user_playlists(limit=50)
playlists = results['items']

playlist_amount = []
for i, item in enumerate(playlists):
    print("%d %s" % (i, item['name']))
    playlist_amount.append(i)
    
#Ask user to select a plyalist
y = False
while y == False:
    x = int(input("\nWhat playlist would you like to analyze?\n"))
    playlist_description = playlists[x]
    playlist_name = playlist_description['name']

    if x not in playlist_amount:
        print("\nSelect a valid number")
    else:
        print("\nYou selected:",playlist_name,"\n")
        y = True
playlistEntries = spotifyObject.playlist_tracks(playlist_description['id'],offset=0)

# Get items from playlist
items = playlistEntries['items']
    
allGenres = []
for item in items:

    track = item['track']
    
    try:
        # Extract track, album, and artist data
        track = item['track']

        album = track['album']
        artists = track['artists']

        # Extract track, album, and artist IDs
        trackId = track['id']
        albumId = album['id']
        artist = artists[0] # Take the first artist
        artistId = artist['id']

        # Extract genre
        artistDetails = spotifyObject.artist(artistId)
        artistGenres = artistDetails['genres']
        
        # Add all genres to list
        for genre in artistGenres:
            allGenres.append(genre)
    except:
        print("Dropped a track")

# Remove repeats
genres = list(set(allGenres))

# Counting occurences for each genre
amount_list = []
for genre in genres:
    genre_amount = 0
    for j in range(len(allGenres)):
        if genre == allGenres[j]:
            genre_amount += 1
    amount_list.append(genre_amount)

# Create ordered list and print histogram
print("\n",playlist_name,"\n")
print(" GENRE                        | SCORE")
genresX = []
amount_listX = []
b=1
while len(amount_list) > 0:
    max_value = max(amount_list)
    max_index = amount_list.index(max_value)
    max_genre = genres[max_index]
    
    print("______________________________|______")
    print(str(b)+". "+max_genre+" "*(30-len(str(b)+". "+max_genre))+"| "+str(max_value)+"      "+"*"*max_value)
    
    genresX.append(max_genre)
    genres.remove(max_genre)
    
    amount_listX.append(amount_list[max_index])
    amount_list.remove(amount_list[max_index])
    b+=1

# Ask user to prune nodes
node_amount = int(input("\n\nWhat is your genre threshold?\n"))

ax = plt.gca()
ax.set_title("Micro-Genre Graph\n"+playlist_name)

# Create graph
g=nx.Graph()

# Add nodes in an ordered fashion
g.add_nodes_from(genresX)
    
for item in items:
    
    try:
        # Extract genre
        track = item['track']
        artists = track['artists']
        artist = artists[0] # Take the first artist
        artistId = artist['id']
        artistDetails = spotifyObject.artist(artistId)
        artistGenres = artistDetails['genres']

        # Get connections
        for genreX in artistGenres:
            for genreY in artistGenres:
                if genreX != genreY:
                    g.add_edge(genreX,genreY)
    except:
        print("Track Dropped")

# Remove extra nodes
XX_amounts = []
XX_genres = []
for i, genre in enumerate(genresX):
    if amount_listX[i] < node_amount:
        g.remove_node(genre)
    else:
        XX_amounts.append(amount_listX[i])
        XX_genres.append(genre)

# Make size of nodes bigger
XX_amounts = [i**(log(7000)/log(XX_amounts[0])) for i in XX_amounts]

nx.draw(g, with_labels=True, node_color="#02D81F", edge_color="#02D81F", node_size=XX_amounts, style=":", font_size=12, font_family="arial black", ax=ax)

plt.show()
