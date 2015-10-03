class Graph(object):

    def __init__(self):
        self.vertex_list = []
        self.edge_list = []
        pass

    def add_vertex(self, vertex):
        if vertex not in self.vertex_list:
            self.vertex_list.append(vertex)
            return len(self.vertex_list) - 1
        else:
            return self.vertex_list.index(vertex)

    def add_edge(self, vertex1, vertex2):
        edge = set([vertex1.uid, vertex2.uid])
        if edge not in self.edge_list:
            self.edge_list.append(edge)
        vertex1.add_edge(edge)
        vertex2.add_edge(edge)
        return edge

    def __str__(self):
        return ""
