from collections import Counter 

import dash
from dash import Dash, dcc, html, Input, Output, State
import networkx as nx

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
import plotly.express as px

def graph(playlist,node_amount):
    """
    graph creates a network of genres present in a user's playlist
    :param playlist: the name of the playlist to graph
    :param node_amount: the amount of nodes you'd like in the graoh
    :return: return the plotly graph
    """

    # Create spotify object with security token
    username = 1221250460
    token = util.prompt_for_user_token(username)
    spotifyObject = spotipy.Spotify(auth=token)

    playlist_name = str(playlist)

    results = spotifyObject.current_user_playlists(limit=50)
    playlists = results['items']
    
    for i, item in enumerate(playlists):
        if playlist == item['name']:
            playlist_description = playlists[i]

    # Get items from playlist
    playlistEntries = spotifyObject.playlist_tracks(playlist_description['id'],offset=0)
    items = playlistEntries['items']
        
    # Collect all the genres from the playlist in a list
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

    # Dictionary (Keys: Genre, Values: Genre Count)
    genre_count = dict(Counter(allGenres))

    # Sort the dictionary by descending values
    genre_count = dict(sorted(genre_count.items(), key = lambda x: x[1], reverse = True))

    # Display the genres and their count
    #for key in genre_count:
        #print(key,'-',genre_count[key])
   
    """
    Construct network with NetworkX
    """

    # Create graph
    g=nx.Graph()

    # Add nodes as genres
    genresX = list(genre_count.keys())
    g.add_nodes_from(genresX)
    
    # Create and add edges
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
    amount_listX = list(genre_count.values())
    XX_amounts = []
    XX_genres = []

    for i, genre in enumerate(genresX):
        if i > node_amount:
            g.remove_node(genre)
        else:
            XX_amounts.append(amount_listX[i])
            XX_genres.append(genre)

    # Make size of nodes bigger
    XX_amounts = [(i**(log(7000)/log(XX_amounts[0])/1.8)) for i in XX_amounts]

    # Create layout for the network
    pos=nx.spring_layout(g)

    # Draw network
    ax = plt.gca()
    ax.set_title("Micro-Genre Graph\n"+playlist_name)
    nx.draw(g, with_labels=True, node_color="#02D81F", edge_color="#02D81F", node_size=XX_amounts, style=":", font_size=12, font_family="arial black", ax=ax)

    """
    Visualize the graph with Plotly
    """

    # Pie chart

    fig2 = px.pie(XX_genres, values = XX_amounts, names = XX_genres)

    # Network

    for node in g.nodes():
        g.node[node]['pos']= pos[node]

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
        mode='lines',
        line=dict(width=0.5, color='#bababa'),
        hoverinfo='none',
        textfont=dict(size=20)
        )

    node_x = []
    node_y = []

    for node in g.nodes():
        x, y = g.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            colorscale='Greens',
            reversescale=False,
            color='Green',
            size=XX_amounts,
            line_width=2),
        text = genresX
        )

    # Show Plotly figure
    fig = go.Figure(data=[edge_trace, node_trace],
        layout=go.Layout(
        #title="Playlist: "+playlist_name,
        titlefont_size=16,
        margin=dict(b=20,l=5,r=5,t=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        )

    fig.update_layout(
        height=700)

    return fig

def get_playlists_options():
    """
    get_playlists_options gets all the playlist options from your spotify account, formatted to work with 
    :return: return a list of dictionaries that describe the playlist options
    """

    # Create spotify object with security token
    username = 1221250460
    token = util.prompt_for_user_token(username)
    spotifyObject = spotipy.Spotify(auth=token)

    # Get the user's playlists
    results = spotifyObject.current_user_playlists(limit=50)
    playlists = results['items']

    # Display current user playlists on the console
    playlist_names=[]
    for i, item in enumerate(playlists):
        #print("%d %s" % (i, item['name']))
        playlist_names.append(item['name'])

    # Construct a list of dictionaries that are compatible with the Dropdown
    options=[]
    for i in playlist_names:
        d = {}
        d['label']=i
        d['value']=i
        options.append(d)
    
    return options

# Retrieve the options for the dropdown
options = get_playlists_options()
value = options[0]
first_value = list(value.items())[0][1]

# Generate the first playlist graph
fig=graph(first_value,20)

app = dash.Dash(__name__)
app.title = "Micro-Genre Network"
app.layout = html.Div(
    #style={'backgroundColor':'#87D653'},
    children=[  
        dcc.Dropdown(
            id='dropdown',
            options=options,
            value=first_value
        ),
        html.Div(
            id='dd-output-container'
        ),
        html.H1(
            children="Micro-Genre Network"
        ),
        html.P(
            children="Allow for some time for the graph to process. The larger the playlist, the longer the time."
        ),
        dcc.Graph(
            id='my_graph',
            figure=fig
        )
    ]
)

@app.callback(
    Output('my_graph', 'figure'),
    Input('dropdown', 'value'),
)
def update_output(first_value):
    amount = 20
    fig = graph(first_value,amount)
    return fig

if __name__ == '__main__':
    app.run_server()