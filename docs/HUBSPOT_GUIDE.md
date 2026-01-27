# Guía de Integración con HubSpot

Este documento detalla cómo configurar la integración con HubSpot para el middleware Landbot-HubSpot, incluyendo cómo obtener el Token de Acceso, los permisos (scopes) necesarios y una lista exhaustiva de las llamadas a la API que realiza la aplicación.

## 1. Obtención del HUBSPOT_ACCESS_TOKEN

Para interactuar con la API de HubSpot, esta aplicación utiliza una **Private App**. Sigue estos pasos para crear una y obtener tu token:

1. Inicia sesión en tu cuenta de HubSpot.
2. Haz clic en el icono de **Configuración** (⚙️) en la barra de navegación principal.
3. En el menú lateral izquierdo, navega a **Integraciones** > **Aplicaciones privadas**.
4. Haz clic en el botón naranja **Crear una aplicación privada**.
5. **Pestaña Información básica**:
    * **Nombre**: Asigna un nombre reconocible, por ejemplo: `Landbot Middleware`.
    * (Opcional) Sube un logo o añade una descripción.
6. **Pestaña Scopes (Permisos)**:
    * Aquí debes seleccionar los permisos que necesita la aplicación. Busca y marca las casillas correspondientes a los scopes listados en la [Sección 2](#2-scopes-requeridos).
7. Haz clic en **Crear aplicación** en la esquina superior derecha.
8. Aparecerá un aviso de confirmación, haz clic en **Continuar creando**.
9. Una vez creada, verás tu **Token de acceso**. Haz clic en **Copiar**.
10. Abre el archivo `.env` en este proyecto y pega el token en la variable `HUBSPOT_ACCESS_TOKEN`:

```env
HUBSPOT_ACCESS_TOKEN=pat-na1-blablabla...
```

---

## 2. Scopes Requeridos

Para que el middleware funcione correctamente, la **Aplicación Privada** debe tener habilitados los siguientes permisos (scopes). Puedes encontrarlos en la pestaña **Scopes** dentro de la configuración de tu aplicación en HubSpot, bajo la categoría **CRM**:

| Categoría | Scope Técnico | Interfaz HubSpot | Justificación |
| :--- | :--- | :--- | :--- |
| **CRM** | `crm.objects.contacts.read` | `crm.objects.contacts` (Read) | Buscar contactos existentes por teléfono. |
| **CRM** | `crm.objects.contacts.write` | `crm.objects.contacts` (Write) | Crear nuevos contactos si no existen. |
| **TIKETS** | `tickets` | tickets | Buscar tickets abiertos para evitar duplicados. |

> [!TIP]
> **Sobre la seguridad:** Al ser una **Aplicación Privada**, solo necesitas el `HUBSPOT_ACCESS_TOKEN`. No es necesario (ni existe) un `CLIENT_SECRET` para este tipo de aplicaciones; ese dato solo se usa en aplicaciones públicas con OAuth 2.0.

* **Documentación Oficial:** [HubSpot Private Apps Overview](https://developers.hubspot.com/docs/api/private-apps)
* **Referencia de Scopes:** [HubSpot API Scopes List](https://developers.hubspot.com/docs/api/usage/scopes)

---

## 3. Llamadas a la API de HubSpot

A continuación se documentan todas las interacciones que realiza `src/services/hubspot_service.py` con la API de HubSpot.

### 3.1. Búsqueda de Ticket Activo

Busca si ya existe un ticket **ABIERTO** para el usuario actual (identificado por su ID de Landbot).

* **API Endpoint**: `POST /crm/v3/objects/tickets/search`
* **Método SDK**: `client.crm.tickets.search_api.do_search`
* **Documentación Oficial**: [CRM Tickets Search API](https://developers.hubspot.com/docs/api/crm/tickets#endpoint-/crm/v3/objects/tickets/search)

### 3.2. Búsqueda de Contacto por Teléfono

Verifica si el número de teléfono del usuario ya existe en el CRM.

* **API Endpoint**: `POST /crm/v3/objects/contacts/search`
* **Método SDK**: `client.crm.contacts.search_api.do_search`
* **Documentación Oficial**: [CRM Contacts Search API](https://developers.hubspot.com/docs/api/crm/contacts#endpoint-/crm/v3/objects/contacts/search)

### 3.3. Creación de Contacto

Si no se encuentra el contacto, se crea uno nuevo.

* **API Endpoint**: `POST /crm/v3/objects/contacts`
* **Método SDK**: `client.crm.contacts.basic_api.create`
* **Documentación Oficial**: [CRM Contacts Create API](https://developers.hubspot.com/docs/api/crm/contacts#endpoint-/crm/v3/objects/contacts)

### 3.4. Creación de Ticket

Crea un nuevo ticket de soporte para la conversación.

* **API Endpoint**: `POST /crm/v3/objects/tickets`
* **Método SDK**: `client.crm.tickets.basic_api.create`
* **Documentación Oficial**: [CRM Tickets Create API](https://developers.hubspot.com/docs/api/crm/tickets#endpoint-/crm/v3/objects/tickets)

### 3.5. Asociación Ticket -> Contacto

Vincula el ticket recién creado con el contacto del usuario.

* **API Endpoint**: `PUT /crm/v4/objects/tickets/{ticketId}/associations/contacts/{contactId}`
* **Método SDK**: `client.crm.associations.v4.basic_api.create`
* **Documentación Oficial**: [CRM Associations V4 API](https://developers.hubspot.com/docs/api/crm/associations)

### 3.6. Creación de Nota

Registra cada mensaje del chat como una nota interna.

* **API Endpoint**: `POST /crm/v3/objects/notes`
* **Método SDK**: `client.crm.objects.notes.basic_api.create`
* **Documentación Oficial**: [CRM Notes Create API](https://developers.hubspot.com/docs/api/crm/notes#endpoint-/crm/v3/objects/notes)

### 3.7. Asociación Nota -> Ticket

Vincula la nota creada con el ticket correspondiente.

* **API Endpoint**: `PUT /crm/v4/objects/notes/{noteId}/associations/tickets/{ticketId}`
* **Método SDK**: `client.crm.associations.v4.basic_api.create`
* **Documentación Oficial**: [CRM Associations V4 API](https://developers.hubspot.com/docs/api/crm/associations)

---

## 4. Configuración del Servidor y Webhooks

### 4.1. El Webhook de Salida (HubSpot -> Landbot)

Para que las respuestas de los agentes en HubSpot lleguen a Landbot, debes configurar un **Workflow** en HubSpot:

1. Crea un nuevo flujo de trabajo basado en **Tickets**.
2. Define el activador (trigger), por ejemplo: *"Cuando el valor de la propiedad `whatsapp_reply_body` ha sido actualizado"*.
3. Añade una acción de **"Enviar Webhook"** (Send Webhook).
4. Configura el webhook:
    * **Método**: `POST`
    * **URL**: `https://tu-servidor.com/webhook/hubspot-outbound`
    * **Autenticación**: No es necesaria si usas una URL protegida o un token personalizado, pero HubSpot permite añadir cabeceras.
5. **Carga útil (Payload)**: Asegúrate de enviar las propiedades requeridas: `ticket_id`, `landbot_id` y `reply_text`.

* **Documentación Oficial:** [Use webhooks in HubSpot workflows](https://knowledge.hubspot.com/workflows/use-webhooks-in-workflows)

### 4.2. Preguntas Frecuentes (FAQ)

**¿Necesito el Client Secret?**
No. Las aplicaciones privadas funcionan exclusivamente con el **Access Token**. El `client_id` y el `client_secret` son solo para aplicaciones públicas (OAuth) destinadas al App Marketplace.

**¿Debo configurar Webhooks en la App Privada?**
No. La sección de webhooks de la App Privada (o de la App Pública) es para eventos a nivel de cuenta. Para esta integración, usamos webhooks disparados por **Workflows**, lo cual da mayor control sobre qué tickets o eventos deben notificar al middleware.
