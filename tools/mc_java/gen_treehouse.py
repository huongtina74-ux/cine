"""Hero set for the pilot: a giant treehouse fortress on a hill above a ruined, zombie-filled town.

Original build (vanilla Java blocks only):
  * a hill with grass, coarse dirt and rock outcrops;
  * one colossal tree: flared roots, tapered trunk of bark blocks, six big branches, noisy leaf crowns
    (persistent leaves, so nothing decays);
  * three ring decks with railings, lanterns and little spruce huts, a spiral stair round the trunk,
    rope bridges out to two branch lookouts, a lit crow's nest at the top;
  * a log palisade with watchtowers, a gate and spike pits round the hilltop;
  * a ruined town in a ring below: broken stone houses, a toppled church tower, campfires, dead trees;
  * a horde of vanilla zombies (no AI, persistent) pressed against the palisade, plus Bin, Bo and Zu.

    python tools/mc_java/gen_treehouse.py OUT_DIR
In game, in order: tree_ground, tree_build_0..N, tree_cast
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_mountains import _hash, noise, smooth  # noqa: E402
from gen_snow_arena import compress, disk, facing_to  # noqa: E402

TX, TZ, G = 1100, 60, -60          # tree centre; G = first air layer of the superflat world
HILL_R, HILL_H = 62, 16
PAL_R = 40                         # palisade radius
TOWN_R0, TOWN_R1 = 62, 112
MAX_CMDS = 60000
V = {}


def put(x, y, z, b):
    V[(round(x), round(y), round(z))] = b


def hill_h(x, z):
    r = math.hypot(x - TX, z - TZ)
    if r > HILL_R:
        return 0
    base = HILL_H * (1 - smooth(8, HILL_R, r))
    return max(0, round(base + 2.5 * (noise(x, z, 9, 201) - .5) * (r > 10)))


def top(x, z):
    return G - 1 + hill_h(x, z)


# ---------------------------------------------------------------- hill
def hill():
    cmds = []
    for x in range(TX - HILL_R, TX + HILL_R + 1):
        for z in range(TZ - HILL_R, TZ + HILL_R + 1):
            h = hill_h(x, z)
            if h <= 0:
                continue
            y = G - 1 + h
            p = noise(x, z, 5, 203)
            cmds.append(f'fill {x} {G} {z} {x} {y - 1} {z} {"stone" if p < .2 else "dirt"}')
            cmds.append(f'setblock {x} {y} {z} {"coarse_dirt" if p > .78 else "rooted_dirt" if p > .72 else "grass_block"}')
    for k in range(9):                                   # rock outcrops
        a = k * 40 + 13
        cx, cz = TX + 48 * math.cos(math.radians(a)), TZ + 48 * math.sin(math.radians(a))
        for x, z, d in disk(cx, cz, 3.5):
            for y in range(top(x, z) - 1, top(x, z) + round(3 - d)):
                cmds.append(f'setblock {x} {y} {z} {"mossy_cobblestone" if _hash(x, y, 7) < .4 else "andesite"}')
    return cmds


# ---------------------------------------------------------------- tree
BARK = 'oak_wood'
LEAF = ['oak_leaves[persistent=true]', 'dark_oak_leaves[persistent=true]', 'azalea_leaves[persistent=true]']
Y0 = G - 1 + HILL_H                    # ground at the trunk
TRUNK_H = 78


def trunk_r(dy):
    return 8.5 - 4.8 * smooth(0, TRUNK_H, dy)


def tree():
    for dy in range(-2, TRUNK_H):                        # tapered trunk with bark noise
        r = trunk_r(dy)
        for x, z, d in disk(TX, TZ, r + .5):
            if d < r or _hash(x, z + dy, 11) < .3 and d < r + .5:
                put(x, Y0 + dy, z, 'dark_oak_wood' if _hash(x * 3, dy, z) < .25 else BARK)
    for k in range(7):                                   # flared roots
        a = math.radians(k * 51.4 + 9)
        for s in range(0, 15):
            rx, rz = TX + (5 + s) * math.cos(a), TZ + (5 + s) * math.sin(a)
            ry = Y0 + 5 - s * .55
            for x, z, d in disk(rx, rz, 1.9 - s * .09):
                for y in range(top(x, z) - 1, round(ry) + 1):
                    put(x, y, z, BARK)
    crowns = []
    for k, (ang_, h0, ln, rise) in enumerate(((20, 38, 26, 10), (140, 44, 24, 12), (250, 40, 27, 10),
                                               (75, 56, 20, 10), (200, 60, 19, 12), (320, 52, 22, 10),
                                               (290, 66, 15, 9), (110, 68, 15, 9))):
        a = math.radians(ang_)
        steps = int(ln * 1.6)
        for s in range(steps + 1):                       # branch: thick to thin, curving up
            t = s / steps
            bx = TX + (3 + ln * t) * math.cos(a)
            bz = TZ + (3 + ln * t) * math.sin(a)
            by = Y0 + h0 + rise * t * t
            for x, z, d in disk(bx, bz, 2.2 - 1.2 * t):
                for y in range(round(by - 1.2 + t), round(by + 1.2 - t) + 1):
                    put(x, y, z, BARK)
        crowns.append((TX + (3 + ln) * math.cos(a), Y0 + h0 + rise + 3, TZ + (3 + ln) * math.sin(a), 13 + k % 4))
        for s2 in range(3, steps, 7):                    # lanterns hanging from the branch on chains
            t = s2 / steps
            hx, hz = TX + (3 + ln * t) * math.cos(a), TZ + (3 + ln * t) * math.sin(a)
            hy = round(Y0 + h0 + rise * t * t) - 2
            put(hx, hy, hz, 'iron_chain[axis=y]')
            put(hx, hy - 1, hz, 'lantern[hanging=true]')
    crowns.append((TX, Y0 + TRUNK_H + 5, TZ, 18))
    for cx, cy, cz, rr in crowns:                        # leaf crowns: lumpy spheres
        for x in range(round(cx - rr - 3), round(cx + rr + 4)):
            for z in range(round(cz - rr - 3), round(cz + rr + 4)):
                for y in range(round(cy - rr * .6), round(cy + rr * .75)):
                    d = math.sqrt((x - cx) ** 2 + ((y - cy) * 1.5) ** 2 + (z - cz) ** 2)
                    lim = rr * (.78 + .38 * noise(x * 1.0, z + y * 3.1, 4, 217))
                    if d < lim and (x, y, z) not in V:
                        V[(x, y, z)] = LEAF[int(_hash(x // 3, z // 3 + y, 223) * 2.6) % 3]
                        if d > lim - 1.2 and _hash(x, y * 7, z) < .02 and y < cy:
                            put(x, y - 1, z, 'cave_vines[berries=true]')
                            put(x, y - 2, z, 'cave_vines_plant[berries=true]')
    return crowns


# ---------------------------------------------------------------- decks, huts, stair, bridges
def deck(y, r_in, r_out):
    for x, z, d in disk(TX, TZ, r_out):
        if d < trunk_r(y - Y0) + .3:
            continue
        put(x, y, z, 'spruce_planks' if (x + z) % 5 else 'stripped_spruce_wood')
        if d >= r_out - 1.05:
            put(x, y + 1, z, 'spruce_fence')
            if _hash(x, z, y) < .12:
                put(x, y + 2, z, 'lantern')
        if r_out - 2.2 < d < r_out - 1 and _hash(x, z, y + 1) < .08:      # corbel braces
            put(x, y - 1, z, f'spruce_stairs[facing={facing_to(x, z, TX, TZ)},half=top]')
    for k in range(8):                                   # diagonal struts down to the trunk
        a = math.radians(k * 45 + 22)
        for s in range(6):
            sx = TX + (r_out - 1.5 - s * .9) * math.cos(a)
            sz = TZ + (r_out - 1.5 - s * .9) * math.sin(a)
            put(sx, y - 1 - s, sz, 'stripped_spruce_log')


def hut(cx, cy, cz, w=3, face='south'):
    for x in range(cx - w, cx + w + 1):
        for z in range(cz - w, cz + w + 1):
            edge = abs(x - cx) == w or abs(z - cz) == w
            corner = abs(x - cx) == w and abs(z - cz) == w
            for y in range(cy + 1, cy + 5):
                if corner:
                    put(x, y, z, 'stripped_spruce_log')
                elif edge:
                    win = y in (cy + 2, cy + 3) and (abs(x - cx) == 1 or abs(z - cz) == 1)
                    put(x, y, z, 'glass_pane' if win else 'spruce_planks')
        put(cx, cy + 1, cz, 'lantern')
    for k in range(w + 2):                               # pyramid roof of stairs
        yy = cy + 5 + k
        rr = w + 1 - k
        if rr < 0:
            break
        for x in range(cx - rr, cx + rr + 1):
            for z in range(cz - rr, cz + rr + 1):
                if max(abs(x - cx), abs(z - cz)) == rr:
                    put(x, yy, z, f'dark_oak_stairs[facing={facing_to(x, z, cx, cz)}]' if rr else 'dark_oak_planks')
    door = {'south': (cx, cz + w), 'north': (cx, cz - w), 'east': (cx + w, cz), 'west': (cx - w, cz)}[face]
    put(door[0], cy + 1, door[1], 'air')
    put(door[0], cy + 2, door[1], 'air')


def spiral(y0, y1, r):
    n = (y1 - y0) * 3
    for i in range(n):
        a = i / 3 * 0.42
        y = y0 + i // 3
        for dr in (0, 1, 2):
            put(TX + (r + dr) * math.cos(a), y, TZ + (r + dr) * math.sin(a), 'spruce_slab[type=top]')
        put(TX + (r + 3) * math.cos(a), y + 1, TZ + (r + 3) * math.sin(a), 'spruce_fence')


def bridge(p, q, sag=3):
    (x0, y0, z0), (x1, y1, z1) = p, q
    n = int(math.hypot(x1 - x0, z1 - z0) * 1.6) + 1
    for i in range(n + 1):
        t = i / n
        x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
        y = y0 + (y1 - y0) * t - sag * 4 * t * (1 - t)
        nx, nz = -(z1 - z0), (x1 - x0)
        ln = math.hypot(nx, nz) or 1
        nx, nz = nx / ln, nz / ln
        put(x, y, z, 'spruce_slab')
        for s in (-1, 1):
            put(x + s * nx, y, z + s * nz, 'spruce_slab')
            put(x + s * 2 * nx, y + 1, z + s * 2 * nz, 'spruce_fence')
            if i % 5 == 0:
                put(x + s * 2 * nx, y + 2, z + s * 2 * nz, 'lantern')


def treehouse(crowns):
    levels = [(Y0 + 16, 16.5), (Y0 + 31, 13.5), (Y0 + 46, 11.5)]
    for y, r in levels:
        deck(y, 0, r)
    hut(TX + 12, Y0 + 16, TZ - 3, 3, 'west')
    hut(TX - 12, Y0 + 16, TZ - 4, 3, 'east')
    hut(TX + 3, Y0 + 31, TZ - 10, 2, 'north')
    hut(TX - 6, Y0 + 46, TZ - 4, 2, 'east')
    spiral(Y0, Y0 + 16, 10)
    spiral(Y0 + 16, Y0 + 31, 8)
    spiral(Y0 + 31, Y0 + 46, 6)
    for (cx, cy, cz, rr) in crowns[:2]:                  # lookouts on two branches, joined by bridges
        lx, ly, lz = cx * .8 + TX * .2, Y0 + 32, cz * .8 + TZ * .2
        for x, z, d in disk(lx, lz, 4.5):
            put(x, ly, z, 'spruce_planks')
            if d > 3.6:
                put(x, ly + 1, z, 'spruce_fence')
        put(lx, ly + 1, lz, 'campfire[lit=true]')
        bridge((TX + (lx - TX) * 13 / math.hypot(lx - TX, lz - TZ), Y0 + 31,
                TZ + (lz - TZ) * 13 / math.hypot(lx - TX, lz - TZ)), (lx, ly, lz), 2)
    ny = Y0 + TRUNK_H - 4                                 # crow's nest
    for x, z, d in disk(TX, TZ, 5.5):
        put(x, ny, z, 'spruce_planks')
        if d > 4.6:
            put(x, ny + 1, z, 'spruce_fence')
    put(TX, ny + 1, TZ, 'lantern')
    for k in (1, 2, 3, 4):
        put(TX, ny + 1 + k, TZ + 4, 'spruce_fence')
    for fx in (1, 2, 3):
        for fy in (3, 4):
            put(TX + fx, ny + fy, TZ + 4, 'orange_wool')    # the brothers' flag


# ---------------------------------------------------------------- palisade, towers, gate, spikes
def palisade():
    gate_a = 90.0                                        # gate faces south (+z), toward the town road
    for x, z, d in disk(TX, TZ, PAL_R + 1):
        if d < PAL_R - .5:
            continue
        a = math.degrees(math.atan2(z - TZ, x - TX))
        if abs((a - gate_a + 180) % 360 - 180) * math.pi / 180 * PAL_R < 3.2:
            continue
        h = 6 + (_hash(x, z, 31) < .5)
        base = top(x, z)
        for y in range(base, base + h):
            put(x, y, z, 'spruce_log')
        put(x, base + h, z, 'pointed_dripstone[vertical_direction=up,thickness=tip]')
        if d >= PAL_R + .3 and _hash(x, z, 37) < .2:   # walkway brackets with torches
            put(x, base + 4, z, 'lantern')
    for k in range(6):                                   # watchtowers
        a = math.radians(k * 60 + 30)
        cx, cz = TX + PAL_R * math.cos(a), TZ + PAL_R * math.sin(a)
        b = top(round(cx), round(cz))
        for x in range(round(cx) - 2, round(cx) + 3):
            for z in range(round(cz) - 2, round(cz) + 3):
                corner = abs(x - round(cx)) == 2 and abs(z - round(cz)) == 2
                for y in range(b, b + 11):
                    if corner:
                        put(x, y, z, 'spruce_log')
                put(x, b + 10, z, 'spruce_planks')
                if abs(x - round(cx)) == 2 or abs(z - round(cz)) == 2:
                    put(x, b + 11, z, 'spruce_fence')
        put(round(cx), b + 11, round(cz), 'campfire[lit=true]')
        for k2 in range(3):
            put(round(cx), b + 12 + k2, round(cz) + 2, 'spruce_fence')
        put(round(cx) + 1, b + 14, round(cz) + 2, 'red_wool')
    gx, gz = TX, TZ + PAL_R                              # gate frame
    for x in range(gx - 4, gx + 5):
        put(x, top(x, gz) + 7, gz, 'spruce_log[axis=x]')
    for x in (gx - 4, gx + 4):
        for y in range(top(x, gz), top(x, gz) + 9):
            put(x, y, gz, 'spruce_log')
        put(x, top(x, gz) + 9, gz, 'lantern')
    for k in range(40):                                  # spike pits in a ring outside the wall
        a = math.radians(k * 9 + 4)
        if abs(k * 9 + 4 - 90) < 10:
            continue
        sx, sz = TX + (PAL_R + 6) * math.cos(a), TZ + (PAL_R + 6) * math.sin(a)
        put(sx, top(round(sx), round(sz)) + 1, sz, 'pointed_dripstone[vertical_direction=up,thickness=tip]')
    for z in range(TZ + PAL_R, TZ + TOWN_R1):            # road down to the town
        for x in range(TX - 2, TX + 3):
            put(x, top(x, z), z, 'dirt_path' if abs(x - TX) < 2 else 'coarse_dirt')


# ---------------------------------------------------------------- ruined town
def ruin(cx, cz, w, d_, h, seed):
    for x in range(cx, cx + w):
        for z in range(cz, cz + d_):
            wall = x in (cx, cx + w - 1) or z in (cz, cz + d_ - 1)
            put(x, G - 1, z, 'cobblestone' if _hash(x, z, seed) < .5 else 'gravel')
            if not wall:
                if _hash(x, z, seed + 5) < .05:
                    put(x, G, z, 'cobweb')
                continue
            hh = round(h * (0.25 + 0.75 * noise(x + seed, z, 3, 241)))
            for y in range(G, G + hh):
                r = _hash(x, y * 13 + z, seed)
                b = 'cracked_stone_bricks' if r < .3 else 'mossy_stone_bricks' if r < .5 else 'stone_bricks'
                if y in (G + 2, G + 3) and (x - cx) % 3 == 1 and (z - cz) % 3 == 1:
                    b = 'air'
                put(x, y, z, b)
    if _hash(cx, cz, seed) < .6:                         # half of a pitched roof still standing
        for k in range(d_ // 2 + 1):
            for x in range(cx, cx + w - int(_hash(cx, k, seed) * w * .6)):
                put(x, G + h + k, cz + k, 'dark_oak_stairs[facing=south]')
                put(x, G + h + k, cz + d_ - 1 - k, 'dark_oak_stairs[facing=north]')
    if _hash(cx, cz, seed + 2) < .5:
        put(cx + 1, G + 2, cz, 'soul_lantern')
    if _hash(cx, cz, seed + 1) < .35:
        put(cx + w // 2, G, cz + d_ // 2, 'campfire[lit=true]')


def town():
    k = 0
    for ring_r in (70, 84, 100):
        n = int(2 * math.pi * ring_r / 15)
        for i in range(n):
            a = 2 * math.pi * i / n + ring_r * .01
            if abs((math.degrees(a) % 360) - 90) < 6:   # keep the road clear
                continue
            cx, cz = round(TX + ring_r * math.cos(a)), round(TZ + ring_r * math.sin(a))
            if _hash(cx, cz, 251) < .12:
                continue
            w, d_ = 5 + int(_hash(cx, cz, 253) * 5), 5 + int(_hash(cz, cx, 257) * 5)
            ruin(cx - w // 2, cz - d_ // 2, w, d_, 5 + int(_hash(cx, cz, 259) * 5), 300 + k)
            k += 1
    cx, cz = TX + 30, TZ + 92                            # toppled church tower
    for y in range(G, G + 14):
        for x in range(cx, cx + 5):
            for z in range(cz, cz + 5):
                if x in (cx, cx + 4) or z in (cz, cz + 4):
                    if y < G + 14 - (x - cx) * 2:
                        put(x, y, z, 'stone_bricks' if _hash(x, y, z) < .7 else 'cracked_stone_bricks')
    for s in range(14):                                   # the fallen spire lying across the street
        for x in range(cx - 2 - s, cx - s):
            put(x, G, cz + 2, 'deepslate_tiles')
            if s < 10:
                put(x, G + 1, cz + 2, 'deepslate_tile_stairs[facing=west]')
    for i in range(70):                                  # dead trees
        a = _hash(i, 3, 261) * 2 * math.pi
        r = TOWN_R0 + _hash(i, 5, 263) * (TOWN_R1 - TOWN_R0 + 15)
        x, z = round(TX + r * math.cos(a)), round(TZ + r * math.sin(a))
        hh = 4 + int(_hash(i, 7, 265) * 5)
        for y in range(G, G + hh):
            put(x, y, z, 'spruce_log')
        put(x + 1, G + hh - 2, z, 'spruce_fence')
        put(x - 1, G + hh - 1, z, 'spruce_fence')


# ---------------------------------------------------------------- ground + cast
def ground():
    out = []
    x0, x1, z0, z1 = TX - TOWN_R1 - 15, TX + TOWN_R1 + 15, TZ - TOWN_R1 - 15, TZ + TOWN_R1 + 15
    for a in range(x0, x1 + 1, 40):
        for b in range(z0, z1 + 1, 40):
            out.append(f'fill {a} {G - 1} {b} {min(a + 39, x1)} {G - 1} {min(b + 39, z1)} podzol replace grass_block')
    return out


def forceload():
    x0, x1, z0, z1 = TX - TOWN_R1 - 15, TX + TOWN_R1 + 15, TZ - TOWN_R1 - 15, TZ + TOWN_R1 + 15
    out = []
    for a in range(x0, x1 + 1, 120):
        for b in range(z0, z1 + 1, 120):
            out.append(f'forceload add {a} {b} {min(a + 119, x1)} {min(b + 119, z1)}')
    return out


def cast(n=650):
    out = ['kill @e[tag=treeset]']
    k = 0
    i = 0
    while k < n:
        a = _hash(i, 1, 271) * 2 * math.pi
        if i % 2 == 0:                                   # half of the horde masses at the gate road
            a = math.radians(90 + (_hash(i, 9, 281) - .5) * 70)
        r = PAL_R + 3 + _hash(i, 2, 273) ** 1.8 * 34
        i += 1
        x, z = TX + r * math.cos(a), TZ + r * math.sin(a)
        y = top(round(x), round(z)) + 1
        yaw = math.degrees(math.atan2(-(TX - x), (TZ - z)))
        kind = 'zombie' if _hash(i, 3, 277) < .82 else 'husk' if _hash(i, 4, 279) < .5 else 'zombie_villager'
        out.append(f'summon {kind} {x:.1f} {y} {z:.1f} {{Tags:["treeset"],NoAI:1b,PersistenceRequired:1b,Silent:1b,'
                   f'Rotation:[{yaw:.0f}f,0f]}}')
        k += 1
    dy = Y0 + 16 + 1                                     # on the first deck, looking south over the gate
    for name, tex, dx, dz, yaw, sc in (('Bin', 'bin', 0.5, 14.5, 0, 1.0), ('Bo', 'bo', -1.8, 14.0, 10, 1.0),
                                       ('Zu', 'zu', 2.4, 14.2, -10, .72)):
        out.append(f'summon mannequin {TX + dx} {dy} {TZ + dz} {{Tags:["treeset"],profile:{{texture:"binbo:entity/cast/{tex}"}},'
                   f'hide_description:1b,immovable:1b,Rotation:[{yaw}f,0f],attributes:[{{id:"minecraft:scale",base:{sc}}}]}}')
    return out


def clear_tree():
    """Air over the hilltop (above the trunk base), so a rebuild never leaves an older tree behind."""
    out = []
    for a in range(TX - 48, TX + 48, 16):
        for b in range(TZ - 48, TZ + 48, 16):
            out.append(f'fill {a} {Y0 + 1} {b} {a + 15} {Y0 + 110} {b + 15} air')
    for a in range(TX - 150, TX + 150, 20):              # the town ring below the hill, then the podzol again
        for b in range(TZ - 150, TZ + 150, 20):
            nx, nz = min(max(TX, a), a + 19), min(max(TZ, b), b + 19)
            if math.hypot(nx - TX, nz - TZ) > HILL_R + 1:
                out.append(f'fill {a} {G} {b} {a + 19} {G + 25} {b + 19} air')
                out.append(f'fill {a} {G - 1} {b} {a + 19} {G - 1} {b + 19} podzol')
    return out


def build_all():
    V.clear()
    crowns = tree()
    treehouse(crowns)
    palisade()
    town()
    build = compress(V)
    files = {'tree_ground': forceload() + ground() + hill(), 'tree_clear': forceload() + clear_tree()}
    for i in range(0, max(1, len(build)), 45000):
        files[f'tree_build_{i // 45000}'] = forceload() + build[i:i + 45000]
    files['tree_cast'] = cast()
    return files


def write(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    files = build_all()
    for name, cmds in files.items():
        assert len(cmds) < MAX_CMDS, (name, len(cmds))
        with open(os.path.join(out_dir, name + '.mcfunction'), 'w', encoding='utf-8') as f:
            f.write('# generated by tools/mc_java/gen_treehouse.py\n' + '\n'.join(cmds) + '\n')
    return {k: len(v) for k, v in files.items()}


if __name__ == '__main__':
    print('TREE_OK', write(sys.argv[1] if len(sys.argv) > 1 else 'tree_out'), 'blocks', len(V))
