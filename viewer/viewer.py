import json
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State, ALL

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

with open('categories.json') as f:
    all_options = json.load(f)

final_attributes = {k["key"]: None for k in all_options if k['parent'] is None}
final_attributes['Hub'] = "Dataloop"


# Function to create the initial mandatory attributes with dropdowns
def generate_attributes_selection():
    global final_attributes
    uls = list()
    for i, (attr, val) in enumerate(final_attributes.items()):
        attr_options = [a for a in all_options if a['key'] == attr][0]
        attr_options_names = [b['name'] for b in attr_options['values']]
        ul = html.Li(id={'type': 'mandatory-attribute', 'index': i},
                     children=[attr,
                               dcc.Dropdown(
                                   id={'type': 'mandatory-dropdown', 'index': i, 'attribute': attr},
                                   options=attr_options_names,
                                   placeholder=f'Select {attr}',
                                   value=val,
                                   style={'margin-left': '10px', 'width': '300px'},
                               )
                               ])
        uls.append(ul)

    return html.Div([
        html.H5("Mandatory Attributes"),

        html.Ul(uls)
    ])


app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(
                id='dynamic-dropdown-container',
                children=generate_attributes_selection(),
                width=12)
        ]),
        dbc.Row([
            dbc.Col(dbc.Button("Export Selection", id="export-button", color="primary", className="mr-2"), width=12)
        ]),
        dbc.Row([
            dbc.Col(dcc.Textarea(id="exported-data", style={'width': '100%', 'height': '200px'}), width=12)
        ])
    ])
])


# Callback to dynamically add dropdowns
@app.callback(
    Output('dynamic-dropdown-container', 'children'),
    Input({'type': 'mandatory-dropdown', 'index': ALL, 'attribute': ALL}, 'value'),
    State('dynamic-dropdown-container', 'children')
)
def update_dropdown(mandatory_selected_values, current_children):
    global final_attributes
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_children

    triggered_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    attribute = triggered_id['attribute']
    selected_value = ctx.triggered[0]['value']
    index = triggered_id['index'] + 1

    if not selected_value:
        return final_attributes
    new_final_attributes = {k["key"]: final_attributes[k["key"]] for k in all_options if k['parent'] is None}
    new_final_attributes[attribute] = selected_value
    keys = list(new_final_attributes.keys())
    for k in keys:
        v = new_final_attributes[k]
        children = [k for k in all_options if k['parent'] == v]
        for c in children:
            if c["key"] not in new_final_attributes:
                new_final_attributes[c['key']] = final_attributes.get(c["key"])
    final_attributes = new_final_attributes
    return generate_attributes_selection()


# Callback to export selected attributes
@app.callback(
    Output('exported-data', 'value'),
    Input('export-button', 'n_clicks'),
    State({'type': 'mandatory-dropdown', 'index': ALL, 'attribute': ALL}, 'value'),
)
def export_selection(n_clicks, mandatory_selected_values):
    if not n_clicks:
        return ""

    return json.dumps(final_attributes, indent=2)


if __name__ == "__main__":
    app.run_server(host="localhost", port=6005)
    # ngrok http 6005
