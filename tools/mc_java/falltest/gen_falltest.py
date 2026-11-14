"""MC-S3 test Short "Which block saves you from a 30-block fall?" (Verity-Verifies-style mechanic test, our own cast and set).

    python gen_falltest.py OUTDIR   # -> OUTDIR/ft_*.mcfunction + tick addition, for datapack binbozu (namespace binbo)

Set: 6 lanes at x = X0 + 4i, z = 0 on the superflat ground (top block y=-61, standing y=-60), far from the city builds.
Each lane: 3x3 ring of polished andesite at y=-60, test block in the centre. One husk (20 HP, does not burn in daylight)
hovers 31 blocks above each lane (NoGravity) and is released one at a time while the camera (spectated marker
armor stand, teleported every tick = smooth) follows it down, then freezes 6 blocks above ground.
Expected Java fall damage: ceil((fall - 3) * multiplier) -> stone 28 (dead), bed x0.5 = 14, hay/honey x0.2 = 6,
slime 0 (bounces), water 0. The run prints measured Health with tellraw at the end (read from latest.log).
"""
import os
import sys

X0, Z0, GY = 2000, 0, -60          # GY = standing level (one above the grass top block)
DROP_Y = GY + 31
LANES = [('stone', 'stone'), ('bed', None), ('hay', 'hay_block'), ('honey', 'honey_block'), ('slime', 'slime_block'), ('water', 'water')]
INTRO, STEP = 100, 110             # ticks


def lane_x(i):
    return X0 + 4 * i


def build():
    c = ['time set 6000', 'weather clear',
         *[f'fill {X0-8} {y0} {Z0-30} {X0+28} {y0+13} {Z0+12} air' for y0 in (GY, GY+14, GY+28)],   # fill limit 32768 blocks
         f'fill {X0-8} {GY-1} {Z0-30} {X0+28} {GY-1} {Z0+12} grass_block']
    for i, (_, blk) in enumerate(LANES):
        x = lane_x(i)
        c.append(f'fill {x-1} {GY} {Z0-1} {x+1} {GY} {Z0+1} polished_andesite')
        if blk == 'water':
            c.append(f'setblock {x} {GY-1} {Z0} water')
            c.append(f'setblock {x} {GY} {Z0} water')
        elif blk:
            c.append(f'setblock {x} {GY} {Z0} {blk}')
        else:   # bed: head on the centre, foot behind it (+z)
            c.append(f'setblock {x} {GY} {Z0+1} air')
            c.append(f'setblock {x} {GY} {Z0} red_bed[facing=north,part=head]')
            c.append(f'setblock {x} {GY} {Z0+1} red_bed[facing=north,part=foot]')
    # backdrop: fence line, lanterns between lanes, a few flowers
    c.append(f'fill {X0-6} {GY} {Z0+5} {X0+26} {GY} {Z0+5} oak_fence')
    for i in range(len(LANES) - 1):
        x = lane_x(i) + 2
        c += [f'setblock {x} {GY} {Z0+3} oak_fence', f'setblock {x} {GY+1} {Z0+3} lantern']
    for dx, dz, f in ((-4, -3, 'poppy'), (-3, 2, 'dandelion'), (23, -2, 'cornflower'), (25, 2, 'oxeye_daisy'), (9, -4, 'dandelion'), (15, -4, 'poppy')):
        c.append(f'setblock {X0+dx} {GY} {Z0+dz} {f}')
    return c


def actors():
    c = ['kill @e[type=husk,tag=fall]', 'kill @e[type=item]', 'kill @e[type=armor_stand,tag=cam]', 'kill @e[type=mannequin,tag=host]']
    for i, (name, _) in enumerate(LANES):
        c.append(f'summon husk {lane_x(i)+0.5} {DROP_Y} {Z0+0.5} {{Tags:["fall","f{i}"],NoGravity:1b,PersistenceRequired:1b,'
                 f'Rotation:[180f,0f],active_effects:[{{id:"minecraft:slowness",amplifier:10b,duration:999999,show_particles:0b}}]}}')
    c.append(f'summon mannequin {X0-3.5} {GY} {Z0-1.5} {{Tags:["host"],profile:{{texture:"binbo:entity/cast/bin"}},'
             f'hide_description:1b,immovable:1b,Rotation:[200f,0f]}}')
    c.append(f'summon armor_stand {X0+10} {GY+1.5} {Z0-28} {{Tags:["cam"],Invisible:1b,NoGravity:1b,Marker:1b,Silent:1b}}')
    return c


def run():
    c = ['scoreboard objectives add bb dummy', 'scoreboard players set #roll bb 0', 'scoreboard players set #ft bb 1',
         'gamemode spectator @a',
         # intro: low wide angle looking up at the six hanging husks
         f'tp @e[type=armor_stand,tag=cam,limit=1] {X0+10.5} {GY+1.5} {Z0-28} facing {X0+10.5} {GY+14} {Z0}',
         'spectate @e[type=armor_stand,tag=cam,limit=1] @a']
    for i in range(len(LANES)):
        c.append(f'schedule function binbo:ft_l{i} {INTRO + STEP*i}t')
    c.append(f'schedule function binbo:ft_end {INTRO + STEP*len(LANES)}t')
    return c


def lane(i):
    x = lane_x(i)
    return ['tag @e[type=husk,tag=cur] remove cur', f'tag @e[type=husk,tag=f{i}] add cur',
            f'tp @e[type=armor_stand,tag=cam,limit=1] {x+0.5} {DROP_Y+2} {Z0-6} facing {x+0.5} {DROP_Y+1} {Z0+0.5}',
            f'data merge entity @e[type=husk,tag=f{i},limit=1] {{NoGravity:0b}}']


def end():
    c = ['tag @e[type=husk,tag=cur] remove cur',
         f'tp @e[type=armor_stand,tag=cam,limit=1] {X0+10.5} {GY+3} {Z0-17} facing {X0+10.5} {GY+0.5} {Z0}',
         'schedule function binbo:ft_report 100t']
    return c


def report():
    c = ['scoreboard players set #ft bb 0']
    for i, (name, _) in enumerate(LANES):
        c.append(f'tellraw @a ["FT {name} ",{{"nbt":"Health","entity":"@e[type=husk,tag=f{i},limit=1]"}}]')
    return c


def tick_lines():
    # follow the released husk from 2 blocks above / 6 behind until it is 5 blocks above the ground, then hold
    return [f'execute if score #ft bb matches 1 as @e[type=husk,tag=cur,limit=1] at @s if entity @s[y={GY+5},dy=200] '
            f'run tp @e[type=armor_stand,tag=cam,limit=1] ~ ~2 ~-6 facing entity @s eyes']


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    files = {'ft_build': build(), 'ft_actors': actors(), 'ft_go': run(), 'ft_end': end(), 'ft_report': report(), 'ft_tick': tick_lines()}
    files.update({f'ft_l{i}': lane(i) for i in range(len(LANES))})
    for k, v in files.items():
        open(os.path.join(out, k + '.mcfunction'), 'w').write('\n'.join(v) + '\n')
    print('FALLTEST_OK', len(files))
