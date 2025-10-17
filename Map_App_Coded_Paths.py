import panel as pn
import io
from pathlib import Path

# Activate Panel extensions
pn.extension()

# Dictionary mapping dropdown options to image file paths
image_sets = {
    "PR": {
        "PR": "/home/ssobie/Desktop/Python/Map_App/Images/PR_Annual_SSP245_cvrd_1981-2010.png",
        "RN": "/home/ssobie/Desktop/Python/Map_App/Images/RN_Annual_SSP245_cvrd_1981-2010.png",
        "SN": "/home/ssobie/Desktop/Python/Map_App/Images/SN_Annual_SSP245_cvrd_1981-2010.png"
    },
    "TAS": {
        "TX": "/home/ssobie/Desktop/Python/Map_App/Images/TX_Annual_SSP245_cvrd_1981-2010.png",
        "TM": "/home/ssobie/Desktop/Python/Map_App/Images/TM_Annual_SSP245_cvrd_1981-2010.png",
        "TN": "/home/ssobie/Desktop/Python/Map_App/Images/TN_Annual_SSP245_cvrd_1981-2010.png"
    },
}

# Default (initial) image
default_image = "/home/ssobie/Desktop/Python/Map_App/Images/CVRD_elevation_map.png"
category_defaults = {
    "PR": "/home/ssobie/Desktop/Python/Map_App/Images/PR_Annual_SSP245_cvrd_1981-2010.png",
    "TAS": "/home/ssobie/Desktop/Python/Map_App/Images/TX_Annual_SSP245_cvrd_1981-2010.png",
}

# Create dropdown menus
category_dropdown = pn.widgets.Select(
    name="Category",
    options=["PR", "TAS"],
    value="PR",
)

image_dropdown = pn.widgets.Select(
    name="Choose an image",
    options=list(image_sets["PR"].keys()),  # default set
    value=None,
)

# Placeholder for image display
default_image = category_defaults[category_dropdown.value]
image_pane = pn.pane.Image(default_image, sizing_mode="scale_both") # 

# Download Button
download_button = pn.widgets.FileDownload(
    label="⬇️ Download Image",
    filename="default_pr.jpg",
    button_type="primary",
    embed=False,
    width=180,
)

def get_image_bytes(path):
    """Return image bytes from file path."""
    with open(Path(path), "rb") as f:
        return io.BytesIO(f.read())

# Callback to update the image
def update_image_options(event):
    """Update image dropdown options when category changes."""
    category = event.new
    image_dropdown.options = list(image_sets[category].keys())
    default_path = category_defaults.get(category, default_image)
    image_pane.object = default_path
    image_dropdown.value = None  # reset image selection
    download_button.filename = Path(default_path).name
    download_button.callback = lambda: get_image_bytes(default_path)

def update_image_display(event):
    """Update displayed image when image dropdown changes."""
    category = category_dropdown.value
    selected_image = event.new
    if selected_image and selected_image in image_sets[category]:
        path = image_sets[category][selected_image]
        image_pane.object = path
        download_button.filename = Path(path).name
        download_button.callback = lambda: get_image_bytes(path)
    else:
        default_path = category_defaults.get(category, default_image)
        image_pane.object = default_path
        download_button.filename = Path(default_path).name
        download_button.callback = lambda: get_image_bytes(default_path)

# Link dropdown changes to callback
category_dropdown.param.watch(update_image_options, 'value')
image_dropdown.param.watch(update_image_display, 'value')

# Initialize download button for the first time
download_button.callback = lambda: get_image_bytes(default_image)

# Create layout
controls = pn.Column(
    "### 🔽 Select Options",
    category_dropdown,
    image_dropdown,
    pn.layout.Spacer(height=10),
    download_button,
    sizing_mode="fixed",
    width=200,
)

layout = pn.Column(
    "# 🖼️ Regional Assessment Map Viewer",
    "Choose a **Category** and then an **Image** to display. Click *Download* to save the map.",
    pn.Row(controls, pn.Spacer(width=20), image_pane),
    sizing_mode="stretch_width",
)

# Show in browser or serve
layout.servable()
