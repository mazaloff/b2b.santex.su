import os
import time
import psutil
import cherrypy
import cheroot.wsgi as wsgi_server
from Project.wsgi import application
from Project import settings_local as settings


def server_http():
    # Mount the application
    cherrypy.tree.graft(application, "/")

    # Unsubscribe the default server
    cherrypy.server.unsubscribe()

    # Instantiate a new server object
    server = cherrypy._cpserver.Server()

    # Configure the server object
    server.socket_host = "127.0.0.1"
    server.socket_port = 8080
    server.thread_pool = 30

    # For SSL Support
    # server.ssl_module = 'pyopenssl'
    # server.ssl_certificate = 'ssl/certificate.crt'
    # server.ssl_private_key = 'ssl/private.key'
    # server.ssl_certificate_chain = 'ssl/bundle.crt'
    # Subscribe this server
    server.subscribe()

    # Example for a 2nd server (same steps as above):
    # Remember to use a different port
    server_api = cherrypy._cpserver.Server()

    # Configure the server object
    server_api.socket_host = "127.0.0.1"
    server_api.socket_port = 8081
    server_api.thread_pool = 31
    server_api.subscribe()

    # Start the server engine (Option 1 *and* 2)
    cherrypy.engine.start()
    cherrypy.engine.block()


def server_wsgi(address, num_threads=10, server_name=None):
    s1_wsgi = wsgi_server.Server(address, application, num_threads, server_name)
    s1_wsgi.start()


def terminate_server(name_server):
    pid_file = os.path.join(settings.BASE_DIR, f'server_{name_server}.pid')
    if os.path.exists(pid_file):
        with open(pid_file, 'r+') as file:
            list_str = file.readlines()
            pid = list_str[0] if len(list_str) > 0 else None
            if pid:
                list_pid = psutil.pids()
                for i in list_pid:
                    try:
                        p = psutil.Process(i)
                    except psutil.NoSuchProcess:
                        continue
                    if p.name() == 'python.exe' and pid == str(p.pid):
                        try:
                            p.terminate()
                            time.sleep(5)
                            break
                        except psutil.AccessDenied:
                            continue
        os.remove(os.path.abspath(pid_file))
