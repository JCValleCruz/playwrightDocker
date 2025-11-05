# Guía de Despliegue - Imagen Playwright

Esta guía te ayudará a exportar la imagen Docker y desplegarla en otro equipo usando GitHub.

## Opción 1: Usando GitHub Container Registry (Recomendado)

### En el equipo de origen:

#### 1. Construir la imagen
```bash
docker compose build
```

#### 2. Etiquetar la imagen para GitHub Container Registry
```bash
docker tag playwright:latest ghcr.io/TU_USUARIO_GITHUB/playwright:latest
```
*Reemplaza `TU_USUARIO_GITHUB` con tu nombre de usuario de GitHub*

#### 3. Autenticarse en GitHub Container Registry
```bash
# Primero, crea un Personal Access Token en GitHub:
# GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
# Marca los permisos: write:packages, read:packages, delete:packages

echo "TU_TOKEN_AQUI" | docker login ghcr.io -u TU_USUARIO_GITHUB --password-stdin
```

#### 4. Subir la imagen
```bash
docker push ghcr.io/TU_USUARIO_GITHUB/playwright:latest
```

#### 5. Subir el código a GitHub
```bash
git init
git add .
git commit -m "Initial commit - Playwright automation"
git branch -M main
git remote add origin https://github.com/TU_USUARIO_GITHUB/beyondup-automation.git
git push -u origin main
```

### En el equipo de destino:

#### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO_GITHUB/beyondup-automation.git
cd beyondup-automation
```

#### 2. Crear el archivo .env
```bash
cat > .env << 'EOF'
BEYONDUP_USER=descargas@axafone.com
BEYONDUP_PASS=Des@fic-2506
BEYONDUP_URL=https://login.beyondup.es
EOF
```

#### 3. Modificar docker-compose.yml para usar la imagen remota
Edita `docker-compose.yml` y cambia:
```yaml
services:
  playwright-service:
    image: ghcr.io/TU_USUARIO_GITHUB/playwright:latest
    # Comenta o elimina la línea "build: ."
```

#### 4. Autenticarse en GitHub Container Registry (si la imagen es privada)
```bash
echo "TU_TOKEN_AQUI" | docker login ghcr.io -u TU_USUARIO_GITHUB --password-stdin
```

#### 5. Levantar el contenedor
```bash
docker compose up -d
```

---

## Opción 2: Exportar/Importar imagen como archivo TAR

### En el equipo de origen:

#### 1. Construir la imagen
```bash
docker compose build
```

#### 2. Exportar la imagen a un archivo
```bash
docker save playwright:latest -o playwright-image.tar
```

#### 3. Subir a GitHub usando Git LFS (para archivos grandes)
```bash
# Instalar Git LFS (solo la primera vez)
git lfs install

# Rastrear archivos .tar con Git LFS
git lfs track "*.tar"
git add .gitattributes

# Subir todo
git add .
git commit -m "Add Playwright Docker image"
git push
```

**NOTA:** Si el archivo TAR es muy grande (>100MB), considera usar GitHub Releases:
- Ve a tu repositorio en GitHub
- Click en "Releases" → "Create a new release"
- Sube el archivo `playwright-image.tar` como asset
- Publica el release

### En el equipo de destino:

#### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO_GITHUB/beyondup-automation.git
cd beyondup-automation
```

Si usaste Git LFS:
```bash
git lfs pull
```

Si usaste GitHub Releases, descarga el archivo .tar desde la página de Releases.

#### 2. Importar la imagen
```bash
docker load -i playwright-image.tar
```

#### 3. Crear el archivo .env
```bash
cat > .env << 'EOF'
BEYONDUP_USER=descargas@axafone.com
BEYONDUP_PASS=Des@fic-2506
BEYONDUP_URL=https://login.beyondup.es
EOF
```

#### 4. Levantar el contenedor
```bash
docker compose up -d
```

---

## Verificar que el contenedor está corriendo

```bash
docker ps
docker logs playwright-beyondup
```

## Ejecutar comandos dentro del contenedor

```bash
docker exec -it playwright-beyondup bash
```

## Detener el contenedor

```bash
docker compose down
```

---

## Recomendaciones de Seguridad

⚠️ **IMPORTANTE:** El archivo `.env` contiene credenciales sensibles.

### NO subir .env a GitHub
Crea un archivo `.gitignore`:
```bash
cat > .gitignore << 'EOF'
.env
*.tar
playwright-image.tar
EOF
```

### En su lugar, crea un archivo .env.example
```bash
cat > .env.example << 'EOF'
BEYONDUP_USER=tu_usuario_aqui
BEYONDUP_PASS=tu_contraseña_aqui
BEYONDUP_URL=https://login.beyondup.es
EOF
```

Y documenta en el README que los usuarios deben copiar `.env.example` a `.env` y configurar sus credenciales.

---

## Estructura del Proyecto

```
beyondup-automation/
├── Dockerfile              # Definición de la imagen
├── docker-compose.yml      # Configuración de servicios
├── .env                    # Variables de entorno (NO subir a Git)
├── .env.example           # Plantilla de variables
├── scripts/               # Scripts de automatización
├── reports/               # Reportes generados
├── screenshots/           # Capturas de pantalla
└── logs/                  # Logs de la aplicación
```

---

## Troubleshooting

### Error: "permission denied"
```bash
sudo chmod -R 755 scripts/ reports/ screenshots/ logs/
```

### Error: "container name already in use"
```bash
docker rm -f playwright-beyondup
docker compose up -d
```

### Ver logs en tiempo real
```bash
docker compose logs -f
```
