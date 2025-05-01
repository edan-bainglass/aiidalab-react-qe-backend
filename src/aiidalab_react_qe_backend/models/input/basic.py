import typing as t

import pydantic as pdt

from aiidalab_react_qe_backend.common.utils import (
    CustomBaseModel,
    Patch,
    WithLabels,
    WithWidget,
    if_,
)


class BasicSettings(CustomBaseModel):
    model_config = pdt.ConfigDict(title="")

    relax: t.Annotated[
        t.Optional[str],
        pdt.Field(title="Relaxation level"),
        WithWidget("toggleGroup"),
        WithLabels(
            [
                "Structure as is",
                "Positions only",
                "Full geometry",
            ],
        ),
    ] = None
    electronic_type: t.Annotated[
        t.Literal[
            "metallic",
            "insulator",
        ],
        pdt.Field(title="Electronic type"),
        WithWidget("toggleGroup"),
        WithLabels(
            [
                "Metallic",
                "Insulator",
            ],
        ),
    ] = "metallic"
    protocol: t.Annotated[
        t.Literal[
            "fast",
            "balanced",
            "stringent",
        ],
        pdt.Field(title="Protocol"),
        WithWidget("toggleGroup"),
        WithLabels(
            [
                "Fast",
                "Balanced",
                "Stringent",
            ],
        ),
    ] = "fast"
    magnetism: t.Annotated[
        bool,
        pdt.Field(title="Magnetism"),
    ] = False
    spin_orbit: t.Annotated[
        bool,
        pdt.Field(title="Spin-orbit coupling"),
    ] = False

    __dependencies__ = ["structure.pbc"]

    __conditionals__ = [
        if_("molecule")
        .is_true()
        .then_(
            patches=[
                Patch("relax")
                .set_options(["none", "positions"])
                .set_default("positions")
            ]
        )
        .else_(
            patches=[
                Patch("relax")
                .set_options(["none", "positions", "positions-cell"])
                .set_default("positions-cell")
            ]
        )
    ]
