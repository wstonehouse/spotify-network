"""
This script does things
"""

from collections import Counter 

import dash
from dash import dcc
from dash import html
import networkx as nx
import plotly.graph_objs as go

import json

from json.decoder import JSONDecodeError

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

import networkx as nx
import matplotlib.pyplot as plt

from math import log

import plotly.graph_objects as go
from chart_studio import plotly
from plotly.graph_objs import *

def network_graph():
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

    x = True
    while x:

        #Ask user to select a plyalist
        y = True
        while y:
            x = int(input("\nWhat playlist would you like to analyze?\n"))
            playlist_description = playlists[x]
            playlist_name = playlist_description['name']

            if x not in playlist_amount:
                print("\nSelect a valid number")
            else:
                print("\nYou selected:",playlist_name,"\n")
                y = False

        # Get items from playlist
        playlistEntries = spotifyObject.playlist_tracks(playlist_description['id'],offset=0)
        items = playlistEntries['items']
            
        # Collect all the genres in the playlist in a list
        allGenres = []
        for item in items:
            track = item['track']
            try:
                # Extract track and artist data
                track = item['track']
                artists = track['artists']

                # Extract track, album, and artist IDs
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

        print(allGenres)

        # Dictionary (Keys: Genre, Values: Genre Count)
        genre_count = dict(Counter(allGenres))

        # Sort the dictionary by descending values
        d = dict(sorted(genre_count.items(), key = lambda x: x[1], reverse = True))

        # Make a list without repeats
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
        node_amount = int(input("\n\nWhat is your genre?\n"))

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
        count=0
        for i, genre in enumerate(genresX):
            if amount_listX[i] < node_amount:
                g.remove_node(genre)
            else:
                XX_amounts.append(amount_listX[i])
                XX_genres.append(genre)
                count+=1

        # Make size of nodes bigger
        XX_amounts = [(i**(log(7000)/log(XX_amounts[0])/1.8)) for i in XX_amounts]

        print("AMOUNTSSSS")
        print(XX_amounts)

        pos=nx.spring_layout(g)

        print(XX_amounts)
        print(g.nodes())

        nx.draw(g, with_labels=True, node_color="#02D81F", edge_color="#02D81F", node_size=XX_amounts, style=":", font_size=12, font_family="arial black", ax=ax)

        for node in g.nodes():
            g.node[node]['pos']= pos[node]

        print(g.nodes(data=True))

        ##########################
        #  plotly shit goes here #
        ##########################

        edge_x = []
        edge_y = []
        for edge in g.edges():
            x0, y0 = g.nodes[edge[0]]['pos']
            x1, y1 = g.nodes[edge[1]]['pos']
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            #hovertemplate="hello",
            #text=max_value,
            #hoverinfo='text',
            mode='lines')

        node_x = []
        node_y = []

        for node in g.nodes():
            x, y = g.nodes[node]['pos']
            node_x.append(x)
            node_y.append(y)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            #hoverinfo='text',
            marker=dict(
                showscale=True,
                # colorscale options
                #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale='Greens',
                reversescale=True,
                color='Green',
                size=XX_amounts,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2),
            text = genresX)

        # SHOW PLOTLY FIGURE FINALLY GOD DAMNNNN!!
        fig = go.Figure(data=[edge_trace, node_trace],
            layout=go.Layout(
            title="Playlist: "+playlist_name,
            titlefont_size=16,
            #hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
            )

        fig.update_layout(
            height=700)


        #fig.show()
     
        return fig

fig = network_graph()

app = dash.Dash(__name__)

app.title = "Micro-Genre Network"

app.layout = html.Div(
    children=[
        html.H1(children="Micro-Genre Network"),
        html.Div(
            className="Graph",
            children=[dcc.Graph(id="my_graph",figure=fig)],
            style={'backgroundColor':'#5F9EA00'}
        )
    ]
)

if __name__ == '__main__':
    app.run_server("debug"==True)