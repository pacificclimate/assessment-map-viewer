import panel as pn
import os

"""
Simple index file container to serve the app at root instead of /Map_and_Tables_App
"""

# Import the main app
from Map_and_Tables_App import app_entrypoint as map_and_tables
from Metro_Van_App import app_entrypoint as metro_van

appver = os.environ.get("APP_VER", "NORTH")

if appver == "MAP_TABLES":
    print("Starting MAP_AND_TABLES app...")
    app = map_and_tables
else:
    print("Starting METRO_VAN app...")
    app = metro_van

# Configure panel to serve at root
pn.serve(app, port=8080, address="0.0.0.0", allow_websocket_origin=["*"], 
         autoreload=True, show=True, title="Assessment Map Viewer")