FROM mcr.microsoft.com/playwright/python:v1.55.0-jammy

# Instalar dependencias Python
RUN pip install playwright python-dotenv

# Directorio de trabajo
WORKDIR /app

# Comando por defecto
CMD ["tail", "-f", "/dev/null"]
