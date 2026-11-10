# Informe de pentest - [PROYECTO]

> Plantilla de trabajo. Elimina instrucciones y textos pendientes. Revisa manualmente secretos y datos sensibles antes de entregar.

## 1. Control del documento

| Campo | Valor |
| --- | --- |
| Proyecto | [NOMBRE] |
| Cliente/laboratorio | [NOMBRE] |
| Autor | [NOMBRE] |
| Fecha de inicio | [AAAA-MM-DD] |
| Fecha de cierre | [AAAA-MM-DD] |
| Clasificacion | Confidencial |

## 2. Resumen ejecutivo

Explica para una persona no tecnica:

- que se evaluo;
- cual es el nivel de riesgo general;
- que cadena de ataque tuvo mayor impacto;
- que tres acciones deberian priorizarse.

## 3. Alcance y Rules of Engagement

| Campo | Valor |
| --- | --- |
| Activos incluidos | [IPS, HOSTS, DOMINIOS] |
| Activos excluidos | [LISTA] |
| Cuentas proporcionadas | [TIPOS, SIN PASSWORDS] |
| Ventana de pruebas | [FECHA/HORA] |
| Tecnicas restringidas | [LISTA] |
| Criterio de parada | [CONDICION] |
| Contacto | [ROL/CANAL] |

## 4. Metodologia y limitaciones

Describe brevemente reconocimiento, enumeracion, explotacion, post-explotacion y cierre. Registra limitaciones de tiempo, acceso, visibilidad o estabilidad que afecten a las conclusiones.

## 5. Cadena de ataque

1. [PUNTO DE ENTRADA]
2. [ACCESO INICIAL]
3. [ESCALADA O MOVIMIENTO LATERAL]
4. [IMPACTO DEMOSTRADO]

## 6. Resumen de hallazgos

| ID | Hallazgo | Severidad | CVSS v4.0 | Activo | Estado |
| --- | --- | --- | --- | --- | --- |
| F-01 | [TITULO] | [CRITICA/ALTA/MEDIA/BAJA] | [VECTOR Y SCORE] | [ACTIVO] | Confirmado |

CVSS Base expresa severidad tecnica. Justifica por separado el riesgo usando exposicion, datos, privilegios, controles y contexto del activo.

## 7. Hallazgos detallados

### [F-01] Titulo del hallazgo

- Severidad: [NIVEL]
- CVSS v4.0: [VECTOR] ([SCORE])
- Activo/servicio: [HOST:PUERTO]
- Estado: Confirmado

#### Resumen y causa raiz

[CONDICION VULNERABLE Y POR QUE EXISTE]

#### Evidencia

[REQUEST, RESPONSE, OUTPUT O CAPTURA MINIMA]

#### Reproduccion

1. [PRECONDICION]
2. [ACCION MINIMA]
3. [RESULTADO OBSERVADO]

#### Impacto

[QUE CONSIGUE UN ATACANTE, SOBRE QUE DATOS/ACTIVOS Y CON QUE PRIVILEGIOS]

#### Mitigacion

[CORRECCION CONCRETA, CONTROL COMPENSATORIO Y PRIORIDAD]

#### Retest

[PRUEBA QUE DEMOSTRARA QUE LA CORRECCION FUNCIONA]

## 8. Evidencias y anexos

| Evidencia | Hallazgo | Ruta/archivo | Descripcion |
| --- | --- | --- | --- |
| E-01 | F-01 | [RUTA] | [DESCRIPCION] |

## 9. Limpieza y estado final

| Artefacto/cambio | Activo | Creado | Retirado | Evidencia |
| --- | --- | --- | --- | --- |
| [FICHERO/CUENTA/TAREA/SERVICIO] | [ACTIVO] | [HORA] | [SI/NO] | [RUTA] |

No borres logs defensivos. Comunica cualquier artefacto que no haya podido retirarse.

## 10. Recomendaciones priorizadas

1. [CORRECCION INMEDIATA QUE ROMPE LA CADENA]
2. [CONTROL A CORTO PLAZO]
3. [MEJORA ESTRUCTURAL]

## 11. Conclusion

Resume riesgo residual, causas raiz repetidas y siguiente paso recomendado.

## QA antes de entregar

- [ ] Cada afirmacion importante tiene evidencia.
- [ ] Cada hallazgo incluye causa, reproduccion, impacto y mitigacion.
- [ ] Severidad y riesgo estan justificados por separado.
- [ ] No hay passwords, tokens, hashes o claves privadas innecesarias.
- [ ] Los activos pertenecen al alcance.
- [ ] La cadena de ataque coincide con los hallazgos.
- [ ] La limpieza esta verificada.
- [ ] Un tercero puede reproducir los pasos minimos.
