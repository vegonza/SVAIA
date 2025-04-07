class Usuario:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = { # Simulamos una base de datos de usuarios
    'user1': Usuario(id=1, username='user1', password=hash('pass1')),
    'user2': Usuario(id=2, username='user2', password=hash('pass2'))
}