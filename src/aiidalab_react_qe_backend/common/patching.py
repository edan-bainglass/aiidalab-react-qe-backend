import typing as t

from aiidalab_react_qe_backend.common.payload_types import PatchRequestPayload
from aiidalab_react_qe_backend.models import MODELS


class SchemaPatcher:
    @staticmethod
    def generate_patch(
        panel_key: str,
        field: str,
        part: str,
        payload: PatchRequestPayload,
    ) -> dict[str, t.Any]:
        if not (Model := MODELS.get(panel_key, None)):
            return {}
        if not (patches := Model.get_backend_patches(field)):
            return {}
        if part not in ("definition", "ui"):
            return {}
        patch = patches.definition if part == "definition" else patches.ui
        return {patch.what: patch.processor(payload.requirements)}
