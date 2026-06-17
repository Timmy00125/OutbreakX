# config/cors.py
import os

from fastapi.middleware.cors import CORSMiddleware


def add_cors_middleware(app):
    default_origins = (
        "http://localhost:3000,http://localhost:8000,"
        "https://outbreak-x-frontend.vercel.app"
    )
    origins = [
        origin.strip()
        for origin in os.getenv("FRONTEND_ORIGINS", default_origins).split(",")
        if origin.strip()
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=r"https://outbreak-x-frontend(-[\w-]+)?\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
