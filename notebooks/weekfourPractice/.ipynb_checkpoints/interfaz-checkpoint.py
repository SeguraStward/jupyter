import streamlit as st

# Título de la aplicación principal
st.title("Sistema Experto De Diagnostico Academico")
st.write("Responde a las preguntas para obtener tu diagnóstico.")

# 1. BARRA LATERAL (Entradas de texto)
st.sidebar.header("Informacion del Estudiante")
nombre = st.sidebar.text_input("Nombre completo")
edad = st.sidebar.number_input("Edad", min_value=15, max_value=100, value=20)
carrera = st.sidebar.text_input("Carrera que estudias")
semestre = st.sidebar.number_input("Semestre actual", min_value=1, max_value=12, value=1)

# 2. CUERPO PRINCIPAL (Los 10 hechos requeridos)
st.header("Hábitos y Situación Actual")

# Usamos componentes básicos y a prueba de fallos
horas_estudio = st.number_input("1. Horas de estudio semanales", min_value=0, max_value=50, value=10)
asistencia = st.slider("2. Porcentaje de asistencia a clases (%)", 0, 100, 80)
sueno = st.number_input("3. Horas de sueño por noche", min_value=0, max_value=12, value=7)
estres = st.slider("4. Nivel de estrés (0 = Nada, 10 = Máximo)", 0, 10, 5)

motivacion = st.selectbox("5. Nivel de motivación", ["Baja", "Media", "Alta"])
organizacion = st.selectbox("6. Nivel de organización", ["Mala", "Regular", "Buena"])

uso_celular = st.checkbox("7. ¿Usas mucho el celular mientras estudias?")
entrega_tardia = st.checkbox("8. ¿Sueles entregar trabajos tarde?")
dificultad_concentracion = st.checkbox("9. ¿Te cuesta concentrarte?")
apoyo_recibido = st.checkbox("10. ¿Cuentas con apoyo familiar o de profesores?")

# 3. BOTÓN DE ANÁLISIS
if st.button("Analizar Perfil"):
    
    st.markdown("---") # Línea separadora clásica
    st.header("Resultados del Diagnóstico")
    
    # Variables por defecto
    perfil = "Indeterminado"
    regla_activada = "Ninguna"
    
    # Motor de Inferencia (Regla de prueba simple)
    if horas_estudio > 15 and asistencia >= 90 and organizacion == "Buena":
        perfil = "Estudiante de Alto Rendimiento"
        regla_activada = "REGLA 1: Horas > 15 Y Asistencia >= 90 Y Organización = Buena"
    else:
        perfil = "Estudiante Promedio o en Riesgo"
        regla_activada = "REGLA DEFAULT: No cumple criterios de alto rendimiento"

    # 4. SECCIÓN DE RESULTADOS Y EXPLICACIÓN
    st.subheader(f"Perfil detectado para {nombre}:")
    
    # Mostrar el resultado visualmente de forma sencilla
    if perfil == "Estudiante de Alto Rendimiento":
        st.success(perfil)
    else:
        st.warning(perfil)
        
    st.write("**Explicación del sistema:**")
    st.write("- **Hechos detectados:** Horas:", horas_estudio, "| Asistencia:", asistencia, "% | Organización:", organizacion)
    st.write("- **Reglas activadas:**", regla_activada)
    st.write("- **Justificación:** El motor de inferencia analizó tus datos y disparó la regla correspondiente a tus hábitos actuales.")