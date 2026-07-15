---
titulo: Sistema de ayuda progresiva
categoria: Plan de estudio
dificultad: Progresiva
prerrequisitos:
  - plantilla_sesion.md
fuentes_internas:
  - ../02_metodologia/metodologia_de_laboratorio.md
  - ../02_metodologia/construccion_y_adaptacion_de_payloads.md
  - registro_de_autonomia.md
fuentes_externas: []
revision: 2026-07-15
estado: revisado
---

# Sistema de pistas

Objetivo: sustituir `atasco → solución completa` por `atasco → diagnóstico → ayuda mínima → nuevo intento`.

## Protocolo

Empieza el reloj cuando lleves dos intentos sin obtener información nueva. En cada nivel escribe una hipótesis y realiza al menos un nuevo experimento antes de subir.

| Nivel | Acción permitida | Tiempo mínimo antes de subir | Evidencia que debes dejar |
|---:|---|---:|---|
| 0 | Releer observaciones, respuestas, errores y controles | 8 min | Qué dato tienes y qué dato estás suponiendo |
| 1 | Identificar exactamente qué entrada controlas | 8 min | Petición/comando y punto de inserción marcados |
| 2 | Identificar transformación, parser y sink probables | 10 min | Dos hipótesis rivales y una predicción por cada una |
| 3 | Consultar documentación oficial del componente | 12 min | Capacidad, sintaxis o restricción documentada y versión observada |
| 4 | Leer una pista conceptual | 10 min | Nuevo modelo o dirección y experimento derivado |
| 5 | Leer una pista sobre la primitiva | 10 min | Efecto mínimo que intentas demostrar |
| 6 | Leer una pista sobre la adaptación | 10 min | Por qué falló la variante básica y qué componente cambia |
| 7 | Consultar solución completa | — | Reconstrucción propia y repetición sin mirar tras 24 h |

Los tiempos son mínimos, no cuotas obligatorias. Sube antes solo si has demostrado que falta información externa; registra el motivo.

## Reglas de seguridad cognitiva

- No cambies tres elementos a la vez.
- Un error nuevo es evidencia, no necesariamente progreso.
- Una herramienta encontrada no confirma que el backend la use.
- No consultes el solucionario para validar una frase: termina primero una resolución completa.
- Tras niveles 4-7, cierra la ayuda y realiza un intento nuevo desde cero.
- Si llegas a nivel 7, agenda D1 y D7 obligatorios sobre un caso distinto.

## Tarjeta de atasco

```text
Observación:
Qué sé realmente:
Qué estoy suponiendo:
Entrada controlada:
Transformaciones probables:
Parser/sink probable:
Hipótesis A / predicción:
Hipótesis B / predicción:
Experimento que cambia una variable:
Nivel solicitado y hora:
```

## Cuándo detener la rama

Detén una hipótesis cuando un control discriminatorio contradiga su predicción dos veces, cuando falte una precondición verificable o cuando continuar exceda el alcance autorizado. Cerrar una rama bien razonada cuenta como resultado.
