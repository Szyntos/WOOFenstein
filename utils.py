def distance_inverse(p1, p2):
    # return distance_2(p1, p2)
    a = ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
    if a == 0:
        return 0.00001 ** -0.5
    return a ** -0.5


def is_visible(point, camera, orient, fov):
    # Check if the point is in the fov (actually if they are in front of the camera)
    vec = [point[0] - camera[0], point[1] - camera[1]]
    a = ((DiamondAngle(vec[0], vec[1]) - 2) * 90) % 360
    acc = 5
    return 10 - acc <= (a - orient + fov / 2 + 10) % 360 <= 10 + 180 + acc


def distance_no_sqrt(p1, p2):
    # return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2
    # return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    if p1[0] > p2[0]:
        if p1[1] > p2[1]:
            return p1[0] - p2[0] + p1[1] - p2[1]
        return p1[0] - p2[0] + p2[1] - p1[1]
    if p1[1] > p2[1]:
        return p2[0] - p1[0] + p1[1] - p2[1]
    return p2[0] - p1[0] + p2[1] - p1[1]


def distance_2(p1, p2):
    # Copied from the Doom wiki
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


def angle_between_lines(edge_index, angle):
    # Old, computationally expensive code

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

    # Every edge is perpendicular, and we know the angle of the ray, so we can easily
    # calculate the angle between an edge and the ray
    a = (90 * abs(edge_index - 1) - angle) % 180 - 90
    return a


def is_between(x, a, b):
    eps = 0.001
    tmp = b
    b = max(a, b)
    a = min(a, tmp)
    if a - eps <= x <= b + eps:
        return 1
    return 0


def same_direction(p, q):
    dif_x_p = (p[1][0] - p[0][0])
    dif_y_p = (p[1][1] - p[0][1])
    dif_x_q = (q[0] - q[0][0])
    dif_y_q = (q[1] - q[0][1])
    if dif_x_p * dif_x_q >= 0 and dif_y_p * dif_y_q >= 0:
        return 1
    return 0


def approx_equals(a, b):
    eps = 0.0001
    if b - eps < a < b + eps:
        return 1
    return 0


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
    # atan2 approximation, yields values form [0, 4]
    if y >= 0:
        return y / (x + y) if x >= 0 else 1 - x / (-x + y)
    else:
        return 2 - y / (-x - y) if x < 0 else 3 + x / (x - y)


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
