import json

from fastapi import FastAPI, HTTPException

from aiidalab_react_qe_backend.registry import discover_plugins

from .models.input import SCHEMA as INPUT_SCHEMA

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
    print(json.dumps(INPUT_SCHEMA, indent=2))
    return INPUT_SCHEMA


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
