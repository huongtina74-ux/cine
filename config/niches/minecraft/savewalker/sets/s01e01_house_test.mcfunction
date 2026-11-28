# SAVEWALKER S1E1 test set (OBSERVED working over RCON on server 1.21.1, 2026-11-02). Platform at y=99 so terrain never matters.
time set night
forceload add -8 -8 8 8
fill -4 99 -4 4 99 4 minecraft:grass_block
fill -2 100 -2 2 103 2 minecraft:oak_planks hollow
setblock 0 100 -2 minecraft:air
setblock 0 101 -2 minecraft:air
setblock 0 100 -4 minecraft:oak_sign[rotation=8]{front_text:{messages:['"ARE YOU THE SAVE?"','""','""','""']}}
# the episode's wrong block
setblock 2 101 -2 minecraft:gravel
execute if block 2 101 -2 minecraft:gravel
save-all flush
