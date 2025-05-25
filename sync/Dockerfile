# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /sync

# Copy the requirements.txt from the root directory
COPY requirements.txt /sync/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the sync directory into the container
COPY . .

# Set the default command to run sync.py
CMD ["python", "sync.py"]