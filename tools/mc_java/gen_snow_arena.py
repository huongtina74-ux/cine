"""Snow castle arena: a hero location for the Bin & Bo war movie (vanilla Java datapack generator).

An original build in the "kingdom arena" genre:
  * round walled arena (r=62) with a dark stone band, crenellations, buttresses, lanterns and arrow slits,
  * 8 towers plus 2 taller gate towers: stone body, spruce lookout room with balcony, deepslate-tile spire,
  * lantern chains between tower tops, gate arch,
  * a castle keep on the south with a viewing balcony and corner turrets (the "leader on the balcony" shot),
  * snow plain, a frozen river with a bridge, hay fields, snowy spruce hills around everything,
  * a crowd of mannequins on the arena floor facing the balcony.

    python tools/mc_java/gen_snow_arena.py OUT_DIR
In game, in order: arena_ground, arena_hills_0..N, arena_build_0..N, arena_trees, arena_crowd
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_mountains import _hash, noise, smooth  # noqa: E402

AX, AZ, G = 700, 60, -60          # arena centre; G = first air layer of the superflat world (grass at G-1)
R_FLOOR, R_WALL0, R_WALL1 = 61, 62, 66
WALL_H = 12                       # walkway level = G + WALL_H
GATE_A = -90.0                    # north (-z)
HILL_R0, HILL_R1 = 100, 168
MAX_CMDS = 60000

V = {}


def put(x, y, z, b):
    V[(x, y, z)] = b


def ang(x, z, cx=AX, cz=AZ):
    return math.degrees(math.atan2(z - cz, x - cx))


def adiff(a, b):
    return abs((a - b + 180) % 360 - 180)


def facing_to(x, z, cx, cz):
    """Stair facing that points from (x,z) toward the centre (so the step goes down outward)."""
    dx, dz = cx - x, cz - z
    if abs(dx) >= abs(dz):
        return 'east' if dx > 0 else 'west'
    return 'south' if dz > 0 else 'north'


def disk(cx, cz, r):
    for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
        for z in range(math.floor(cz - r), math.ceil(cz + r) + 1):
            d = math.hypot(x - cx, z - cz)
            if d < r:
                yield x, z, d


def stone(x, y, z):
    h = _hash(x * 7 + y, z * 13 - y, 5)
    return 'cracked_stone_bricks' if h < .12 else 'mossy_stone_bricks' if h < .16 else 'stone_bricks'


def rough(x, y, z):
    h = _hash(x + y * 31, z - y * 17, 9)
    return ('cobblestone', 'stone_bricks', 'andesite', 'stone', 'cracked_stone_bricks')[int(h * 4.99)]


# ---------------------------------------------------------------- arena floor + wall
def arena():
    for x, z, d in disk(AX, AZ, R_FLOOR + 1):
        a = ang(x, z)
        b = 'polished_andesite'
        if d < 7:
            b = 'chiseled_stone_bricks' if d < 3 else 'polished_diorite'
        elif int(d) % 11 == 0:
            b = 'stone_bricks'
        elif min(adiff(a, k * 45 + 22.5) for k in range(8)) * d * math.pi / 180 < .9:
            b = 'polished_diorite'
        elif d > 57:
            b = 'stone_bricks'
        put(x, G - 1, z, b)
    for x, z, d in disk(AX, AZ, R_WALL1 + 3):
        if d < R_WALL0 - 1:
            continue
        a = ang(x, z)
        arc = a * math.pi / 180 * 64           # position along the wall in blocks
        gate = adiff(a, GATE_A) * math.pi / 180 * 64 <= 4.5
        if R_WALL0 - 1 <= d < R_WALL0:          # inner pilasters + low parapet
            if int(arc) % 7 == 0 and not gate:
                for y in range(G, G + WALL_H - 1):
                    put(x, y, z, 'polished_andesite')
                put(x, G + WALL_H - 1, z, 'stone_brick_slab[type=top]')
            if not gate:
                put(x, G + WALL_H, z, 'stone_brick_wall')
                if int(arc) % 9 == 0:
                    put(x, G + WALL_H + 1, z, 'lantern')
                if int(arc) % 7 == 3:                   # hanging banners between the pilasters
                    col = 'red' if int(arc) // 7 % 2 == 0 else 'yellow'
                    put(x, G + 9, z, f'{col}_wall_banner[facing={facing_to(x, z, AX, AZ)}]')
        elif R_WALL0 <= d < R_WALL1 - 1:        # core
            for y in range(G - 1, G + WALL_H):
                if gate and y < G + 9 and not (y == G + 8 and adiff(a, GATE_A) * math.pi / 180 * 64 > 3.5):
                    continue
                b = stone(x, y, z)
                if y == G + WALL_H - 1:
                    b = 'polished_andesite'
                    if not gate and _hash(x, z, 47) < .4:
                        put(x, G + WALL_H, z, 'snow')
                if gate and y >= G + 8:
                    b = 'chiseled_stone_bricks' if adiff(a, GATE_A) * math.pi / 180 * 64 < .8 else 'stone_bricks'
                put(x, y, z, b)
            if not gate:
                pass
        elif R_WALL1 - 1 <= d < R_WALL1:        # outer face + battlements
            top = G + WALL_H + 2 if int(arc) % 2 == 0 else G + WALL_H + 1
            for y in range(G - 1, top):
                if gate and y < G + 9 and not (y == G + 8 and adiff(a, GATE_A) * math.pi / 180 * 64 > 3.5):
                    continue
                b = stone(x, y, z)
                if y <= G + 1 or y == G + WALL_H - 1:
                    b = 'polished_andesite'
                if y == G + 9:
                    b = 'polished_deepslate'
                if y in (G + 5, G + 6) and int(arc) % 6 == 3 and not gate:
                    b = 'air'
                put(x, y, z, b)
            if not gate and int(arc) % 2 == 0:
                put(x, top, z, 'snow')
        elif not gate and int(arc) % 12 in (0, 1):  # buttresses
            if d < R_WALL1 + 1:
                top = G + 9
            elif d < R_WALL1 + 2:
                top = G + 5
            else:
                top = G + 2
            for y in range(G - 1, top):
                put(x, y, z, 'stone_bricks')
            put(x, top, z, 'stone_brick_slab')


# ---------------------------------------------------------------- towers
def spire(cx, cz, y0, r0, h, mat='deepslate_tile', dormers=True, flag='red_wool'):
    for k in range(h):
        rk = r0 * (1 - k / h) ** 1.15
        if rk < .6:
            put(round(cx), y0 + k, round(cz), f'{mat}s')
            continue
        for x, z, d in disk(cx, cz, rk):
            edge = d >= rk - 1.05
            put(x, y0 + k, z, f'{mat}_stairs[facing={facing_to(x, z, cx, cz)}]' if edge else f'{mat}s')
    for x, z, d in disk(cx, cz, r0 + .9):            # flared eave
        if d >= r0 - .1:
            put(x, y0, z, f'{mat}_slab')
    if dormers and r0 >= 6:                           # four little gable windows with a lit room behind
        rk = r0 * (1 - 3 / h) ** 1.15
        e = int(rk)
        icx, icz = round(cx), round(cz)
        for ax, az in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for lat in (-1, 0, 1):
                lx, lz = (0, lat) if ax else (lat, 0)
                bx, bz = icx + ax * e + lx, icz + az * e + lz
                for yy in (y0 + 2, y0 + 3):
                    put(bx, yy, bz, 'glass_pane' if lat == 0 else 'dark_oak_planks')
                put(bx, y0 + 4, bz, f'{mat}s' if lat == 0 else
                    f'{mat}_stairs[facing={"east" if lx + lz < 0 and ax == 0 else "west" if ax == 0 else "south" if lx + lz < 0 else "north"}]')
                put(bx, y0 + 1, bz, 'stripped_spruce_log')
            put(icx + ax * (e + 0) , y0 + 5, icz + az * (e + 0), f'{mat}_slab')
            put(icx + ax * (e - 1), y0 + 2, icz + az * (e - 1), 'shroomlight')
    ax0, az0 = round(cx), round(cz)
    put(ax0, y0 + h, az0, 'deepslate_tile_wall')
    for k in (1, 2, 3):
        put(ax0, y0 + h + k, az0, 'end_rod')
    put(ax0, y0 + h + 4, az0, 'lightning_rod')
    if flag:
        for fx in (1, 2, 3):
            for fy in (2, 3):
                put(ax0 + fx, y0 + h + fy, az0, flag)


def tower(cx, cz, body=22, r=6.0, spire_h=18, flag='red_wool'):
    top = G + body
    rib_a = [k * 45 + 22.5 for k in range(8)]
    win_a = [k * 90 + 45 for k in range(4)]
    for x, z, d in disk(cx, cz, r + 1.2):
        a = ang(x, z, cx, cz)
        if d >= r:                                    # plinth + ribs outside the body
            if d < r + 1:
                for y in range(G - 1, G + 3):
                    put(x, y, z, 'polished_andesite')
                put(x, G + 3, z, f'stone_brick_stairs[facing={facing_to(x, z, cx, cz)}]')
                if min(adiff(a, ra) for ra in rib_a) * d * math.pi / 180 < .7:
                    for y in range(G + 3, top - 3):
                        put(x, y, z, 'polished_andesite')
                    put(x, top - 3, z, f'stone_brick_stairs[facing={facing_to(x, z, cx, cz)}]')
            continue
        for y in range(G - 1, top):
            b = stone(x, y, z) if d >= r - 1.5 else 'stone_bricks'
            if y <= G + 2:
                b = 'polished_andesite'
            elif y <= G + 6 and d >= r - 1.5 and _hash(x * 3 + y, z, 41) < .35:
                b = 'mossy_stone_bricks'
            if y in (G + 10, G + body - 4) and d >= r - 1.5:
                b = 'polished_deepslate'
            put(x, y, z, b)
        if d >= r - 1.2:                              # framed windows, lit from inside
            arc_off = min(adiff(a, wa) for wa in win_a) * d * math.pi / 180
            for y0w in (G + 6, G + 14):
                if arc_off < 1.0:
                    put(x, y0w - 1, z, 'polished_andesite')
                    for yy in range(y0w, y0w + 3):
                        put(x, yy, z, 'glass_pane')
                    put(x, y0w + 3, z, 'chiseled_stone_bricks' if arc_off < .5 else 'polished_deepslate')
                elif arc_off < 1.8:
                    for yy in range(y0w - 1, y0w + 4):
                        put(x, yy, z, 'polished_andesite')
        elif r - 2.6 <= d < r - 1.2:
            a2 = min(adiff(a, wa) for wa in win_a) * d * math.pi / 180
            if a2 < 1.0:
                for y0w in (G + 6, G + 14):
                    put(x, y0w + 1, z, 'shroomlight')
    for x, z, d in disk(cx, cz, r + 1.6):            # machicolation teeth + balcony
        if d >= r - .2:
            a = ang(x, z, cx, cz)
            tooth = int(a * math.pi / 180 * d) % 2 == 0
            if d < r + .9:
                put(x, top - 1, z, f'stone_brick_stairs[facing={facing_to(x, z, cx, cz)},half=top]')
                if tooth:
                    put(x, top - 2, z, f'stone_brick_stairs[facing={facing_to(x, z, cx, cz)},half=top]')
            put(x, top, z, 'spruce_slab[type=top]')
            if d >= r + .6:
                put(x, top + 1, z, 'spruce_fence')
                if adiff(a, round(a / 45) * 45) < 5:
                    put(x, top + 2, z, 'lantern')
    room_r = r - 1
    for x, z, d in disk(cx, cz, room_r):              # timber-framed lookout room, glazed, lit
        put(x, top, z, 'spruce_planks')
        if d >= room_r - 1.1:
            a = ang(x, z, cx, cz)
            post = adiff(a, round(a / 45) * 45) < 9
            for y in range(top + 1, top + 6):
                if post:
                    b = 'stripped_spruce_log'
                elif y == top + 1:
                    b = 'dark_oak_planks'
                elif y in (top + 2, top + 3):
                    b = 'glass_pane'
                elif y == top + 4:
                    b = 'stripped_spruce_wood'
                else:
                    b = 'dark_oak_planks'
                put(x, y, z, b)
            if post:
                put(x, top + 4, z, 'gold_block')
        elif d < 1.0:
            put(x, top + 5, z, 'shroomlight')
        elif d < 2.2 and _hash(x, z, 43) < .3:
            put(x, top + 1, z, 'lantern')
    spire(cx, cz, top + 6, r + 1.5, spire_h, flag=flag)
    return top


def wall_point(a, r=64.0):
    return AX + r * math.cos(math.radians(a)), AZ + r * math.sin(math.radians(a))


def chain_between(p, q, y, sag=4):
    (x0, z0), (x1, z1) = p, q
    n = int(math.hypot(x1 - x0, z1 - z0) * 1.5) + 1
    axis = 'x' if abs(x1 - x0) >= abs(z1 - z0) else 'z'
    last = None
    for i in range(n + 1):
        t = i / n
        x, z = round(x0 + (x1 - x0) * t), round(z0 + (z1 - z0) * t)
        yy = round(y - sag * 4 * t * (1 - t))
        if (x, yy, z) == last:
            continue
        last = (x, yy, z)
        if (x, yy, z) not in V:
            put(x, yy, z, f'iron_chain[axis={axis}]')  # 1.21.9+ renamed chain -> iron_chain
            if i % 6 == 3 and (x, yy - 1, z) not in V:
                put(x, yy - 1, z, 'lantern[hanging=true]')


def towers():
    tops = []
    for k in range(1, 9):
        a = GATE_A + 40 * k
        cx, cz = wall_point(a)
        tops.append((a, (cx, cz), tower(cx, cz)))
    for s in (-1, 1):
        a = GATE_A + s * 11
        cx, cz = wall_point(a, 65)
        tops.append((a, (cx, cz), tower(cx, cz, body=27, r=6.5, spire_h=24)))
    tops.sort(key=lambda t: (t[0] - GATE_A) % 360)
    for (a0, p0, t0), (a1, p1, t1) in zip(tops, tops[1:] + tops[:1]):
        if adiff(a0, a1) < 30:     # the two gate towers: a lintel garland over the gate
            chain_between(p0, p1, min(t0, t1) + 1, sag=3)
            continue
        chain_between(p0, p1, min(t0, t1) + 1, sag=5)


# ---------------------------------------------------------------- keep with the balcony (south)
def keep():
    x0, x1, z0, z1 = AX - 20, AX + 20, AZ + 70, AZ + 96
    H = 30
    lit = []
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            shell = x in (x0, x0 + 1, x1 - 1, x1) or z in (z0, z0 + 1, z1 - 1, z1)
            for y in range(G - 1, G + H):
                if not shell and y not in (G - 1, G + H - 1):
                    continue
                b = rough(x, y, z) if shell else 'stone_bricks'
                if shell and y in (G + 8, G + 18) :
                    b = 'polished_deepslate'
                if shell and (x in (x0, x1) or z in (z0, z1)) and y % 10 in (3, 4, 5) and (x + z) % 4 == 0 and y > G + 1:
                    b = 'glass_pane'
                    if y % 10 == 4:
                        lit.append((x + (1 if x == x0 else -1 if x == x1 else 0), y,
                                    z + (1 if z == z0 else -1 if z == z1 else 0)))
                put(x, y, z, b)
            if shell and (x in (x0, x1) or z in (z0, z1)) and (x + z) % 2 == 0:
                put(x, G + H, z, 'stone_bricks')
    for p in lit:                                                  # light behind the keep windows
        put(*p, 'shroomlight')
    for cx, cz in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):      # corner turrets
        for x, z, d in disk(cx, cz, 5):
            for y in range(G - 1, G + H + 8):
                put(x, y, z, rough(x, y, z) if y > G + 2 else 'polished_andesite')
        spire(cx, cz, G + H + 8, 6, 14)
    for x, z, d in disk(AX, (z0 + z1) / 2, 8):                     # central donjon
        for y in range(G + H, G + H + 14):
            b = rough(x, y, z)
            if y == G + H + 6 and d > 6.8:
                b = 'polished_deepslate'
            put(x, y, z, b)
    spire(AX, (z0 + z1) / 2, G + H + 14, 9.5, 22)
    # balcony over the arena wall, carried on four piers
    by = G + 24
    for x in range(AX - 7, AX + 8):
        for z in range(AZ + 56, z0):
            put(x, by, z, 'polished_andesite' if (x + z) % 2 else 'stone_bricks')
            if x in (AX - 7, AX + 7) or z == AZ + 56:
                put(x, by + 1, z, 'stone_brick_wall')
                if (x - AX) % 7 == 0 and (z == AZ + 56 or (z - AZ) % 4 == 0):
                    put(x, by + 2, z, 'lantern')
            put(x, by - 1, z, 'stone_brick_slab[type=top]')
    for px in (AX - 6, AX + 6):
        for pz in (AZ + 57, AZ + 67):
            for y in range(G - 1, by - 1):
                for dx in (0, 1):
                    for dz in (0, 1):
                        if (px + dx, y, pz + dz) not in V or 'stone' not in V[(px + dx, y, pz + dz)]:
                            put(px + dx - (1 if px > AX else 0), y, pz + dz, rough(px, y, pz))
    for x in range(AX - 2, AX + 3):                                 # door from the keep
        for y in range(by + 1, by + 5):
            put(x, y, z0, 'air')
            put(x, y, z0 + 1, 'air')
    # banners of our own (plain colours, no emblems)
    for x in (AX - 4, AX + 4):
        for y in range(by - 6, by - 1):
            put(x, y, AZ + 55, 'red_wool' if y > by - 3 else 'yellow_wool')


# ---------------------------------------------------------------- outside: road, river, fields
def river_z(x):
    return AZ - 112 + 9 * math.sin((x - AX) / 23.0) + 4 * math.sin((x - AX) / 9.0)


def outside():
    for x in range(AX - 4, AX + 5):                      # road north from the gate
        for z in range(round(river_z(AX)) - 4, AZ - R_WALL1 + 1):
            put(x, G - 1, z, 'gravel' if abs(x - AX) < 3 else 'coarse_dirt')
            if abs(x - AX) == 4 and z % 8 == 0:
                put(x, G, z, 'spruce_fence')
                put(x, G + 1, z, 'spruce_fence')
                put(x, G + 2, z, 'lantern')
    for x in range(AX - HILL_R1, AX + HILL_R1 + 1):      # frozen river
        rz = river_z(x)
        for z in range(round(rz) - 5, round(rz) + 6):
            d = abs(z - rz)
            if d < 3.5:
                put(x, G - 1, z, 'ice')
                put(x, G - 2, z, 'water')
            elif d < 5:
                put(x, G - 1, z, 'packed_ice' if _hash(x, z, 3) < .5 else 'snow_block')
    rz = round(river_z(AX))
    for x in range(AX - 3, AX + 4):                      # bridge
        for z in range(rz - 6, rz + 7):
            put(x, G, z, 'spruce_planks')
            if abs(x - AX) == 3:
                put(x, G + 1, z, 'spruce_fence')
                if z % 4 == 0:
                    put(x, G + 2, z, 'lantern')
    for side in (-1, 1):                                 # hay fields between wall and river
        for fx in range(4):
            x0 = AX + side * (12 + fx * 15)
            for x in range(min(x0, x0 + side * 12), max(x0, x0 + side * 12) + 1):
                for z in range(AZ - 96, AZ - 72):
                    if math.hypot(x - AX, z - AZ) < R_WALL1 + 6:
                        continue
                    edge = x in (x0, x0 + side * 12) or z in (AZ - 96, AZ - 73)
                    if edge:
                        put(x, G, z, 'spruce_fence')
                    elif (z % 3) != 0:
                        put(x, G - 1, z, 'hay_block')


def hill_height(x, z):
    r = math.hypot(x - AX, z - AZ)
    if r < HILL_R0 or r > HILL_R1 + 4:
        return 0
    ring = smooth(HILL_R0, HILL_R0 + 22, r) * (1 - smooth(HILL_R1 - 10, HILL_R1 + 4, r))
    n = 0.75 * noise(x, z, 34, 101) + 0.25 * noise(x, z, 12, 103)
    h = ring * (4 + 34 * n ** 1.5)
    near_river = abs(z - river_z(x))
    h *= smooth(5, 16, near_river)                      # the river cuts a valley
    if abs(x - AX) < 6 and z < AZ:                      # and the road keeps its pass
        h *= smooth(4, 8, abs(x - AX))
    return max(0, round(h))


def hills():
    hm = {}
    for x in range(AX - HILL_R1 - 4, AX + HILL_R1 + 5):
        for z in range(AZ - HILL_R1 - 4, AZ + HILL_R1 + 5):
            h = hill_height(x, z)
            if h:
                hm[(x, z)] = h
    cmds, trees = [], []
    for (x, z), h in hm.items():
        nb = [hm.get((x + dx, z + dz), 0) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        slope = max(abs(h - v) for v in nb)
        y = G - 1 + h
        if h > 3:
            cmds.append(f'fill {x} {G} {z} {x} {y - 3} {z} stone')
        if h > 1:
            cmds.append(f'fill {x} {max(G, y - 2)} {z} {x} {y - 1} {z} {"stone" if slope >= 3 else "dirt"}')
        if 3 <= slope < 5:                              # snow sticks to all but the real cliffs
            cmds.append(f'setblock {x} {y} {z} snow_block')
        elif slope >= 5:
            p = noise(x, z, 6, 107)
            cmds.append(f'setblock {x} {y} {z} {"stone" if p < .45 else "andesite" if p < .75 else "snow_block"}')
        else:
            cmds.append(f'setblock {x} {y} {z} grass_block[snowy=true]')
            cmds.append(f'setblock {x} {y + 1} {z} snow')
            if slope <= 1 and _hash(x, z, 109) < .045:
                trees.append(f'place feature minecraft:spruce {x} {y + 1} {z}')
    return cmds, trees


# ---------------------------------------------------------------- crowd
COLORS = [0xB02E26, 0x3C44AA, 0xF9FFFE, 0x1D1D21, 0xFED83D, 0x5E7C16, 0x169C9C, 0x8932B8, 0xF9801D, 0x835432, 0x474F52, 0xC74EBD]


def crowd(n_max=2000):
    out = ['kill @e[type=mannequin,tag=arenacrowd]']
    bx, bz = AX, AZ + 60
    step = 2.15
    k = 0
    zz = AZ - 56.0
    while zz < AZ + 52 and k < n_max:
        xx = AX - 56.0 + (_hash(int(zz * 10), 1, 7) * step)
        while xx < AX + 56:
            jx = xx + (_hash(int(xx * 10), int(zz * 10), 11) - .5) * 1.2
            jz = zz + (_hash(int(xx * 10), int(zz * 10), 13) - .5) * 1.2
            aisle = abs(jx - AX) < 2.6 or math.hypot(jx - AX, jz - AZ) < 5   # clear aisle gate -> balcony
            if math.hypot(jx - AX, jz - AZ) < R_FLOOR - 4 and not aisle and k < n_max:
                yaw = math.degrees(math.atan2(-(bx - jx), (bz - jz))) + (_hash(k, 3, 17) - .5) * 30
                c1 = COLORS[int(_hash(k, 5, 19) * len(COLORS)) % len(COLORS)]
                c2 = COLORS[int(_hash(k, 6, 23) * len(COLORS)) % len(COLORS)]
                eq = f'chest:{{id:"leather_chestplate",components:{{"minecraft:dyed_color":{c1}}}}},legs:{{id:"leather_leggings",components:{{"minecraft:dyed_color":{c2}}}}}'
                if _hash(k, 8, 29) < .3:
                    eq += ',head:{id:"iron_helmet"}'
                sc = .92 + _hash(k, 9, 31) * .12
                out.append(f'summon mannequin {jx:.2f} {G} {jz:.2f} {{Tags:["arenacrowd"],hide_description:1b,immovable:1b,'
                           f'Rotation:[{yaw:.0f}f,0f],equipment:{{{eq}}},attributes:[{{id:"minecraft:scale",base:{sc:.2f}}}]}}')
                k += 1
            xx += step
        zz += step * .9
    # the leader on the balcony + the cast
    out.append(f'summon mannequin {AX + .5} {G + 25} {AZ + 58.5} {{Tags:["arenacrowd"],profile:{{texture:"binbo:entity/cast/bin"}},'
               f'CustomName:"Bin",CustomNameVisible:1b,hide_description:1b,immovable:1b,Rotation:[180f,0f]}}')
    out.append(f'summon mannequin {AX - 1.5} {G + 25} {AZ + 60} {{Tags:["arenacrowd"],profile:{{texture:"binbo:entity/cast/bo"}},'
               f'hide_description:1b,immovable:1b,Rotation:[170f,0f]}}')
    out.append(f'summon mannequin {AX + 2.3} {G + 25} {AZ + 60} {{Tags:["arenacrowd"],profile:{{texture:"binbo:entity/cast/zu"}},'
               f'hide_description:1b,immovable:1b,Rotation:[190f,0f],attributes:[{{id:"minecraft:scale",base:0.72}}]}}')
    return out, k


# ---------------------------------------------------------------- output
def compress(vox):
    cols = {}
    for (x, y, z), b in vox.items():
        cols.setdefault((x, z), []).append((y, b))
    runs = []
    for (x, z), lst in cols.items():
        lst.sort()
        y0, b0, yp = lst[0][0], lst[0][1], lst[0][0]
        for y, b in lst[1:] + [(None, None)]:
            if y is not None and y == yp + 1 and b == b0:
                yp = y
                continue
            runs.append((z, y0, yp, b0, x))
            if y is not None:
                y0, b0, yp = y, b, y
    runs.sort()
    cmds, i = [], 0
    while i < len(runs):
        z, y0, y1, b, x0 = runs[i]
        x1 = x0
        while i + 1 < len(runs) and runs[i + 1][:4] == (z, y0, y1, b) and runs[i + 1][4] == x1 + 1:
            i += 1
            x1 += 1
        if (x0, y0) == (x1, y1):
            cmds.append(f'setblock {x0} {y0} {z} {b}')
        else:
            cmds.append(f'fill {x0} {y0} {z} {x1} {y1} {z} {b}')
        i += 1
    return cmds


def forceload():
    x0, x1, z0, z1 = AX - HILL_R1 - 4, AX + HILL_R1 + 4, AZ - HILL_R1 - 4, AZ + HILL_R1 + 4
    out, step = [], 120
    for a in range(x0, x1 + 1, step):
        for b in range(z0, z1 + 1, step):
            out.append(f'forceload add {a} {b} {min(a + step - 1, x1)} {min(b + step - 1, z1)}')
    return out


def ground():
    out = []
    x0, x1, z0, z1 = AX - HILL_R1 - 4, AX + HILL_R1 + 4, AZ - HILL_R1 - 4, AZ + HILL_R1 + 4
    for a in range(x0, x1 + 1, 40):
        for b in range(z0, z1 + 1, 40):
            out.append(f'fill {a} {G - 1} {b} {min(a + 39, x1)} {G - 1} {min(b + 39, z1)} snow_block replace grass_block')
    return out


def clear_hills():
    """Air above the hill ring, so a re-run never leaves old peaks behind (re-run arena_build_0 afterwards)."""
    out, s = [], 16
    for a in range(AX - HILL_R1 - 4, AX + HILL_R1 + 5, s):
        for b in range(AZ - HILL_R1 - 4, AZ + HILL_R1 + 5, s):
            nx = min(max(AX, a), a + s - 1)
            nz = min(max(AZ, b), b + s - 1)
            if math.hypot(nx - AX, nz - AZ) > HILL_R0 - 4:
                out.append(f'fill {a} {G} {b} {a + s - 1} {G + 50} {b + s - 1} air')
    return out


def chunks(cmds, n):
    return [cmds[i:i + n] for i in range(0, len(cmds), n)] or [[]]


def build_all():
    V.clear()
    arena()
    towers()
    keep()
    outside()
    build = compress(V)
    hill_cmds, trees = hills()
    crowd_cmds, n = crowd()
    files = {'arena_ground': forceload() + ground() + clear_hills()}
    for i, part in enumerate(chunks(hill_cmds, 45000)):
        files[f'arena_hills_{i}'] = forceload() + part
    for i, part in enumerate(chunks(build, 45000)):
        files[f'arena_build_{i}'] = forceload() + part
    files['arena_trees'] = forceload() + trees
    files['arena_crowd'] = crowd_cmds
    return files, n


def write(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    files, n = build_all()
    for name, cmds in files.items():
        assert len(cmds) < MAX_CMDS, (name, len(cmds))
        with open(os.path.join(out_dir, name + '.mcfunction'), 'w', encoding='utf-8') as f:
            f.write('# generated by tools/mc_java/gen_snow_arena.py\n' + '\n'.join(cmds) + '\n')
    return {k: len(v) for k, v in files.items()}, n


if __name__ == '__main__':
    counts, n = write(sys.argv[1] if len(sys.argv) > 1 else 'arena_out')
    print('ARENA_OK', counts, 'crowd', n, 'blocks', len(V))
