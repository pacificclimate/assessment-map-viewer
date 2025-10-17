import panel as pn
import io
from pathlib import Path

# Activate Panel extensions
pn.extension()

# Dictionary mapping dropdown options to image file paths
BASE_IMAGE_FOLDER = Path("/home/ssobie/Desktop/Python/Map_App/Images/")
CATEGORY_OPTIONS = ["SSP245", "SSP585"]

def get_category_folder(category):
    """Return Path to folder for a category."""
    folder = BASE_IMAGE_FOLDER / category
    return folder if folder.exists() else None

def find_images(category):
    """Return list of image names matching category."""
    images = []
    image_folder = get_category_folder(category)
    images = image_folder.glob("*.png")
    return list(images)

def get_image_path(category, image_name):
    """Return full Path to image."""
    folder = get_category_folder(category)
    if folder:
        file = folder / f"{image_name}"
        return file if file.exists() else get_default_image(category)
    return None

# Default (initial) image
default_image = "/home/ssobie/Desktop/Python/Map_App/Images/CVRD_elevation_map.png"
category_defaults = {
    "SSP245": "/home/ssobie/Desktop/Python/Map_App/Images/SSP245/PR_Annual_SSP245_cvrd_1981-2010.png",
    "SSP585": "/home/ssobie/Desktop/Python/Map_App/Images/SSP585/PR_Annual_SSP585_cvrd_1981-2010.png",
}

def get_default_image(category):
    """Return default image Path for category."""
    folder = get_category_folder(category)
    file = folder / "Default.jpg"
    return file if file.exists() else None



category_dropdown = pn.widgets.Select(name="Scenario", options=CATEGORY_OPTIONS, value="SSP245")
image_dropdown = pn.widgets.Select(name="Choose an image", options=find_images("SSP245"), value=None)

default_image = get_default_image(category_dropdown.value)

# Placeholder for image display
image_pane = pn.pane.Image(default_image, sizing_mode="scale_both") # 

download_button = pn.widgets.FileDownload(
    label="⬇️ Download Image",
    filename=default_image.name if default_image else "image.jpg",
    button_type="primary",
    embed=False,
    width=180,
)
def get_image_bytes(path):
    with open(path, "rb") as f:
        return io.BytesIO(f.read())

def update_download_button(path):
    if path:
        download_button.filename = path.name
        download_button.callback = lambda: get_image_bytes(path)

update_download_button(default_image)

# Callback to update the image
def update_image_options(event):
    """Update image dropdown and preview when category changes."""
    category = event.new
    images = find_images(category)
    image_dropdown.options = images
    image_dropdown.value = None
    default_path = get_default_image(category)
    image_pane.object = default_path
    update_download_button(default_path)

def update_image_display(event):
    """Display image matching selected category and image name."""
    category = category_dropdown.value
    image_name = event.new
    path = get_image_path(category, image_name) if image_name else get_default_image(category)
    image_pane.object = path
    update_download_button(path)


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
    "Choose a **Scenario** and then an **Image** to display. Click *Download* to save the map.",
    pn.Row(controls, pn.Spacer(width=20), image_pane),
    sizing_mode="stretch_width",
)

# Show in browser or serve
layout.servable()
