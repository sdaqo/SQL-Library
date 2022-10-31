from library_db import create_app
from library_db.logger import RequestHandler

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", request_handler=RequestHandler, debug=True)
