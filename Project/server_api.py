from Project.server import server_wsgi
import Project.settings_local as settings

if __name__ == '__main__':
    name_server = 'exchange'
    server_wsgi(settings.SERVER_ARI, 10, f'server{name_server}')
