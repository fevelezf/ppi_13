import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Crear un DataFrame de pandas para registrar los gastos
data = {'Fecha': [], 'Categoría': [], 'Monto': []}
df = pd.DataFrame(data)

# Título de la aplicación
st.title("Seguimiento de Gastos Personales")

# Botón de "Entrar" para acceder a la aplicación
if st.button("Entrar"):
    # Menú principal
    opcion = st.selectbox("Seleccione una opción:", ["Agregar Gasto", "Calcular Estadísticas", "Salir"])

    if opcion == "Agregar Gasto":
        fecha = st.text_input("Ingrese la fecha (YYYY-MM-DD):")
        categoria = st.text_input("Ingrese la categoría del gasto:")
        monto = st.number_input("Ingrese el monto del gasto:")

        if st.button("Agregar Gasto"):
            # Agregar el gasto al DataFrame
            df.loc[len(df)] = [fecha, categoria, monto]
            st.success("Gasto agregado exitosamente.")

    elif opcion == "Calcular Estadísticas":
        if not df.empty:
            # Estadísticas generales
            promedio_total = df['Monto'].mean()
            gasto_total = df['Monto'].sum()

            # Estadísticas por categoría
            estadisticas_por_categoria = df.groupby('Categoría')['Monto'].sum()

            st.write("\nEstadísticas Generales:")
            st.write(f"Promedio Mensual: {promedio_total}")
            st.write(f"Gasto Total: {gasto_total}")

            st.write("\nEstadísticas por Categoría:")
            st.write(estadisticas_por_categoria)

            # Crear un gráfico de pastel de la distribución de gastos por categoría
            fig, ax = plt.subplots()
            ax.pie(estadisticas_por_categoria, labels=estadisticas_por_categoria.index, autopct='%1.1f%%')
            ax.set_title('Distribución de Gastos por Categoría')
            st.pyplot(fig)
        else:
            st.warning("No hay datos de gastos para calcular estadísticas.")

    elif opcion == "Salir":
        st.balloons()
        st.stop()

# Guardar los datos en un archivo CSV
if not df.empty:
    df.to_csv('gastos_personales.csv', index=False)

