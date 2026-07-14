---
titulo: Examen de Linux
categoria: Exámenes
dificultad: Intermedia
prerrequisitos:
  - ../04_linux/enum_privesc_linux.md
fuentes_internas:
  - ../../tools/concepts.py
fuentes_externas: []
revision: 2026-07-14
estado: revisado
---

# Examen de Linux

1. Explica usuario real/efectivo y cómo SUID modifica el modelo.
2. Interpreta una salida `sudo -l` con regla y entorno.
3. Compara sudo, SUID y capabilities.
4. Identifica precondiciones de cron, PATH y wildcard injection.
5. Diagnostica por qué un binario SUID no conserva privilegios.
6. Explica el riesgo de grupos Docker/LXD/disk.
7. Decide cuándo un exploit de kernel es justificable.
8. Propón mitigaciones para dos vectores sin usar “bloquear comando”.
9. Construye una tabla observación-hipótesis-prueba para NFS `no_root_squash`.
10. Escenario: usuario de servicio, cron root, script no escribible y módulo Python escribible. Demuestra la ruta mínima, controles, impacto y restauración.

## Rúbrica

Mecanismos 25; precondiciones 25; pruebas y evidencia 30; mitigación y limpieza 20.
