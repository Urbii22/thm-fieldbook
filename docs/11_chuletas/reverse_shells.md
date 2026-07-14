---
titulo: "Reverse Shells"
categoria: Chuletas
dificultad: Operativa
prerrequisitos:
  - ../02_metodologia/construccion_y_adaptacion_de_payloads.md
fuentes_internas:
  - ../../tools/concepts.py
fuentes_externas: []
revision: 2026-07-14
estado: revisado
---

# Reverse Shells

Solo para laboratorios autorizados. Sustituye variables, confirma versión y guarda salida.

## Decisión rápida

1. Confirma alcance, identidad y conectividad.
2. Parte de una señal; no ejecutes toda la tabla.
3. Predice salida y prepara un control negativo.
4. Ejecuta la prueba menos intrusiva.
5. Registra evidencia y vuelve al módulo si falla.

## Señales

- Tienes ejecucion de comandos (RCE, `lfi-a-rce`, una inyeccion) pero aun no una shell interactiva.
- Tu listener no recibe nada: revisa que LHOST sea TU IP de atacante (VPN, no la local) y que el puerto no este ocupado ni filtrado.

## Comandos y pruebas

| Prueba | Objetivo/contexto | Evidencia esperada |
|---|---|---|
| `nc -lvnp 4444` | Pone tu maquina a escuchar para recibir una reverse shell. -l escucha, -v verboso, -n sin DNS, -p el puerto. Debe estar abierto ANTES de lanzar el payload. | 'listening on [any] 4444' y luego 'connect to ... from ...' cuando entre. Si no entra nada, el LHOST/puerto del payload no coincide o hay un firewall de salida. |

## Diagnóstico

| Síntoma | Comprobar |
|---|---|
| Sin respuesta | ruta, DNS, puerto, listener y firewall |
| Rechazo | sintaxis, credenciales, permisos y versión |
| Salida distinta | control negativo, caché y estado |
| Resultado parcial | identidad efectiva y precondiciones |

## Cierre

- Guardar comando adaptado y salida.
- Anotar qué confirma y qué no.
- No persistir secretos en notas compartidas.
- Restaurar cambios del laboratorio.

Fuente operativa: [conceptos de Fieldbook](../../tools/concepts.py). Método: [construcción de payloads](../02_metodologia/construccion_y_adaptacion_de_payloads.md).
