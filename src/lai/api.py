"""Private, default-closed API. Unvalidated bodies and errors are never echoed."""

import json
from datetime import date, datetime
from importlib.resources import files
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, Response
from starlette.middleware.trustedhost import TrustedHostMiddleware

from lai import __version__
from lai.answers.contracts import AnswerDocument, DisplayLanguage
from lai.answers.service import AnswerService
from lai.retrieval.models import RetrievalResult
from lai.triage.contracts import TriageRequest
from lai.triage.pipeline import SafetyNavigator

MAX_BODY_BYTES = 16_384


class DisabledPath:
    def run(self, request: TriageRequest, as_of: date) -> RetrievalResult:
        raise RuntimeError("navigation_not_configured")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def create_app(service: AnswerService | None = None) -> FastAPI:
    service = service or AnswerService(SafetyNavigator(DisabledPath()))
    application = FastAPI(
        title="LAi private prototype",
        version=__version__,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    application.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]", "testserver"]
    )

    @application.middleware("http")
    async def private_headers(request: Request, call_next: Any) -> Response:
        response: Response = await call_next(request)
        response.headers.update(
            {
                "Cache-Control": "no-store",
                "Referrer-Policy": "no-referrer",
                "X-Content-Type-Options": "nosniff",
                "Content-Security-Policy": (
                    "default-src 'none'; script-src 'self'; style-src 'self'; "
                    "connect-src 'self'; base-uri 'none'; form-action 'self'; "
                    "frame-ancestors 'none'"
                ),
                "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            }
        )
        return response

    @application.exception_handler(RequestValidationError)
    async def validation_failure(request: Request, error: RequestValidationError) -> JSONResponse:
        return JSONResponse({"error": "invalid_request"}, status_code=422)

    @application.get("/health")
    def health() -> dict[str, str | bool]:
        return {"status": "prototype", "version": __version__, "navigator_enabled": False}

    @application.get("/")
    def home() -> HTMLResponse:
        return HTMLResponse(files("lai.answers").joinpath("ui/index.html").read_text())

    @application.get("/assets/app.css")
    def stylesheet() -> Response:
        return Response(
            files("lai.answers").joinpath("ui/app.css").read_bytes(), media_type="text/css"
        )

    @application.get("/assets/app.js")
    def script() -> Response:
        return Response(
            files("lai.answers").joinpath("ui/app.js").read_bytes(), media_type="text/javascript"
        )

    @application.get("/api/capabilities")
    def capabilities() -> dict[str, object]:
        as_of = datetime.now(ZoneInfo("Asia/Colombo")).date()
        languages: tuple[DisplayLanguage, ...] = ("en", "si")
        return {
            "public_launch_enabled": False,
            "private_navigation_configured": service.navigator.policy.research_navigation_enabled,
            "copy_reviewed": {
                language: service.copy_ready(language, as_of) for language in languages
            },
            "display_languages": ["si", "en"],
        }

    @application.get("/assets/labels.json")
    def labels() -> Response:
        return Response(
            files("lai.answers").joinpath("ui/labels.json").read_bytes(),
            media_type="application/json",
        )

    @application.post("/api/answers", response_model=AnswerDocument)
    async def answer(request: Request) -> Response:
        if request.url.query:
            return JSONResponse({"error": "query_parameters_not_allowed"}, status_code=400)
        origin = request.headers.get("origin")
        if origin and origin.rstrip("/") != str(request.base_url).rstrip("/"):
            return JSONResponse({"error": "origin_not_allowed"}, status_code=403)
        if request.headers.get("content-type", "").split(";", 1)[0].lower() != "application/json":
            return JSONResponse({"error": "json_required"}, status_code=415)
        length = request.headers.get("content-length")
        if length is not None:
            try:
                count = int(length)
                if count < 0:
                    raise ValueError("invalid_length")
            except ValueError:
                return JSONResponse({"error": "invalid_request"}, status_code=400)
            if count > MAX_BODY_BYTES:
                return JSONResponse({"error": "request_too_large"}, status_code=413)
        try:
            body = bytearray()
            async for part in request.stream():
                if len(body) + len(part) > MAX_BODY_BYTES:
                    return JSONResponse({"error": "request_too_large"}, status_code=413)
                body.extend(part)
            payload = json.loads(body, object_pairs_hook=unique_object)
            pending = [(payload, 0)]
            while pending:
                value, depth = pending.pop()
                if depth > 16:
                    raise ValueError("json_depth_exceeded")
                children = (
                    value.values()
                    if isinstance(value, dict)
                    else value
                    if isinstance(value, list)
                    else ()
                )
                pending.extend((child, depth + 1) for child in children)
        except Exception:
            return JSONResponse({"error": "invalid_json"}, status_code=400)
        try:
            result = service.answer(payload, datetime.now(ZoneInfo("Asia/Colombo")).date())
            return JSONResponse(result.model_dump(mode="json"))
        except Exception:
            return JSONResponse({"error": "answer_unavailable"}, status_code=503)

    return application


app = create_app()
