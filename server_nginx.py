import os
from server import server_wsgi, terminate_server
from Project import settings_local as settings

if __name__ == '__main__':
    name_server = 'nginx'
    terminate_server(name_server)
    file_pid = os.path.join(settings.BASE_DIR, f'server_{name_server}.pid')
    with open(file_pid, 'w') as file:
        file.write(str(os.getpid()))
    server_wsgi(settings.SERVER_NGINX, 2, f'server{name_server}')
