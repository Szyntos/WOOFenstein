import math

import pygame

import map_2


class Renderer:
    def __init__(self, game_map, width3d, fov, ray_count):
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

    def draw_rays(self, x0, y0, orient):
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
                [[obj.x_scaled, obj.y_scaled], [obj.x_scaled + obj.width_scaled, obj.y_scaled],
                 [obj.x_scaled + obj.width_scaled, obj.y_scaled + obj.height_scaled],
                 [obj.x_scaled, obj.y_scaled + obj.height_scaled], obj.type])

        to_check = [[] for _ in range(len(objects))]
        up = not (0 <= orient <= 90 - self.fov / 2 or 270 + self.fov / 2 <= orient <= 359)
        down = not (90 + self.fov / 2 <= orient <= 270 - self.fov / 2)
        right = not (180 + self.fov / 2 <= orient <= 360 - self.fov / 2)
        left = not (0 + self.fov / 2 <= orient <= 180 - self.fov / 2)
        i = 0
        for obj in self.game_map.objects.sprites():
            obj_center = (obj.rect.x + obj.width / 2, obj.rect.y + obj.height / 2)
            if obj_center[0] - x0 > 0 and left:
                to_check[i].append([0, 3])
            elif right:
                to_check[i].append([1, 2])
            if obj_center[1] - y0 < 0 and down:
                to_check[i].append([3, 2])
            elif up:
                to_check[i].append([0, 1])
            i += 1
        i = 0
        self.ray_collisions = [[] for _ in circle]
        for point in circle:
            ray = [[x0, y0], point]
            collisions = []
            j = 0
            for obj_corner_pairs in to_check:
                intersections = []
                for pair in obj_corner_pairs:
                    edge = [object_corners[j][pair[0]], object_corners[j][pair[1]]]
                    # pygame.draw.line(self.game_map.screen, pygame.Color(222, 0, 0, 255),
                    #                  edge[0], edge[1])
                    intersection = line_intersection(ray, edge)
                    intersections.append([intersection, object_corners[j][4], j])
                    # if distance([x0, y0], intersection) < min_dist:
                    # min_dist = distance([x0, y0], intersection)

                if intersections:
                    collisions.append(min(intersections, key=lambda x: distance([x0, y0], x[0])))
                j += 1

            collisions.sort(key=lambda x: distance([x0, y0], x[0]))
            collisions_proper = []
            j = 0
            while j < len(collisions) and collisions[j][1] == "Glass":
                collisions_proper.append(collisions[j])
                j += 1
            if j < len(collisions):
                collisions_proper.append(collisions[j])
            # lines = []
            # for_lines = [[[x0, y0]]] + collisions_proper
            # for j in range(len(for_lines) - 1):
            #     lines.append([for_lines[j], for_lines[j + 1]])
            # c_box = hex_to_rgb("#A8A8A8") + [122]
            # c_glass = hex_to_rgb("#247F93") + [122]
            # c = (255, 255, 255, 120)
            # j = 0
            # for line in lines:
            #     if j > 0:
            #         if line[0][1] == "Box":
            #
            #             c = combine_colors(c, c_box)
            #         else:
            #             c = combine_colors(c, c_glass)
            #
            #     pygame.draw.line(self.game_map.screen, pygame.Color(c),
            #                      line[0][0], line[1][0])
            #     j += 1
            self.ray_collisions[i] = collisions_proper
            i += 1

    def render(self):
        self.game_map.screen.blit(self.cell, (0, 0))
        self.game_map.screen.blit(self.floor, (0, self.game_map.height / 2))
        # print(self.rays)
        const = self.game_map.height * 30 * self.game_map.scale

        # distances = [[[self.scales[i] * distance([self.x0, self.y0], self.ray_collisions[i][j][0]),
        #                self.ray_collisions[i][j][1], self.ray_collisions[i][j][2]]
        #               for j in range(len(self.ray_collisions[i]))] for i in range(len(self.ray_collisions))]
        distances_normalised = [[[self.scales[i] * distance([self.x0, self.y0], self.ray_collisions[i][j][0]),
                                  self.ray_collisions[i][j][1], self.ray_collisions[i][j][2]]
                                 for j in range(len(self.ray_collisions[i]))]
                                for i in range(len(self.ray_collisions))]
        distances_circle = [distances_normalised[i][0][0] for i in range(len(distances_normalised))]
        # self.rays = [[self.rays[i][j] * self.scales[i] for j in range(len(self.rays[i]))]
        #              for i in range(len(self.scales))]
        dw = self.width3d / len(distances_normalised)
        c_box = hex_to_rgb("#A8A8A8") + [122]
        c_glass = hex_to_rgb("#2A97B0") + [122]
        c = c_box
        for i in range(len(distances_normalised)):
            for j in range(len(distances_normalised[i])):
                obj_type = distances_normalised[i][j][1]
                if j == 0:
                    if obj_type == "Box":
                        c = c_box
                    else:
                        c = c_glass
                elif j > 0:
                    if obj_type == "Box":

                        c = combine_colors(c, c_box)
                    else:
                        c = combine_colors(c, c_glass)
                b = max(0, min(255, 1 / distances_circle[i]))
                c = combine_colors(c, [b, b, b, 255])
                #         # print(self.width3d - (i+1)*dw)
                pygame.draw.rect(self.game_map.screen, pygame.Color(c),
                                 pygame.Rect(self.width3d - (i + 1) * dw, self.game_map.height / 2 -
                                             (const / (distances_normalised[i][j][0])) / 2 , dw + 1,
                                             const / (distances_normalised[i][j][0])/2))
                pygame.draw.rect(self.game_map.screen, pygame.Color(c),
                                 pygame.Rect(self.width3d - (i + 1) * dw, self.game_map.height / 2-1, dw + 1,
                                             const / distances_normalised[i][j][0]/2))


def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


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


def line_intersection(ray, edge):
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
    r01 = max(0, r01 - 7)
    g01 = max(0, g01 - 7)
    b01 = max(0, b01 - 7)
    return [r01, g01, b01, a01 * 255]


def hex_to_rgb(h):
    h = h.lstrip('#')
    return list(float(int(h[i:i + 2], 16)) for i in (0, 2, 4))
