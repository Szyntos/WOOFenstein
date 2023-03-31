import math

import pygame

import map


class Renderer:
    def __init__(self, game_map, width3d, fov, ray_count):
        self.width3d = width3d
        self.game_map = game_map
        self.fov = fov
        self.ray_count = ray_count
        self.rays = []
        self.obj_col = []
        self.angles = [math.atan(i / ray_count * math.tan(fov / 2 * math.pi / 180)) * 180 / math.pi for i in
                       range(-ray_count, ray_count + 1)]
        # print(self.angles)
        self.scales = [math.cos(a * math.pi / 180) for a in self.angles]

        self.bg = pygame.Surface((self.width3d, self.game_map.height))
        self.bg.fill((0, 0, 0))
        self.cell = pygame.Surface((self.width3d, self.game_map.height/2))
        self.floor = pygame.Surface((self.width3d, self.game_map.height/2))
        self.cell.fill("#7E7463")
        self.floor.fill("#525252")
        # self.scales = [1 for a in self.angles]

    def draw_rays(self, x0, y0, orient):
        r = 1000
        circle = [[r * math.sin((orient + self.angles[abs(i)] * ((i >= 0) - (i < 0)) + 180) * math.pi / 180) + x0,
                   r * math.cos((orient + self.angles[abs(i)] * ((i >= 0) - (i < 0)) + 180) * math.pi / 180) + y0]
                  for i in range(len(self.angles))]

        object_corners = []
        for obj in self.game_map.objects.sprites():
            object_corners.append(
                [[obj.rect.x, obj.rect.y], [obj.rect.x + obj.width, obj.rect.y],
                 [obj.rect.x + obj.width, obj.rect.y + obj.height],
                 [obj.rect.x, obj.rect.y + obj.height]])
        to_check = [[] for _ in range(len(self.game_map.objects.sprites()))]
        i = 0
        # right = 360 > orient > 180 or (orient - self.fov / 2) % 360 == 0 or \
        #         360 > (orient - self.fov / 2) % 360 > 180 \
        #         or (orient + self.fov / 2) % 360 == 180 or 360 > (orient + self.fov / 2) % 360 > 180 or 1
        # up = 270 > orient > 90 or (orient - self.fov / 2) % 360 == 270 or \
        #      270 > (orient - self.fov / 2) % 360 > 90 \
        #      or (orient + self.fov / 2) % 360 == 90 or 270 > (orient + self.fov / 2) % 360 > 90
        for obj in self.game_map.objects.sprites():
            obj_center = (obj.rect.x + obj.width / 2, obj.rect.y + obj.height / 2)
            # print((orient - self.fov / 2) % 360, orient)
            #
            # print(right, up)
            if obj_center[0] - x0 > 0:
                to_check[i].append([0, 3])
            else:
                to_check[i].append([1, 2])
            if obj_center[1] - y0 < 0:
                to_check[i].append([3, 2])
            else:
                to_check[i].append([0, 1])
            i += 1
        i = 0
        self.rays = [[] for _ in circle]
        for point in circle:
            ray = [[x0, y0], point]
            collisions = []
            min_dist = 10000000
            j = 0
            for obj_corner_pairs in to_check:
                intersections = []
                for pair in obj_corner_pairs:
                    line = [object_corners[j][pair[0]], object_corners[j][pair[1]]]
                    intersection = line_intersection(ray, line)
                    if intersection == [10000, 1000]:
                        continue
                    intersections.append(intersection)
                    # if distance([x0, y0], intersection) < min_dist:
                    # min_dist = distance([x0, y0], intersection)
                collisions.append([[x0, y0], min(intersections, key=lambda x: distance([x0, y0], x)), j])
                j += 1

            collisions.sort(key=lambda x: distance(x[0], x[1]))
            to_draw = [0]
            tint = 0
            k = 0
            while k < len(self.game_map.objects.sprites()) - 1:
                if self.game_map.objects.sprites()[collisions[k][2]].type == "Glass":
                    to_draw.append(k + 1)
                else:
                    break
                k += 1
            # if self.game_map.objects.sprites()[collisions[0][2]].type == "Glass":
            #     pygame.draw.line(self.game_map.screen, pygame.Color(120, 120, 255, 255), collisions[0][1],
            #                      collisions[1][1])
            collisions = [[collisions[0][0], collisions[0][0], collisions[0][2]]] + collisions
            lines = []
            for t in to_draw:
                lines.append([collisions[0][1], collisions[t + 1][1]])
                self.rays[i].append(distance(collisions[0][1], collisions[t + 1][1]))
                # break
            for line in lines:
                pygame.draw.line(self.game_map.screen, pygame.Color(255 - 50 * tint, 255 - 50 * tint, 255, 255),
                                 line[0], line[1])
            #     tint += 1
            i += 1

    def render(self):
        self.game_map.screen.blit(self.cell, (0, 0))
        self.game_map.screen.blit(self.floor, (0, self.game_map.height/2))
        # print(self.rays)
        const = self.game_map.height*50
        self.rays = [[self.rays[i][j] * self.scales[i] for j in range(len(self.rays[i]))]
                     for i in range(len(self.scales))]
        dw = self.width3d / len(self.rays)
        for i in range(len(self.rays)):
            for j in range(len(self.rays[i])):
                c = "#A8A8A8"
                if len(self.rays[i]) > 1:
                    c= "#88E3F7"
                if j > 0:
                    c = "#9AC3CC"
                # print(self.width3d - (i+1)*dw)
                pygame.draw.rect(self.game_map.screen, pygame.Color(c),
                                 pygame.Rect(self.width3d - (i + 1) * dw, self.game_map.height / 2 -
                                             (const / (self.rays[i][j])) / 2, dw+1,
                                             const / self.rays[i][j]))


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


def line_intersection(l1, l2):
    licznik_a = (l1[1][1] - l1[0][1])
    licznik_c = (l2[1][1] - l2[0][1])
    mianownik_a = (l1[1][0] - l1[0][0])
    mianownik_c = (l2[1][0] - l2[0][0])
    if approx_equals(mianownik_a, 0) and approx_equals(mianownik_c, 0):
        return [10000000, 10000000]

    if approx_equals(mianownik_a, 0):
        c = licznik_c / mianownik_c
        d = l2[1][1] - c * l2[1][0]
        if is_between(l1[0][0], l2[0][0], l2[1][0]) and is_between(c * l1[0][0] + d, l2[0][1],
                                                                   l2[1][1]) and same_direction(l1, [l1[0][0],
                                                                                            c * l1[0][0] + d]):
            return [l1[0][0], c * l1[0][0] + d]
        return [10000000, 10000000]

    if approx_equals(mianownik_c, 0):
        a = licznik_a / mianownik_a
        b = l1[1][1] - a * l1[1][0]
        if is_between(l2[0][0], l2[0][0], l2[1][0]) and is_between(a * l2[0][0] + b, l2[0][1],
                                                                   l2[1][1]) and same_direction(l1, [l2[0][0],
                                                                                            a * l2[0][0] + b]):
            return [l2[0][0], a * l2[0][0] + b]
        return [10000000, 10000000]

    a = licznik_a / mianownik_a
    b = l1[1][1] - a * l1[1][0]
    c = licznik_c / mianownik_c
    d = l2[1][1] - c * l2[1][0]
    if approx_equals(a, c):
        return [10000000, 10000000]

    x = (d - b) / (a - c)
    y = a * x + b
    if is_between(x, l2[0][0], l2[1][0]) and is_between(y, l2[0][1], l2[1][1]) and same_direction(l1, [x, y]):
        return [x, y]
    return [10000000, 10000000]
