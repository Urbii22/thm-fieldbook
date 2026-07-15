---
titulo: Informe de revisión pedagógica — fase 2
categoria: Meta
dificultad: Inicial
prerrequisitos:
  - auditoria_pedagogica_fase2.md
fuentes_internas:
  - auditoria_pedagogica_fase2.md
  - progreso.md
  - ../../scripts/validate_docs.py
fuentes_externas: []
revision: 2026-07-15
estado: revisado
---

# Informe de revisión pedagógica — fase 2

## Alcance ejecutado

La auditoría previa se utilizó como fuente de verdad. La fase no repitió el diagnóstico: sustituyó material de plantilla por secuencias didácticas basadas en observación, hipótesis rivales, experimentos discriminatorios, resultado y transferencia.

| Lote | Archivos | Cambio pedagógico principal |
|---|---:|---|
| 1. Fundamentos y metodología | 7 | Laboratorios concretos, árbol general de diagnóstico y cinco construcciones completas de payload |
| 2. SQLi y LFI | 2 | Reconstrucción de consulta/ruta, contexto, oráculos, capas de lectura e interpretación |
| 3. SSRF, command y argument injection | 3 | Identificación de cliente, resolución y redirects; shell frente a `argv`; options frente a operandos |
| 4. Upload y autenticación | 3 | Pipeline almacenar/recuperar/interpretar y modelo de estado, binding, replay, autorización y revocación |
| 5. Linux privilege escalation | 5 | Hallazgo → permisos → identidad efectiva → precondiciones → capacidad mínima → evidencia |
| 6. Ejercicios y pistas | 2 | Siete prácticas nuevas de decisión, construcción, diagnóstico, parsers, transferencia y mini-room |
| 7. Control editorial y publicación | 3 + PDF | Validador del estándar profundo, registro de progreso, informe y regeneración de artefactos |

## Estándar aplicado

Los trece módulos técnicos prioritarios incluyen Caso A básico, Caso B de adaptación, Caso C de transferencia y Caso D de falso positivo. Las resoluciones no parten del payload final: explicitan qué se sabe, hipótesis rivales, experimento, predicciones y evidencia obtenida. Cada módulo contiene además una anatomía verificable del payload importante desde el contexto de entrada hasta las condiciones en las que no funcionaría.

El estado `revisado` se aplicó únicamente a los módulos reescritos en profundidad. El campo `payloads_heredados_revisados: true` indica que el contenido heredado fue evaluado y que el validador debe comprobar el nuevo contrato pedagógico, no la conservación literal de recetas antiguas.

## Correcciones técnicas destacadas

- SQLi diferencia contexto numérico y textual, consulta probable, pares verdadero/falso, canal de evidencia y adaptación dependiente del motor.
- LFI separa traversal, lectura, `include`, interpretación, wrappers, sufijos y permisos.
- SSRF distingue petición del navegador y del servidor, DNS, representación, IP efectiva, redirects y capacidades reales del cliente HTTP.
- Command injection diferencia experimentalmente shell y ejecución directa, con controles negativos y canales blind.
- Argument injection explica cuándo existe splitting, cómo se forma `argv` y cuándo una opción u operando adicional no implica una shell.
- File upload no equipara aceptación, persistencia, recuperación, interpretación y ejecución.
- Autenticación trata sesión y MFA como máquinas de estado con binding, frescura, replay, autorización, expiración y revocación.
- Linux incorpora RUID/EUID, pérdida de privilegios, `nosuid`, `no_new_privs`, entorno de cron, PATH efectivo, RunAs, argumentos y variables de sudo, y comprobaciones dependientes de versión.

## Ejercicios y solucionario

El cuaderno añade E21-E27: siguiente experimento, construcción por capas, diagnóstico de fallo, hipótesis rivales, reconocimiento de parser, transferencia sin revelar la vulnerabilidad y mini-room. Cada solución compleja ofrece tres pistas progresivas y una resolución completa con controles negativos.

## Validaciones

- `python -m scripts.validate_docs`: metadatos, enlaces locales, tablas, bloques de código, estructura, casos A-D, anatomía de payloads y cobertura PDF.
- `python -m unittest discover -s tests -v`: 20 pruebas superadas.
- `git diff --check`: higiene del diff y espacios finales.
- Búsqueda editorial: ausencia de enunciados clonados usados como sustituto de casos.
- Construcción PDF y comprobación de cobertura/páginas mediante `scripts/build_docs.py`.
- Inspección visual de una muestra representativa de metodología, web, Linux, ejercicios y solucionario.

## Pendientes

No quedan pendientes dentro del alcance de los lotes prioritarios. Los módulos no incluidos conservan su estado previo y pueden someterse a otra revisión profunda en una fase futura.
