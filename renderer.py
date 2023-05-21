import math

from imports import *
from map import *
from utils import *


class Renderer:
    def __init__(self, game_map, width3d, fov, ray_count):
        self.width3d = width3d
        self.game_map = game_map
        self.fov = fov
        self.ray_count = ray_count  # Actual number of rays is 2*ray_count-1
        self.ray_collisions = []
        self.obj_col = []
        self.over = 0

        self.angles = [math.atan(i / ray_count * math.tan(fov / 2 * math.pi / 180)) * 180 / math.pi for i in
                       range(-ray_count, ray_count + 1)]  # Angle between camera orientation and each ray
        self.scales = [1 / math.cos(a * math.pi / 180) for a in self.angles]  # Scaling factor for each ray

        self.bg = pygame.Surface((self.width3d, self.game_map.height))
        self.bg.fill((0, 0, 0))

        self.ceil = pygame.Surface((self.width3d, self.game_map.height / 2))
        self.ceil_color = hex_to_rgb("#97b4b7")
        # self.ceil_color = hex_to_rgb("#000000")

        self.floor = pygame.Surface((self.width3d, self.game_map.height / 2))
        self.floor_color = hex_to_rgb("#6d6a50")
        # self.floor_color = hex_to_rgb("#000000")

        self.ceil.fill(self.ceil_color)
        self.floor.fill(self.floor_color)

        # Default camera coordinates
        self.x0 = 0
        self.y0 = 0

    def set_fov(self, fov):
        self.fov = fov
        self.angles = [math.atan(i / self.ray_count * math.tan(fov / 2 * math.pi / 180)) * 180 / math.pi for i in
                       range(-self.ray_count, self.ray_count + 1)]  # Angle between camera orientation and each ray
        self.scales = [1 / math.cos(a * math.pi / 180) for a in self.angles]  # Scaling factor for each ray

    def set_ray_count(self, ray_count):
        self.ray_count = ray_count
        self.angles = [math.atan(i / self.ray_count * math.tan(self.fov / 2 * math.pi / 180)) * 180 / math.pi for i in
                       range(-self.ray_count, self.ray_count + 1)]  # Angle between camera orientation and each ray
        self.scales = [1 / math.cos(a * math.pi / 180) for a in self.angles]  # Scaling factor for each ray

    def generate_data(self, x0, y0, orient):
        self.x0 = x0
        self.y0 = y0

        # Generating rays' endpoints
        r = 1000000
        circle = [[r * math.sin((orient + self.angles[abs(i)] + 180) * math.pi / 180) + x0,
                   r * math.cos((orient + self.angles[abs(i)] + 180) * math.pi / 180) + y0]
                  for i in range(len(self.angles))]

        objects = (self.game_map.objects.sprites() +
                   self.game_map.enemies.sprites() +
                   self.game_map.projectiles.sprites())

        # Due to all objects being rectangles we can check only the collisions between rays and edges
        object_corners = []
        for obj in objects:
            object_corners.append(
                [[obj.x, obj.y], [obj.x + obj.width, obj.y],
                 [obj.x + obj.width, obj.y + obj.height],
                 [obj.x, obj.y + obj.height], obj])

        # We can disregard not visible corners filtering by the relative position of the camera to the object and
        # by the direction the camera is facing
        to_check = [[] for _ in range(len(objects))]
        # Checking camera's direction
        up = 0 <= (orient - self.fov / 2 + 90) % 360 <= 180 or 0 <= (orient + self.fov / 2 + 90) % 360 <= 180
        down = 0 <= (orient - self.fov / 2 + 270) % 360 <= 180 or 0 <= (orient + self.fov / 2 + 270) % 360 <= 180
        right = 0 <= (orient - self.fov / 2 + 180) % 360 <= 180 or 0 <= (orient + self.fov / 2 + 180) % 360 <= 180
        left = 0 <= (orient - self.fov / 2) % 360 <= 180 or 0 <= (orient + self.fov / 2) % 360 <= 180
        i = 0
        for obj in objects:
            obj_center = (obj.x + obj.width / 2, obj.y + obj.height / 2)
            # if object is not behind the camera
            if not ((not down) and obj.y > y0 or (not up) and obj.y + obj.height < y0 or (not left) and
                    obj.x + obj.width < x0 or (not right) and obj.x > x0):
                # checking on which edge is the camera looking
                if obj_center[0] - x0 > 0 and right:
                    to_check[i].append([3, 0])
                elif left:
                    to_check[i].append([1, 2])
                if obj_center[1] - y0 < 0 and up:
                    to_check[i].append([2, 3])
                elif down:
                    to_check[i].append([0, 1])
            n = len(to_check[i])
            # Check if edges are in the fov (actually if they are in front of the camera)
            if n == 1:
                if not (is_visible(object_corners[i][to_check[i][0][0]], [x0, y0], orient, self.fov) or
                        is_visible(object_corners[i][to_check[i][0][1]], [x0, y0], orient, self.fov)):
                    to_check[i] = []
            elif n > 1:
                tmp = [k for k in to_check[i][0] if k not in to_check[i][1]] + \
                      [k for k in to_check[i][1] if k not in to_check[i][0]]
                if not (is_visible(object_corners[i][tmp[0]], [x0, y0], orient, self.fov) or
                        is_visible(object_corners[i][tmp[1]], [x0, y0], orient, self.fov)):
                    to_check[i] = []
            i += 1
        return circle, object_corners, to_check

    def generate_rays(self, x0, y0, orient):
        circle, object_corners, to_check = self.generate_data(x0, y0, orient)
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
                    intersection = line_intersection(ray, edge)
                    # Intersections contains the collision point, the object and the angle between an edge and the ray
                    intersections.append([intersection, object_corners[j][4],
                                          angle_between_lines(pair[0], self.angles[i] + orient)])

                # One ray can only intersect one object once, so we're searching for the closest intersection
                if intersections:
                    collisions.append(min(intersections, key=lambda x: distance_no_sqrt([x0, y0], x[0])))
                j += 1

            collisions.sort(key=lambda x: distance_no_sqrt([x0, y0], x[0]))

            # We append to collisions_proper all the semitransparent collisions and an opaque one if there is any
            collisions_proper = []
            j = 0
            while j < len(collisions) and collisions[j][1].type == "semitransparent":
                collisions_proper.append(collisions[j])
                j += 1
            if j < len(collisions):
                collisions_proper.append(collisions[j])

            self.ray_collisions[i] = collisions_proper
            i += 1

    def draw_rays(self, all=0):
        # Draw the main ray and two rays on the boundary of the fov
        i = 0
        for i in range(len(self.ray_collisions)):
            collisions_proper = self.ray_collisions[i]
            if i == int(len(self.ray_collisions) / 2) or i == 0 or i == len(self.ray_collisions) - 1 or all:
                lines = []
                for_lines = [[[self.x0, self.y0], GameObject(0, self.game_map, 0, 0, 0, 0)]] + collisions_proper
                for j in range(len(for_lines) - 1):
                    lines.append([[for_lines[j][0][0] * self.game_map.scale + self.game_map.vector[0],
                                   for_lines[j][0][1] * self.game_map.scale + self.game_map.vector[1]],
                                  [for_lines[j + 1][0][0] * self.game_map.scale + self.game_map.vector[0],
                                   for_lines[j + 1][0][1] * self.game_map.scale + self.game_map.vector[1]],
                                  for_lines[j + 1][1]])

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

    def render(self):
        h = -40
        if self.over:
            self.game_map.screen.blit(self.bg, (0, 0))
            return
        # draw the ceiling and the floor
        self.game_map.screen.blit(self.ceil, (0, 0 + h))
        self.game_map.screen.blit(self.floor, (0, self.game_map.height / 2 + h))

        # 3D height scaling
        const = self.game_map.height * 50

        distances_normalised = [[[self.scales[i] * distance_inverse([self.x0, self.y0], self.ray_collisions[i][j][0]),
                                  self.ray_collisions[i][j][1], self.ray_collisions[i][j][2]]
                                 for j in range(len(self.ray_collisions[i]))]
                                for i in range(len(self.ray_collisions))]

        dw = self.width3d / len(distances_normalised)

        c = (0, 0, 0, 255)

        for i in range(len(distances_normalised)):
            for j in range(len(distances_normalised[i])):
                if j == 0:
                    # Do not apply the color blend on the first collision
                    c = distances_normalised[i][j][1].color
                elif j > 0:
                    c = combine_colors(c, distances_normalised[i][j][1].color)
                # Creating glare / differentiating the faces by the angle to the camera
                b = 12 / (j + 4) * max(0, min(255, abs(distances_normalised[i][j][2]) / 360 * 255))
                c = combine_colors([220 - b, 220 - b, 220 - b, 60], c)
                # Objects further away are darker
                b = 12 / (j + 4) * max(0, min(255, abs(1 / distances_normalised[i][j][0]) ** 2 / 7000))
                c = [max(max(0, i - 70), i - b / 4) for i in c]
                # Blending color with the floor and the ceiling
                if distances_normalised[i][j][1].type == "semitransparent":
                    cu = combine_colors(self.ceil_color + [60], c)
                    cd = combine_colors(self.floor_color + [60], c)

                    sat = 1.5
                    cu = saturation(cu, sat)
                    cd = saturation(cd, sat)
                    if not type(distances_normalised[i][j][1]) == Projectile or 1:
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
