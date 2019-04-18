
USER = '{{ db_user }}'
PASSWORD = '{{ db_pass }}'
HOST = '{{ db_host }}'
PORT = '{{ db_port }}'
DB = '{{ db_name }}'
DATABASE_URI = 'mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(USER, PASSWORD, HOST, PORT, DB)

