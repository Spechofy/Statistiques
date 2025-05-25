# Utilisation d'une image Python légère
FROM python:3.10-slim

# Définition du répertoire de travail
WORKDIR /app

ENV PYTHONPATH=/app

# Accept build arguments for secrets
ARG NEO4J_URI
ARG NEO4J_USER
ARG NEO4J_PASSWORD

# Set environment variables from build arguments
ENV NEO4J_URI=$NEO4J_URI
ENV NEO4J_USER=$NEO4J_USER
ENV NEO4J_PASSWORD=$NEO4J_PASSWORD

# Copie du fichier de dépendances et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Exposition du port
EXPOSE 8005

# Commande pour lancer FastAPI avec Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
