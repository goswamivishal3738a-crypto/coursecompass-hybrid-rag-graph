import networkx as nx
import matplotlib.pyplot as plt

def render_knowledge_graph(user_query=""):
    """Generates a dynamic knowledge graph based on the specific course queried."""
    
    # 1. Initialize the master directed graph
    master_graph = nx.DiGraph()
    
    # Add nodes based on actual syllabus PDFs
    master_graph.add_node("Software\nEngineering")
    master_graph.add_node("Math for AI")
    master_graph.add_node("Intro to AI")
    master_graph.add_node("Machine\nLearning")
    master_graph.add_node("Deep\nLearning")
    
    # Add edges (logical prerequisite relationships)
    master_graph.add_edge("Software\nEngineering", "Intro to AI", label="Recommended")
    master_graph.add_edge("Math for AI", "Machine\nLearning", label="Prerequisite")
    master_graph.add_edge("Intro to AI", "Machine\nLearning", label="Prerequisite")
    master_graph.add_edge("Machine\nLearning", "Deep\nLearning", label="Prerequisite")
    
    # 2. Determine target course from user query
    query_lower = user_query.lower()
    target_node = None
    
    if "deep learning" in query_lower:
        target_node = "Deep\nLearning"
    elif "machine learning" in query_lower or "ml " in query_lower:
        target_node = "Machine\nLearning"
    elif "intro" in query_lower or "intro to ai" in query_lower:
        target_node = "Intro to AI"
    elif "math" in query_lower or "calculus" in query_lower:
        target_node = "Math for AI"
    elif "software" in query_lower or "engineering" in query_lower:
        target_node = "Software\nEngineering"
        
    # 3. Extract the relevant Subgraph
    if target_node and target_node in master_graph.nodes():
        # Find all prerequisites (ancestors) leading to the target course
        relevant_nodes = nx.ancestors(master_graph, target_node)
        relevant_nodes.add(target_node) # Include the target course itself
        display_graph = master_graph.subgraph(relevant_nodes)
    else:
        # Fallback: Show the full graph if no specific course is mentioned
        display_graph = master_graph

    # 4. Set up the plot rendering environment
    fig, ax = plt.subplots(figsize=(9, 6))
    pos = nx.spring_layout(display_graph, seed=42, k=1.5)
    
    # Draw graph components
    nx.draw_networkx_nodes(display_graph, pos, node_color='#D6EAF8', node_size=3500, edgecolors='black', ax=ax)
    nx.draw_networkx_labels(display_graph, pos, font_size=9, font_weight="bold", ax=ax)
    nx.draw_networkx_edges(display_graph, pos, edge_color='gray', arrows=True, arrowsize=20, ax=ax)
    
    # Add text labels to the edges
    edge_labels = nx.get_edge_attributes(display_graph, 'label')
    nx.draw_networkx_edge_labels(display_graph, pos, edge_labels=edge_labels, font_color='red', font_size=8, ax=ax)
    
    # Hide the axis lines
    ax.set_axis_off()
    
    return fig