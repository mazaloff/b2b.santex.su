from Project.server import server_wsgi
import Project.settings_local as settings

if __name__ == '__main__':
    name_server = 'api'
    server_wsgi(settings.SERVER_ARI, 2, f'server{name_server}')
