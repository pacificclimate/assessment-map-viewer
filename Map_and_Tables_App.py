import panel as pn
import os
import io
import yaml

pn.extension()

# --- Load configuration options once at module level ---
_config_cache = None

def _load_config():
    global _config_cache
    if _config_cache is None:
        CONFIG_FILE = os.getenv("APP_CONFIG", "config.yaml")
        
        if not os.path.isfile(CONFIG_FILE):
            raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")
        
        with open(CONFIG_FILE, "r") as f:
            _config_cache = yaml.safe_load(f)
    
    return _config_cache

def make_app():

    # Get cached configuration
    config = _load_config()
    
    BASE_PATH = config["base_path"]
    CAT_ORDER = config.get("category_order", [])
    REGION_OPTIONS = config.get("region_order", [])
    LOGO_PATH = config.get("logo_path", None)
    APP_TITLE = config.get("app_title", "Data Explorer")

    pn.extension(raw_css=[
        """
        select, .bk-input {
            font-size: 12pt !important;
        }
        """
    ])

    pn.extension(raw_css=[
        """
        /* Increase font size for all Panel buttons */
        .bk-btn, .bk-btn-primary {
            font-size: 14pt !important;
            padding: 3px 6px !important;
        }
        """
    ])

    MAPS_PATH = BASE_PATH + 'Maps'
    TABLES_PATH = BASE_PATH + 'Tables'

    # Map Scenario Menu
    scenario = pn.widgets.Select(
        name='Map Scenario', 
        options=['Select Map Scenario' , 'SSP245', 'SSP585'], 
        value='Select Map Scenario',
        styles={'font-size': '14pt'} 
    )
    # Map Scenario Menu
    tablescen = pn.widgets.Select(
        name='Table Scenario', 
        options=['Select Table Scenario' , 'SSP245', 'SSP585'], 
        value='Select Table Scenario',
        styles={'font-size': '14pt'} 
    )

    category = pn.widgets.Select(name='Category', options=[],styles={'font-size': '14pt'})
    variable = pn.widgets.Select(name='Variable', options=[],styles={'font-size': '14pt'})
    map = pn.widgets.Select(name='Choose a Map', options=[],styles={'font-size': '14pt'})

    REGION_OPTIONS.insert(0,'Select Region')
    DISPLAY_REGIONS = {d.replace("_", " "): d for d in REGION_OPTIONS}
    region = pn.widgets.Select(
        name='Region',
        options=DISPLAY_REGIONS,
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
        if scenario.value != 'Select Map Scenario':
            new_path = os.path.join(MAPS_PATH, scenario.value) #'Maps_'+
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
        if scenario.value != 'Select Map Scenario' and category.value:
            new_path = os.path.join(MAPS_PATH, scenario.value, category.value) #'Maps_'+
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
        if scenario.value != 'Select Map Scenario' and variable.value:
            new_path = os.path.join(MAPS_PATH, scenario.value, category.value, variable.value) #'Maps_'+
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
        scenario_name = tablescen.value
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
    tablescen.param.watch(update_region_file, 'value')
    region.param.watch(update_region_file, "value")

    # Function updated to accept all bound widget values
    def display_selection(scenario_val, category_val, variable_val, map_val):
        # Show only placeholder names if scenario not selected
        if scenario_val == 'Select Map Scenario' or not scenario_val:
            download_map.disabled = True
            return pn.pane.Markdown(f"""
    **Selection Options:**

    - Scenario: Select Map Scenario  
    - Category: Select Category  
    - Variable: Select Variable  
    - Map: Choose a Map
    - Table: Choose a Table
    """,
        styles={
            "font-size": "14pt",
            "line-height": "1.2",
        })
        path_display = os.path.join(MAPS_PATH, scenario_val or '', category_val or '', variable_val or '', map_val or '') # 'Maps_'+

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

    # PCIC Logo
    if LOGO_PATH and os.path.isfile(LOGO_PATH):
        logo_pane = pn.pane.PNG(
            LOGO_PATH,
            width=300,           # adjust as needed
            align="start",
            styles={"margin-top": "10px"}
        )
    else:
        logo_pane = pn.pane.Markdown("")  # empty placeholder if logo missing

    # App Title
    title_pane = pn.pane.HTML(
        f"""
        <div style='
            font-size: 20pt;
            font-weight: bold;
            text-align: center;
            color: #004361;
            background-color: #FFFFFF;
            padding: 10px;
            border-radius: 0px;
            margin-bottom: 0px;
        '>{APP_TITLE}</div>
        """
    )

    # Bind widget values explicitly
    display_pane = pn.bind(
        display_selection,
        scenario_val=scenario,
        category_val=category,
        variable_val=variable,
        map_val=map
    )

    sidebar = pn.Column(
        pn.pane.Markdown("## 🗺️ Maps", styles={"font-size": "12pt", 
                                                "font-weight": "bold",
                                                "margin-top": "0px",
                                                "margin-bottom": "0px"}),  # 👈 Section title   
        scenario, 
        category, 
        variable, 
        map, 
        pn.pane.HTML("<style>.bk-btn {font-size: 16pt !important;}</style>"),
        download_map,
        pn.layout.Spacer(height=10),
        pn.layout.Divider(),
        pn.pane.Markdown("## 📊 Tables", styles={"font-size": "12pt", "font-weight": "bold"}),  # 👈 Second section title
        tablescen,
        region,
        pn.layout.Spacer(height=10),
        download_table,
        pn.layout.Spacer(height=10),
        pn.layout.Divider(),
        pn.layout.Spacer(height=10),
        logo_pane,
        width=400,
    )

    # Layout
    layout = pn.Column(
        title_pane,
        pn.Row(
            sidebar,
            display_pane
        ),
    )
    return layout

# layout.servable()

# Do not call make_app() at module import time!
def app_entrypoint():
    content = make_app()
    template = pn.template.FastListTemplate(
        title="Assessment Viewer",
        main=[content],
    )
    return template
