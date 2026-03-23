# Use Python base image
FROM python:3.10-slim

# Install LibreOffice + dependencies
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    libreoffice-impress \
    poppler-utils \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 10000

# Start app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]