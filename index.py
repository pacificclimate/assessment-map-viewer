import panel as pn
import os

"""
Simple index file container to serve the app at root instead of /Map_and_Tables_App
"""

# Import the main app
from Map_and_Tables_App import app_entrypoint as north_app_entrypoint
from Metro_Van_App import app_entrypoint as van_app_entrypoint

appver = os.environ.get("APP_VER", "NORTH")

if appver == "NORTH":
    app = north_app_entrypoint
else:
    app = van_app_entrypoint

# Configure panel to serve at root
pn.serve(app, port=8080, address="0.0.0.0", allow_websocket_origin=["*"], 
         autoreload=True, show=True, title="Assessment Map Viewer")