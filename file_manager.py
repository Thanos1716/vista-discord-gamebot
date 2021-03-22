import math
import sqlite3
import numpy as np
from noise import snoise2  # pnoise2, ???
from PIL import Image

save_db_filepath = "saves/demo_world/world_data.db"
savename = "demo_world"


def get_temp(x, y):
    t_octaves = 8
    t_freq = 512
    return int(snoise2(x / t_freq, y / t_freq, t_octaves) * 128) + 127  # Temp


def get_elevation(x, y, x_max, y_max):
    e_octaves = 6
    e_freq = 32 * e_octaves
    grad_max = 191
    grad_min = 63
    max_dist = math.sqrt(x_max ** 2 + y_max ** 2)
    grad = int(grad_max - math.sqrt(
        ((((x_max / 2) - (x % x_max)) / max_dist) * ((grad_max - grad_min) * 2)) ** 2 + (
                (((y_max / 2) - (y % y_max)) / max_dist) * ((grad_max - grad_min) * 2)) ** 2))
    grad += int(snoise2(x / e_freq, y / e_freq, e_octaves) * 64)  # Elevation noise
    return grad


def get_humidity(x, y):
    h_octaves = 2
    h_freq = 256
    return int(snoise2(x / h_freq, y / h_freq, h_octaves) * 128) + 127  # Humidity


# def get_adjacent(x, y, img, rec):
#     img[x, y] = [30, rec*20, rec*20, 255]
#     found = 0
#     inds = 0
#     for i in range(-1, 2):
#         for j in range(-1, 2):
#             if get_elevation(x + j, y + i) < get_elevation(x, y) and rec > 0:
#                 if get_elevation(x + j, y + i) == min(min(
#                 get_elevation(x + k, y + l) for k in range(-1, 2)) for l in range(-1, 2)):
#                     get_adjacent(x + j, y + i, img, rec-1)
#                     print("Recursion", rec, end="\n")
#                     found += 1
#                 else:
#                     img[x + j, y + i] = [30, rec * 20, rec * 20, 255]
#                     print("Spread", end=" ")
#                     inds += 1
#     if found >= 1:
#         img[x, y] = [200, 200, 0, 255]
#
#     if inds >= 1:
#         img[x, y] = [255, 0, 255, 255]
#
#     if found >= 1 and inds >= 1:
#         img[x, y] = [0, 0, 0, 255]


def create_map(seed):
    y_max = 512
    x_max = y_max

    seed = list(str(seed))
    x_add, y_add = int(seed[0] + seed[1]) * x_max, int(seed[2] + seed[3]) * y_max
    seed = "".join(seed)

    arr = np.zeros([x_max, y_max, 4], dtype=np.uint8)
    arr[:, :, 3] = 255

    y_max, x_max = arr.shape[:2]

    for y in range(y_max):
        for x in range(x_max):
            val = [0, 0, 0, 255]

            temp = get_temp(x + x_add, y + y_add)  # Temp
            elevation = get_elevation(x + x_add, y + y_add, x_max, y_max)
            humidity = get_humidity(x + x_add, y + y_add)

            # if val[1] < 128:
            #     val = [0, 36, 69, 255]
            # elif val[0] > 128 and val[2] > 128:
            #     val = [67, 213, 82, 255]
            # elif val[0] > 128:
            #     val = [210, 194, 12, 255]
            # else:
            #     pass

            if elevation < 127:  # Ocean
                val = [0, 36, 69, 255]

            elif 148 > elevation and temp > 148:  # Beach
                val = [255, 191, 0, 255]

            elif elevation > 174 and temp < 88:  # Snow
                val = [255, 255, 255, 255]

            elif humidity + int(snoise2(x, y, 100) * 128 + 127) > 255:  # Trees
                val = [0, 63, 0, 255]  # [0, 63, 0, 255]

            else:
                val = [0, 127, 0, 255]

            if int(snoise2(x, y, 100) * 128 + 127) > 226 and elevation >= 127:  # Villages
                val = [0, 0, 0, 255]

            # if int(snoise2(x, y, 100) * 128 + 127) > 226 and elevation >= 175:  # Springs
            #     val = [255, 0, 0, 255]
            #     print("Elevation: " + str(elevation))

            if x == 245 and y == 245:
                val = [255, 0, 0, 255]

            # val = [temp, elevation, humidity, 255]

            for i in range(4):
                if val[i] > 255 or val[i] < 0:
                    pass
                    raise ValueError(f"List index out of range where x = {x} and y = {y}, val = {val}")

            # val = [elevation, 0, 0, 255]

            arr[y, x] = val

    # for y in range(y_max):
    #     for x in range(x_max):
    #         print(list(arr[y, x, :]))
    # if list(arr[y, x]) == [255, 0, 0, 255]:
    #     print(x, y)
    #     get_adjacent(x, y, arr, 19)

    img = Image.fromarray(arr, 'RGBA')
    img.save(f'saves/{savename}/{seed}.png')


def exec_sql(path, *code):
    try:
        with sqlite3.connect(path) as conn:
            cur = conn.cursor()
            rows = []

            for arguments in range(len(code)):
                cur.execute(code[arguments])
                rows += cur.fetchall()
            for x in range(len(rows)):
                for cols in range(len(rows)):
                    if len(rows[cols]) == 1:
                        rows[cols] = rows[cols][0]
                if len(rows) == 1:
                    rows = rows[0]
                conn.commit()

        return rows
    except sqlite3.Error as error:
        raise Exception(f"SQLError: {error} in code '{code}'")
