# Variables de configuración
CONTAINER_NAME = entorno_ia
IMAGE_NAME = ai_workspace
PORT = 8888
STREAMLIT_PORT = 8501
STREAMLIT_APP ?= /app/app.py
APP ?= $(STREAMLIT_APP)
TOKEN = curso_ia
URL = http://localhost:$(PORT)
STREAMLIT_URL = http://localhost:$(STREAMLIT_PORT)

# Colores para la terminal
BLUE = \033[1;34m
GREEN = \033[1;32m
YELLOW = \033[1;33m
RESET = \033[0m

.PHONY: help up down build status clean shell streamlit

help:
	@echo "$(BLUE)Comandos disponibles para tu Laboratorio de IA:$(RESET)"
	@echo "  $(GREEN)make up$(RESET)      - Enciende el entorno y muestra el acceso"
	@echo "  $(GREEN)make down$(RESET)    - Apaga el entorno de forma segura"
	@echo "  $(GREEN)make build$(RESET)   - Reconstruye la imagen (usa si cambias el Dockerfile)"
	@echo "  $(GREEN)make status$(RESET)  - Verifica si el contenedor está activo"
	@echo "  $(GREEN)make shell$(RESET)   - Entra a la terminal interna del contenedor"
	@echo "  $(GREEN)make streamlit$(RESET) APP=/app/archivo.py - Ejecuta Streamlit"
	@echo "  $(GREEN)make clean$(RESET)   - Borra archivos temporales y contenedores detenidos"

up:
	@echo "$(BLUE)🚀 Iniciando tu laboratorio de Inteligencia Artificial...$(RESET)"
	@docker compose up -d
	@echo "\n$(GREEN)✅ ¡Entorno listo para trabajar!$(RESET)"
	@echo "$(YELLOW)📍 Dirección:$(RESET) $(URL)"
	@echo "$(YELLOW)🔑 Contraseña:$(RESET) $(TOKEN)"
	@echo "$(BLUE)-------------------------------------------------------$(RESET)"
	@echo "Tip: Abre la URL en tu navegador y usa la contraseña arriba mencionada."

down:
	@echo "$(YELLOW)🛑 Deteniendo el entorno...$(RESET)"
	@docker compose down
	@echo "$(GREEN)Libros cerrados. ¡Hasta la próxima sesión!$(RESET)"

build:
	@echo "$(BLUE)🛠 Construyendo imagen de Docker...$(RESET)"
	@docker compose build

status:
	@echo "$(BLUE)📊 Estado del contenedor:$(RESET)"
	@docker ps --filter "name=$(CONTAINER_NAME)"

shell:
	@echo "$(BLUE)💻 Entrando a la terminal del contenedor...$(RESET)"
	@docker exec -it $(CONTAINER_NAME) /bin/bash

streamlit:
	@echo "$(BLUE)🌐 Iniciando Streamlit en $(STREAMLIT_URL)...$(RESET)"
	@docker exec -it $(CONTAINER_NAME) streamlit run $(APP) --server.address 0.0.0.0 --server.port $(STREAMLIT_PORT)

clean:
	@echo "$(YELLOW)🧹 Limpiando sistema...$(RESET)"
	@docker system prune -f
	@echo "$(GREEN)Sistema limpio.$(RESET)"
