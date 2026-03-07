FROM python:3.11-slim

WORKDIR /app

# Instalamos dependencias del sistema mínimas + locales para teclado español
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    locales \
    && sed -i '/es_ES.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

# Configurar locale en español
ENV LANG=es_ES.UTF-8
ENV LANGUAGE=es_ES:es
ENV LC_ALL=es_ES.UTF-8

# Instalamos tus librerías + paquete de idioma español para JupyterLab
RUN pip install --no-cache-dir \
    jupyterlab numpy pandas matplotlib seaborn scikit-learn networkx nltk \
    jupyterlab-language-pack-es-ES

# Descarga automática de datos comunes de NLTK
RUN python -m nltk.downloader punkt stopwords wordnet

# Configurar JupyterLab en español por defecto
RUN mkdir -p /root/.jupyter/lab/user-settings/@jupyterlab/translation-extension && \
    echo '{"locale": "es_ES"}' > /root/.jupyter/lab/user-settings/@jupyterlab/translation-extension/plugin.jupyterlab-settings

EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token='curso_ia'"]
