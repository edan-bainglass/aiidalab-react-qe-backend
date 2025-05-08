import typing as t

import pydantic as pdt

from aiidalab_react_qe_backend.common.utils import (
    CustomBaseModel,
    WithDependency,
    IsConditional,
    WithItems,
    WithLabels,
    WithUI,
    WithWidget,
    if_,
    requires,
)


class MagnetizationSettings(CustomBaseModel):
    model_config = pdt.ConfigDict(title="Magnetization")

    mode: t.Annotated[
        t.Literal[
            "moments",
            "total",
        ],
        pdt.Field(
            title="Input mode",
        ),
        WithWidget("toggleGroup"),
        WithLabels(
            labels=[
                "Initial magnetic moments",
                "Total magnetization",
            ]
        ),
        WithDependency(["basic.electronic_type"]),
        IsConditional,
    ] = "moments"

    tot_magnetization: t.Annotated[
        float,
        pdt.Field(
            title="Total magnetization",
            ge=0.0,
            multiple_of=0.1,
        ),
        WithDependency(["basic.electronic_type"]),
        IsConditional,
    ] = 1

    moments: t.Annotated[
        list[float],
        pdt.Field(
            title="Initial magnetic moments",
        ),
        WithUI(
            schema={
                "ui:options": {"classNames": "mt-2"},
                "items": {
                    "generatedFrom": "structure.species",
                    "template": "{{species}}",
                },
            }
        ),
        WithItems(default=0.1),
        WithDependency(
            [
                "structure.species",
                "basic.electronic_type",
            ]
        ),
        IsConditional,
    ]

    __requires__ = requires("basic.magnetism").is_true()

    __conditionals__ = [
        if_("basic.electronic_type")
        .equals("insulator")
        .then_(
            properties=[
                "tot_magnetization",
            ]
        )
        .else_(
            properties=[
                "mode",
            ],
            conditions=[
                if_("mode")
                .equals("moments")
                .then_(
                    properties=[
                        "moments",
                    ]
                )
                .else_(
                    properties=[
                        "tot_magnetization",
                    ],
                ),
            ],
        )
    ]
