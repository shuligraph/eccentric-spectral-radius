import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from matplotlib.backends.backend_pdf import PdfPages

def build_family_tree(connection_config):
    """
    Builds a family tree based on a specific configuration connecting V_i to u_i or v_i.
    `connection_config` is a list of 6 elements, each being 'u' or 'v'.
    """
    G = nx.Graph()
    
    # Build the main path P: "u" center, u_1 to u_7 on the left, v_1 to v_7 on the right
    path_nodes = ["u"] + [f"u_{i}" for i in range(1, 8)] + [f"v_{i}" for i in range(1, 8)]
    edges = [("u", "u_1")] + [(f"u_{i}", f"u_{i+1}") for i in range(1, 7)]
    edges += [("u", "v_1")] + [(f"v_{i}", f"v_{i+1}") for i in range(1, 7)]
    G.add_edges_from(edges)
    
    # Correct vertex counts for V_i sets
    V_orders = [3, 4, 2, 3, 3, 4]
    
    # Fix 1: Connect V_i vertices to correct u_i or v_i based on configuration
    for i, (order, config) in enumerate(zip(V_orders, connection_config)):
        V_set = [f"V{i+1}_{j}" for j in range(1, order + 1)]
        G.add_nodes_from(V_set)
        connect_to = f"{config}_{i+1}"  # This connects to u_i or v_i based on config
        for node in V_set:
            G.add_edge(node, connect_to)

    return G

def spectral_radius(G):
    adjacency_matrix = nx.adjacency_matrix(G).todense()
    eigenvalues = np.linalg.eigvals(adjacency_matrix)
    return max(abs(eigenvalues))

def is_isomorphic(G, H):
    return nx.is_isomorphic(G, H)

def plot_graph(G, title, ax):
    """
    Plot graph on a given axis instead of creating a new figure.
    """
    # Define a layout to place P's nodes in a horizontal line
    pos = {}
    # Horizontal line for path P
    pos["u"] = (0, 0)
    for i in range(1, 8):
        pos[f"u_{i}"] = (-i, 0)  # Left side of u
        pos[f"v_{i}"] = (i, 0)   # Right side of u
    
    # Improve V_i set layout
    for node in G.nodes:
        if node.startswith("V"):
            connected_node = list(G[node])[0]
            base_x, _ = pos[connected_node]
            # Get V set number and position within set
            v_num = int(node.split("_")[0][1])  # Extract number from V1, V2, etc.
            v_idx = int(node.split("_")[1])
            
            # Arrange V_i sets in a more organized way below their connected nodes
            pos[node] = (base_x + (v_idx - 1) * 0.3, -1 - 0.5 * v_num)

    # Draw the graph
    nx.draw(G, pos, ax=ax, with_labels=False, node_size=25, 
            node_color="skyblue", edge_color="gray",
            labels={node: node for node in G.nodes()},
            font_size=0)
    ax.set_title(title)

# Generate all configurations and compute spectral radius
configs = list(product(['u', 'v'], repeat=6))
unique_graphs = []
spectral_radii = []

for config in configs:
    G = build_family_tree(config)
    radius = spectral_radius(G)
    
    # Check for isomorphism with already stored graphs
    if not any(is_isomorphic(G, existing_graph) for existing_graph in unique_graphs):
        unique_graphs.append(G)
        spectral_radii.append(radius)

# Sort graphs by spectral radius in descending order
sorted_graphs = sorted(zip(unique_graphs, spectral_radii), key=lambda x: x[1], reverse=True)

# Fix 2: Plot multiple graphs per page
with PdfPages("family_trees_by_spectral_radius.pdf") as pdf:
    num_graphs = len(sorted_graphs)
    graphs_per_page = 6  # 2x3 grid
    num_pages = (num_graphs + graphs_per_page - 1) // graphs_per_page
    
    for page in range(num_pages):
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.ravel()
        
        # Plot up to 6 graphs per page
        start_idx = page * graphs_per_page
        end_idx = min(start_idx + graphs_per_page, num_graphs)
        
        for i, (G, radius) in enumerate(sorted_graphs[start_idx:end_idx]):
            plot_graph(G, f"Tree {start_idx + i + 1}\nSpectral Radius: {radius:.4f}", axes[i])
            print(f"Tree {start_idx + i + 1}: Spectral Radius = {radius:.4f}")
        
        # Clear any unused subplots
        for j in range(i + 1, graphs_per_page):
            axes[j].axis('off')
        
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()

print("All family trees have been saved to 'family_trees_by_spectral_radius.pdf'.")