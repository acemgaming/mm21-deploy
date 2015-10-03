class Node(object):

    def __init__(self, graph, node_type):
        self.node_type = node_type  #
        self.connected_nodes = []  # list of edges
        self.uid = graph.add_vertex(self)

    def add_edge(self, edge):
        if edge not in self.connected_nodes:
            self.connected_nodes.append(edge)

    def __str__(self):
        s = str(self.uid) + "-" + self.node_type
        # s += str(self.connected_nodes) + "\n"
        return s

    def __repr__(self):
        s = str(self.uid) + "-" + self.node_type
        # s += str(self.connected_nodes) + "\n"
        return s

    @staticmethod
    def get_ISP_node(graph):
        return Node(graph, "ISP")

    @staticmethod
    def get_DC_node(graph):
        return Node(graph, "Data Center")

    @staticmethod
    def get_small_city_node(graph):
        return Node(graph, "Small City")

    @staticmethod
    def get_medium_city_node(graph):
        return Node(graph, "Medium City")

    @staticmethod
    def get_large_city_node(graph):
        return Node(graph, "Large City")
