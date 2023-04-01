import math

import pygame

import map


class Renderer:
    def __init__(self, game_map, width3d, fov, ray_count):
        # self.colors = {obj_examples[i].type: obj_examples[i].color for i in range(len(obj_examples))}
        self.width3d = width3d
        self.game_map = game_map
        self.fov = fov
        self.ray_count = ray_count
        self.ray_collisions = []
        self.obj_col = []
        self.angles = [math.atan(i / ray_count * math.tan(fov / 2 * math.pi / 180)) * 180 / math.pi for i in
                       range(-ray_count, ray_count + 1)]
        # print(self.angles)
        self.scales = [math.cos(a * math.pi / 180) for a in self.angles]
        self.bg = pygame.Surface((self.width3d, self.game_map.height))
        self.bg.fill((0, 0, 0))
        self.cell = pygame.Surface((self.width3d, self.game_map.height / 2))

        self.floor = pygame.Surface((self.width3d, self.game_map.height / 2))
        self.cell_color = hex_to_rgb("#7E7463")
        self.floor_color = hex_to_rgb("#525252")
        self.cell.fill("#7E7463")
        self.floor.fill("#525252")
        self.x0 = 0
        self.y0 = 0
        # self.scales = [1 for a in self.angles]

    def generate_data(self, x0, y0, orient):
        self.x0 = x0
        self.y0 = y0
        r = 1000000
        circle = [[r * math.sin((orient + self.angles[abs(i)] + 180) * math.pi / 180) + x0,
                   r * math.cos((orient + self.angles[abs(i)] + 180) * math.pi / 180) + y0]
                  for i in range(len(self.angles))]
        objects = self.game_map.objects.sprites()
        object_corners = []
        for obj in objects:
            object_corners.append(
                [[obj.x, obj.y], [obj.x + obj.width, obj.y],
                 [obj.x + obj.width, obj.y + obj.height],
                 [obj.x, obj.y + obj.height], obj,
                 [[obj.width, 0], [0, obj.height], [-obj.width, 0], [0, -obj.height]]])

        to_check = [[] for _ in range(len(objects))]
        up = not (0 <= orient <= 90 - self.fov / 2 or 270 + self.fov / 2 <= orient <= 360)
        down = not (90 + self.fov / 2 <= orient <= 270 - self.fov / 2)
        right = not (180 + self.fov / 2 <= orient <= 360 - self.fov / 2)
        left = not (0 + self.fov / 2 <= orient <= 180 - self.fov / 2)
        i = 0
        for obj in self.game_map.objects.sprites():
            obj_center = (obj.x + obj.width / 2, obj.y + obj.height / 2)
            if not ((not up) and obj.y > y0 or (not down) and obj.y + obj.height < y0 or
                    (not right) and obj.x + obj.width < x0 or (not left) and obj.x > x0):
                if obj_center[0] - x0 > 0 and left:
                    to_check[i].append([3, 0])
                elif right:
                    to_check[i].append([1, 2])
                if obj_center[1] - y0 < 0 and down:
                    to_check[i].append([2, 3])
                elif up:
                    to_check[i].append([0, 1])
            i += 1
        return circle, object_corners, to_check

    def generate_rays(self, x0, y0, orient):
        scanline = [[x0, y0], [1000000 * math.sin((orient + 180) * math.pi / 180) + x0,
                               1000000 * math.cos((orient + 180) * math.pi / 180) + y0]]
        circle, object_corners, to_check = self.generate_data(x0, y0, orient)
        i = 0
        self.ray_collisions = [[] for _ in circle]
        for point in circle:
            ray = [[x0, y0], point]
            ray_vec = [ray[1][0] - ray[0][0], ray[1][1] - ray[0][1]]
            collisions = []
            j = 0
            for obj_corner_pairs in to_check:
                intersections = []
                for pair in obj_corner_pairs:
                    edge = [object_corners[j][pair[0]], object_corners[j][pair[1]]]
                    #     # pygame.draw.line(self.game_map.screen, pygame.Color(222, 0, 0, 255),
                    #     #                  [edge[0][0] * self.game_map.scale + self.game_map.vector[0],
                    #     #                   edge[0][1] * self.game_map.scale + self.game_map.vector[1]],
                    #     #                  [edge[1][0] * self.game_map.scale + self.game_map.vector[0],
                    #     #                   edge[1][1] * self.game_map.scale + self.game_map.vector[1]], 3)
                    intersection = line_intersection(ray, edge)
                    intersections.append([intersection, object_corners[j][4], angle_between_lines(ray_vec, pair[0])])
                #
                if intersections:
                    collisions.append(min(intersections, key=lambda x: distance_no_sqrt([x0, y0], x[0])))
                # collisions += intersections
                j += 1
            #
            collisions.sort(key=lambda x: distance_no_sqrt([x0, y0], x[0]))
            collisions_proper = []
            j = 0
            while j < len(collisions) and collisions[j][1].type == "Glass":
                collisions_proper.append(collisions[j])
                j += 1
            if j < len(collisions):
                collisions_proper.append(collisions[j])
            self.ray_collisions[i] = collisions_proper
            i += 1

    def draw_rays(self):
        i = 0
        for i in range(len(self.ray_collisions)):
            collisions_proper = self.ray_collisions[i]
            if i == int(len(self.ray_collisions) / 2) or i == 0 or i == len(self.ray_collisions) - 1:
                lines = []
                for_lines = [[[self.x0, self.y0], map.GameObject(0, self.game_map, 0, 0, 0, 0)]] + collisions_proper
                for j in range(len(for_lines) - 1):
                    lines.append([[for_lines[j][0][0] * self.game_map.scale + self.game_map.vector[0],
                                   for_lines[j][0][1] * self.game_map.scale + self.game_map.vector[1]],
                                  [for_lines[j + 1][0][0] * self.game_map.scale + self.game_map.vector[0],
                                   for_lines[j + 1][0][1] * self.game_map.scale + self.game_map.vector[1]],
                                  for_lines[j + 1][1]])
                # c_box = hex_to_rgb("#A8A8A8") + [122]
                # c_glass = hex_to_rgb("#247F93") + [100]
                # c_glass = (0, 0, 255, 50)
                # c = (255, 255, 255, 120)
                c = (255, 0, 0, 120)
                j = 0
                for line in lines:
                    if j > 0:
                        c = combine_colors(lines[j - 1][2].color, c)

                    pygame.draw.line(self.game_map.screen, pygame.Color(c),
                                     line[0], line[1])
                    j += 1
        i += 1

    def render(self):
        self.game_map.screen.blit(self.cell, (0, 0))
        self.game_map.screen.blit(self.floor, (0, self.game_map.height / 2))
        # print(self.rays)
        const = self.game_map.height * 30

        # distances = [[[self.scales[i] * distance([self.x0, self.y0], self.ray_collisions[i][j][0]),
        #                self.ray_collisions[i][j][1], self.ray_collisions[i][j][2]]
        #               for j in range(len(self.ray_collisions[i]))] for i in range(len(self.ray_collisions))]
        distances_normalised = [[[self.scales[i] * distance([self.x0, self.y0], self.ray_collisions[i][j][0]),
                                  self.ray_collisions[i][j][1], self.ray_collisions[i][j][2]]
                                 for j in range(len(self.ray_collisions[i]))]
                                for i in range(len(self.ray_collisions))]
        # distances_circle = [distances_normalised[i][0][0] for i in range(len(distances_normalised))]
        # self.rays = [[self.rays[i][j] * self.scales[i] for j in range(len(self.rays[i]))]
        #              for i in range(len(self.scales))]
        dw = self.width3d / len(distances_normalised)
        # c_box = hex_to_rgb("#A8A8A8") + [122]
        # c_glass = hex_to_rgb("#2A97B0") + [122]
        c = (0, 0, 0, 255)
        for i in range(len(distances_normalised)):
            for j in range(len(distances_normalised[i])):
                if j == 0:
                    c = distances_normalised[i][j][1].color
                elif j > 0:
                    c = combine_colors(c, distances_normalised[i][j][1].color)
                b = 12 / (j + 4) * max(0, min(255, abs(distances_normalised[i][j][2]) / 360 * 255))
                c = combine_colors([220 - b, 220 - b, 220 - b, 60], c)
                # pygame.draw.rect(self.game_map.screen, pygame.Color(c),
                #                  pygame.Rect(self.width3d - (i + 1) * dw, self.game_map.height / 2 -
                #                              (const / (distances_normalised[i][j][0])) / 2, dw + 1,
                #                              const / (distances_normalised[i][j][0]) / 2))
                # pygame.draw.rect(self.game_map.screen, pygame.Color(c),
                #                  pygame.Rect(self.width3d - (i + 1) * dw, self.game_map.height / 2 - 1, dw + 1,
                #                              const / distances_normalised[i][j][0] / 2))
                pygame.draw.rect(self.game_map.screen, pygame.Color(c),
                                 pygame.Rect(self.width3d - (i + 1) * dw, self.game_map.height / 2 -
                                             (const / (distances_normalised[i][j][0])) / 2, dw + 1,
                                             const / (distances_normalised[i][j][0])))


def distance(p1, p2):
    # return distance_2(p1, p2)
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def distance_no_sqrt(p1, p2):
    # return distance_2(p1, p2)
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2
    # return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def distance_2(p1, p2):
    dx = (abs(p1[0] - p2[0]))
    dy = (abs(p1[1] - p2[1]))
    m = max(dx, dy)
    dx /= m
    dy /= m
    dx = int(dx)
    dy = int(dy)
    if dx < dy:
        return (dx + dy - (dx >> 1)) * m
    return (dx + dy - (dy >> 1)) * m


def angle_between_lines(v1, edge_index):
    # v1 = [l1[1][0] - l1[0][0], l1[1][1] - l1[0][1]]
    # v2 = [l2[1][0] - l2[0][0], l2[1][1] - l2[0][1]]
    # a = (math.acos(((v1[0] * v2[0] + v1[1] * v2[1]) /
    #                 (math.sqrt((v1[0] ** 2 + v1[1] ** 2) * (v2[0] ** 2 + v2[1] ** 2))))) * 180 / math.pi - 90)
    # a = ((DiamondAngle(v1[1], v1[0]) - DiamondAngle(v2[1], v2[0]) - 2) / 4 * 360) % 180 - 90
    # if l2 == 0:
    #     # right
    #     a = ((DiamondAngle(v1[1], v1[0]) - 0 - 2) / 4 * 360) % 180 - 90
    # elif l2 == 1:
    #     # left
    #     a = ((DiamondAngle(v1[1], v1[0]) - 1 - 2) / 4 * 360) % 180 - 90
    # elif l2 == 2:
    #     # up
    #     a = ((DiamondAngle(v1[1], v1[0]) + 0 - 2) / 4 * 360) % 180 - 90
    # elif l2 == 3:
    #     # right
    #     a = ((DiamondAngle(v1[1], v1[0]) + 1 + 2) / 4 * 360) % 180 - 90
    # else:
    #     a = 180
    a = ((DiamondAngle(v1[1], v1[0]) + abs(edge_index-1)-1) * 90) % 180 - 90
    # print(a)
    return a


def is_between(x, a, b):
    eps = 0.001
    tmp = b
    b = max(a, b)
    a = min(a, tmp)
    if a - eps <= x <= b + eps:
        return 1
    return 0


def same_direction(l, p):
    dif_x = (l[1][0] - l[0][0])
    dif_y = (l[1][1] - l[0][1])
    dif_x_p = (p[0] - l[0][0])
    dif_y_p = (p[1] - l[0][1])
    if dif_x * dif_x_p >= 0 and dif_y * dif_y_p >= 0:
        return 1
    return 0


def approx_equals(a, b):
    eps = 0.0001
    if b - eps < a < b + eps:
        return 1
    return 0


def line_intersection_1(ray, edge):
    numerator_a = (ray[1][1] - ray[0][1])
    numerator_c = (edge[1][1] - edge[0][1])
    denominator_a = (ray[1][0] - ray[0][0])
    denominator_c = (edge[1][0] - edge[0][0])
    if approx_equals(denominator_a, 0) and approx_equals(denominator_c, 0):
        return ray[1]

    if approx_equals(denominator_a, 0):
        c = numerator_c / denominator_c
        d = edge[1][1] - c * edge[1][0]
        if is_between(ray[0][0], edge[0][0], edge[1][0]) and \
                is_between(c * ray[0][0] + d, edge[0][1], edge[1][1]) and \
                same_direction(ray, [ray[0][0], c * ray[0][0] + d]):
            return [ray[0][0], c * ray[0][0] + d]
        return ray[1]

    if approx_equals(denominator_c, 0):
        a = numerator_a / denominator_a
        b = ray[1][1] - a * ray[1][0]
        if is_between(edge[0][0], edge[0][0], edge[1][0]) and \
                is_between(a * edge[0][0] + b, edge[0][1], edge[1][1]) and \
                same_direction(ray, [edge[0][0], a * edge[0][0] + b]):
            return [edge[0][0], a * edge[0][0] + b]
        return ray[1]

    a = numerator_a / denominator_a
    b = ray[1][1] - a * ray[1][0]
    c = numerator_c / denominator_c
    d = edge[1][1] - c * edge[1][0]
    if approx_equals(a, c):
        return ray[1]

    x = (d - b) / (a - c)
    y = a * x + b
    if is_between(x, edge[0][0], edge[1][0]) and is_between(y, edge[0][1], edge[1][1]) and \
            same_direction(ray, [x, y]):
        return [x, y]
    return ray[1]


def combine_colors(c0, c1):
    # c0 = (r, g, b, a)
    a0 = c0[3] / 255
    r0 = c0[0]
    g0 = c0[1]
    b0 = c0[2]
    a1 = c1[3] / 255
    r1 = c1[0]
    g1 = c1[1]
    b1 = c1[2]
    a01 = (1 - a0) * a1 + a0
    if a01 == 0:
        a01 = 0.01
    r01 = ((1 - a0) * a1 * r1 + a0 * r0) / a01
    g01 = ((1 - a0) * a1 * g1 + a0 * g0) / a01
    b01 = ((1 - a0) * a1 * b1 + a0 * b0) / a01
    r01 = max(0, r01 - 15)
    g01 = max(0, g01 - 15)
    b01 = max(0, b01 - 15)
    return [r01, g01, b01, a01 * 255]


def hex_to_rgb(h):
    h = h.lstrip('#')
    return list(float(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def DiamondAngle(y, x):
    if y >= 0:
        return y / (x + y) if x >= 0 else 1 - x / (-x + y)
    else:
        return 2 - y / (-x - y) if x < 0 else 3 + x / (x - y)
    # return y / (x + y) if y >= 0 and x >= 0 else 1 + x / (x - y) if y >= 0 and x < 0 else 2 + y / (
    #         x + y) if y < 0 and x < 0 else 3 + x / (x - y)


def line_intersection(ray, edge):
    A = [ray[1][0] - ray[0][0], ray[1][1] - ray[0][1]]
    B = [edge[0][0] - edge[1][0], edge[0][1] - edge[1][1]]
    C = [ray[0][0] - edge[0][0], ray[0][1] - edge[0][1]]
    numerator_a = B[1] * C[0] - B[0] * C[1]
    denominator = A[1] * B[0] - A[0] * B[1]
    if denominator == 0:
        return ray[1]
    if denominator > 0:
        if numerator_a < 0 or numerator_a > denominator:
            return ray[1]
    elif numerator_a > 0 or numerator_a < denominator:
        return ray[1]
    numerator_b = A[0] * C[1] - A[1] * C[0]
    if denominator > 0:
        if numerator_b < 0 or numerator_b > denominator:
            return ray[1]
    elif numerator_b > 0 or numerator_b < denominator:
        return ray[1]
    a = numerator_a / denominator
    return [ray[0][0] + a * A[0], ray[0][1] + a * A[1]]
