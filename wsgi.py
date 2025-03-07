"""
WSGI entry point for production deployments

This file allows the application to be deployed with WSGI servers
like Gunicorn or uWSGI.
"""

from app import app

if __name__ == "__main__":
    app.run()