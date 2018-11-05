from Project.wsgi import application
import cherrypy
import cheroot.wsgi as wsgi_server


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
