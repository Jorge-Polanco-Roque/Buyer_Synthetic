# 🐳 Buyer Synthetic™ - Docker Deployment Guide

Este documento proporciona instrucciones completas para ejecutar Buyer Synthetic™ usando Docker y Docker Compose.

## 📋 Requisitos Previos

### Instalaciones Necesarias
- **Docker**: v20.10 o superior
- **Docker Compose**: v2.0 o superior
- **Git**: Para clonar el repositorio

### Verificar Instalaciones
```bash
docker --version
docker-compose --version
# O para Docker Compose v2:
docker compose version
```

## 🚀 Inicio Rápido

### 1. Setup Automático (Recomendado)
```bash
# Clonar repositorio
git clone https://github.com/Jorge-Polanco-Roque/Buyer_Synthetic.git
cd Buyer_Synthetic

# Ejecutar setup automático
./scripts/setup.sh
```

### 2. Configurar Variables de Entorno
```bash
# Editar archivo de configuración
nano .env

# Configurar tu API key de OpenAI (obligatorio para GenAI Mode)
OPENAI_API_KEY=tu_api_key_aquí
```

### 3. Ejecutar la Aplicación
```bash
# Opción 1: Script de ejecución
./scripts/run.sh

# Opción 2: Docker Compose
docker-compose up -d

# Opción 3: Docker Compose con servicios adicionales
docker-compose --profile dev up -d
```

### 4. Acceder a la Aplicación
- **Dashboard Principal**: http://localhost:8505
- **Dashboard Desarrollo**: http://localhost:8506 (con perfil dev)

## 🔧 Configuración Detallada

### Variables de Entorno Disponibles

#### API Configuration
```bash
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_MODEL=gpt-4                    # gpt-4, gpt-3.5-turbo
TEMPERATURE=0.7                        # 0.0 - 1.0
MAX_TOKENS=2000                        # Máximo tokens por respuesta
```

#### Survey Configuration
```bash
MIN_SAMPLE_SIZE=100                    # Tamaño mínimo de muestra
MAX_SAMPLE_SIZE=1000                   # Tamaño máximo de muestra
DEFAULT_SAMPLE_SIZE=300                # Tamaño por defecto
```

#### LangGraph Configuration
```bash
LANGGRAPH_MAX_RETRIES=2                # Reintentos máximos
LANGGRAPH_VALIDATION_THRESHOLD=0.7     # Umbral de validación
```

#### Logging
```bash
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR
```

### Estructura de Volúmenes

```
proyecto/
├── data/                              # Datos persistentes
│   ├── input/                         # Muestras generadas
│   ├── output/                        # Resultados y análisis
│   └── temp/                          # Archivos temporales
├── logs/                              # Logs de la aplicación
└── .env                               # Variables de entorno
```

## 🏗️ Servicios Disponibles

### Servicio Principal (buyer-synthetic)
- **Puerto**: 8505
- **Función**: Dashboard principal de producción
- **Recursos**: CPU optimizado, memoria limitada

### Servicio de Desarrollo (buyer-dev)
- **Puerto**: 8506
- **Función**: Dashboard con hot-reload para desarrollo
- **Activación**: `docker-compose --profile dev up`

### Servicios Opcionales

#### Redis (Caché)
- **Puerto**: 6379
- **Función**: Caché para mejorar rendimiento
- **Volumen**: `redis_data`

#### PostgreSQL (Base de Datos)
- **Puerto**: 5432
- **Función**: Persistencia de datos avanzada
- **Configuración**: Ver docker-compose.yml

## 📜 Scripts Disponibles

### 🔨 Build Script (`./scripts/build.sh`)
```bash
# Construir imagen con tag latest
./scripts/build.sh

# Construir con tag específico
./scripts/build.sh v1.0.0
```

### 🚀 Run Script (`./scripts/run.sh`)
```bash
# Ejecutar contenedor en puerto por defecto (8505)
./scripts/run.sh

# Ejecutar con tag y puerto específicos
./scripts/run.sh latest 8510
```

### ⚙️ Setup Script (`./scripts/setup.sh`)
```bash
# Setup completo automático
./scripts/setup.sh
```

### 🧪 Test Script (`./scripts/test.sh`)
```bash
# Ejecutar tests en contenedor
./scripts/test.sh

# Test con tag específico
./scripts/test.sh v1.0.0
```

## 🎛️ Comandos Docker Útiles

### Gestión de Contenedores
```bash
# Ver contenedores ejecutándose
docker ps

# Ver logs del contenedor
docker logs -f buyer-synthetic-app

# Acceder al shell del contenedor
docker exec -it buyer-synthetic-app bash

# Parar contenedor
docker stop buyer-synthetic-app

# Remover contenedor
docker rm buyer-synthetic-app
```

### Gestión de Imágenes
```bash
# Ver imágenes locales
docker images buyer-synthetic

# Remover imagen
docker rmi buyer-synthetic:latest

# Limpiar imágenes no utilizadas
docker image prune
```

### Docker Compose
```bash
# Iniciar servicios
docker-compose up -d

# Ver logs de todos los servicios
docker-compose logs -f

# Parar servicios
docker-compose down

# Reconstruir servicios
docker-compose up --build -d

# Iniciar solo servicio específico
docker-compose up buyer-synthetic
```

## 🔍 Debugging y Troubleshooting

### Problemas Comunes

#### 1. Puerto en Uso
```bash
# Error: "Port 8505 is already in use"
# Solución: Cambiar puerto o matar proceso
lsof -ti:8505 | xargs kill -9
# O usar puerto diferente
./scripts/run.sh latest 8510
```

#### 2. API Key No Configurada
```bash
# Error: "OPENAI_API_KEY no configurada"
# Solución: Verificar archivo .env
cat .env | grep OPENAI_API_KEY
```

#### 3. Permisos de Archivos
```bash
# Error: Permission denied
# Solución: Ajustar permisos
sudo chown -R $USER:$USER data/ logs/
chmod -R 755 data/ logs/
```

#### 4. Memoria Insuficiente
```bash
# Error: Container killed (OOMKilled)
# Solución: Aumentar memoria Docker o limitar uso
docker update --memory="2g" buyer-synthetic-app
```

### Verificación de Salud
```bash
# Health check manual
curl -f http://localhost:8505/_stcore/health

# Verificar logs de aplicación
docker logs buyer-synthetic-app | grep -i error

# Test de integración
./scripts/test.sh
```

### Logs Detallados
```bash
# Logs en tiempo real
docker-compose logs -f buyer-synthetic

# Logs específicos por servicio
docker-compose logs buyer-synthetic redis

# Filtrar logs por nivel
docker logs buyer-synthetic-app 2>&1 | grep ERROR
```

## 🚀 Despliegue en Producción

### Configuración Recomendada

#### 1. Variables de Entorno de Producción
```bash
# .env.production
LOG_LEVEL=WARNING
DEFAULT_SAMPLE_SIZE=500
LANGGRAPH_MAX_RETRIES=3
```

#### 2. Docker Compose para Producción
```bash
# Usar archivo específico
docker-compose -f docker-compose.prod.yml up -d
```

#### 3. Proxy Reverso (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8505;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Monitoreo

#### 1. Health Checks
```bash
# Configurar monitoreo automatizado
*/5 * * * * curl -f http://localhost:8505/_stcore/health || echo "Service down"
```

#### 2. Logs Centralizados
```bash
# Configurar logrotate
/var/log/buyer-synthetic/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

## 🔒 Seguridad

### Mejores Prácticas

1. **Variables de Entorno**
   - Nunca commits API keys al repositorio
   - Usar secretos de Docker Swarm o Kubernetes

2. **Red**
   - Usar red interna para servicios
   - Exponer solo puertos necesarios

3. **Usuarios**
   - Contenedores corren como usuario no-root
   - Limitar permisos de archivos

4. **Imágenes**
   - Usar imágenes oficiales
   - Escanear vulnerabilidades regularmente

### Configuración de Seguridad
```yaml
# docker-compose.security.yml
services:
  buyer-synthetic:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
```

## 📊 Métricas y Monitoreo

### Métricas Básicas
```bash
# Uso de recursos
docker stats buyer-synthetic-app

# Información del contenedor
docker inspect buyer-synthetic-app
```

### Configuración de Prometheus (Opcional)
```yaml
# Habilitar métricas en docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
```

## 🆘 Soporte

### Recursos de Ayuda
- **Documentación**: README.md del proyecto
- **Issues**: https://github.com/Jorge-Polanco-Roque/Buyer_Synthetic/issues
- **Docker Docs**: https://docs.docker.com/

### Información de Debug
```bash
# Recopilar información para soporte
echo "=== System Info ===" > debug.txt
docker --version >> debug.txt
docker-compose --version >> debug.txt
echo "=== Container Info ===" >> debug.txt
docker inspect buyer-synthetic-app >> debug.txt
echo "=== Logs ===" >> debug.txt
docker logs buyer-synthetic-app >> debug.txt
```

---

## 📝 Notas Adicionales

- Los volúmenes de datos persisten entre reinicios de contenedores
- Para desarrollo, usar el perfil `dev` que incluye hot-reload
- El health check está configurado para verificar el estado de la aplicación
- Redis está disponible para optimización de caché (opcional)

**¡Disfruta usando Buyer Synthetic™ en Docker! 🎉**