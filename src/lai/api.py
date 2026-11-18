"""Health-only API scaffold. Product endpoints are introduced in T5."""

from fastapi import FastAPI

from lai import __version__

app = FastAPI(
    title="LAi private prototype",
    version=__version__,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {"status": "prototype", "version": __version__, "navigator_enabled": False}
