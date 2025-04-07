class Usuario:
    def __init__(self, id, first_name, last_name, password):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.password = password

users = {
    'user1@gmail.com': Usuario(id=1, first_name='tonto', last_name="elquelolea", password=hash('pass1')),
    'user2@gmail.com': Usuario(id=1, first_name='tonto', last_name="elquelolea2", password=hash('pass2'))
}