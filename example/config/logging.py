config = {
    "default": "stack",
    "channels": {
        "stack": {"driver": "stack", "channels": ["console", "file"]},
        "console": {"driver": "console"},
        "file": {"driver": "file", "path": "storage/logs/app.log"},
    },
}
