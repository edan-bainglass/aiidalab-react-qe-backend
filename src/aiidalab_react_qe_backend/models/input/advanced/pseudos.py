import typing as t

import pydantic as pdt

from aiidalab_react_qe_backend.common.utils import (
    CustomBaseModel,
    DependsOn,
    DynamicFieldFragment,
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
        t.Optional[str],
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
        DependsOn(["basic.spin_orbit"]),
    ] = None
    accuracy: t.Annotated[
        t.Optional[str],
        pdt.Field(
            title="Accuracy",
        ),
        WithWidget("toggleGroup"),
        DynamicFieldFragment(
            endpoint="/api/core/schema/dynamic/accuracy/labels",
            requires=["pseudos.family"],
            target="ui",
            path="ui:enumNames",
        ),
    ] = None
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
        DependsOn(["structure.species"]),
    ]

    __conditionals__ = [
        if_("basic.spin_orbit")
        .is_false()
        .then_(
            patches=[
                Patch("family").set_options(["PseudoDojo", "SSSP"]).set_default("SSSP")
            ],
            conditions=[
                if_("family")
                .equals("SSSP")
                .then_(
                    patches=[
                        Patch("accuracy")
                        .set_options(["efficiency", "precision"])
                        .set_default("efficiency")
                    ]
                )
                .else_(
                    patches=[
                        Patch("accuracy")
                        .set_options(["standard", "stringent"])
                        .set_default("standard")
                    ]
                )
            ],
        )
        .else_(
            patches=[
                Patch("family").set_options(["PseudoDojo"]).set_default("PseudoDojo"),
                Patch("accuracy")
                .set_options(["standard", "stringent"])
                .set_default("standard"),
            ]
        )
    ]
