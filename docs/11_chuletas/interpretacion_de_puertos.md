---
titulo: "Interpretacion De Puertos"
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

# Interpretacion De Puertos

Solo para laboratorios autorizados. Sustituye variables, confirma versión y guarda salida.

## Decisión rápida

1. Confirma alcance, identidad y conectividad.
2. Parte de una señal; no ejecutes toda la tabla.
3. Predice salida y prepara un control negativo.
4. Ejecuta la prueba menos intrusiva.
5. Registra evidencia y vuelve al módulo si falla.

## Señales

- Un puerto alto o raro responde con cabeceras HTTP.
- El nombre de servicio de Nmap no coincide con el banner o con el comportamiento.
- open|filtered
- 53/udp

## Comandos y pruebas

| Prueba | Objetivo/contexto | Evidencia esperada |
|---|---|---|
| `nmap -sC -sV -Pn -p <PUERTO> $IP` | Confirma que habla realmente el puerto y recoge scripts/banners utiles. | Servicio, producto, version y pistas como titulos HTTP o certificados. |
| `curl -i http://$IP:<PUERTO>/` | Una comprobacion HTTP directa separa una aplicacion web real de una etiqueta de puerto equivocada. | Status, cabeceras y posiblemente framework o rutas a enumerar. |
| `nmap -sU -Pn -p 53,69,123,161 $IP` | Comprueba UDP de alto valor sin barrer todo a ciegas. | Puertos open o open\|filtered para profundizar. |
| `nmap -sU -sV -Pn -p <PUERTOS_UDP> $IP` | Identifica versiones en los UDP que merecen seguimiento. | Banner o respuesta del servicio. |

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
