#Se importan las librerias necesarias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from tinydb import TinyDB, Query
import base64
from io import BytesIO
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#from forex_python.converter import CurrencyRates

# Cargar el CSS personalizado
with open("custom.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Función para crear un gráfico de barras por categorías de gastos e ingresos (Sebastian)
def crear_grafico_barras_categorias():
    '''Esta funcion realiza un gráfico de barras de la 
    gastos sumatoria de ingresos por categoria que
    haya tenido el usuario
    '''
    User = Query()
    username = st.session_state.username
    user_data = db_data.search(User.username == username)

    # Filtrar datos de gastos e ingresos
    categorias_gastos = {}
    categorias_ingresos = {}

    for d in user_data:
        if d['Tipo'] == 'Gasto':
            categoria = d['Categoría']
            monto = d['Monto']
            if categoria in categorias_gastos:
                categorias_gastos[categoria] += monto
            else:
                categorias_gastos[categoria] = monto
        elif d['Tipo'] == 'Ingreso':
            categoria = d['Categoría']
            monto = d['Monto']
            if categoria in categorias_ingresos:
                categorias_ingresos[categoria] += monto
            else:
                categorias_ingresos[categoria] = monto

    # Nos ayudamos de el tipo de dato set para poder crear la lista completa
    # De categorías
    categorias_g = set(list(categorias_gastos.keys()))
    categorias_i = set(list(categorias_ingresos.keys()))
    categorias = list(categorias_g.union(categorias_i))
    gastos = [categorias_gastos[categoria] if categoria in categorias_gastos else 0 for categoria in categorias]
    ingresos = [categorias_ingresos[categoria] if categoria in categorias_ingresos else 0 for categoria in categorias]

    # Posiciones en el eje x
    x = np.arange(len(categorias))

    # Ancho de las barras
    width = 0.35

    # Crear el gráfico de barras
    fig, ax = plt.subplots()
    # Primero graficamos gastos y luego ingresos
    ax.bar(x - width/2, gastos, width, label='Gastos', color='red')
    ax.bar(x + width/2, ingresos, width, label='Ingresos', color='green')

    ax.set_xlabel('Categorías')
    ax.set_ylabel('Monto')
    ax.set_title(f'Gastos e Ingresos por Categoría de {username}')
    ax.set_xticks(x)
    ax.set_xticklabels(categorias, rotation=45, ha="right")
    ax.legend()

    st.pyplot(fig)


# Función para enviar un correo electrónico
def enviar_correo(destinatario, asunto, cuerpo):
    ''' Esta funcion envia correo segun el destinatario, el asunto y el cuerpo
    Usando servidores TTS para el envio de ellos , usando contraseña de aplicacion y el correo
    '''

    #Puerto y Servidor
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Usuario y contraseña de correo
    smtp_username = 'gerenciafinanzapp@gmail.com'  
    smtp_password = 'ejla icim yzls rfpy'  
    # Crear el mensaje MIME
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = destinatario
    msg['Subject'] = asunto

    # Adjuntar el cuerpo del correo al mensaje con codificación UTF-8
    body = cuerpo.encode('utf-8')
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    context = ssl.create_default_context()
    try:
        # Iniciar conexión con el servidor SMTP de Gmail utilizando TLS
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(smtp_username, smtp_password)
            
            # Enviar el correo con el mensaje MIME como string
            server.sendmail(smtp_username, destinatario, msg.as_string())

        st.success("Correo enviado con éxito")

    except Exception as e:
        st.error(f"Error al enviar el correo: {e}")

# Función para crear un gráfico de torta de gastos e ingresos (Sebastian)
def crear_grafico_barras_gastos_ingresos():
    '''Esta funcion realiza un gráfico de barras de de la sumatoria
    de gastos e ingresos que haya tenido el usuario
    '''
    User= Query()
    username = st.session_state.username
    user_data = db_data.search(User.username == username)
    
    # Filtrar datos de gastos e ingresos
    gastos = [d['Monto'] for d in user_data if d['Tipo'] == 'Gasto']
    ingresos = [d['Monto'] for d in user_data if d['Tipo'] == 'Ingreso']
    
    # Calcular el total de gastos e ingresos
    total_gastos = sum(gastos)
    total_ingresos = sum(ingresos)
    
    # Crear el gráfico de barras
    labels = ['Gastos', 'Ingresos']
    values = [total_gastos, total_ingresos]
    colors = ['red', 'green']
    
    fig, ax = plt.subplots()
    ax.bar(labels, values, color=colors)
    ax.set_ylabel('Porcentaje')
    st.pyplot(fig)

# Función para descargar los datos en formato Excel
def descargar_datos_excel(df):
    '''Esta Funcion permite descargar los datos de cada usuario en un excel
    '''
# Crear un buffer de BytesIO para escribir el archivo Excel
    output = BytesIO()

    # Inicializar el escritor para el archivo Excel
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    try:
        # Escribe el DataFrame en el archivo Excel
        df.to_excel(writer, index=False)

        # Cerrar el escritor para finalizar el proceso de escritura
        writer.close()

        # Lee los datos del buffer
        excel_data = output.getvalue()

        # Codifica los datos en base64 para descargar el archivo
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="datos.xlsx">Descargar archivo Excel</a>'

        # Muestra el enlace para descargar el archivo en la app de Streamlit
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al intentar descargar los datos: {e}")

# Obtener el nombre de usuario actual después del inicio de sesión
def get_current_user():
    '''Esta funcion obtiene el nombre del usuario actual despues
    del inicio de sesion
    '''
    return st.session_state.username


# Función para registrar un nuevo usuario
def registrar_usuario(username, password, first_name, last_name, email, confirm_password):
    '''Esta funcion usa la libreria tinydb para registrar un usuario en un archivo llamado
    db_users
    '''
    User = Query()
    # Verifica si el usuario ya existe en la base de datos
    if db_users.search(User.username == username):
        return False, "El usuario ya existe. Por favor, elija otro nombre de usuario."

    # Verifica si las contraseñas coinciden
    if password != confirm_password:
        return False, "Las contraseñas no coinciden. Por favor, vuelva a intentar."

    # Agrega el nuevo usuario a la base de datos
    db_users.insert({'username': username, 'password': password, 'first_name': first_name, 'last_name': last_name, 'email': email})

    return True, "Registro exitoso. Ahora puede iniciar sesión."


# Función para verificar credenciales
def verificar_credenciales(username, password):
    '''Esta funcion recibe como argumento el username y el password y verifica que
    sean inguales para permitir el ingreso al sistema
    '''
    User = Query()
    # Busca el usuario en la base de datos
    user = db_users.get((User.username == username) & (User.password == password))
    if user:
        return True, "Inicio de sesión exitoso."
    else:
        return False, "Credenciales incorrectas. Por favor, verifique su nombre de usuario y contraseña."


# Función para mostrar los gastos e ingresos del usuario actual
def mostrar_gastos_ingresos():
    '''Esta funcion hace un filtrado en db_data segun el usuario en ese momento y 
    muestra los gastos e ingresos
    '''
    username = st.session_state.username
    User = Query()
    user_data = db_data.search(User.username == username)
    st.write(f"Gastos e Ingresos de {username}:")

    # Convierte los datos en un DataFrame de pandas
    df = pd.DataFrame(user_data)

    # Muestra el DataFrame en forma de tabla
    st.write(df)
    crear_grafico_barras_gastos_ingresos()

    

def crear_fon_com(usernam, fon_name, members):
    """La función obtiene como primer parametro el username
    de el usuario actual de la aplicación, el nombre de el fondo que desea
    establecer al fondo a crear y los miembros que serán añadidos al 
    fondo"""
    # Añadimos el fondo común a la base de datos con la función
    # Insert pero primero creamos un diccionario donde el valor
    # por defecto del aporte de todos los miembros sea 0
    members = members.split(", ")
    members.append(usernam)
    mem_dic = dict(zip(members, [0] * len(members)))
    
    # Insertamos en la base de datos la información necesaria
    # para crear el fondo común y su historial
    db_us_fon_com.insert({"username": usernam, "fon_name": fon_name, "members": mem_dic})
    db_his_fon_com.insert({"username": usernam, "fon_name": fon_name, "historial": []})

def mostrar_fon_com(fon_elegido):
    """La función obtiene como parámetro de entrada
    el nombre de el fondo elegido a mostrar e internamente 
    realiza todos los procedimientos para graficarlo"""
    
    # Realizamos la búsqueda en la base de datos con las
    # dos llaves que vuelven única la busqueda, que son el 
    # username del usuario y el nombre de el fondo elegido
    User = Query()
    username = st.session_state.username
    fon_data = db_us_fon_com.search(
        (User.username == username) & (User.fon_name == fon_elegido))
    
    # Accedemos a los miembros de el fondo común
    # y nos ayudamos de el tipo de dato pandas.Series
    # para imprimir en pantalla
    df_mem = pd.Series(fon_data[0]["members"])
    st.write(df_mem)
    
    # Retornamos una lista de todos los nombres de
    # los miembros en el fondo ya que nos servirá 
    # para realizar el selectbox
    return(fon_data[0]["members"].keys())

def upd_fon(fon_elegido , miem, amount):
    """La función obtiene como primer parametro
    el nombre de el fondo elegido el miembro al cual se
    realizaran las modificaciones y por último el valor
    a modificar"""

    # Realizamos la búsqueda en la base de datos con las
    # dos llaves que vuelven única la busqueda, que son el 
    # username del usuario y el nombre de el fondo elegido
    User = Query()
    username = st.session_state.username
    fon_data = db_us_fon_com.search(
        (User.username == username) & (User.fon_name == fon_elegido))
    
    # Accedemos a los miembros de el fondo común
    # para poder actualizar el dato deseado
    data_act = fon_data[0]["members"]
    # Actualizamos en el diccionario el dato deseado
    data_act[miem]+=amount

    # Luego de hacer el query requerido
    # actualizamos en la base de datos la columna
    # members, sobreescribiendola con el diccionario
    # actualizado
    db_us_fon_com.update({"members": data_act}, ((User.username == username) & (User.fon_name == fon_elegido)))
    st.success("Se ha registrado correctamente")


def upd_his_fon(fon_elegido , miem, amount, description):
    """La función obtiene como primer parametro
    el nombre de el fondo elegido, el valor
    a modificar y la descripción que se guardará
    en el historial"""

    # Realizamos la búsqueda en la base de datos con las
    # dos llaves que vuelven única la busqueda, que son el 
    # username del usuario y el nombre de el fondo elegido
    User = Query()
    username = st.session_state.username
    fon_data = db_his_fon_com.search(
        (User.username == username) & (User.fon_name == fon_elegido))
    
    # Accedemos a los miembros de el fondo común
    # para poder actualizar el dato deseado
    data_act = fon_data[0]["historial"]
    # Agregamos en um diccionario el dato deseado
    data_act.append({"Miembro": miem, "Monto": amount,
                    "Descripción": description})

    # Luego de hacer el query requerido
    # actualizamos en la base de datos la columna
    # historial, sobreescribiendola la lista
    # actualizada
    db_his_fon_com.update({"historial": data_act}, ((User.username == username) & (User.fon_name == fon_elegido)))



def calculate_amortization(interest_rate, months, loan_amount):
    # Calculating the monthly interest rate
    monthly_interest_rate = interest_rate / 12 / 100
    
    # Calculating the monthly payment using the formula for an amortizing loan
    monthly_payment = (loan_amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -months)
    
    # Creating a DataFrame for the amortization schedule
    amortization_schedule = pd.DataFrame(
        columns=['Month','Payment', 'Principal',
                'Interest', 'Remaining Balance'])
    remaining_balance = loan_amount
    
    for month in range(1, months + 1):
        interest = remaining_balance * monthly_interest_rate
        principal = monthly_payment - interest
        remaining_balance -= principal
        
        amortization_schedule = amortization_schedule._append({
            'Month': month,
            'Payment': monthly_payment,
            'Principal': principal,
            'Interest': interest,
            'Remaining Balance': remaining_balance
        }, ignore_index=True)

    amortization_schedule.rename({"Month": "Mes", "Payment": "Pago",
                                "Pricipal": "Abono a deuda", "Interest": "Abono a interes",
                                "remaining_balance": "Deuda actual"})
    return monthly_payment, amortization_schedule





# Inicializa la base de datos para usuarios, gastos e ingresos
# y fondos comunes
db_users = TinyDB('usuarios.json')
db_data = TinyDB('data.json')
db_us_fon_com = TinyDB('us_fon_com.json')
db_his_fon_com = TinyDB('db_his_fon_com.json')
# Inicializar la variable de sesión para el nombre de usuario
if 'username' not in st.session_state:
    st.session_state.username = None

# Título de la aplicación
st.title("Seguimiento de Gastos Personales")

# Menú desplegable en la barra lateral
if get_current_user() is not None:
    # Sidebar menu options for logged-in users
    menu_option = st.sidebar.selectbox("Menú", ["Pagina Principal", "Registrar Gasto",
                                                "Registrar Ingreso", "Mostrar Gastos e Ingresos",
                                                "Crear Fondo Común", "Fondos comunes",
                                                "Descargar Gastos e Ingresos", "Cerrar Sesión",
                                                "Calculadora de Préstamos"])
else:
    # Sidebar menu options for non-logged-in users
    menu_option = st.sidebar.selectbox("Menú", ["Inicio", "Inicio de Sesion", "Registro","Conversion de Moneda",
                                                "Calculadora de Préstamos"])

# Si el usuario elige "Cerrar Sesión", restablecer la variable de sesión a None
if menu_option == "Cerrar Sesión":
    st.session_state.username = None
    st.success("Sesión cerrada con éxito. Por favor, inicie sesión nuevamente.")

# Si el usuario ya ha iniciado sesión, mostrar los botones
if get_current_user() is not None:
    username = st.session_state.username
    User = Query()
    user_data = db_data.search(User.username == username)
    # Convierte los datos en un DataFrame de pandas
    df = pd.DataFrame(user_data)
    if menu_option == "Pagina Principal":
        username = get_current_user()
        st.write(f'<h4 style="font-size: 26px; font-weight: bold; text-align: center;">Hola {username}!</h4>', unsafe_allow_html=True)

        # Calculate total expenses and income for the user
        User = Query()
        user_data = db_data.search(User.username == username)
        gastos = sum(d['Monto'] for d in user_data if d['Tipo'] == 'Gasto')
        ingresos = sum(d['Monto'] for d in user_data if d['Tipo'] == 'Ingreso')

        # Display the total expenses and income
        st.write(f"<h4 style='font-size: 26px;'>En total te has gastado: {gastos}</h4>", unsafe_allow_html=True)
        st.write(f"<h4 style='font-size: 26px;'>Has tenido unos ingresos por el valor de: {ingresos}</h4>", unsafe_allow_html=True)


    # Botones para registrar gasto, ingreso o ver registros
    if menu_option == "Registrar Gasto":
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
    if menu_option == "Registrar Ingreso":
        st.header("Registrar Ingreso")
        with st.form("registrar_Ingreso_form"):
            fecha = st.date_input("Fecha del Ingreso")
            categoria_ingresos = st.selectbox("Seleccione la categoría:", ['Salario', 'Varios'])
            monto = st.number_input("Ingrese el monto:")
            if st.form_submit_button("Registrar"):
                username = st.session_state.username
                db_data.insert({'username': username, 'Fecha': str(fecha), 'Tipo': 'Ingreso', 'Categoría': categoria_ingresos, 'Monto': monto})
                st.success("Ingreso registrado exitosamente.")

    if menu_option == "Mostrar Gastos e Ingresos":
        mostrar_gastos_ingresos()
        crear_grafico_barras_categorias()

    if menu_option == "Crear Fondo Común":
        st.header("Crear Fondo Común")
        fon_name = st.text_input("Nombre del Fondo Común:")
        Members = st.text_input("Integrantes del fondo(Por favor separar cor\
                                coma y espacio)")
        if st.button("Registrar"):
            crear_fon_com(st.session_state.username, fon_name, Members)
            st.success("El fondo ha sido creado")

    if menu_option == "Fondos comunes":
        # Realizamos un query al sistema para verificar
        # si el usuario posee fondos comunes, de lo contrario
        # se saltara al else
        
        st.header("Tus Fondos Comunes")
        User = Query()
        username = st.session_state.username
        fon_data = db_us_fon_com.search(User.username == username)

        if fon_data:
            User = Query()
            username = st.session_state.username
            fon_data = db_us_fon_com.search(User.username == username)
            df =  pd.DataFrame(fon_data)
            lista = df["fon_name"].to_list()
            selected_fon = st.selectbox("Elija el fondo al que desee acceder",
                        lista)
            if selected_fon:
                User = Query()
                username = st.session_state.username
                fon_data = db_us_fon_com.search(
                (User.username == username) & (User.fon_name == selected_fon))
                df_mem = pd.Series(fon_data[0]["members"])
                st.write(df_mem)
                lista = fon_data[0]["members"].keys()
                miem = st.selectbox('Seleccione el miembro', lista)
                amount = st.number_input('Ingresa la cantidad que deseas añadir o retirar', min_value=1.0, step=1.0)
                description = st.text_input("Añada una descripción para el historial")

                Users = Query()
                username = st.session_state.username
                fon_hist = db_his_fon_com.search(
                (Users.username == username) & (Users.fon_name == selected_fon))
                df_his = pd.DataFrame(fon_hist[0]["historial"])
                st.write(df_his)

            if st.button("Actualizar"):
                upd_fon(selected_fon, miem, amount)
                upd_his_fon(selected_fon, miem, amount, description)
            

        else:
            st.write("Aún no tienes un fondo común, \
                    anímate a crear uno")

    if menu_option == "Descargar Gastos e Ingresos":
        st.header("Descarga Aca tus datos para tu gestion en Casa ¡Animate!")
        descargar_datos_excel(df)


    if menu_option == "Calculadora de Préstamos":
        st.write("Calculadora de Préstamos")
        

        interest_rate = st.number_input('Tasa de interés anual (%)',
                                        min_value=0.01, value=5.0, step=0.01)
        months = st.number_input('Número de meses', min_value=1,
                                value=12, step=1)
        loan_amount = st.number_input('Monto del préstamo',
                                    min_value=1.0, value=1000.0, step=1.0)

        if st.button('Calcular'):
            monthly_payment, amortization_table = calculate_amortization(
                interest_rate, months, loan_amount)
            
            st.subheader('Detalles del Préstamo')
            st.write(f'Monto del préstamo: {loan_amount}')
            st.write(f'Tasa de interés anual: {interest_rate}%')
            st.write(f'Número de meses: {months}')
            st.write(f'Cuota mensual: {monthly_payment:.2f}')
            
            st.subheader('Tabla de Amortización')
            st.write(amortization_table)


else:

    if menu_option == "Inicio":
        # Enlace a consejos financieros
        st.header("Consejos Financieros")
        st.write("Aquí encontrarás consejos financieros útiles para mejorar tus finanzas personales.")
        st.write("1. Ahorra una parte de tus ingresos cada mes.")
        st.write("2. Crea un presupuesto y ajústate a él.")
        st.write("3. Paga tus deudas a tiempo.")
        st.write("4. Invierte tu dinero sabiamente.")
        st.write("5. Educa tu mente financiera.")

        # Enlace a videos de YouTube
        st.header("Ahorrar no es solo guardar, sino tambien, saber gastar")
        st.write('<h4 style="font-size: 26px; color: #000000; font-family: cursive; font-weight: bold; text-align: center;">Y para ti... ¿Qué es ahorrar?</h4>', unsafe_allow_html=True)

        st.video("https://www.youtube.com/watch?v=KDxhvehEius&ab_channel=MedallaMilagrosa")

        st.write('<h4 style="font-size: 26px; color: #000000; font-family: cursive; font-weight: bold; text-align: center;">Tan facil como jugar... es ahorrar</h4>', unsafe_allow_html=True)

        st.video("https://www.youtube.com/watch?v=gqtojhFaSlE&ab_channel=Bancolombia")

        st.write('<h4 style="font-size: 26px; color: #000000; font-family: cursive; font-weight: bold; text-align: center;">Y... ¿Sabes que es un ciclo economico?</h4>', unsafe_allow_html=True)

        st.video("https://www.youtube.com/watch?v=7jklUV3QE70&list=PLYV86yxR8Np89gAhNR8LTpSe7_QthTMHY&index=4&ab_channel=MedallaMilagrosa")

        st.write('<h2 style="font-size: 30px; color: #000000; font-family: cursive; font-weight: bold; text-align: center;">¡Prepara tu camino hacia un futuro financiero más sólido! Regístrate ahora.</h2>', unsafe_allow_html=True)
    
    # Inicio de sesión
    elif menu_option == "Inicio de Sesion":
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

            elif not login_successful:
                st.error(message)

            elif st.button("Olvidaste la contraseña"):

                st.write("Olvidaste tu Contraseña")

                # Campos para ingresar el nombre de usuario y el correo electrónico
                username_forgot = st.text_input("Nombre de Usuario:")
                email_forgot = st.text_input("Correo Electrónico:")

                if st.button("Enviar Correo de Restablecimiento"):
                    # Verifica si el usuario y el correo coinciden en la base de datos
                    User = Query()
                    user_info = db_users.get((User.username == username_forgot) & (User.email == email_forgot))

                    if user_info:
                        # Recupera la contraseña existente del usuario
                        contrasena_actual = user_info['password']

                        # Envia un correo electrónico con la contraseña existente
                        destinatario = email_forgot
                        asunto = 'Recuperación de Contraseña - Finanzapp'
                        cuerpo = f'Tu contraseña actual es: {contrasena_actual}.\n\nRecuerdala, Recuerda que es personal e intransferible'

                        enviar_correo(destinatario, asunto, cuerpo)

                        st.success("Se ha enviado un correo con tu contraseña actual.")
                    else:
                        st.error("El usuario o el correo electrónico no existen en la base de datos..")
            

    elif menu_option == "Calculadora de Préstamos":
        st.write("Calculadora de Préstamos")
        

        interest_rate = st.number_input('Tasa de interés anual (%)',
                                        min_value=0.01, value=5.0, step=0.01)
        months = st.number_input('Número de meses', min_value=1,
                                value=12, step=1)
        loan_amount = st.number_input('Monto del préstamo',
                                    min_value=1.0, value=1000.0, step=1.0)

        if st.button('Calcular'):
            monthly_payment, amortization_table = calculate_amortization(
                interest_rate, months, loan_amount)
            
            st.subheader('Detalles del Préstamo')
            st.write(f'Monto del préstamo: {loan_amount}')
            st.write(f'Tasa de interés anual: {interest_rate}%')
            st.write(f'Número de meses: {months}')
            st.write(f'Cuota mensual: {monthly_payment:.2f}')
            
            st.subheader('Tabla de Amortización')
            st.write(amortization_table)

    elif menu_option == "Registro":
        st.write("Registro de Usuario")

        # Campos de registro
        first_name = st.text_input("Nombre del Usuario:")
        last_name = st.text_input("Apellidos del Usuario:")
        email = st.text_input("Correo electronico del Usuario:")
        new_username = st.text_input("Nuevo Nombre de Usuario:")
        new_password = st.text_input("Nueva Contraseña:", type = "password")
        confirm_password = st.text_input("Confirmar contraseña:", type = "password")

        # Crear dos columnas para los botones
        col1, col2 = st.columns(2)
        # Casilla de verificación para aceptar la política de datos personales
        # Inicializa la variable aceptar_politica
        
        # Variable de estado para rastrear si el usuario ha visto la política
        if 'politica_vista' not in st.session_state:
            st.session_state.politica_vista = False

        # Botón para abrir la ventana emergente en la segunda columna
        if col2.button("Ver Política de Tratamiento de Datos"):
            with open("politica_datos.txt", "r") as archivo:
                politica = archivo.read()
                with st.expander("Política de Tratamiento de Datos",expanded=True):
                    st.write(politica)
                    st.session_state.politica_vista = True
                # Casilla de verificación para aceptar la política
        aceptar_politica = st.checkbox("Acepta la política de datos personales")

        # Botón de registro de usuario en la primera columna
        if col1.button("Registrarse") and aceptar_politica and st.session_state.politica_vista:
            registration_successful, message = registrar_usuario(new_username, new_password, first_name, last_name, email, confirm_password)
            if registration_successful:
                st.success(message)
                destinatario = email  
                asunto = 'Registro Exitoso Finanzapp'
                cuerpo = (f'Hola {first_name} ,  Te damos la bienvenida a finanzapp\n Estamos muy felices de que estes con nostros, Ahora podras registrar tus gastos e ingresos, podras verificar graficos y mucho mas...\n Tu Usuario es: {new_username} \n Tu contrasena es: {new_password} \n Es un placer que estes con nostros, Recuerda que ahorrando con Finanzapp, te rinde mas el dinero... ')

                enviar_correo(destinatario, asunto, cuerpo)
            else:
                st.error(message)

        if not aceptar_politica:
            st.warning("Por favor, acepta la política de datos personales antes de registrarte.")

        if not st.session_state.politica_vista:
            st.warning("Por favor, ve la política de datos personales antes de registrarte.")

    elif menu_option == "Salir":
        st.balloons()
        st.stop()

# Botón acerca de nosotros esquina inferior derecha (Sebastian)
st.markdown('<a class="popup-button" href="https://docs.google.com/document/d/e/2PACX-1vTNHzaSOTiy_uLe8uhSkzz12P_emSLGI7usf53F10noX3W-PfVVBK8PEXUizMSwi-zFPD1hEykVAxpZ/pub" target="_blank">Acerca de nosotros</a>',
            unsafe_allow_html=True)