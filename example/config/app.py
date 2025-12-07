import os

config = {
    "name": "example",
    "version": "1.0.0",
    "env": os.getenv("APP_ENV", "production"),
    "debug": os.getenv("APP_DEBUG", False),
    "timezone": "EST",
    "key": os.getenv("APP_KEY"),
}
