# Animal Long Slide vertical

## Production identity

Animal Long Slide is authored procedural 3D animation that borrows the visual grammar of a game. It must not be represented internally as captured or authentic gameplay.

## Production grammar

A module is a short animal challenge built from a scene template, a standardized animal rig, a bounded animation sequence, optional obstacles, a controlled physics window, camera beats, semantic reaction events, and a visible outcome.

Preferred motion order:

1. controlled idle/run/path motion;
2. controlled slide motion;
3. short bounded collision/physics event;
4. controlled recovery/outcome motion.

Do not use unconstrained rigid-body simulation for the full module unless a qualified template explicitly requires it.

## Asset policy

External assets are quarantined until commercial-use rights, provenance, content hash, compatibility, and production readiness are recorded. Unknown or personal-use-only assets cannot enter production.

Animal assets should be normalized to a stable factory profile with root orientation, world scale, ground offset, camera target height, collider strategy, animation clip compatibility, and canonical identifiers.

## Variation policy

A new episode must vary more than colors or animal order. Prefer meaningful variation across challenge structure, obstacle sequence, outcome, camera moments, timing, and scene mechanics. Track a deterministic originality signature for every planned episode.

## QC

Mandatory vertical gates include asset rights, rig compatibility, ground contact, collision integrity, camera framing, event pacing, duration integrity, and novelty. Preview/QC should run before beauty render. Failed deterministic checks should be repaired without invoking a reasoning model when possible.
