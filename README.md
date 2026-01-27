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
    HUBSPOT_ACCESS_TOKEN=pat-na1-xxxx... 
    LANDBOT_API_TOKEN=xxxx...
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
    python3 src/scripts/update_webhook.py https://TU-NUEVA-URL.loca.lt/webhook/hubspot-outbound
    ```

2. **En Landbot:** Ve al bloque **Webhook** en tu flujo y actualiza la URL a:
    `https://TU-NUEVA-URL.loca.lt/webhook/landbot-inbound`

### Scripts de Utilidad

* `python src/scripts/oauth_setup.py`: Realiza el handshake inicial de OAuth.
* `python src/scripts/register_channel.py`: Registra el canal personalizado en HubSpot.
* `python src/scripts/update_webhook.py`: Actualiza la URL del webhook en el canal de HubSpot sin tener que borrar y recrear todo el canal.
