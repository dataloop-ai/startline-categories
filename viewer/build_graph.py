import json
from pyvis.network import Network

with open('attributes.json') as f:
    attributes = json.load(f)
    attributes = {attribute['key']: [v['name'] for v in attribute['values']] for attribute in attributes}

with open('dependencies.json') as f:
    dependencies = json.load(f)

# Create a network
net = Network(height="800px", width="100%", directed=True, notebook=False)
# Add root and mandatory attributes
key = "DPK"
net.add_node(f"{key}", label=f"{key}", title=f"{key}")
for value in ["Category", "Provider", "Media Type", "Deployed By", "License"]:
    net.add_node(f"{value}", label=f"{value}", title=f"{value}")
    net.add_edge(f"{key}", f"{value}")

# Add nodes and edges based on dependencies
for key, values in attributes.items():
    net.add_node(f"{key}", label=f"{key}", title=f"{key}")
    for value in values:
        net.add_node(f"{key}.{value}", label=f"{value}", title=f"{value}")
        net.add_edge(f"{key}", f"{key}.{value}")

for dependency in dependencies:
    if_key = dependency['if']['key']
    if_value = dependency['if']['value']
    required_keys = dependency['then']['required_keys']
    for req_key in required_keys:
        net.add_edge(f"{if_key}.{if_value}", f"{req_key}")

# Enable physics for better visualization of large graphs
net.toggle_physics(True)

# Generate and save the network as an HTML file
net.save_graph("dependency_tree.html")
