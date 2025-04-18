import typing as t

import pydantic as pdt


class Test1Input(pdt.BaseModel):
    model_config = pdt.ConfigDict(
        title="First test plugin",
    )
    some_float: t.Annotated[
        float,
        pdt.Field(
            title="Float (in some units)",
            default=0.5,
            ge=0,
            le=1,
            multiple_of=0.1,
        ),
    ]
    some_integer: t.Annotated[
        int,
        pdt.Field(
            title="Even integer (in some other units)",
            default=2,
            gt=0,
            le=10,
            multiple_of=2,
        ),
    ]


def get_plugin() -> dict[str, t.Any]:
    return {
        "id": "test1",
        "label": "First test plugin",
        "input": {
            "schema": Test1Input.model_json_schema(),
            "ui": {
                "ui:options": {"title": False},
                "some_integer": {
                    "ui:dependency": {
                        "parameter": "structure",
                        "relationship": "<= {{parameter}}.nsites",
                    }
                },
            },
        },
        "resources": {},
        "output": {
            "schema": {},
            "ui": {
                "bands_data": {
                    "ui:widget": "BandsDataWidget",
                    "ui:options": {
                        "layout": {
                            "show_title": True,
                            "show_description": True,
                            "show_plot": True,
                            "show_table": False,
                        },
                        "config": {
                            "title": "Band structure",
                            "description": "Band structure of the system",
                            "plot_type": "band_structure",
                            "show_plot": True,
                            "show_table": False,
                        },
                    },
                }
            },
        },
    }
