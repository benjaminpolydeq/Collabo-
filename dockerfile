# Collabo Application - Dockerfile
# Image légère pour déploiement

# Utiliser Python slim pour une image légère
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Collabo Team <contact@collabo-app.com>"
LABEL description="Application de networking intelligent et sécurisée"
LABEL version="1.0.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Créer un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 collabouser

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements
COPY requirements-minimal.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copier le code de l'application
COPY app/ ./app/
COPY assets/ ./assets/
COPY config.yaml .

# Créer le dossier data avec les bonnes permissions
RUN mkdir -p data && chown -R collabouser:collabouser /app

# Changer d'utilisateur
USER collabouser

# Exposer le port Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

# Commande de démarrage
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]