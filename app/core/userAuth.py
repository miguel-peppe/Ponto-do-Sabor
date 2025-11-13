from .imports import *
from database.db import *

class Funcionario(UserMixin):
    def __init__(self, id, nome, cpf, cargo):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.cargo = cargo
        
