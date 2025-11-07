import panel as pn
import os

"""
Simple index file container to serve the app at root instead of /Map_and_Tables_App
"""

# Import the main app
from Map_and_Tables_App import layout as north_layout
from Metro_Van_App import layout as van_layout

appver = os.environ.get("APP_VER", "NORTH")

if appver == "NORTH":
    layout = north_layout
else:
    layout = van_layout

# Configure panel to serve at root
pn.serve(layout, port=8080, address="0.0.0.0", allow_websocket_origin=["*"], 
         autoreload=True, show=True, title="Assessment Map Viewer")