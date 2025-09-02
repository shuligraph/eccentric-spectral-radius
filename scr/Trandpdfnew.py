import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import os
from networkx.drawing.nx_pydot import graphviz_layout
import math
from matplotlib import gridspec as mpl_gridspec

def generate_trees(num_vertices):
    # Generate all non-isomorphic trees with the given number of vertices
    all_trees = list(nx.nonisomorphic_trees(num_vertices))
    return all_trees

def calculate_eccentricities(tree):
    # Calculate eccentricities for each node in the tree
    eccentricities = tuple(sorted(nx.eccentricity(tree).values()))
    return eccentricities

def sort_trees_by_largest_eigenvalue(trees):
    # Sort trees based on the largest eigenvalue
    sorted_trees = sorted(trees, key=lambda tree: max(np.linalg.eigvals(nx.adjacency_matrix(tree).toarray())), reverse=True)
    return sorted_trees

DEFAULT_SAVE_PATH = "tree_visualization.pdf"

# Graphviz 'dot' layout tuning
PER_ROW = 7  # trees per row
GRAPHVIZ_DOT_ATTRS = {
    'nodesep': '0.04',   # horizontal spacing in inches (default ~0.25)
    'ranksep': '0.06',   # vertical spacing in inches (default ~0.5)
    'ratio': 'compress', # try to compress ranks
    'margin': '0.02',    # reduce outer margin
}
VIEW_ZOOM_OUT = 1.5  # >1 expands axes limits so graph looks smaller
WSPACE = 0.02  # horizontal space between subplots
HSPACE = 0.02  # vertical space between subplots

def visualize_trees(trees, num_vertices, sequence_number, save_path=None):
    # Visualize all trees with configurable items per row (dot engine)
    rows = math.ceil(len(trees) / PER_ROW) if trees else 1
    fig = plt.figure(figsize=(14, 2.1 * rows), constrained_layout=False)
    gs = fig.add_gridspec(rows, PER_ROW, wspace=WSPACE, hspace=HSPACE)

    for i, tree in enumerate(trees):
        r, c = divmod(i, PER_ROW)
        ax = fig.add_subplot(gs[r, c])

        # Tight Graphviz spacing while keeping 'dot' layout
        g = tree.copy()
        g.graph['graph'] = {**g.graph.get('graph', {}), **GRAPHVIZ_DOT_ATTRS}
        pos = graphviz_layout(g, prog="dot")

        # Compute expanded axes limits to make the drawing appear smaller
        xs = np.fromiter((p[0] for p in pos.values()), dtype=float)
        ys = np.fromiter((p[1] for p in pos.values()), dtype=float)
        cx, cy = xs.mean(), ys.mean()
        w = xs.max() - xs.min()
        h = ys.max() - ys.min()
        # Guard small sizes
        w = w if w > 0 else 1.0
        h = h if h > 0 else 1.0
        half_w = 0.5 * w * VIEW_ZOOM_OUT
        half_h = 0.5 * h * VIEW_ZOOM_OUT
        xlim = (cx - half_w, cx + half_w)
        ylim = (cy - half_h, cy + half_h)

        nx.draw(
            tree,
            pos=pos,
            with_labels=False,
            node_size=9,
            node_color='black',
            edge_color='gray',
            linewidths=0.5,
            ax=ax,
        )
        # Apply the expanded limits so the graph occupies less area
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        # Keep equal aspect to avoid distortion
        ax.set_aspect('equal', adjustable='box')
        maxvalue = np.linalg.eigvalsh(nx.to_numpy_array(tree)).max()
        ax.set_title(f"Tree {i + 1}\nRadius: {maxvalue.real: .5f}", fontsize=10, pad=2)

    # Enforce subplot spacing explicitly (do not use tight_layout here)
    fig.subplots_adjust(wspace=WSPACE, hspace=HSPACE)

    if save_path is None:
        save_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), DEFAULT_SAVE_PATH)

    plt.savefig(save_path, format='pdf', dpi=300, bbox_inches='tight')
    print(f"Visualization saved to {save_path}")

def main():
    num_vertices = 14  # Change this to the desired number of vertices
    r = 4
    d = 7

    all_trees = generate_trees(num_vertices)

    # Filter trees based on eccentricities
    filtered_trees = [tree for tree in all_trees if r <= min(nx.eccentricity(tree).values()) and max(nx.eccentricity(tree).values()) <= d]

    # Create a dictionary to store trees based on eccentricities
    eccentricity_dict = {}

    for tree in filtered_trees:
        eccentricities = calculate_eccentricities(tree)
        if eccentricities not in eccentricity_dict:
            eccentricity_dict[eccentricities] = [tree]
        else:
            eccentricity_dict[eccentricities].append(tree)

    # Visualize all trees with the same eccentricities
    for sequence_number, eccentricities in enumerate(eccentricity_dict.keys(), start=1):
        print(f"Sequence Number: {sequence_number}")
        print(f"Eccentricities: {eccentricities}")

    sequence_number_input = int(input("Enter the sequence number to visualize trees: "))

    if sequence_number_input not in range(1, len(eccentricity_dict) + 1):
        print("Invalid sequence number.")
        return

    selected_trees = eccentricity_dict[list(eccentricity_dict.keys())[sequence_number_input - 1]]
    sorted_trees = sort_trees_by_largest_eigenvalue(selected_trees)

    print("\nVisualizing Trees:")
    visualize_trees(sorted_trees, num_vertices, sequence_number_input)

if __name__ == "__main__":
    main()
