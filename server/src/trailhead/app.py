"""Main module for the introductory programming web server."""

__author__ = "Kris Jordan <kris@cs.unc.edu>"
__copyright__ = "Copyright 2023"
__license__ = "MIT"

import os
from fastapi import FastAPI, WebSocket
from fastapi.concurrency import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .web_socket_manager import WebSocketManager
from .file_observer import FileObserver
from .controller import web_socket_controller

web_socket_manager = WebSocketManager(web_socket_controller)
"""Web Socket Manager handles connections and dispatches to the controller."""

# Get the path of this file
__path__ = os.path.dirname(__file__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This function is called before the FastAPI web server begins, yields while
    the web server is running, then shuts down depencies when halting. It is
    responsible for starting and stopping the file observer and the web socket
    manager.
    """
    file_observer = FileObserver(".", web_socket_manager.notify)
    yield
    file_observer.stop()
    await web_socket_manager.stop()


app = FastAPI(lifespan=lifespan)
"""The FastAPI web server instance."""


@app.websocket("/ws")
async def websocket_endpoint(client: WebSocket):
    """The FastAPI web socket endpoint dispatches out to Web Socket Manager."""
    await web_socket_manager.accept(client)


app.mount("/assets", StaticFiles(directory=f"{__path__}/static/assets", html=True))
"""Static files are served from the static HTML directory."""


@app.get("/{full_path:path}")
async def read_index(full_path: str):
    return FileResponse(f"{__path__}/static/index.html")
