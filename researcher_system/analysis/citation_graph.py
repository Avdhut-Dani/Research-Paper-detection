import networkx as nx

def build_graph(citations):
    G=nx.DiGraph()
    for i,c in enumerate(citations):
        G.add_edge("paper",c+str(i))
    return G
