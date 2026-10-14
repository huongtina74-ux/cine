"""Species specs for the channel's own toy-style animals (no bpy).

Every animal is built from the same family of smooth, rounded parts (vinyl
toy look), so the whole cast shares one style: oversized head, big glossy
eyes, short legs, soft outline. Proportions are in metres for a ~1 m body;
the renderer rescales each animal to its target length.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ToySpec:
    species: str
    body: tuple[float, float, float]  # ellipsoid radii x (width), y (length), z (height)
    leg_length: float
    leg_radius: float
    head_radius: float
    snout: tuple[float, float, float]  # radii; (0,0,0) = none
    ears: str  # round | pointy | floppy | big_disc | none
    ear_size: float
    tail: str  # thin | tuft | curl | stub | none
    skin: tuple[float, float, float]
    belly: tuple[float, float, float]
    snout_color: tuple[float, float, float]
    pattern: str = "none"  # spots | stripes | none
    pattern_color: tuple[float, float, float] = (0.05, 0.05, 0.06)
    features: tuple[str, ...] = field(default_factory=tuple)  # trunk, tusks, horns, mane, bill


SPECS: dict[str, ToySpec] = {
    "cow": ToySpec("cow", (0.36, 0.55, 0.32), 0.34, 0.085, 0.30, (0.20, 0.16, 0.14), "floppy", 0.14, "tuft",
                   (0.97, 0.97, 0.96), (0.97, 0.97, 0.96), (1.0, 0.55, 0.62), "spots", features=("horns",)),
    "tiger": ToySpec("tiger", (0.32, 0.56, 0.28), 0.32, 0.08, 0.29, (0.17, 0.13, 0.11), "round", 0.10, "thin",
                     (1.0, 0.52, 0.10), (1.0, 0.96, 0.9), (1.0, 0.96, 0.9), "stripes"),
    "elephant": ToySpec("elephant", (0.45, 0.6, 0.42), 0.36, 0.13, 0.36, (0.0, 0.0, 0.0), "big_disc", 0.30, "thin",
                        (0.50, 0.62, 0.86), (0.66, 0.76, 0.92), (0.66, 0.76, 0.92), features=("trunk", "tusks")),
    "lion": ToySpec("lion", (0.33, 0.55, 0.29), 0.32, 0.085, 0.28, (0.16, 0.13, 0.11), "round", 0.09, "tuft",
                    (1.0, 0.66, 0.16), (1.0, 0.84, 0.5), (1.0, 0.9, 0.7), features=("mane",)),
    "hippo": ToySpec("hippo", (0.46, 0.6, 0.38), 0.26, 0.13, 0.33, (0.30, 0.24, 0.22), "round", 0.07, "stub",
                     (0.58, 0.42, 0.84), (0.84, 0.66, 0.90), (0.86, 0.62, 0.86)),
    "pig": ToySpec("pig", (0.36, 0.5, 0.32), 0.26, 0.085, 0.29, (0.13, 0.08, 0.10), "pointy", 0.10, "curl",
                   (1.0, 0.55, 0.66), (1.0, 0.72, 0.80), (1.0, 0.42, 0.56)),
    "zebra": ToySpec("zebra", (0.32, 0.55, 0.30), 0.40, 0.075, 0.27, (0.15, 0.20, 0.13), "pointy", 0.12, "tuft",
                     (0.98, 0.98, 0.98), (0.98, 0.98, 0.98), (0.25, 0.25, 0.28), "stripes", features=("mane_strip",)),
    "gorilla": ToySpec("gorilla", (0.40, 0.46, 0.40), 0.32, 0.12, 0.30, (0.18, 0.12, 0.14), "round", 0.07, "none",
                       (0.20, 0.20, 0.24), (0.42, 0.40, 0.46), (0.48, 0.44, 0.50)),
}


def spec(species: str) -> ToySpec:
    try:
        return SPECS[species]
    except KeyError:
        raise KeyError(f"no toy spec for {species!r}; known: {sorted(SPECS)}") from None


# Gait: a 16-frame trot; diagonal legs move together.
RUN_FRAMES = 10  # quick toy scurry: ~2.4 strides per second at 24 fps
LEG_SWING_DEG = 38.0
BODY_BOB = 0.035
LEG_PHASE = {"Leg_FL": 0.0, "Leg_BR": 0.0, "Leg_FR": 0.5, "Leg_BL": 0.5}
