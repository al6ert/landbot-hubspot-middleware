# Guía de Configuración en Landbot

Este documento detalla cómo configurar Landbot para integrarse con el middleware, permitiendo que los mensajes fluyan hacia HubSpot y las respuestas de los agentes regresen al chat de Landbot.

## 1. Obtención del LANDBOT_API_TOKEN

Para que el middleware pueda enviar mensajes de vuelta a Landbot, necesita un **API Token** válido.

1. Inicia sesión en tu panel de [Landbot](https://app.landbot.io/).
2. Haz clic en tu perfil (esquina inferior izquierda) y ve a **Settings** > **Account**.
3. Busca la sección **API Token**.
4. Haz clic en el botón para copiar el token.
5. Abre el archivo `.env` en este proyecto y pega el token en la variable `LANDBOT_API_TOKEN`:

```env
LANDBOT_API_TOKEN=3abc...tu_token_aqui...
```

* **Documentación Oficial:** [Where can I find the API Token?](https://knowledgecenter.landbot.io/article/7pzz66nmo0-where-can-i-find-the-api-token)

---

## 2. Configuración del Webhook en el Bot (Inbound)

Para enviar los mensajes de los usuarios desde Landbot al middleware, debes usar un bloque **Webhook** en tu flujo de bot.

### Paso 2.1: Captura de Información del Usuario

Asegúrate de haber capturado o tener disponibles las siguientes variables del sistema:

* `@name`: El nombre del usuario.
* `@phone`: El número de teléfono (especialmente importante para WhatsApp).
* `@id`: El ID interno de Landbot del cliente.

### Paso 2.2: Configurar el Bloque Webhook

Añade un bloque **Webhook** en el punto del flujo donde quieras que la conversación se transfiera a HubSpot (por ejemplo, después de que el usuario elija "Hablar con un humano").

1. **URL to send data**: `https://tu-servidor.com/webhook/landbot-inbound`
2. **Method**: `POST`
3. **Customize Body**: Activado (JSON).
4. **JSON Structure**:

```json
{
  "customer": {
    "id": @id,
    "name": "@name",
    "phone": "@phone"
  },
  "message": "@last_input",
  "timestamp": @timestamp
}
```

> [!IMPORTANT]
> Asegúrate de que `@id` no lleve comillas si es un número, mientras que `@name`, `@phone` y `@last_input` deben ir entre comillas como strings.

1. **Test Step**: Puedes realizar una prueba para verificar que el middleware recibe los datos correctamente.

* **Documentación Oficial:** [Webhooks Block Overview](https://knowledgecenter.landbot.io/article/1qlnbhwgsj-webhooks)

---

## 3. Envío de Mensajes desde el Middleware (Outbound)

El middleware utiliza la **Customer API** de Landbot para enviar respuestas desde los agentes de HubSpot.

### Endpoint Utilizado

* **URL**: `POST https://api.landbot.io/v1/customers/{customer_id}/send_text/`
* **Cuerpo de la petición**:

```json
{
  "message": "Hola, ¿en qué puedo ayudarte?"
}
```

### Consideraciones para WhatsApp

Si estás usando el canal de WhatsApp, recuerda que Landbot solo puede enviar mensajes de texto libre si la **ventana de 24 horas** de la sesión está abierta. De lo contrario, la API devolverá un error (400 Forbidden/Expired).

* **Documentación Oficial:** [Customer API - Send Text](https://api.landbot.io/#send-a-text-message)

---

## 4. Referencias y Documentación Oficial

* **Centro de Conocimiento (Knowledge Center):** [https://knowledgecenter.landbot.io/](https://knowledgecenter.landbot.io/)
* **Referencia de la API (API Docs):** [https://api.landbot.io/](https://api.landbot.io/)
* **Gestión de Clientes via API:** [Customer API Endpoints](https://api.landbot.io/#customers)
