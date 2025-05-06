import json
import typing as t

import pydantic as pdt
from fastapi import FastAPI, HTTPException

from aiidalab_react_qe_backend.models.input.advanced import ADVANCED_SETTINGS
from aiidalab_react_qe_backend.models.input.basic import BasicSettings
from aiidalab_react_qe_backend.registry import discover_plugins

app = FastAPI()


@app.get("/api/plugins")
def list_plugins():
    plugins = {
        plugin["id"]: {
            "label": plugin["label"],
            "active": False,
        }
        for plugin in discover_plugins()
    }
    print(json.dumps(plugins, indent=2))
    return plugins


@app.get("/api/core/schemas/input")
def get_core_input_schema():
    input_schema = {
        "basic": BasicSettings.model_full_schema(),
        "advanced": {
            category: schema.model_full_schema()
            for category, schema in ADVANCED_SETTINGS.items()
        },
    }
    print(json.dumps(input_schema, indent=2))
    return input_schema


@app.get("/api/plugin/schemas/{plugin_id}/{schema_key}")
def get_plugin_schema(plugin_id: str, schema_key: str):
    for plugin in discover_plugins():
        if plugin["id"] == plugin_id:
            schema = plugin.get(schema_key, {})
            print(json.dumps(schema, indent=2))
            return schema
    raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")


@app.post("/api/submit")
def submit_workflow(payload: dict):
    print(json.dumps(payload, indent=2))
    return {"status": "success", "data": payload}


class AccuracyInput(pdt.BaseModel):
    pseudos_family: t.Literal["SSSP", "PseudoDojo"]


# TODO consider generalizing this endpoint (maybe providing labels in the model?)
@app.post("/api/core/schema/dynamic/accuracy/labels")
async def get_accuracy_labels(data: AccuracyInput):
    labels = (
        ["Efficiency", "Precision"]
        if data.pseudos_family == "SSSP"
        else ["Standard", "Stringent"]
        if data.pseudos_family == "PseudoDojo"
        else []
    )
    print(json.dumps(labels, indent=2))
    return labels
