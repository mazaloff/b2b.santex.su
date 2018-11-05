from server import server_wsgi
from Project import settings_local as settings

if __name__ == '__main__':
    server_wsgi(settings.SERVER_NGINX, 10, 'nginx_server')
