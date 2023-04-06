import math

import pygame

import map
import random


class Renderer:
    def __init__(self, game_map, width3d, fov, ray_count):
        self.width3d = width3d
        self.game_map = game_map
        self.fov = fov
        self.ray_count = ray_count  # Actual number of rays is 2*ray_count-1
        self.ray_collisions = []
        self.obj_col = []

        self.angles = [math.atan(i / ray_count * math.tan(fov / 2 * math.pi / 180)) * 180 / math.pi for i in
                       range(-ray_count, ray_count + 1)]  # Angle between player orientation and each ray
        self.scales = [1 / math.cos(a * math.pi / 180) for a in self.angles]  # Scaling factor for each ray

        self.bg = pygame.Surface((self.width3d, self.game_map.height))
        self.bg.fill((0, 0, 0))

        self.ceil = pygame.Surface((self.width3d, self.game_map.height / 2))
        self.ceil_color = hex_to_rgb("#97b4b7")

        self.floor = pygame.Surface((self.width3d, self.game_map.height / 2))
        self.floor_color = hex_to_rgb("#6d6a50")

        self.ceil.fill(self.ceil_color)
        self.floor.fill(self.floor_color)

        # Default camera coordinates
        self.x0 = 0
        self.y0 = 0

    def generate_data(self, x0, y0, orient):
        self.x0 = x0
        self.y0 = y0

        # Generating rays' endpoints
        r = 1000000
        circle = [[r * math.sin((orient + self.angles[abs(i)] + 180) * math.pi / 180) + x0,
                   r * math.cos((orient + self.angles[abs(i)] + 180) * math.pi / 180) + y0]
                  for i in range(len(self.angles))]

        objects = self.game_map.objects.sprites()

        # Due to all objects being rectangles we can check only the collisions between rays and edges
        object_corners = []
        for obj in objects:
            object_corners.append(
                [[obj.x, obj.y], [obj.x + obj.width, obj.y],
                 [obj.x + obj.width, obj.y + obj.height],
                 [obj.x, obj.y + obj.height], obj,
                 [[obj.width, 0], [0, obj.height], [-obj.width, 0], [0, -obj.height]]])

        # We can disregard not visible corners filtering by the relative position of the player to the object and
        # by the direction the camera is facing
        to_check = [[] for _ in range(len(objects))]
        # Checking camera's direction
        up = (0 <= orient <= 90 - self.fov / 2 or 270 + self.fov / 2 <= orient <= 360)
        down = (90 + self.fov / 2 <= orient <= 270 - self.fov / 2)
        right = (180 + self.fov / 2 <= orient <= 360 - self.fov / 2)
        left = (0 + self.fov / 2 <= orient <= 180 - self.fov / 2)

        i = 0
        for obj in self.game_map.objects.sprites():
            obj_center = (obj.x + obj.width / 2, obj.y + obj.height / 2)
            # print(not (up and obj.y > y0 or down and obj.y + obj.height < y0 or
            #         right and obj.x + obj.width < x0 or left and obj.x > x0))
            if not (up and obj.y > y0 or down and obj.y + obj.height < y0 or
                    right and obj.x + obj.width < x0 or left and obj.x > x0):
                if obj_center[0] - x0 > 0 and not left:
                    to_check[i].append([3, 0])
                elif not right:
                    to_check[i].append([1, 2])
                if obj_center[1] - y0 < 0 and not down:
                    to_check[i].append([2, 3])
                elif not up:
                    to_check[i].append([0, 1])
            n = len(to_check[i])
            circle_size = 2
            if n == 1:
                # pygame.draw.circle(self.game_map.screen, "yellow", [object_corners[i][to_check[i][0][0]][0] * self.game_map.scale + self.game_map.vector[0],
                #                                                   object_corners[i][to_check[i][0][0]][1]] * self.game_map.scale + self.game_map.vector[1], circle_size)
                #
                # pygame.draw.circle(self.game_map.screen, "yellow", [object_corners[i][to_check[i][0][1]][0] * self.game_map.scale + self.game_map.vector[0],
                #                                                   object_corners[i][to_check[i][0][1]][1] * self.game_map.scale + self.game_map.vector[1]], circle_size)

                if not (is_visible(object_corners[i][to_check[i][0][0]], [x0, y0], orient, self.fov) or
                        is_visible(object_corners[i][to_check[i][0][1]], [x0, y0], orient, self.fov)):
                    pass
                    # to_check[i] = []
            elif n > 1:
                tmp = [k for k in to_check[i][0] if k not in to_check[i][1]] + \
                      [k for k in to_check[i][1] if k not in to_check[i][0]]
                # pygame.draw.circle(self.game_map.screen, "yellow", [object_corners[i][tmp[0]][0] * self.game_map.scale + self.game_map.vector[0],
                #                                                   object_corners[i][tmp[0]][1] * self.game_map.scale + self.game_map.vector[1]], circle_size)
                # pygame.draw.circle(self.game_map.screen, "yellow", [object_corners[i][tmp[1]][0] * self.game_map.scale + self.game_map.vector[0],
                #                                                   object_corners[i][tmp[1]][1] * self.game_map.scale + self.game_map.vector[1]], circle_size)
                # print(tmp)
                # print((orient + self.fov / 2) % 360, orient, is_visible(object_corners[i][tmp[0]], [x0, y0], orient, self.fov),
                #       (orient - self.fov / 2) % 360)
                if not (is_visible(object_corners[i][tmp[0]], [x0, y0], orient, self.fov) or
                        is_visible(object_corners[i][tmp[1]], [x0, y0], orient, self.fov)):
                    to_check[i] = []
            i += 1
        return circle, object_corners, to_check

    def generate_rays(self, x0, y0, orient):
        # scanline = [[x0, y0], [1000000 * math.sin((orient + 180) * math.pi / 180) + x0,
        #                        1000000 * math.cos((orient + 180) * math.pi / 180) + y0]]
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
                    intersection = line_intersection(ray, edge)
                    intersections.append([intersection, object_corners[j][4],
                                          angle_between_lines(ray_vec,
                                                              pair[0], self.angles[i] + orient)])
                #
                if intersections:
                    collisions.append(min(intersections, key=lambda x: distance_no_sqrt([x0, y0], x[0])))
                # collisions += intersections
                j += 1
            #
            collisions.sort(key=lambda x: distance_no_sqrt([x0, y0], x[0]))

            collisions_proper = []
            j = 0
            while j < len(collisions) and collisions[j][1].type == "semitransparent":
                collisions_proper.append(collisions[j])
                j += 1
            # collisions_proper.sort(key=lambda x: (random.random() * 323))
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
                # c = (255, 0, 0, 120)
                c = (255, 255, 255, 1)
                j = 0
                for line in lines:
                    if j > 0:
                        c = combine_colors(lines[j - 1][2].color, c)
                    size = 1
                    if i == int(len(self.ray_collisions) / 2):
                        size = 3
                    pygame.draw.line(self.game_map.screen, pygame.Color(c),
                                     line[0], line[1], size)
                    j += 1
        i += 1

    def draw_visible_edges(self, x0, y0, orient):
        circle, object_corners, to_check = self.generate_data(x0, y0, orient)
        j = 0
        for obj_corner_pairs in to_check:
            for pair in obj_corner_pairs:
                edge = [object_corners[j][pair[0]], object_corners[j][pair[1]]]
                pygame.draw.line(self.game_map.screen, pygame.Color(222, 222, 222, 255),
                                 [edge[0][0] * self.game_map.scale + self.game_map.vector[0],
                                  edge[0][1] * self.game_map.scale + self.game_map.vector[1]],
                                 [edge[1][0] * self.game_map.scale + self.game_map.vector[0],
                                  edge[1][1] * self.game_map.scale + self.game_map.vector[1]], 1)
            j += 1

    def render(self, i=0):
        self.game_map.screen.blit(self.ceil, (0, 0))
        self.game_map.screen.blit(self.floor, (0, self.game_map.height / 2))
        # print(self.rays)
        const = self.game_map.height * 50

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
        # h = -400
        h = 0
        for i in range(len(distances_normalised)):
            for j in range(len(distances_normalised[i])):
                if j == 0:
                    c = distances_normalised[i][j][1].color
                elif j > 0:
                    c = combine_colors(c, distances_normalised[i][j][1].color)
                b = 12 / (j + 4) * max(0, min(255, abs(distances_normalised[i][j][2]) / 360 * 255))
                c = combine_colors([220 - b, 220 - b, 220 - b, 60], c)
                b = 12 / (j + 4) * max(0, min(255, abs(1 / distances_normalised[i][j][0]) ** 2 / 7000))
                c = [max(max(0, i - 70), i - b / 4) for i in c]
                if distances_normalised[i][j][1].type == "semitransparent":
                    sat = 1.5
                    cu = combine_colors(self.ceil_color + [60], c)
                    cd = combine_colors(self.floor_color + [60], c)
                    cu = saturation(cu, sat)
                    cd = saturation(cd, sat)
                    pygame.draw.rect(self.game_map.screen, pygame.Color(cu),
                                     pygame.Rect(self.width3d - (i + 1) * dw, self.game_map.height / 2 -
                                                 (const * (distances_normalised[i][j][0])) / 2 + h, dw + 1,
                                                 const * (distances_normalised[i][j][0]) / 2))
                    pygame.draw.rect(self.game_map.screen, pygame.Color(cd),
                                     pygame.Rect(self.width3d - (i + 1) * dw, self.game_map.height / 2 - 1 + h, dw + 1,
                                                 const * distances_normalised[i][j][0] / 2))
                else:
                    pygame.draw.rect(self.game_map.screen, pygame.Color(c),
                                     pygame.Rect(self.width3d - (i + 1) * dw, self.game_map.height / 2 -
                                                 (const * (distances_normalised[i][j][0])) / 2 + h, dw + 1,
                                                 const * (distances_normalised[i][j][0])))


def distance(p1, p2):
    # return distance_2(p1, p2)
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** -0.5


def is_visible(obj_center, player, orient, fov):
    vec = [obj_center[0] - player[0], obj_center[1] - player[1]]
    a = ((DiamondAngle(vec[0], vec[1]) - 2) * 90) % 360
    # print("a:", a)
    # print((a - orient + fov/2)%360)
    acc = 5
    return 10 - acc <= (a - orient + fov / 2 + 10) % 360 <= 10 + 180 + acc
    # if (orient + fov / 2 + acc) % 360 > (orient - fov / 2 - acc) % 360:
    #     return not ((orient + fov / 2 + acc) % 360 <= a <= 0 or 0 <= a <= (orient - fov / 2 - acc) % 360)
    # else:
    #     return ((orient + fov / 2 + acc) % 360 <= a <= (orient - fov / 2 - acc) % 360)


def distance_no_sqrt(p1, p2):
    # return distance_2(p1, p2)
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2
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


def angle_between_lines(v1, edge_index, angle):
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
    # a = ((DiamondAngle(v1[1], v1[0]) + abs(edge_index-1)-1) * 90) % 180 - 90
    # print("DIA", (DiamondAngle(v1[1], v1[0])))
    # print("and", (-angle/90 + 3))

    # a = (((-angle / 90 + 3) + (abs(edge_index - 1) - 1)) * 90) % 180 - 90
    a = (90 * abs(edge_index - 1) - angle) % 180 - 90

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
    dimming_factor = -10
    r01 = max(0, r01 - r0 / 6 + dimming_factor)
    g01 = max(0, g01 - g0 / 6 + dimming_factor)
    b01 = max(0, b01 - b0 / 6 + dimming_factor)
    return [r01, g01, b01, a01 * 255]


def hex_to_rgb(h):
    h = h.lstrip('#')
    return list((int(h[i:i + 2], 16)) for i in (0, 2, 4))


def saturation(c, sat):
    tmp = c[3]
    c = [min(254, i + 10) for i in c]
    gray = 0.2989 * c[0] + 0.5870 * c[1] + 0.1140 * c[2]
    c = [int(min(254.0, (max(0.0, -gray * sat + i * (1 + sat))))) for i in c]
    c[3] = tmp
    return c


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
