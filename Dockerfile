# Utilisation d'une image Python légère
FROM python:3.10-slim

# Définition du répertoire de travail
WORKDIR /app

ENV PYTHONPATH=/app

# Copie du fichier de dépendances et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Exposition du port
EXPOSE 8000

# Commande pour lancer FastAPI avec Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
