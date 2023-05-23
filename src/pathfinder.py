import pyvisgraph as vg
from shapely.geometry import Polygon
from shapely import unary_union

import src.utils
from src.blocks import Border
import pygame
import math


def draw_path(path, game_map):
    for i in range(len(path) - 1):
        pygame.draw.line(game_map.screen, "#000000",
                         [path[i].x * game_map.scale + game_map.vector[0],
                          path[i].y * game_map.scale + game_map.vector[1]],
                         [path[i + 1].x * game_map.scale + game_map.vector[0],
                          path[i + 1].y * game_map.scale + game_map.vector[1]], 1)


def get_path_length(path):
    if len(path) < 2:
        return 0
    l = 0
    for i in range(len(path) - 1):
        l += src.utils.vector_length([path[i].x - path[i + 1].x, path[i].y - path[i + 1].y])
    return l


class Pathfinder:
    def __init__(self):
        self.leeway = 0
        self.objects = []
        self.visibilityGraph = vg.VisGraph()

    def change_objects(self, new_objects):
        polygons = []
        for obj in new_objects:
            if type(obj) != Border:
                polygons.append(Polygon([(obj.x - self.leeway, obj.y - self.leeway),
                                         (obj.x + obj.width + self.leeway, obj.y - self.leeway),
                                         (obj.x + obj.width + self.leeway, obj.y + obj.height + self.leeway),
                                         (obj.x - self.leeway, obj.y + obj.height + self.leeway)]))
        u = unary_union(polygons)
        if type(u) == Polygon:
            corners = list(u.exterior.coords)
            obj = []
            for point in corners:
                obj.append(vg.Point(point[0], point[1]))
            self.objects.append(obj)
            return
        self.objects = []
        for poly in u.geoms:
            corners = list(poly.exterior.coords)
            obj = []
            for point in corners:
                obj.append(vg.Point(point[0], point[1]))
            self.objects.append(obj)

    def build_graph(self):
        self.visibilityGraph.build(self.objects)

    def find_shortest(self, a, b):
        a = vg.Point(int(a[0]), int(a[1]))
        b = vg.Point(int(b[0]), int(b[1]))
        return self.visibilityGraph.shortest_path(a, b)
