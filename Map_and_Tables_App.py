import panel as pn
import os
import io

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
BASE_PATH = "/home/ssobie/Desktop/Data/Climate_Assessments/Northeast_2025/"
MAPS_PATH = BASE_PATH + 'Maps_with_ERA5'
TABLES_PATH = BASE_PATH + 'Tables'

# Widgets
scenario = pn.widgets.Select(
    name='Scenario', 
    options=['Select Scenario', 'Maps_SSP245', 'Maps_SSP585'], 
    value='Select Scenario',
    styles={'font-size': '14pt'} 
)

category = pn.widgets.Select(name='Category', options=[],styles={'font-size': '14pt'})
variable = pn.widgets.Select(name='Variable', options=[],styles={'font-size': '14pt'})
map = pn.widgets.Select(name='Choose a Map', options=[],styles={'font-size': '14pt'})

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
    button_type="primary",
    filename="Table.xlsx",
    embed=False,
    disabled=True  # Start disabled
)

CAT_ORDER = ["Precipitation_Indices", "Temperature_Indices", "Drought_Indices",
             "Return_Levels","Return_Period_Changes"]

# Update categories when scenario changes
def update_categories(event):
    if scenario.value != 'Select Scenario':
        new_path = os.path.join(MAPS_PATH, scenario.value)
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
        new_path = os.path.join(MAPS_PATH, scenario.value, category.value)
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
        new_path = os.path.join(MAPS_PATH, scenario.value, category.value, variable.value)
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

scenario.param.watch(update_categories, 'value')
category.param.watch(update_variables, 'value')
variable.param.watch(update_maps, 'value')


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
    path_display = os.path.join(MAPS_PATH, scenario_val or '', category_val or '', variable_val or '', map_val or '')

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

# Layout
layout = pn.Row(
    pn.Column(scenario, 
              category, 
              variable, 
              map, 
              pn.layout.Spacer(height=10),
              pn.pane.HTML("<style>.bk-btn {font-size: 18pt !important;}</style>"),
              download_map,
              pn.layout.Spacer(height=30),
              pn.layout.Divider(),
              pn.layout.Spacer(height=30),
              download_table,
              width=450),
    display_pane
)

layout.servable()
