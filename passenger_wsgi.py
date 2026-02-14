from a2wsgi import ASGIMiddleware
from server import app

# Pass the ASGI app to a2wsgi to create a WSGI application
application = ASGIMiddleware(app)
