from __future__ import annotations

import copy
import json
from typing import Any


class WorkflowTemplateCompiler:
    """Recursively replace ${TOKEN} placeholders in ComfyUI API JSON templates.

    Whole-string placeholders preserve non-string types, e.g. "${SEED}" -> 12345.
    Embedded placeholders are converted to strings.
    """

    def compile(self, template: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
        return self._walk(copy.deepcopy(template), values)

    def _walk(self, value: Any, values: dict[str, Any]) -> Any:
        if isinstance(value, dict):
            return {k: self._walk(v, values) for k, v in value.items()}
        if isinstance(value, list):
            return [self._walk(v, values) for v in value]
        if not isinstance(value, str):
            return value
        if value.startswith("${") and value.endswith("}") and value.count("${") == 1:
            key = value[2:-1]
            if key not in values:
                raise KeyError(f"Missing workflow token: {key}")
            return values[key]
        out = value
        for key, replacement in values.items():
            out = out.replace("${" + key + "}", str(replacement))
        unresolved = self.unresolved(out)
        if unresolved:
            raise KeyError(f"Unresolved workflow tokens: {sorted(unresolved)}")
        return out

    @staticmethod
    def unresolved(value: Any) -> set[str]:
        payload = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
        found: set[str] = set()
        pos = 0
        while True:
            start = payload.find("${", pos)
            if start < 0: break
            end = payload.find("}", start + 2)
            if end < 0: break
            found.add(payload[start + 2:end]); pos = end + 1
        return found
