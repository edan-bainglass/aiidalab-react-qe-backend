import typing as t

import pydantic as pdt


class BandsInput(pdt.BaseModel):
    energy_cutoff: float = pdt.Field(
        40.0,
        ge=10,
        le=200,
        description="Energy cutoff (Ry)",
    )
    kpoint_distance: float = pdt.Field(
        0.1,
        gt=0,
        description="K-point distance",
    )


class BandsResources(pdt.BaseModel):
    pw_code: str = pdt.Field(
        ...,
        description="Quantum ESPRESSO pw.x code",
    )
    nb_mpi: int = pdt.Field(
        1,
        gt=0,
        description="Number of MPI ranks",
    )


class BandsOutput(pdt.BaseModel):
    band_structure: t.Any  # placeholder for real structure or reference


def get_plugin() -> dict[str, t.Any]:
    return {
        "id": "bands",
        "label": "Band Structure",
        "schemas": {
            "input": BandsInput.model_json_schema(),
            "resources": BandsResources.model_json_schema(),
            "output": BandsOutput.model_json_schema(),
        },
    }
