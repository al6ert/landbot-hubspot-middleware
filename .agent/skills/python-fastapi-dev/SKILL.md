---
name: python-fastapi-dev
description: Desarrolla servicios y APIs en Python/FastAPI con buenas prácticas, código simple y robusto; ejemplos: crear endpoints CRUD, integrar DB async con SQLAlchemy, añadir validación Pydantic y tests.
---
# python-fastapi-dev

## Goal

Construir y mejorar APIs FastAPI en Python con código limpio, seguro y consistente, manteniendo simplicidad y robustez.

## When to use

- Cuando el usuario pide crear o modificar endpoints FastAPI en Python.
- Cuando se requiere integrar bases de datos, autenticación o validación en FastAPI.
- Cuando se solicita pruebas para APIs FastAPI (pytest, httpx, TestClient).

## When NOT to use

- Para scripts simples sin servidor web ni API.
- Para frameworks distintos a FastAPI (Django, Flask, etc.) sin mención explícita.

## Inputs

- Requisitos de endpoint (ruta, método, payload, respuesta).
- Detalles de persistencia (DB, ORM, esquema, migraciones).
- Requisitos de seguridad y permisos (auth, scopes, CORS).
- Convenios del proyecto (estilo, estructura, dependencias).

## Outputs

- Código Python/FastAPI claro y consistente.
- Esquemas Pydantic v2 con validación robusta.
- Tests con pytest + httpx/TestClient cuando aplique.
- Notas de configuración o cambios necesarios.

## Procedure

1. Alinear requisitos y restricciones (inputs, outputs, errores, auth).
2. Diseñar modelos Pydantic y contratos de API simples.
3. Implementar lógica con separación clara (routers, services, data).
4. Añadir manejo de errores y validaciones explícitas.
5. Incluir pruebas focalizadas y ejemplos de uso si se pide.

## Constraints / Safety

- Mantener el diseño simple y coherente con el proyecto.
- Evitar dependencias nuevas sin necesidad o sin pedir permiso.
- No exponer secretos ni datos sensibles en ejemplos o logs.
- Pedir confirmación antes de acciones destructivas.
- Respetar convenciones de tipado y linting existentes.

## Examples

**User:** "Crea un endpoint POST /leads con validación y guarda en DB"
**Agent:** Define el esquema Pydantic v2, agrega el router FastAPI, usa SQLAlchemy async para persistencia, maneja errores de validación y devuelve un response 201 con el objeto creado.

**User:** "Añade tests para el endpoint GET /leads"
**Agent:** Implementa pruebas con pytest y httpx/TestClient, cubre casos de éxito y error, y valida el contrato de respuesta.
