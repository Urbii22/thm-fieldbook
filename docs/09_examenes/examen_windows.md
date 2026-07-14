---
titulo: Examen de Windows
categoria: Exámenes
dificultad: Intermedia
prerrequisitos:
  - ../05_windows/enum_privesc_windows.md
fuentes_internas:
  - ../../tools/concepts.py
fuentes_externas: []
revision: 2026-07-14
estado: revisado
---

# Examen de Windows

1. Interpreta `whoami /priv` sin asumir que todo privilegio está habilitado.
2. Explica servicio, cuenta de servicio, binario y ACL.
3. Determina condiciones de un unquoted service path.
4. Contrasta AlwaysInstallElevated y DLL hijacking.
5. Analiza credenciales guardadas y su validación segura.
6. Explica token impersonation y su precondición.
7. Distingue UAC de frontera de seguridad completa.
8. Diseña pruebas para tareas programadas y autoruns.
9. Propón mitigaciones para servicios y registro.
10. Escenario: WinPEAS señala tres hallazgos. Prioriza, descarta dos falsos positivos y demuestra uno con evidencia de identidad efectiva.

## Rúbrica

Modelo de permisos 30; interpretación 20; prueba mínima 30; mitigación 20.
