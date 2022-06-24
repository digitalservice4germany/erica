import logging
import time

from fastapi import FastAPI, Request
from fastapi_sqlalchemy import DBSessionMiddleware
from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from erica.api.exception_handling import generate_exception_handlers
from erica.api.v2.api_v2 import api_router_02
from erica.config import get_settings
from erica.erica_legacy.api.api import api_router
from erica.erica_legacy.pyeric.eric import verify_using_stick
from erica.infrastructure.sqlalchemy.database import engine_args

app = FastAPI(
    title="Erica Service",
    version="2.0.0",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)
app.exception_handlers = generate_exception_handlers(app)


class DongleStatus:
    """
    Instrumentation helper to regularly check whether we still have a connection to the dongle.
    Caches results and only checks in fixed intervals to avoid performance penalties.
    """

    check_interval_in_seconds = 60
    last_checked = 0
    dongle_up_status = 1.0

    @classmethod
    def get(cls):
        now = time.time()
        if now - cls.last_checked > cls.check_interval_in_seconds:
            cls.dongle_up_status = 1.0 if verify_using_stick() else 0.0
            cls.last_checked = now

        return cls.dongle_up_status


if get_settings().dongle_connected:
    # Add a metric from prometheus_client - these are automatically exported by the instrumentator.
    up_metric = Gauge('up', 'Is the job available', ['job'])
    up_metric.labels(job='erica').set(1.0)  # Always 1 when the erica_app is running.
    up_metric.labels(job='dongle').set_function(DongleStatus.get)

    # Add router
    app.include_router(api_router)

app.include_router(api_router_02)

app.add_middleware(DBSessionMiddleware, db_url=get_settings().database_url, engine_args=engine_args)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # TODO Remove the split once v1 is no longer in use
    #  Split after tax_number_validity to not log any tax number information contained in the URL
    if len(request.url.path.split("tax_number_validity", 1)) > 1:
        stripped_request_url_path = request.url.path.replace(request.url.path.split("tax_number_validity", 1)[1], "")
    else:
        stripped_request_url_path = request.url.path
    logging.getLogger().info(f"Erica got request at request path={stripped_request_url_path}")

    response = await call_next(request)

    return response

# Add default metrics and expose endpoint.
Instrumentator().instrument(app).expose(app)

# Sentry error tracking
try:
    if get_settings().sentry_dsn_api:
        sentry_sdk.init(
            dsn=get_settings().sentry_dsn_api,
            environment=get_settings().env_name,
        )
        app.add_middleware(SentryAsgiMiddleware)
except Exception as e:
    # pass silently if the Sentry integration failed
    logging.getLogger().warn(f"Sentry integration failed to load: {e}")
    pass
