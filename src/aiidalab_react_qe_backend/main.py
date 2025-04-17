from fastapi import FastAPI, HTTPException
from aiidalab_react_qe_backend.registry import discover_plugins

app = FastAPI()


@app.get("/api/plugins")
def list_plugins():
    """
    Return a list of available plugins.
    """
    return [{"id": p["id"], "label": p["label"]} for p in discover_plugins()]


@app.get("/api/plugins/{plugin_id}/schemas")
def get_plugin_schema(plugin_id: str):
    """
    Return the schema definitions for a specific plugin.
    """
    for plugin in discover_plugins():
        if plugin["id"] == plugin_id:
            return plugin["schemas"]
    raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")
