---
titulo: Metodología de laboratorio y room
categoria: Metodología
dificultad: Inicial
prerrequisitos:
  - ../01_fundamentos/bases_de_datos_y_flujo_de_datos.md
fuentes_internas:
  - ../../tools/guides.py#metodologia
  - ../../tools/concepts.py#recon-metodologia
  - ../../tools/concepts.py#rules-of-engagement-scope
fuentes_externas:
  - https://owasp.org/www-project-web-security-testing-guide/
revision: 2026-07-14
estado: revisado
---

# Metodología de laboratorio y room

## Objetivos

Pasar de evidencia a hipótesis comprobable, diseñar pruebas mínimas, reconocer niveles de confirmación y abandonar líneas sin soporte.

## Flujo general

1. Confirma alcance, objetivo, restricciones y horario.
2. Crea inventario de hosts, nombres, puertos, servicios, tecnologías e identidades.
3. Convierte cada observación en una hipótesis concreta.
4. Define la evidencia que confirmaría y la que refutaría.
5. Ejecuta la prueba mínima de menor riesgo.
6. Interpreta resultado y control negativo.
7. Amplía solo si cambia la conclusión o el impacto.
8. Registra evidencia y siguiente decisión.

## Plantilla de hipótesis

| Observación | Hipótesis | Prueba mínima | Resultado esperado | Resultado obtenido | Conclusión |
|---|---|---|---|---|---|
| | | | | | |

## Plantilla de entrada a sink

- Entrada controlada:
- Transformaciones conocidas:
- Componente que procesa la entrada:
- Sink potencial:
- Restricciones observadas:
- Primitiva que quiero demostrar:
- Evidencia esperada:
- Payload mínimo:
- Adaptaciones posibles:

## Mapa de superficie

Organiza por frontera, no por herramienta:

| Frontera | Activos | Entradas | Identidad | Dependencia | Evidencia |
|---|---|---|---|---|---|
| Internet-web | vhost/API | path, query, body, headers | anónima/usuario | DB, filesystem | petición-respuesta |
| Host local | procesos/servicios | config, entorno, archivos | usuario efectivo | kernel, sudo | permisos y ejecución |
| Dominio | cuentas/equipos | LDAP, SMB, Kerberos | principal | DC, AD CS | relaciones/tickets |

## Niveles de certeza

- **No confirmada**: posibilidad basada en diseño o tecnología.
- **Indicio**: comportamiento compatible, pero con explicaciones alternativas.
- **Confirmación**: prueba reproducible demuestra la primitiva.
- **Explotación**: se usa la primitiva para obtener una capacidad adicional.
- **Impacto**: consecuencia sobre confidencialidad, integridad o disponibilidad dentro del alcance.

No llames SQLi a un `500` ni SSRF a una demora aislada. Añade controles: entrada inocua, destino inexistente, repetición y comparación.

## Cuando falla la prueba básica

Clasifica antes de adaptar:

1. transporte incorrecto;
2. entrada no controlada;
3. parser distinto;
4. sintaxis/contexto incorrectos;
5. normalización o filtro;
6. sink no alcanzado;
7. efecto sin canal observable;
8. hipótesis falsa.

Cada adaptación debe discriminar entre dos causas. Probar listas aleatorias aumenta ruido sin aumentar conocimiento.

## Investigar herramientas y errores

Extrae nombre, versión, sintaxis mostrada y fase del error. Consulta primero manual oficial, ayuda local y documentación del proyecto. Reproduce la mínima invocación en un entorno propio. Un mensaje puede proceder de proxy, framework, librería, herramienta externa o sistema operativo; atribuirlo al componente equivocado produce payloads inútiles.

## Abandonar una hipótesis

Detente cuando la entrada no llega al componente, controles positivos y negativos son indistinguibles, la evidencia contradice el mecanismo, o el coste/riesgo supera el valor. Registra qué se descartó y bajo qué condiciones; podría reabrirse con nueva evidencia.

## Pistas progresivas

1. identificar la entrada;
2. nombrar el componente;
3. indicar la primitiva;
4. señalar la restricción;
5. mostrar un fragmento, nunca la solución completa antes del intento.

## Referencias

- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Guías internas](../../tools/guides.py)

Anterior: [Flujo de datos](../01_fundamentos/bases_de_datos_y_flujo_de_datos.md). Siguiente: [Construcción de payloads](construccion_y_adaptacion_de_payloads.md).
