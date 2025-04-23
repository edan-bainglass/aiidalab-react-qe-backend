import json

from fastapi import FastAPI, HTTPException

from aiidalab_react_qe_backend.registry import discover_plugins

app = FastAPI()


@app.get("/api/plugins")
def list_plugins():
    """
    Return a list of available plugins.
    """
    plugins = [{"id": p["id"], "label": p["label"]} for p in discover_plugins()]
    print(json.dumps(plugins, indent=2))
    return plugins


@app.get("/api/plugins/{plugin_id}/{schema_key}")
def get_plugin_schema(plugin_id: str, schema_key: str):
    """
    Return the schema definitions for a specific plugin.
    """
    for plugin in discover_plugins():
        if plugin["id"] == plugin_id:
            schema = plugin.get(schema_key, {})
            print(json.dumps(schema, indent=2))
            return schema
    raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")


@app.post("/api/submit")
def submit_workflow(payload: dict):
    """
    Submit a workflow to the backend.
    """
    # Here you would implement the logic to submit the workflow
    # For now, we just return the payload for demonstration purposes
    print(json.dumps(payload, indent=2))
    return {"status": "success", "data": payload}
