
from typing import Dict, List, Set, Tuple
import numpy as np

def lab_distance(lab1: Tuple[float, float, float], lab2: Tuple[float, float, float]):
    delta_e = math.sqrt(
        (lab1[0] - lab2[0]) ** 2 + 
        (lab1[1] - lab2[1]) ** 2 + 
        (lab1[2] - lab2[2]) ** 2
    )
    return delta_e
    
class Graph:
    def __init__(self, ) -> None:
        self.node_neighbors:Dict[int, Dict[int, float]] = {}
        self.label_vs_nodes: Dict[int, Set] = {}
        self.node_vs_label = {}
        self.visited = {}

    def get_label(self, node):
        return self.node_vs_label[node]

    def get_nodes(self, label):
        return self.label_vs_nodes[label]

    def build(self, labcolors, labels):
        l = len(labels)
        self.add_node(-1, -1)
        for node1, label1, labcolor1 in zip(range(l), labels, labcolors):
            self.add_node(node1, label1)
            self.add_edge(-1, node1, 0)
            for node2, label2, labcolor2 in zip(range(l), labels, labcolors):
                if node1 == node2:
                    continue
                self.add_node(node2, label2)
                distance = lab_distance(labcolor1, labcolor2)
                if label1 == label2:
                    # 两个节点的label一致，他们必然不能连接
                    assert node1 in self.get_group_nodes(node2)
                    assert node2 in self.get_group_nodes(node1)
                    continue
                self.add_edge(node1, node2, distance)
    
    def __str__(self) -> str:
        multi_lines = ''
        for node, neighbords in self.node_neighbors.items():
            one_line = '[{}]{} -> '.format(self.node_vs_label[node], node)
            for neighbord, distance in neighbords.items():
                one_line += '([{}]{},{}) '.format(self.node_vs_label[neighbord], neighbord, distance)
            multi_lines += one_line + '\n'
        return multi_lines

    def get_group_nodes(self, node):
        label = self.node_vs_label[node]
        return self.label_vs_nodes[label]

    def can_visit(self, node):
        for node in self.get_group_nodes(node):
            if self.visited.get(node, False):
                return False
        return True

    def make_visited(self, node):
        self.visited[node] = True

    def make_unvisited(self, node):
        self.visited[node] = False

    def add_node(self, node, label):
        if node not in self.node_neighbors:
            self.node_neighbors[node] = {}
            self.node_vs_label[node] = label

        if label not in self.label_vs_nodes:
            self.label_vs_nodes[label] = {node}
            
        self.label_vs_nodes[label].add(node)

    def add_edge(self, node1, node2, distance):
        assert node1 in self.node_neighbors
        assert node2 in self.node_neighbors
        self.node_neighbors[node1][node2] = distance
        self.node_neighbors[node2][node1] = distance

    def get_max_path(self, start_node, max_nums_of_nodes) -> Tuple[float, List[int]]:
        if max_nums_of_nodes == 0:
            return 0, [start_node]

        self.make_visited(start_node)
        distances = []
        paths = []
        for node, distance in self.node_neighbors[start_node].items():
            if not self.can_visit(node):
                continue
            path_distance, path = self.get_max_path(node, max_nums_of_nodes-1)
            distances.append(path_distance + distance)
            paths.append([start_node, *path])

        self.make_unvisited(start_node)
        if not distances:
            # why?
            return 0, [start_node]

        index = np.argmax(distances)
        max_path_distance, max_path = distances[index], paths[index]

        return max_path_distance, max_path
