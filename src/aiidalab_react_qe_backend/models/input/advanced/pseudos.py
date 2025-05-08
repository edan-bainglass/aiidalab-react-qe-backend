import typing as t

import pydantic as pdt

from aiidalab_react_qe_backend.common.utils import (
    BackendPatch,
    CustomBaseModel,
    WithDependency,
    WithBackendPatches,
    Patch,
    WithItems,
    WithLabels,
    WithUI,
    WithWidget,
    if_,
)


class PseudopotentialSettings(CustomBaseModel):
    model_config = pdt.ConfigDict(title="Pseudopotentials")

    functional: t.Annotated[
        t.Literal[
            "pbe",
            "pbe_sol",
        ],
        pdt.Field(
            title="Functional",
        ),
        WithWidget("toggleGroup"),
        WithLabels(
            labels=[
                "PBE",
                "PBEsol",
            ]
        ),
    ] = "pbe_sol"

    family: t.Annotated[
        str,
        pdt.Field(
            title="Family",
        ),
        WithWidget("toggleGroup"),
        WithLabels(
            labels=[
                "PseudoDojo",
                "SSSP",
            ]
        ),
        WithDependency(["basic.spin_orbit"]),
    ]

    accuracy: t.Annotated[
        str,
        pdt.Field(
            title="Accuracy",
        ),
        WithWidget("toggleGroup"),
        WithDependency(["basic.protocol"]),
        WithBackendPatches(
            ui=BackendPatch(
                what="labels",
                requires=["pseudos.family"],
                processor=lambda params: ["Efficiency", "Precision"]
                if params["pseudos.family"] == "SSSP"
                else ["Standard", "Stringent"]
                if params["pseudos.family"] == "PseudoDojo"
                else [],
            )
        ),
    ]

    pseudopotentials: t.Annotated[
        list[str],
        pdt.Field(
            title="Pseudopotentials",
        ),
        WithItems(format="data-url"),
        WithUI(
            schema={
                "ui:options": {"classNames": "mt-2"},
                "items": {
                    "ui:hideError": True,
                    "ui:options": {"accept": ".UPF"},
                    "generatedFrom": "structure.species",
                    "template": "{{species}}",
                },
            }
        ),
        WithDependency(["structure.species"]),
    ]

    __conditionals__ = [
        if_("basic.spin_orbit")
        .is_true()
        .then_(
            patches=[
                Patch("family").set_options(["PseudoDojo"]).set_default("PseudoDojo")
            ],
        )
        .else_(
            patches=[
                Patch("family").set_options(["PseudoDojo", "SSSP"]).set_default("SSSP")
            ]
        ),
        if_("family")
        .equals("SSSP")
        .then_(
            patches=[
                Patch("accuracy").set_options(["efficiency", "precision"]),
            ],
            conditions=[
                if_("basic.protocol")
                .equals("stringent")
                .then_(
                    patches=[
                        Patch("accuracy").set_default("precision"),
                    ],
                )
                .else_(
                    patches=[
                        Patch("accuracy").set_default("efficiency"),
                    ],
                )
            ],
        )
        .else_(
            patches=[
                Patch("accuracy").set_options(["standard", "stringent"]),
            ],
            conditions=[
                if_("basic.protocol")
                .equals("stringent")
                .then_(
                    patches=[
                        Patch("accuracy").set_default("stringent"),
                    ],
                )
                .else_(
                    patches=[
                        Patch("accuracy").set_default("standard"),
                    ],
                )
            ],
        ),
    ]
