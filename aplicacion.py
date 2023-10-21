import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from tinydb import TinyDB, Query

# Inicializa la base de datos para usuarios y gastos e ingresos
db_users = TinyDB('usuarios.json')
db_data = TinyDB('data.json')

# Inicializar la variable de sesión para el nombre de usuario
if 'username' not in st.session_state:
    st.session_state.username = None

# Obtener el nombre de usuario actual después del inicio de sesión
def get_current_user():
    return st.session_state.username

# Función para cargar o crear un archivo CSV para el usuario actual
def get_user_data(username):
    user_data_filename = f"{username}_data.csv"
    if not os.path.exists(user_data_filename):
        # Si el archivo no existe, crea un DataFrame vacío
        return pd.DataFrame({'Fecha': [], 'Tipo': [], 'Categoría': [], 'Monto': []})
    else:
        # Si el archivo existe, carga los datos desde el archivo CSV
        return pd.read_csv(user_data_filename)

# Función para registrar un nuevo usuario
def registrar_usuario(username, password):
    User = Query()
    # Verifica si el usuario ya existe en la base de datos
    if db_users.search(User.username == username):
        return False, "El usuario ya existe. Por favor, elija otro nombre de usuario."

    # Agrega el nuevo usuario a la base de datos
    db_users.insert({'username': username, 'password': password})

    return True, "Registro exitoso. Ahora puede iniciar sesión."


# Función para verificar credenciales
def verificar_credenciales(username, password):
    User = Query()
    # Busca el usuario en la base de datos
    user = db_users.get((User.username == username) & (User.password == password))
    if user:
        return True, "Inicio de sesión exitoso."
    else:
        return False, "Credenciales incorrectas. Por favor, verifique su nombre de usuario y contraseña."

# Función para mostrar los gastos e ingresos del usuario actual
def mostrar_gastos_ingresos():
    username = st.session_state.username
    User = Query()
    user_data = db_data.search(User.username == username)
    st.write(f"Gastos e Ingresos de {username}:")

    # Convierte los datos en un DataFrame de pandas
    df = pd.DataFrame(user_data)

    # Muestra el DataFrame en forma de tabla
    st.write(df)

# Título de la aplicación
st.title("Seguimiento de Gastos Personales")

# Menú desplegable en la barra lateral
menu_option = st.sidebar.selectbox("Menú", ["Inicio", "Registro", "Cerrar Sesión"])  # Agregar la opción "Cerrar Sesión"

# Si el usuario elige "Cerrar Sesión", restablecer la variable de sesión a None
if menu_option == "Cerrar Sesión":
    st.session_state.username = None
    st.success("Sesión cerrada con éxito. Por favor, inicie sesión nuevamente.")

# Si el usuario ya ha iniciado sesión, mostrar los botones
if get_current_user() is not None:
    st.write(f"Bienvenido, {get_current_user()}!")

    # Botones para registrar gasto, ingreso o ver registros
    option = st.selectbox("Selecciona una opción:", ["", "Registrar Gasto", "Registrar Ingreso"])
    if option == "":
        st.header("El ahorro es la semilla que plantas hoy para cosechar un futuro financiero más sólido y seguro.")
    if option == "Registrar Gasto":
        st.header("Registrar Gasto")
        with st.form("registrar_gasto_form"):
            fecha = st.date_input("Fecha del Gasto")
            # Cambiar el campo de texto por un menú desplegable para la categoría
            categoria_gastos = st.selectbox("Seleccione la categoría:", ["Alimentación", "Cuentas y pagos", "Casa", "Transporte", "Ropa", "Salud e higiene", "Diversión", "Otros gastos"])
            monto = st.number_input("Ingrese el monto:")
            if st.form_submit_button("Registrar"):
                username = st.session_state.username
                db_data.insert({'username': username, 'Fecha': str(fecha), 'Tipo': 'Gasto', 'Categoría': categoria_gastos, 'Monto': monto})
                st.success("Gasto registrado exitosamente.")
                # Limpiar los campos después de registrar el gasto
                fecha = ""
                categoria_gastos = ""
                monto = 0.0

    # Establecer la opción del menú seleccionada en la variable de estado
    st.session_state.option = ""
    if option == "Registrar Ingreso":
        st.header("Registrar Ingreso")
        with st.form("registrar_Ingreso_form"):
            fecha = st.date_input("Fecha del Ingreso")
            categoria_ingresos = st.selectbox("Seleccione la categoría:", ['Salario', 'Varios'])
            monto = st.number_input("Ingrese el monto:")
            if st.form_submit_button("Registrar"):
                username = st.session_state.username
                db_data.insert({'username': username, 'Fecha': str(fecha), 'Tipo': 'Ingreso', 'Categoría': categoria_ingresos, 'Monto': monto})
                st.success("Ingreso registrado exitosamente.")
    if st.button("Ver Gastos e Ingresos"):
        mostrar_gastos_ingresos()
else:
    # Inicio de sesión
    if menu_option == "Inicio":
        st.write("Bienvenido al inicio de la aplicación.")

        # Campos de inicio de sesión
        username = st.text_input("Nombre de Usuario:")
        password = st.text_input("Contraseña:", type="password")

        if st.button("Iniciar Sesión"):
            login_successful, message = verificar_credenciales(username, password)
            if login_successful:
                st.success(message)
                # Almacenar el nombre de usuario en la sesión
                st.session_state.username = username  
            else:
                st.error(message)
    elif menu_option == "Registro":
        st.write("Registro de Usuario")

        # Campos de registro
        new_username = st.text_input("Nuevo Nombre de Usuario:")
        new_password = st.text_input("Nueva Contraseña:", type="password")

        #Boton de registro de usuario
        if st.button("Registrarse"):
            registration_successful, message = registrar_usuario(new_username, new_password)
            if registration_successful:
                st.success(message)
            else:
                st.error(message)
    elif menu_option == "Salir":
        st.balloons()
        st.stop()