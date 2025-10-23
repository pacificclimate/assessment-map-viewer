import panel as pn
import os
import io
import yaml

# --- Load configuration options ---
CONFIG_FILE = "config.yaml"

with open(CONFIG_FILE, "r") as f:
    config = yaml.safe_load(f)

BASE_PATH = config["base_path"]
CAT_ORDER = config.get("category_order", [])
REGION_OPTIONS = config.get("region_order", [])


#pn.extension()
pn.extension(raw_css=[
    """
    select, .bk-input {
        font-size: 14pt !important;
    }
    """
])

pn.extension(raw_css=[
    """
    /* Increase font size for all Panel buttons */
    .bk-btn, .bk-btn-primary {
        font-size: 16pt !important;
        padding: 3px 6px !important;
    }
    """
])

#BASE_PATH = "/home/ssobie/Desktop/Python/Map_App/Images/"
#BASE_PATH = "/home/ssobie/Desktop/Data/Climate_Assessments/Northeast_2025/"
MAPS_PATH = BASE_PATH + 'Maps_with_ERA5'
TABLES_PATH = BASE_PATH + 'Tables_with_ERA5'

# Widgets
scenario = pn.widgets.Select(
    name='Scenario', 
    options=['Select Scenario' , 'SSP245', 'SSP585'], 
    value='Select Scenario',
    styles={'font-size': '14pt'} 
)

category = pn.widgets.Select(name='Category', options=[],styles={'font-size': '14pt'})
variable = pn.widgets.Select(name='Variable', options=[],styles={'font-size': '14pt'})
map = pn.widgets.Select(name='Choose a Map', options=[],styles={'font-size': '14pt'})

REGION_OPTIONS.insert(0,'Select Region')
region = pn.widgets.Select(
    name='Region',
    options=REGION_OPTIONS,
    value=REGION_OPTIONS[0] if REGION_OPTIONS else None,
    styles={'font-size': '14pt'}
)

# Download Map button
download_map = pn.widgets.FileDownload(
    label="⬇️ Download Map",
    button_type="primary",
    filename="image.png",
    embed=False,
    disabled=True  # Start disabled
)

# Download Table button
download_table = pn.widgets.FileDownload(
    label="⬇️ Download Summary Table",
    button_type="success",
    filename="Table.xlsx",
    embed=False,
    disabled=True  # Start disabled
)

# Update categories when scenario changes
def update_categories(event):
    if scenario.value != 'Select Scenario':
        new_path = os.path.join(MAPS_PATH, 'Maps_'+scenario.value)
        if os.path.isdir(new_path):
            found_dirs = [d for d in os.listdir(new_path) if os.path.isdir(os.path.join(new_path, d))]
            dirs = [d for d in CAT_ORDER if d in found_dirs]
             # Replace underscores with spaces
            display_dirs = {d.replace("_", " "): d for d in dirs}
            category.options = display_dirs
            category.value = None #dirs[0] if dirs else None
        else:
            category.options = []
            category.value = None
    else:
        category.options = []
        category.value = None
        variable.options = []
        variable.value = None
        map.options = []
        map.value = None
        download_map.disabled = True

# Update variables when category changes
def update_variables(event):
    if scenario.value != 'Select Scenario' and category.value:
        new_path = os.path.join(MAPS_PATH, 'Maps_'+scenario.value, category.value)
        if os.path.isdir(new_path):
            dirs = sorted([d for d in os.listdir(new_path) if os.path.isdir(os.path.join(new_path, d))])
            variable.options = dirs
            variable.value = None #dirs[0] if dirs else None
        else:
            variable.options = []
            variable.value = None
    else:
        variable.options = []
        variable.value = None
        download_map.disabled = True      

# Update maps when variable changes
def update_maps(event):
    if scenario.value != 'Select Scenario' and variable.value:
        new_path = os.path.join(MAPS_PATH, 'Maps_'+scenario.value, category.value, variable.value)
        if os.path.isdir(new_path):
            files = sorted([f for f in os.listdir(new_path) if os.path.isfile(os.path.join(new_path, f))])
            map.options = files
            map.value = None #files[0] if files else None
        else:
            map.options = []
            map.value = None
    else:
        map.options = []
        map.value = None
        download_map.disabled = True

# Summary Table File Selection
def update_region_file(event):
    region_name = region.value
    scenario_name = scenario.value
    if not region_name:
        download_table.disabled = True
        return

    # Construct expected Excel file path
    region_file = os.path.join(TABLES_PATH, f"{region_name}_{scenario_name}_Projections_Summary_Table.xlsx")

    if os.path.isfile(region_file):
        # Enable the button and set callback
        download_table.disabled = False
        download_table.filename = f"{region_name}_{scenario_name}_Projections_Summary_Table.xlsx"

        def get_region_file():
            with open(region_file, "rb") as f:
                return io.BytesIO(f.read())
        download_table.callback = get_region_file
    else:
        download_table.disabled = True

scenario.param.watch(update_categories, 'value')
category.param.watch(update_variables, 'value')
variable.param.watch(update_maps, 'value')
region.param.watch(update_region_file, "value")


# Function updated to accept all bound widget values
def display_selection(scenario_val, category_val, variable_val, map_val):
    # Show only placeholder names if scenario not selected
    if scenario_val == 'Select Scenario' or not scenario_val:
        download_map.disabled = True
        return pn.pane.Markdown(f"""
**Selection Options:**

- Scenario: Select Scenario  
- Category: Select Category  
- Variable: Select Variable  
- Map: Choose a Map
- Table: Choose a Table
""")
    path_display = os.path.join(MAPS_PATH, 'Maps_'+scenario_val or '', category_val or '', variable_val or '', map_val or '')

    # If an image file is selected → display the image
    if map_val and os.path.isfile(path_display) and path_display.lower().endswith('.png'):
        # Enable download button
        download_map.disabled = False
        download_map.filename = map_val

        # Define file download callback
        def get_file():
            with open(path_display, "rb") as f:
                return io.BytesIO(f.read())
        download_map.callback = get_file
        return pn.pane.PNG(path_display, height=650)
    download_map.disabled = True
    return pn.pane.Markdown(f"""
**Selected Options:**

- Scenario: {scenario_val}  
- Category: {category_val}  
- Variable: {variable_val}  
- Map: {map_val}  
- Path: {path_display}
""")

# Bind widget values explicitly
display_pane = pn.bind(
    display_selection,
    scenario_val=scenario,
    category_val=category,
    variable_val=variable,
    map_val=map
)

sidebar = pn.Column(
    pn.pane.Markdown("## 🗺️ Maps", styles={"font-size": "16pt", "font-weight": "bold"}),  # 👈 Section title   
    scenario, 
    category, 
    variable, 
    map, 
    pn.layout.Spacer(height=10),
    pn.pane.HTML("<style>.bk-btn {font-size: 18pt !important;}</style>"),
    download_map,
    pn.layout.Spacer(height=30),
    pn.layout.Divider(),
    pn.layout.Spacer(height=20),
    pn.pane.Markdown("## 📊 Tables", styles={"font-size": "16pt", "font-weight": "bold"}),  # 👈 Second section title
    region,
    download_table,
    width=400,
)

# Layout
layout = pn.Row(
    sidebar,
    display_pane
)

layout.servable()
