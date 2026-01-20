class Users:
    """
    Clase Entidad que representa a un Usuario en el sistema.
    Se usa para transportar datos entre el Servicio y el Repositorio.
    """
    def __init__(self, id, name, lastname, email, password, role_id):
        self.id = id
        self.name = name
        self.lastname = lastname
        self.email = email
        self.password = password
        self.role_id = role_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'lastname': self.lastname,
            'email': self.email,
            'role_id': self.role_id
        }