from library_db import create_app
from library_db.logger import RequestHandler

app = create_app()

if __name__ == "__main__":
    app.run(request_handler=RequestHandler)
