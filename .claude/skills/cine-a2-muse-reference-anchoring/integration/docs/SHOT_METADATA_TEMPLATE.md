# Writers Room -> Director / DOP -> Flow/Muse Shot Metadata

Every shot must provide a structured JSON record that conforms to `schemas/SHOT.schema.json`. No regex searching screenplay for character tags. Only list those *physically visible*, including expressive CGI animals/robots. If no character is visible, `activeCharacterTags: []` is valid. `location_id + space_id + location_view_id` remain mandatory even when no characters are visible. Choose existing `space_id` from Location Registry, such as `BH-ATELIER`, not an arbitrary English short name.

The writer describes the emotional and physical first-frame event. Director assigns eyeline, camera, blocking. Art assigns user-approved outfit and exact character/location plate IDs. Sound assigns voice files. The resolver must reject unapproved/missing assets and never invent missing ones. In Muse, first create and approve standalone masters, then individual angle/face/expression plates, then anchored story shots. 10s I2V must preserve the approved first frame.

Sample `EP001_S010` references Lia/Bubu and `BELL/BH-ATELIER/FORWARD` but currently **production-blocked** because none of those assets have individually approved original view files.

Do not use textual placeholders like `approved_master: master/Lia_master_v1.png` unless the actual file exists, its checksum matches, and a human reviewer approved it. Use metadata states honestly.