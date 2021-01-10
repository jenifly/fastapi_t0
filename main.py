from uvicorn import run

from core.init import get_default_app

app = get_default_app()

if __name__ == "__main__":
    run('main:app', host='127.0.0.1', port=3333, reload=True)
