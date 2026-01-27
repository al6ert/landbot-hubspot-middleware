# Guía de Integración con HubSpot (Custom Channels - Public App)

Este documento detalla cómo configurar la integración con HubSpot utilizando **Custom Channels** (Conversaciones). Debido a limitaciones de HubSpot, esta funcionalidad requiere una **Public App** (OAuth).

## 1. Creación de la Public App

Para usar Custom Channels API, debes tener una cuenta de Desarrollador y crear una **Public App** (no una Private App).

> **⚠️ IMPORTANTE**: HubSpot tiene dos tipos de apps bajo "Legacy apps":
>
> - **Private App**: Solo te da Access Token y Client Secret. **NO sirve para Custom Channels**.
> - **Public App**: Te da **App ID**, **Client ID** y **Client Secret**. **Esta es la que necesitas**.

### Pasos para crear la Public App

1. Inicia sesión en tu cuenta de desarrollador en [app.hubspot.com](https://app.hubspot.com/).
2. En el menú lateral izquierdo, haz clic en **Development** (Desarrollo).
3. Dentro de Development, haz clic en **Legacy apps** (Aplicaciones anteriores).
4. En la esquina superior derecha, haz clic en **Create app**.
5. **¡IMPORTANTE!** Aparecerá un diálogo preguntando el tipo de app. Selecciona **Public app** (no Private app).
6. Completa la información básica:
    - **Name**: `Landbot Middleware` (o lo que prefieras).
    - **Description**: Integración para chats de Landbot.
7. Ve a la pestaña **Auth**:
    - Aquí encontrarás tu **App ID**, **Client ID** y **Client Secret**. Copia estos tres valores.
    - En **Redirect URL**, añade: `http://localhost:8000/oauth-callback` (esto es para el script de setup local).
8. Ve a la pestaña **Scopes** y añade los siguientes permisos (asegúrate de marcarlos como Obligatorios):
    - `crm.objects.contacts.read`
    - `crm.objects.contacts.write`
    - `conversations.custom_channels.read`
    - `conversations.custom_channels.write`
    - `conversations.read`
    - `conversations.write`
    - `conversations.visitor_identification.tokens.create`
9. Guarda los cambios.

## 2. Configuración Inicial

### 2.1. Variables de Entorno (.env)

Necesitamos varios datos de tu cuenta de desarrollador y de la App.

```env
# Credenciales de la App (HubSpot Developers > Tu App > Auth)
HUBSPOT_CLIENT_ID=...
HUBSPOT_CLIENT_SECRET=...

# ID de la App (HubSpot Developers > Tu App > Settings)
HUBSPOT_APP_ID=...

# Developer API Key (HubSpot Developers > Home > Get API Key)
# OJO: No es el Access Token de un portal, es la Key de la cuenta de desarrollador.
HUBSPOT_DEVELOPER_API_KEY=...

# Token de Landbot (Igual que antes)
LANDBOT_API_TOKEN=...
```

### 2.2. Obtención del Refresh Token

Hemos creado un script para facilitar el proceso de OAuth (Handshake):

1. Asegúrate de haber rellenado `HUBSPOT_CLIENT_ID` y `HUBSPOT_CLIENT_SECRET` en tu `.env`.
2. Ejecuta:

    ```bash
    python src/scripts/oauth_setup.py
    ```

3. El script te dará una URL. Ábrela en tu navegador.
4. Selecciona la cuenta de HubSpot donde quieres instalar el canal.
5. Acepta los permisos.
6. El script capturará el código y obtendrá tu **Refresh Token**.
7. Añade el token a tu `.env`:

    ```env
    HUBSPOT_REFRESH_TOKEN=...
    ```

---

## 3. Registro del Canal

Una vez autenticado, registra el canal en tu cuenta de HubSpot.

1. Ejecuta:

    ```bash
    python src/scripts/register_channel.py
    ```

2. Introduce la URL de tu Webhook (e.g., `https://tu-tunnel.loca.lt/webhook/hubspot-outbound`).
3. Guarda los IDs generados en tu `.env`:

    ```env
    HUBSPOT_CHANNEL_ID=...
    HUBSPOT_CHANNEL_ACCOUNT_ID=...
    ```

---

## 4. Funcionamiento Automático

El middleware ahora gestiona la autenticación automáticamente:

- Usa el `HUBSPOT_REFRESH_TOKEN` para obtener un `ACCESS_TOKEN` válido cada vez que lo necesita (o cuando caduca).
- No necesitas rotar tokens manualmente.

---

## 5. Webhooks

La configuración de webhooks se realiza automáticamente al registrar el canal.

- **Evento**: `OUTGOING_CHANNEL_MESSAGE_CREATED`
- **Destino**: Tu URL configurada en el script de registro.
- **Flujo**: Agente responde en HubSpot -> Webhook -> Middleware -> Landbot.
