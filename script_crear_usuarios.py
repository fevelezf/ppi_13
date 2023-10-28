from tinydb import TinyDB, Query

db_users = TinyDB('usuarios.json')
db_users.insert({'username': "pepe", 'password':
                  "pepee", 'first_name': "pepe", 'last_name': "perez", 'email': "perez@gmail.com"})
db_users.insert({'username': "fevelezf", 'password': "Tampa.20", 'first_name':
                  "Felipe", 'last_name': "Velez", 'email': "fevelezf@unal.edu.co"})
db_users.insert({'username': "Aguinaga", 'password': "finanzapp", 'first_name':
                  "Sebastian", 'last_name': "Aguinaga", 'email': "saguinaga@unal.edu.co"})