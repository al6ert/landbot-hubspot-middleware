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

* **URL Local:** `POST http://localhost:8000/webhook/hubspot-outbound`
* **Uso:** Configurar en el Workflow de HubSpot.
* **Trigger del Workflow:** Cuando `whatsapp_reply_body` ("Propiedad Personalizada") cambia.
