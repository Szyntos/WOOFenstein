import math
import pygame

from src.blocks import GameObject
from src.map import GameMap
from src.moveable import Projectile
import src.utils as utils


class Intersection:
    def __init__(self, point: utils.Point, obj, angle: float = 0):
        self.point = point
        self.object = obj
        self.angle = angle

    def distance(self, point: utils.Point) -> float:
        return utils.distance_no_sqrt(point, self.point)


class RayLine:
    def __init__(self, point1: utils.Point, point2: utils.Point,
                 obj: GameObject):
        self.point1 = point1
        self.point2 = point2
        self.object = obj


class Renderer:
    def _create_angles(self) -> list[float]:
        """ Angle between camera orientation and each ray. """
        angles = []
        for i in range(-self.ray_count, self.ray_count + 1):
            alpha = self.fov / 2 * math.pi / 180
            beta = i / self.ray_count * math.tan(alpha)
            angle = math.atan(beta) * 180 / math.pi
            angles.append(angle)
        return angles

    def _create_scales(self) -> list[float]:
        """ Scaling factor for each ray. """
        return [1 / math.cos(a * math.pi / 180) for a in self.angles]

    def _init_bg(self):
        self.bg = pygame.Surface((self.width3d, self.game_map.height))
        self.bg.fill((0, 0, 0))

    def _init_ceil(self):
        self.ceil = pygame.Surface((self.width3d, self.game_map.height / 2))
        self.ceil_color = utils.hex_to_rgb("#97b4b7")
        # self.ceil_color = hex_to_rgb("#000000")
        self.ceil.fill(self.ceil_color)

    def _init_floor(self):
        filename = "./img/floor.jpg"
        self.floor = pygame.image.load(filename).convert()
        self.floor = pygame.transform.scale(self.floor,
                                            (self.width3d, self.game_map.height / 2))
        self.floor.set_colorkey("BLACK")
        # self.floor = pygame.Surface((self.width3d, self.game_map.height / 2))
        self.floor_color = utils.hex_to_rgb("#6d6a50")
        # self.floor_color = hex_to_rgb("#000000")
        # self.floor.fill(self.floor_color)

    def __init__(self, game_map: GameMap, width3d: float, fov: float, ray_count: int):
        self.width3d = width3d
        self.game_map = game_map
        self.fov = fov
        self.ray_count = ray_count  # Actual number of rays is 2*ray_count-1
        self.ray_collisions = []
        self.obj_col = []
        self.over = 0
        self.angles = self._create_angles()
        self.scales = self._create_scales()
        self._init_bg()
        self._init_ceil()
        self._init_floor()
        # Default camera coordinates
        self.cam_position = utils.Point(0, 0)

    def set_fov(self, fov: float):
        self.fov = fov
        self.angles = self._create_angles()
        self.scales = self._create_scales()

    def set_ray_count(self, ray_count: int):
        self.ray_count = ray_count
        self.angles = self._create_angles()
        self.scales = self._create_scales()

    def _create_circle(self, orient: float, r: float = 1000000) -> list[utils.Point]:
        circle = []
        for i in range(len(self.angles)):
            alpha = (orient + self.angles[abs(i)] + 180) * math.pi / 180
            x = r * math.sin(alpha) + self.cam_position.x
            y = r * math.cos(alpha) + self.cam_position.y
            circle.append(utils.Point(x, y))
        return circle

    def _get_objects(self) -> list:  # list[_TSprite]
        return (self.game_map.objects.sprites() +
                self.game_map.enemies.sprites() +
                self.game_map.projectiles.sprites() +
                self.game_map.objectives.sprites())

    def _get_corners(self, objects: list) -> list[list[utils.Point]]:
        corners = []
        for obj in objects:
            current_corners = [
                    utils.Point(obj.x, obj.y), utils.Point(obj.x + obj.width, obj.y),
                    utils.Point(obj.x + obj.width, obj.y + obj.height),
                    utils.Point(obj.x, obj.y + obj.height)
                ]
            corners.append(current_corners)
        return corners

    def _camera_direction(self, orient: float) -> utils.Direction:
        alpha = orient - self.fov / 2
        beta = orient + self.fov / 2
        up = 0 <= (alpha + 90) % 360 <= 180 or 0 <= (beta + 90) % 360 <= 180
        down = 0 <= (alpha + 270) % 360 <= 180 or 0 <= (beta + 270) % 360 <= 180
        right = 0 <= (alpha + 180) % 360 <= 180 or 0 <= (beta + 180) % 360 <= 180
        left = 0 <= alpha % 360 <= 180 or 0 <= beta % 360 <= 180
        return utils.Direction(up, down, right, left)

    def _is_behind_camera(self, obj, cam_direction: utils.Direction) -> bool:
        position = self.cam_position
        return not (
            (not cam_direction.down) and obj.y > position.y or
            (not cam_direction.up) and obj.y + obj.height < position.y or
            (not cam_direction.left) and obj.x + obj.width < position.x or
            (not cam_direction.right) and obj.x > position.x
        )

    def move_player(self, x0: float, y0: float):
        self.cam_position = utils.Point(x0, y0)

    def move_camera(self, x0: float, y0: float, orient: float):
        self.cam_position = utils.Point(x0, y0)
        # Generating rays' endpoints
        circle = self._create_circle(orient)
        objects = self._get_objects()
        # Due to all objects being rectangles we can check only the collisions between rays and edges
        all_corners = self._get_corners(objects)
        # We can disregard not visible corners filtering by the relative position of the camera to the object and
        # by the direction the camera is facing
        corners_to_check = []
        # Checking camera's direction
        cam_direction = self._camera_direction(orient)
        for i, obj in enumerate(objects):
            obj_center = utils.Point(obj.x + obj.width / 2, obj.y + obj.height / 2)
            checked_corners = []
            corners = all_corners[i]
            # if object is not behind the camera
            if self._is_behind_camera(obj, cam_direction):
                # checking on which edge is the camera looking
                if obj_center.x - self.cam_position.x > 0 and cam_direction.right:
                    checked_corners.append([3, 0])
                elif cam_direction.left:
                    checked_corners.append([1, 2])
                if obj_center.y - self.cam_position.y < 0 and cam_direction.up:
                    checked_corners.append([2, 3])
                elif cam_direction.down:
                    checked_corners.append([0, 1])
            n = len(checked_corners)
            # Check if edges are in the fov (actually if they are in front of the camera)
            if n == 1:
                corner1 = corners[checked_corners[0][0]]
                corner2 = corners[checked_corners[0][1]]
                if not (utils.is_visible(corner1, self.cam_position, orient, self.fov) or
                        utils.is_visible(corner2, self.cam_position, orient, self.fov)):
                    checked_corners = []
            elif n > 1:
                tmp = [k for k in checked_corners[0] if k not in checked_corners[1]] + \
                      [k for k in checked_corners[1] if k not in checked_corners[0]]
                corner1 = corners[tmp[0]]
                corner2 = corners[tmp[1]]
                if not (utils.is_visible(corner1, self.cam_position, orient, self.fov) or
                        utils.is_visible(corner2, self.cam_position, orient, self.fov)):
                    checked_corners = []
            corners_to_check.append(checked_corners)
        return objects, circle, all_corners, corners_to_check

    def generate_rays(self, x0, y0, orient):
        objects, circle, object_corners, to_check = self.move_camera(x0, y0, orient)
        point0 = utils.Point(x0, y0)
        self.ray_collisions = [[] for _ in circle]
        for i, point in enumerate(circle):
            ray = [point0, point]
            collisions = []
            for j, obj_corner_pairs in enumerate(to_check):
                intersections = []
                for corner1, corner2 in obj_corner_pairs:
                    edge = [object_corners[j][corner1], object_corners[j][corner2]]
                    intersection_point = utils.line_intersection(ray, edge)
                    angle = utils.angle_between_lines(corner1, self.angles[i] + orient)
                    intersection = Intersection(intersection_point, objects[j], angle)
                    intersections.append(intersection)
                # One ray can only intersect one object once, so we're searching for the closest intersection
                if intersections:
                    closest = min(intersections, key=lambda x: x.distance(point0))
                    collisions.append(closest)

            collisions.sort(key=lambda x: x.distance(point0))

            # We append to collisions_proper all the semitransparent collisions and an opaque one if there is any
            collisions_proper = []
            for collision in collisions:
                collisions_proper.append(collision)
                if collision.object.type != "semitransparent":
                    break

            self.ray_collisions[i] = collisions_proper

    def draw_rays(self, all=0):
        # Draw the main ray and two rays on the boundary of the fov
        collisions = len(self.ray_collisions)
        for i, collisions_proper in enumerate(self.ray_collisions):
            if i == int(collisions / 2) or i == 0 or i == collisions - 1 or all:
                lines = []
                obj0 = GameObject(0, self.game_map, 0, 0, 0, 0)
                points_with_0 = [self.cam_position] + [inter.point for inter in collisions_proper]
                objects_with_0 = [obj0] + [inter.object for inter in collisions_proper]
                for j in range(len(points_with_0) - 1):
                    current = points_with_0[j + 1]
                    last = points_with_0[j]
                    point1 = utils.Point(
                        last.x * self.game_map.scale + self.game_map.vector[0],
                        last.y * self.game_map.scale + self.game_map.vector[1]
                    )
                    point2 = utils.Point(
                        current.x * self.game_map.scale + self.game_map.vector[0],
                        current.y * self.game_map.scale + self.game_map.vector[1]
                    )
                    lines.append(RayLine(point1, point2, objects_with_0[j + 1]))

                # c = (255, 0, 0, 120)
                c = (255, 255, 255, 1)
                for j, line in enumerate(lines):
                    if j > 0:
                        c = utils.combine_colors(lines[j - 1].object.color, c)
                    size = 1
                    if i == int(collisions / 2):
                        size = 3
                    pygame.draw.line(self.game_map.screen, pygame.Color(c),
                                     line.point1, line.point2, size)

    def draw_visible_edges(self, x0, y0, orient):
        _, _, object_corners, to_check = self.move_camera(x0, y0, orient)
        for j, obj_corner_pairs in enumerate(to_check):
            for corner1, corner2 in obj_corner_pairs:
                edge = [object_corners[j][corner1], object_corners[j][corner2]]
                pygame.draw.line(self.game_map.screen, pygame.Color(222, 222, 222, 255),
                                 [edge[0][0] * self.game_map.scale + self.game_map.vector[0],
                                  edge[0][1] * self.game_map.scale + self.game_map.vector[1]],
                                 [edge[1][0] * self.game_map.scale + self.game_map.vector[0],
                                  edge[1][1] * self.game_map.scale + self.game_map.vector[1]], 1)

    def _get_normalised_distances(self):
        distances = []
        for i, current_collisions in enumerate(self.ray_collisions):
            row = []
            for collision in current_collisions:
                inverse_distance = utils.distance_inverse(self.cam_position, collision.point)
                cell = [self.scales[i] * inverse_distance,
                        collision.object, collision.angle]
                row.append(cell)
            distances.append(row)
        return distances

    def render(self):
        h = -40
        # draw the ceiling and the floor
        self.game_map.screen.blit(self.ceil, (0, 0 + h))
        self.game_map.screen.blit(self.floor, (0, self.game_map.height / 2 + h))

        # 3D height scaling
        const = self.game_map.height * 70

        distances_normalised = self._get_normalised_distances()

        dw = self.width3d / len(distances_normalised)

        c = (0, 0, 0, 255)
        for i, current_distances in enumerate(distances_normalised):
            for j, distance in enumerate(current_distances):
                if j == 0:
                    # Do not apply the color blend on the first collision
                    c = distance[1].color
                elif j > 0:
                    c = utils.combine_colors(c, distance[1].color)
                # Creating glare / differentiating the faces by the angle to the camera
                b = 12 / (j + 4) * max(0, min(255, abs(distance[2]) / 360 * 255))
                c = utils.combine_colors([220 - b, 220 - b, 220 - b, 60], c)
                # Objects further away are darker
                b = 12 / (j + 4) * max(0, min(255, abs(1 / distance[0]) ** 3 / 10000000))
                c = [max(max(0, i - 70), i - b / 4) for i in c]
                # Blending color with the floor and the ceiling
                if distance[1].type == "semitransparent":
                    cu = utils.combine_colors(self.ceil_color + [60], c)
                    cd = utils.combine_colors(self.floor_color + [60], c)

                    sat = 1.5
                    cu = utils.saturation(cu, sat)
                    cd = utils.saturation(cd, sat)
                    if not type(distance[1]) == Projectile:
                        up = pygame.Rect(
                            self.width3d - (i + 1) * dw,
                            self.game_map.height / 2 - (const * (distance[0])) / 2 + h,
                            dw + 1,
                            const * (distance[0]) / 2)
                        pygame.draw.rect(self.game_map.screen, pygame.Color(cu), up)
                    down = pygame.Rect(
                        self.width3d - (i + 1) * dw,
                        self.game_map.height / 2 - 1 + h,
                        dw + 1,
                        const * distance[0] / 2)
                    pygame.draw.rect(self.game_map.screen, pygame.Color(cd), down)
                else:
                    box = pygame.Rect(
                        self.width3d - (i + 1) * dw,
                        self.game_map.height / 2 -
                        (const * (distance[0])) / 2 + h,
                        dw + 1,
                        const * (distance[0]))
                    pygame.draw.rect(self.game_map.screen, pygame.Color(c), box)
