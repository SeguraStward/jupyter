import streamlit as st
import json
from dataclasses import dataclass, field

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1: DEFINICIÓN DE OBJETOS DEL SISTEMA EXPERTO
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Regla:
    """Objeto que representa una regla IF-THEN del sistema experto."""

    id: str                            # Identificador único (R1, R2, ...)
    nombre: str                        # Nombre legible de la regla
    perfil: str                        # Perfil/diagnóstico que concluye
    prioridad: int                     # Prioridad (mayor = más específica)
    condiciones_texto: list            # Descripción legible de cada condición
    evaluar: object = None             # Función lambda que evalúa los hechos
    recomendaciones: list = field(default_factory=list)

    def se_cumple(self, hechos: dict) -> bool:
        """Evalúa si la regla se activa con los hechos dados."""
        try:
            return self.evaluar(hechos)
        except Exception:
            return False


@dataclass
class ResultadoInferencia:
    """Almacena el resultado completo de una inferencia."""

    perfil_principal: str
    nivel_riesgo: str           # Bajo, Medio, Alto, Crítico
    color_riesgo: str           # Color para visualización
    reglas_activadas: list
    reglas_no_activadas: list
    puntuacion: float           # 0-100
    recomendaciones: list
    hechos: dict


# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2: BASE DE REGLAS (8 reglas → 4+ perfiles)
# ═══════════════════════════════════════════════════════════════════════════════

def construir_base_reglas():
    """Retorna la lista completa de reglas del sistema experto."""

    reglas = [
        # ── PERFIL: ALTO RENDIMIENTO ──────────────────────────────────────
        Regla(
            id="R1",
            nombre="Alto rendimiento integral",
            perfil="Alto Rendimiento",
            prioridad=10,
            condiciones_texto=[
                "Horas de estudio > 15 semanales",
                "Asistencia >= 85%",
                "Organización = Buena",
                "Motivación = Alta",
                "No entrega tareas tarde",
            ],
            evaluar=lambda h: (
                h["horas_estudio"] > 15
                and h["asistencia"] >= 85
                and h["organizacion"] == "Buena"
                and h["motivacion"] == "Alta"
                and not h["entrega_tardia"]
            ),
            recomendaciones=[
                "Mantén tu ritmo actual, estás en excelente camino.",
                "Considera proyectos extracurriculares o de investigación.",
                "Podrías ser tutor o mentor para otros compañeros.",
            ],
        ),
        Regla(
            id="R2",
            nombre="Alto rendimiento con estrés manejable",
            perfil="Alto Rendimiento",
            prioridad=9,
            condiciones_texto=[
                "Horas de estudio > 12 semanales",
                "Asistencia >= 80%",
                "Estrés <= 5",
                "Sueño >= 6 horas",
                "Organización != Mala",
            ],
            evaluar=lambda h: (
                h["horas_estudio"] > 12
                and h["asistencia"] >= 80
                and h["estres"] <= 5
                and h["sueno"] >= 6
                and h["organizacion"] != "Mala"
            ),
            recomendaciones=[
                "Tu equilibrio entre estudio y descanso es adecuado.",
                "Cuida no aumentar la carga para mantener el estrés bajo.",
            ],
        ),

        # ── PERFIL: RENDIMIENTO REGULAR ───────────────────────────────────
        Regla(
            id="R3",
            nombre="Estudiante promedio estable",
            perfil="Rendimiento Regular",
            prioridad=6,
            condiciones_texto=[
                "Horas de estudio entre 8 y 15",
                "Asistencia entre 60% y 84%",
                "Motivación = Media",
            ],
            evaluar=lambda h: (
                8 <= h["horas_estudio"] <= 15
                and 60 <= h["asistencia"] <= 84
                and h["motivacion"] == "Media"
            ),
            recomendaciones=[
                "Intenta incrementar tus horas de estudio de a poco.",
                "Establece un horario fijo semanal para estudiar.",
                "Busca técnicas de estudio activo (Pomodoro, mapas mentales).",
            ],
        ),
        Regla(
            id="R4",
            nombre="Estudiante con potencial desaprovechado",
            perfil="Rendimiento Regular",
            prioridad=5,
            condiciones_texto=[
                "Motivación = Alta",
                "Organización = Mala",
                "Uso excesivo del celular",
                "Dificultad de concentración",
            ],
            evaluar=lambda h: (
                h["motivacion"] == "Alta"
                and h["organizacion"] == "Mala"
                and h["uso_celular"]
                and h["dificultad_concentracion"]
            ),
            recomendaciones=[
                "Tienes buena motivación pero necesitas organización.",
                "Usa apps de bloqueo de distracciones mientras estudias.",
                "Divide tus tareas grandes en pasos pequeños y concretos.",
            ],
        ),

        # ── PERFIL: EN RIESGO ACADÉMICO ───────────────────────────────────
        Regla(
            id="R5",
            nombre="Riesgo por hábitos deficientes",
            perfil="En Riesgo Académico",
            prioridad=7,
            condiciones_texto=[
                "Horas de estudio < 5 semanales",
                "Entrega tardía de trabajos",
                "Organización = Mala",
            ],
            evaluar=lambda h: (
                h["horas_estudio"] < 5
                and h["entrega_tardia"]
                and h["organizacion"] == "Mala"
            ),
            recomendaciones=[
                "Establece un mínimo de 1 hora diaria de estudio.",
                "Usa una agenda o calendario para tus entregas.",
                "Acude a asesorías académicas de tu institución.",
            ],
        ),
        Regla(
            id="R6",
            nombre="Riesgo por inasistencia y desmotivación",
            perfil="En Riesgo Académico",
            prioridad=7,
            condiciones_texto=[
                "Asistencia < 60%",
                "Motivación = Baja",
                "No cuenta con apoyo",
            ],
            evaluar=lambda h: (
                h["asistencia"] < 60
                and h["motivacion"] == "Baja"
                and not h["apoyo_recibido"]
            ),
            recomendaciones=[
                "Es fundamental retomar la asistencia a clases.",
                "Busca un grupo de estudio o compañero de apoyo.",
                "Habla con un tutor o consejero académico cuanto antes.",
            ],
        ),

        # ── PERFIL: SITUACIÓN CRÍTICA ─────────────────────────────────────
        Regla(
            id="R7",
            nombre="Situación crítica por agotamiento",
            perfil="Situación Crítica",
            prioridad=8,
            condiciones_texto=[
                "Estrés >= 8",
                "Sueño < 5 horas",
                "Dificultad de concentración",
                "Motivación = Baja",
            ],
            evaluar=lambda h: (
                h["estres"] >= 8
                and h["sueno"] < 5
                and h["dificultad_concentracion"]
                and h["motivacion"] == "Baja"
            ),
            recomendaciones=[
                "Tu salud física y mental debe ser la prioridad.",
                "Busca apoyo psicológico en tu institución.",
                "Considera reducir tu carga académica este periodo.",
                "Mejora tu higiene de sueño como primer paso.",
            ],
        ),
        Regla(
            id="R8",
            nombre="Situación crítica multifactorial",
            perfil="Situación Crítica",
            prioridad=8,
            condiciones_texto=[
                "Horas de estudio < 3 semanales",
                "Asistencia < 50%",
                "Entrega tardía de trabajos",
                "Estrés >= 7",
                "No cuenta con apoyo",
            ],
            evaluar=lambda h: (
                h["horas_estudio"] < 3
                and h["asistencia"] < 50
                and h["entrega_tardia"]
                and h["estres"] >= 7
                and not h["apoyo_recibido"]
            ),
            recomendaciones=[
                "Se detectan múltiples factores de riesgo simultáneos.",
                "Es urgente buscar apoyo institucional (tutorías, consejería).",
                "Prioriza las materias más importantes y reorganiza tu carga.",
                "Habla con tu coordinador académico sobre tus opciones.",
            ],
        ),
    ]

    return reglas


# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3: MOTOR DE INFERENCIA
# ═══════════════════════════════════════════════════════════════════════════════

def ejecutar_inferencia(hechos, reglas):
    """
    Motor de inferencia: evalúa todas las reglas contra los hechos,
    determina el perfil principal por prioridad y calcula el nivel de riesgo.
    """

    reglas_activadas = []
    reglas_no_activadas = []

    # Evaluar cada regla
    for regla in reglas:
        if regla.se_cumple(hechos):
            reglas_activadas.append(regla)
        else:
            reglas_no_activadas.append(regla)

    # Determinar perfil principal (regla activada de mayor prioridad)
    if reglas_activadas:
        regla_ganadora = max(reglas_activadas, key=lambda r: r.prioridad)
        perfil_principal = regla_ganadora.perfil
        recomendaciones = regla_ganadora.recomendaciones.copy()
        # Agregar recomendaciones de otras reglas activadas (sin duplicar)
        for r in reglas_activadas:
            if r.id != regla_ganadora.id:
                for rec in r.recomendaciones:
                    if rec not in recomendaciones:
                        recomendaciones.append(rec)
    else:
        perfil_principal = "Sin Diagnóstico Claro"
        recomendaciones = [
            "Tus datos no coinciden con ningún patrón definido.",
            "Considera hablar con un asesor académico para una evaluación personal.",
        ]

    # Calcular puntuación académica (0-100)
    puntuacion = calcular_puntuacion(hechos)

    # Determinar nivel y color de riesgo según perfil
    mapa_riesgo = {
        "Alto Rendimiento":      ("Bajo",    "[Bajo]"),
        "Rendimiento Regular":   ("Medio",   "[Medio]"),
        "En Riesgo Académico":   ("Alto",    "[Alto]"),
        "Situación Crítica":     ("Crítico", "[Critico]"),
        "Sin Diagnóstico Claro": ("Indeterminado", "[N/A]"),
    }

    nivel_riesgo, color_riesgo = mapa_riesgo.get(
        perfil_principal, ("Indeterminado", "[N/A]")
    )

    return ResultadoInferencia(
        perfil_principal=perfil_principal,
        nivel_riesgo=nivel_riesgo,
        color_riesgo=color_riesgo,
        reglas_activadas=reglas_activadas,
        reglas_no_activadas=reglas_no_activadas,
        puntuacion=puntuacion,
        recomendaciones=recomendaciones,
        hechos=hechos,
    )


def calcular_puntuacion(hechos):
    """Calcula una puntuación académica compuesta de 0 a 100."""

    puntaje = 0.0

    # Horas de estudio (máx 25 pts)
    puntaje += min(hechos["horas_estudio"] / 20, 1.0) * 25

    # Asistencia (máx 20 pts)
    puntaje += (hechos["asistencia"] / 100) * 20

    # Sueño adecuado: 7-9 ideal (máx 10 pts)
    sueno = hechos["sueno"]
    if 7 <= sueno <= 9:
        puntaje += 10
    elif 6 <= sueno < 7 or 9 < sueno <= 10:
        puntaje += 7
    elif 5 <= sueno < 6:
        puntaje += 4
    else:
        puntaje += 1

    # Estrés bajo (máx 10 pts, invertido)
    puntaje += max(0, (10 - hechos["estres"])) * 1.0

    # Motivación (máx 10 pts)
    mapa_mot = {"Baja": 2, "Media": 6, "Alta": 10}
    puntaje += mapa_mot.get(hechos["motivacion"], 5)

    # Organización (máx 10 pts)
    mapa_org = {"Mala": 2, "Regular": 6, "Buena": 10}
    puntaje += mapa_org.get(hechos["organizacion"], 5)

    # Penalizaciones (hasta -15 pts)
    if hechos["uso_celular"]:
        puntaje -= 4
    if hechos["entrega_tardia"]:
        puntaje -= 5
    if hechos["dificultad_concentracion"]:
        puntaje -= 4
    if not hechos["apoyo_recibido"]:
        puntaje -= 2

    return round(max(0.0, min(100.0, puntaje)), 1)


# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4: INTERFAZ STREAMLIT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    st.set_page_config(
        page_title="Sistema Experto Académico",
        page_icon="",
        layout="wide",
    )

    st.title("Sistema Experto de Diagnóstico Académico")
    st.caption("Sistema basado en reglas IF-THEN para análisis del perfil estudiantil")

    # ── BARRA LATERAL: Datos generales del estudiante ─────────────────────
    st.sidebar.header("Datos del Estudiante")
    nombre = st.sidebar.text_input("Nombre completo", placeholder="Ej: María López")
    edad = st.sidebar.number_input("Edad", min_value=15, max_value=100, value=20)
    carrera = st.sidebar.text_input("Carrera", placeholder="Ej: Ingeniería en Sistemas")
    semestre = st.sidebar.number_input("Semestre actual", min_value=1, max_value=12, value=1)

    st.sidebar.markdown("---")
    st.sidebar.info(
        "Completa todos los campos del panel principal y presiona "
        "**Analizar Perfil** para obtener tu diagnóstico."
    )

    # ── CUERPO PRINCIPAL: Captura de los 10+ hechos ───────────────────────
    st.header("Hábitos y Situación Actual")
    st.write("Responde con honestidad para obtener un diagnóstico preciso.")

    col1, col2 = st.columns(2)

    with col1:
        horas_estudio = st.slider(
            "1. Horas de estudio semanales",
            min_value=0, max_value=40, value=10, step=1,
            help="Total de horas dedicadas al estudio fuera de clase.",
        )
        asistencia = st.slider(
            "2. Porcentaje de asistencia a clases (%)",
            min_value=0, max_value=100, value=80, step=5,
        )
        sueno = st.slider(
            "3. Horas de sueño por noche",
            min_value=0, max_value=14, value=7, step=1,
        )
        estres = st.slider(
            "4. Nivel de estrés (0 = Nada, 10 = Máximo)",
            min_value=0, max_value=10, value=5, step=1,
        )
        motivacion = st.selectbox(
            "5. Nivel de motivación",
            options=["Baja", "Media", "Alta"],
            index=1,
        )

    with col2:
        organizacion = st.selectbox(
            "6. Nivel de organización",
            options=["Mala", "Regular", "Buena"],
            index=1,
        )
        uso_celular = st.checkbox(
            "7. ¿Usas mucho el celular mientras estudias?",
        )
        entrega_tardia = st.checkbox(
            "8. ¿Sueles entregar trabajos tarde?",
        )
        dificultad_concentracion = st.checkbox(
            "9. ¿Te cuesta concentrarte al estudiar?",
        )
        apoyo_recibido = st.checkbox(
            "10. ¿Cuentas con apoyo familiar o de profesores?",
            value=True,
        )
        materias_dificiles = st.multiselect(
            "11. Materias que te resultan difíciles",
            options=[
                "Matemáticas", "Programación", "Física", "Inglés",
                "Estadística", "Bases de datos", "Redes", "Otra",
            ],
            help="Selecciona todas las que apliquen.",
        )
        metodo_estudio = st.selectbox(
            "12. Método de estudio principal",
            options=[
                "Leer apuntes", "Resúmenes propios", "Videos/Tutoriales",
                "Ejercicios prácticos", "Grupos de estudio", "Ninguno definido",
            ],
        )

    # ── Construir diccionario de HECHOS ───────────────────────────────────
    hechos = {
        "nombre": nombre or "Estudiante",
        "edad": edad,
        "carrera": carrera or "No especificada",
        "semestre": semestre,
        "horas_estudio": horas_estudio,
        "asistencia": asistencia,
        "sueno": sueno,
        "estres": estres,
        "motivacion": motivacion,
        "organizacion": organizacion,
        "uso_celular": uso_celular,
        "entrega_tardia": entrega_tardia,
        "dificultad_concentracion": dificultad_concentracion,
        "apoyo_recibido": apoyo_recibido,
        "materias_dificiles": materias_dificiles,
        "metodo_estudio": metodo_estudio,
    }

    # ── BOTÓN DE ANÁLISIS ─────────────────────────────────────────────────
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        analizar = st.button(
            "Analizar Perfil Académico",
            use_container_width=True,
            type="primary",
        )

    if analizar:
        # Cargar reglas y ejecutar inferencia
        reglas = construir_base_reglas()
        resultado = ejecutar_inferencia(hechos, reglas)

        # Guardar en session_state para persistencia
        st.session_state["resultado"] = resultado
        st.session_state["hechos"] = hechos

    # ── MOSTRAR RESULTADOS (si existen) ───────────────────────────────────
    if "resultado" in st.session_state:
        resultado = st.session_state["resultado"]
        hechos_guardados = st.session_state["hechos"]

        st.markdown("---")

        # ── Pestañas de resultados ────────────────────────────────────────
        tab_resumen, tab_explicacion, tab_reglas, tab_hechos = st.tabs([
            "Resumen", "Explicación", "Reglas", "Hechos",
        ])

        # ── TAB 1: RESUMEN ────────────────────────────────────────────────
        with tab_resumen:
            st.subheader(
                f"Diagnóstico para {hechos_guardados['nombre']}"
            )

            # Métricas principales
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Perfil", resultado.perfil_principal)
            m2.metric("Riesgo", f"{resultado.color_riesgo} {resultado.nivel_riesgo}")
            m3.metric("Puntuación", f"{resultado.puntuacion}/100")
            m4.metric("Reglas activadas", f"{len(resultado.reglas_activadas)}/8")

            # Barra de progreso de puntuación
            st.write("**Puntuación académica compuesta:**")
            st.progress(resultado.puntuacion / 100)

            # Color del perfil
            colores_perfil = {
                "Alto Rendimiento":      "success",
                "Rendimiento Regular":   "warning",
                "En Riesgo Académico":   "error",
                "Situación Crítica":     "error",
                "Sin Diagnóstico Claro": "info",
            }
            tipo_alerta = colores_perfil.get(resultado.perfil_principal, "info")
            getattr(st, tipo_alerta)(
                f"**Perfil principal:** {resultado.perfil_principal}"
            )

            # Ranking de perfiles (cuántas reglas de cada perfil se activaron)
            st.subheader("Ranking de perfiles detectados")
            perfiles_conteo = {}
            for r in resultado.reglas_activadas:
                perfiles_conteo[r.perfil] = perfiles_conteo.get(r.perfil, 0) + 1

            if perfiles_conteo:
                for perfil, conteo in sorted(
                    perfiles_conteo.items(), key=lambda x: -x[1]
                ):
                    st.write(f"**{perfil}** — {conteo} regla(s) activada(s)")
                    st.progress(min(conteo / 4, 1.0))
            else:
                st.info("No se activó ninguna regla con los datos proporcionados.")

            # Recomendaciones
            st.subheader("Recomendaciones")
            for rec in resultado.recomendaciones:
                st.write(f"- {rec}")

        # ── TAB 2: EXPLICACIÓN ────────────────────────────────────────────
        with tab_explicacion:
            st.subheader("Explicación del Razonamiento")

            st.write(
                "El motor de inferencia evaluó **8 reglas** contra los "
                f"**{len(hechos_guardados)} hechos** capturados. "
                "A continuación se detalla el proceso completo."
            )

            st.markdown("#### Historial de inferencia")
            reglas_todas = construir_base_reglas()
            for regla in reglas_todas:
                activada = regla.se_cumple(hechos_guardados)
                icono = "[SI]" if activada else "[NO]"
                with st.expander(
                    f"{icono} {regla.id}: {regla.nombre}  →  {regla.perfil}"
                ):
                    st.write(f"**Prioridad:** {regla.prioridad}")
                    st.write("**Condiciones evaluadas:**")
                    for cond in regla.condiciones_texto:
                        st.write(f"  - {cond}")
                    st.write(
                        f"**Resultado:** {'ACTIVADA' if activada else 'No cumplida'}"
                    )

            st.markdown("#### Justificación final")
            st.info(
                f"Se activaron **{len(resultado.reglas_activadas)}** reglas. "
                f"La regla de mayor prioridad determinó el perfil "
                f"**{resultado.perfil_principal}**. "
                f"La puntuación compuesta es **{resultado.puntuacion}/100** "
                f"lo que corresponde a un nivel de riesgo **{resultado.nivel_riesgo}**."
            )

        # ── TAB 3: REGLAS DEL SISTEMA ─────────────────────────────────────
        with tab_reglas:
            st.subheader("Base de Reglas del Sistema Experto")
            st.write(
                "Estas son las reglas IF-THEN que definen el "
                "comportamiento del sistema."
            )
            reglas_todas = construir_base_reglas()
            for regla in reglas_todas:
                with st.expander(f"{regla.id} — {regla.nombre} (Prioridad: {regla.prioridad})"):
                    st.write("**SI** se cumplen TODAS las siguientes condiciones:")
                    for c in regla.condiciones_texto:
                        st.write(f"  - {c}")
                    st.write(f"**ENTONCES** → Perfil: **{regla.perfil}**")
                    st.write("**Recomendaciones asociadas:**")
                    for rec in regla.recomendaciones:
                        st.write(f"  - {rec}")

        # ── TAB 4: HECHOS CAPTURADOS ──────────────────────────────────────
        with tab_hechos:
            st.subheader("Base de Hechos Capturados")
            st.write("Estos son los datos que el sistema utilizó para inferir:")

            hechos_mostrar = {
                "Nombre": hechos_guardados["nombre"],
                "Edad": hechos_guardados["edad"],
                "Carrera": hechos_guardados["carrera"],
                "Semestre": hechos_guardados["semestre"],
                "Horas de estudio (sem.)": hechos_guardados["horas_estudio"],
                "Asistencia (%)": hechos_guardados["asistencia"],
                "Sueño (hrs/noche)": hechos_guardados["sueno"],
                "Estrés (0-10)": hechos_guardados["estres"],
                "Motivación": hechos_guardados["motivacion"],
                "Organización": hechos_guardados["organizacion"],
                "Uso excesivo del celular": "Sí" if hechos_guardados["uso_celular"] else "No",
                "Entrega tardía": "Sí" if hechos_guardados["entrega_tardia"] else "No",
                "Dificultad de concentración": "Sí" if hechos_guardados["dificultad_concentracion"] else "No",
                "Apoyo recibido": "Sí" if hechos_guardados["apoyo_recibido"] else "No",
                "Materias difíciles": ", ".join(hechos_guardados["materias_dificiles"]) or "Ninguna",
                "Método de estudio": hechos_guardados["metodo_estudio"],
            }

            for clave, valor in hechos_mostrar.items():
                st.write(f"- **{clave}:** {valor}")

        # ── SECCIÓN EXTRA: Exportar y reiniciar ──────────────────────────
        st.markdown("---")
        col_exp, col_reset = st.columns(2)

        with col_exp:
            exportar = {
                "estudiante": {
                    "nombre": hechos_guardados["nombre"],
                    "edad": hechos_guardados["edad"],
                    "carrera": hechos_guardados["carrera"],
                    "semestre": hechos_guardados["semestre"],
                },
                "diagnostico": {
                    "perfil": resultado.perfil_principal,
                    "nivel_riesgo": resultado.nivel_riesgo,
                    "puntuacion": resultado.puntuacion,
                    "reglas_activadas": [r.id for r in resultado.reglas_activadas],
                    "recomendaciones": resultado.recomendaciones,
                },
                "hechos": {
                    k: v for k, v in hechos_guardados.items()
                    if k not in ("nombre", "edad", "carrera", "semestre")
                },
            }
            st.download_button(
                label="Exportar resultados (JSON)",
                data=json.dumps(exportar, ensure_ascii=False, indent=2),
                file_name=f"diagnostico_{hechos_guardados['nombre'].replace(' ', '_')}.json",
                mime="application/json",
            )

        with col_reset:
            if st.button("Reiniciar Análisis"):
                for key in ["resultado", "hechos"]:
                    st.session_state.pop(key, None)
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()