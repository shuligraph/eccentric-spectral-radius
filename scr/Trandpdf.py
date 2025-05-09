import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import os
from networkx.drawing.nx_pydot import graphviz_layout

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

def visualize_trees(trees, num_vertices, sequence_number, save_path=None):
    # Visualize all trees with five in each line
    plt.figure(figsize=(14, 3 * ((len(trees) - 1) // 5 + 1)))

    for i, tree in enumerate(trees):
        plt.subplot((len(trees) - 1) // 5 + 1, 5, i + 1)

        pos = graphviz_layout(tree, prog="dot")
        
        nx.draw(tree, pos=pos, with_labels=False, node_size=10, node_color='black', edge_color='gray', linewidths=0.5)
        maxvalue = max(np.linalg.eigvals(nx.adjacency_matrix(tree).toarray()))
        plt.title(f"Tree {i + 1}\nRadius: {maxvalue.real: .5f}", fontsize=10)

    plt.tight_layout()

    if save_path is None:
        save_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), DEFAULT_SAVE_PATH)

    plt.savefig(save_path, format='pdf')
    print(f"Visualization saved to {save_path}")

def main():
    num_vertices = 11  # Change this to the desired number of vertices
    r = 3
    d = 5

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
