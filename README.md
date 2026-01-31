# Landbot ↔ HubSpot Middleware

Middleware de integración bidireccional "No-DB", utilizando HubSpot Tickets como fuente de verdad.

## ✨ Funcionalidades Clave

* **Sin Base de Datos:** Utiliza propiedades de HubSpot (`landbot_customer_id`) para mantener el estado.
* **Gestión de Contactos Automática:**
  * Busca el contacto por teléfono antes de crear el ticket.
  * Si no existe, **crea el contacto** automáticamente.
  * Asocia el Ticket al Contacto para mantener el historial CRM limpio.

## 🚀 Instalación

1. **Requisitos:** Python 3.11+
2. **Instalar dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Configurar Variables de Entorno:**
    Crea un archivo `.env` en la raíz con:

    > **Notas de configuración:**
    > * Para HubSpot: Consulta la [Guía de HubSpot](docs/HUBSPOT_GUIDE.md).
    > * Para Landbot: Consulta la [Guía de Landbot](docs/LANDBOT_GUIDE.md).

    ```ini
    # Landbot
    LANDBOT_API_TOKEN=xxxx...

    # HubSpot App (OAuth)
    HUBSPOT_CLIENT_ID=xxxx...
    HUBSPOT_CLIENT_SECRET=xxxx...
    HUBSPOT_REFRESH_TOKEN=xxxx...

    # HubSpot Developer (Only for registration)
    HUBSPOT_DEVELOPER_API_KEY=xxxx...
    HUBSPOT_APP_ID=xxxx...

    # HubSpot Channel (Generated)
    HUBSPOT_CHANNEL_ID=xxxx...
    HUBSPOT_CHANNEL_ACCOUNT_ID=xxxx...
    ```

## 🏃 Como Ejecutar

```bash
uvicorn src.main:app --reload
```

API Docs disponibles en: `http://localhost:8000/docs`

## 🔗 Endpoints

### 1. Landbot Inbound (Human Takeover)

* **URL Local:** `POST http://localhost:8000/webhook/landbot-inbound`
* **Uso:** Configurar en el bloque "Webhook" de Landbot al iniciar el handoff.

### 2. HubSpot Outbound (Agent Reply)

* **URL:** `POST https://tu-servidor.com/webhook/hubspot-outbound`
* **Uso:** Recibe notificaciones automáticas cuando un agente responde en la bandeja de entrada de HubSpot (Custom Channel).
* **Configuración:** Se configura automáticamente mediante los scripts de registro.

## 🛠 Desarrollo Local y Troubleshooting

### Actualización de Webhooks (Localtunnel)

Si estás usando un túnel local (`localtunnel`, `ngrok`), la URL cambiará cada vez que reinicies el proceso. Para que los mensajes sigan llegando tanto a HubSpot como a Landbot, debes actualizar la URL en ambos sitios:

1. **En HubSpot:** Ejecuta el script de actualización rápida:

    ```bash
    python src/scripts/update_webhook.py https://TU-NUEVA-URL.loca.lt/webhook/hubspot-outbound
    ```

2. **En Landbot:** Ve al bloque **Webhook** en tu flujo y actualiza la URL a:
    `https://TU-NUEVA-URL.loca.lt/webhook/landbot-inbound`

### Scripts de Utilidad

* `python src/scripts/oauth_setup.py`: Realiza el handshake inicial de OAuth para obtener el `HUBSPOT_REFRESH_TOKEN`.
* `python src/scripts/register_channel.py`: Registra el canal personalizado en HubSpot (Crea el Channel y el ChannelAccount).
* `python src/scripts/update_webhook.py`: Actualiza la URL del webhook en el canal de HubSpot sin tener que borrar y recrear todo el canal.
* `python src/scripts/check_channel.py`: Verifica el estado actual del canal en HubSpot.
* `python src/scripts/update_channel_capabilities.py`: Utilidad para actualizar qué tipos de mensajes soporta el canal (adjuntos, etc).

## 🛣️ Consideraciones de Arquitectura y Futuro

### 1. Viabilidad Multi-cliente (SaaS)

Es totalmente viable, pero requiere evolucionar la arquitectura "No-DB":

* **Base de Datos:** Actualmente usamos `.env` para un único cliente. Para escalar, necesitamos una DB (PostgreSQL/Redis) que asocie un `tenant_id` (en la URL del webhook) con sus respectivas credenciales (`ACCESS_TOKEN`, `CHANNEL_ID`, etc).
* **OAuth dinámico:** El flujo de `oauth_setup.py` debería ser una interfaz web donde cada cliente autorice la app.
* **Monetización:** Se puede monetizar mediante el HubSpot App Marketplace, cobrando por "conversaciones procesadas" o una suscripción mensual.

### 2. Escalabilidad y Fiabilidad (Colas)

Actualmente usamos `BackgroundTasks` de FastAPI. Para producción:

* **Redis + Celery/RQ:** Es recomendable mover el procesamiento a colas persistentes. Esto permite gestionar picos de tráfico y, lo más importante, **reintentos automáticos** si la API de Landbot o HubSpot falla temporalmente.

### 3. Despliegue en Producción

* **Adiós al Túnel:** `make tunnel` es una herramienta de desarrollo. En producción, la app debe correr tras un proxy inverso (Nginx) con un dominio fijo y SSL.
* **Refactor de Config:** El script `update_webhook.py` debería ejecutarse solo durante el setup inicial o via CI/CD cuando el dominio de producción cambie.
