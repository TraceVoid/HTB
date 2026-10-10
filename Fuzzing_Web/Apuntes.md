# Directorio y Difusion de Archivos
Las aplicaciones web a menudo tienen directorios y archivos que no estan directamente vinculados o visibles para los usuarios. Estos recursos ocultos pueden contener informacion delicada, archivos de copias de seguridad, de configuracion o inclusio versiones de aplicaciones antiguas y vulnerables. El directorio y la difusion de archivos tienen como objetivo descubrir estos activos ocultos, proporcionando a los atacantes puntos de entrada potenciales o informacion valiosa para una mayor explotacion.

## Descubrir activos ocultos.
Las aplicaciones web a menudo abergan un tesoro de recursos ocultos: directorios, archivos y end points que son facilmente accesibles a traves de la interfaz principal. Estas areas ocultas pueden contener informacion valiosa para los atacantes incluyendo:
° Sensitive data: Archivos de copia de seguridad, ajustes de configuracion registros que contengan credenciales de usuario u otra informacion confidencial.
° Outdated content: Versiones antiguas de archivoso scriptsque puedan ser vulnerables a exploits conocidos.
° Development resources: Entornos de prueba, sitios de preparacion o paneles administrativos que podrian utilizarse para realizar ataques adicionales.
° Hidden funtionalities: Funcionalidades o puntos dinales no documentados que podrian exponer vulnreabilidades inesperadas.
El descubrir estos recursos ocultos es crucial para los investigadores de seguridad y los pentestrs.
Esto mismo permite comprender mejor la superficie de ataque y las posibles vulnerabilidades de una aplicacion web.

### La importancia de encontrar activos ocultos.
Descubrir estas vulnerabilidades ocultas no es tarea facil. Cada hallazgo contribuye a obtener una vision completa de la estructura y funcionalidad de la aplicacion web, algo esencial para una evaluacion de seguridad exhaustiva. Estas areas ocultas suelen carcer de las solidas medidad de seguridad presentes en los componentes de acceso publico, lo que las convierte en objetivos de suma prioridad para la explotacion. Al identificar de proactivamente estas vulnerabilidades, podra adelantarse a las ciberamenazas.
Aunque un activo ocultono revele de forma directa una vulnerabilidad, la informacion obtenida puede resultar invaluable en las etapas posteriores de una prueba de penetración. Esto podría incluir desde comprender la arquitectura tecnológica adyacente hasta descubrir datos confidenciales que puedan ser utilizados para ataques posteriores.

``` Dierctory and file fuzzing ```
Estos son algunos de los métodos mas eficaces para descubrir estos recursos ocultos. Esto implica sondear sistemáticamente la aplicación web con una lista de posibles nombres de directorios y archivos, y analizar las respuestas del servidor para identificar recursos validos. 

### WordList
Las wordlist (lista de palabras) son fundamentales para el fuzzin de directorios y archivos. Proporcionan los nombres potenciales de directorios y archivos que la herramienta elegida utilizara para sondear la aplicacion web. Las wordlist que sean eficaces puedes aumentar significativamente las probabilidades de descubrir recursos ocultos.
Estas mismas se sueles recopilar de diferentes fuentes. Esto incluye, por lo general, rastrear la web en busca de nombres de directorios y archivos comunes, analizarfiltraciones de datos disponibles de forma publica y extraer informacion de directorios de vulnerabilidades conocidad, Estas listas se revisan de forma minusiosa, eliminando duplicados y entradas irrelevantes para garantizar una eficiencia y efectividad optimas direante las operaciones de fuzzing. El objetivos es crear wordlist completas de posibles directorios y nombres de archivos que probablemente se encuentren en los servidores web, lo que permite sondear de manera mas optima una aplicacion objetivo en busca de recursos ocultos.


## Directorios y Archivos fuzzing
Las aplicaciones web tienen varios directorios y archivos que estos no tienen un link o son visibles para los usuarios. Estos recursos ocultos suelen contener informacion sencible, backup de archivos, archivos de configuracion, o versiones de aplicaciones vulnerables. 

## Descubriendo Activos ocultos.
Las aplicaciones web a menudo contienen recursos ocultos: directorios, archivos y endpoints que no son facilmente accesibles a traves de su interfaz principal.

Descubrir estos activos es crucial a la hora de hacer pruebas de seguridad. Proporciona una comprension mas profunda de la superficie de ataque y algunas posibles vulns de una aplicacion web.

## Realizando el fuzzing
Usaremos ``` ffuf ```, esta es una herramienta de fuzzing potente y flexible, para descubrir directorios y archivos ocultos.

### FFUF
   ° Lista de palabras: Proporcionas a ffuf una lista de palabras que contiene posibles nombres de directorios o archivos.
  °  URL con la palabra clave FUZZ: Construyes una URL con la palabra clave FUZZ como marcador de posición donde se insertarán las entradas de la lista de palabras.
 °   Peticiones: ffuf itera a través de la lista de palabras, reemplazando la palabra clave FUZZ en la URL con cada entrada y enviando peticiones HTTP al servidor web objetivo.
  °  Análisis de respuesta: ffuf analiza las respuestas del servidor (códigos de estado, longitud del contenido, etc.) y filtra los resultados según tus criterios.

Para buscar extensiones de archivos en contreto se usara ``` -e <Punto:extension> -v ```, ejemplo;
```bash
 ffuf -w /usr/share/seclists/Discovery/Web-Content/common.txt -u http://IP:PORT/FUZZ -e .php,.html,.txt,.bak,.js -v 
```
## Fuzzing recursivo
El fuzzing recursivo es una forma mas automatizad a en la estruictura de directorios de una aplicacion web. Cuenta con 3 pasos:
1. ``` Fuzzing inicial ```: El proceso comienza en el directorio raiz de la web (/). El fuzzer comienza a enviar peticiones basandose en la wordlists que contenga los posibles nombre de directorios y archivos. 
2. ``` Descubrimiento y Expansion de Directorios ```: Cuando se encuentra un directorio valido, el fuzzer no solo se limita a anotarlo. Crea una nueva rama para ese directori, y añade el nombre del directorio a la URL base.
3. ``` Profundidad Iterativa ```: El rpoceso de repite para cada directorio que se descubr, creando mas ramas y expandiendo el alcance del fuzzing mas profundamente en la estructura de la aplicacion web. Esto es hasta que se alcance un limite de profunduidad especificado.

Para la edicion recursiva, se usa la flag/comando ``` -recursion ```. Esto le indica a nuestra herramienta ***ffuf*** que haga fuzzing de manera recursiva en cualquier directorio que se encuentre.

## Sé Responsable
Aunque el fuzzing recursivo sea una tecnica muy util en el ambito de la enumeración,también puede consumir muchos recuros, especialmente en aplicaciones web grandes. Un número excesivo de estas peticiones puede sobrecargar el servidor que tenemos como objetivo, caussando potencialmente problemas con el rendimiento o incluso activar sistemas de defensa.
``` ffuf ``` proporciona opciones para ajustar este proceso de recursividad.
- ```-recursion-depth```: Esta flag/comando nos permitirá establecer una profundidad máxima para la exploración recursiva. Por ejemplo ```-recursion-depth 2```esto limita el fuzzig a dos niveles de profundidad.
- ```-rate```: Puedes controlar la tasa a la que ```ffuf``` envía peticiones por segundo, evitando que el servidor se sobrecargue.
- ```-timeout```: Esta petición establece el tiempo de espera (timeout) para las peticiones individules, ayudando a evitar que el fuzzer se quede colgado en objetvos que no responden.

## Fuzzing de parámetros y valores
Partiendo del descubrimiento de directorios y archivos ocultos, ahora profundizaremos en el fuzzing de parámetros y valores. Esta técnica se centra en manipular los parámetos y sus valores dentro de las solicitudes web para descubrir vulns en la forma en que la aplicación procesa las entradas.
Los parámetros son los mensajeros de la web, transportando información vital entre el navegador y el servidor en el que se aloja la aplicación web.

## Parámetros GET; compartiendo información abiertamente
A menudo se observaran parametros ``` GET ``` drectamente en la URL, después de un signo de interrogación (```?```). Mútiples parámetros se encadenan usando el signo ampersand (```&```).
** Ejemplo **: ```https://example.com/search?query=fuzzing&category=security``` 
En esta URL:
- **query** es un parametro con el valor "fuzzing"
- **category** es otro parametro con el valor "security"

Los parametros GET son como una postal: su informacion es visible para cualquiera que eche un vistado a la URL. Se utilizan principalmente para acciones que no cambian el estado del servidor, como buscar o filtrar.

## *Parametros POST: comunicacion tras bambalinas*
Mientras que los parametros GET son como una postal abierta, los parametros POST son mas como sobre sellados, transportando su informacion de manera mas discreta dentro del cuerpo de la solicitud HTTP.
Este metodo no es visible directamente en la URL, lo que los convierte en los metodos mas usados/preferidos para transmitir datos sensibles como crendenciales de inicio de sesion, informacion personal o detalles financieros.

Cuando se envia un formulario o se interactua con una pagina web que usa solicitudes POST, sucede lo siguiente:

1.- **Recopilacion de datos**: La informacion que se ingresa en los campos del formulario se recopila y prepara para su transmision.
2.- **Codificacion**: Estos datos se codifican en un formato especifico, tipicamente ***aplication/x-www-form-urlencoded***.

## Por que estos parametros son importantes para el fuzzing
Los parametros son las puertas de enlace a traves de las cuales se puede interactiar con una aplicacion web. Al manipular sus valores, puedes probar como responde la aplicacion a diferentes entradas, descubriendo protenciales vulnerabilidades. Por ejemplo:
   - Alterar un ID de producto en la URL de un carrito de compras podría revelar errores de precios o acceso no autorizado a los pedidos de otros usuarios.
   - Modificar un parámetro oculto en una solicitud podría desbloquear funciones ocultas o administrativas.
   - Inyectar código malicioso en una consulta de búsqueda podría exponer vulnerabilidades como Cross-Site Scripting (XSS) o inyección SQL (SQL Injection o SQLi).

## Fuzzing de Hosts Virtuales y Subdominios
El alojamiento viertual es uno de los responsables que permite que múltiples sitios web o diminios se sirvan desde un unico servidor o direccion IP. Cada vhost (Virtual Hosts) esta asociadoc on un nombre de dominio o nombre de host unico. Cuando un cliente envia una solicitus HTTP, el servidor examina la cabecera ´´´Hosts´´' para determinar que contenido entregar.

Los subdominios, son extensiones de un nombre de dominio principal. creando una jerarquia en su estructura dentro del mismo dominio. Se utilizan para organizar diferentes secciones o servicios dentro de un sitio web. Por ejemplo ´´´blog.exxample.com´´´ y ´´´shop.example.com´´´. Estos son subdomios del mismo dominio principal ***example***. A diferencia de los vhost, los subdominios se resuelven a direcciones IP especificas a traves de registros DNS (Sistema de Nombres de Dominios/Domine Names System).

## Uso de gobuster
gobuster es una herramienta muy parecida a fuff, con la diferencia de este hace un tipo "fuerza bruta" hacia los subdominios de la pagina.
Una de sus flags/comandos de uso es;
- ´´´vhost´´´: este activa el modo de fuzzing de vhost de gobuster indicandole que se centre en descubrir hosts virtuales en lugar de directorios o archivos.
- ´´´--append-domain´´´: Este flags es crucial le indica a Gobuster que anexe el dominio base a cada palabra de la lista de palabras. Esto asegura que la cabecera ´´´Host´´´ en cada solicitud incluya un nombre de dominio completo, lo cual es esencial para el descubrimiento de vhost.

## Fuzzing de subdominios con Gobuster uwu
A menudo se le asocia a la herramienta de gobuster a solo descubrir vhost y directorios, pero esta herramienta tiene aun mas posibilidades de cuales se pueden aprovechar aun mas. Gobuster se destaca en la enumeracion de subdominios, un paso crucial a la hora de mapear la superficie de ataque **(attack surface)** de un dominios, es crucial tener dicho mapeo lo mas completo posible y el probar sistematicamente variaciones de posibles nombre de subdominio. gobuster puede descubrir subdominios ocultos u olvidades que podrian alojar informacion valiosa o vulnerable.

El comando mas usado es: 
´´´gobuster dns -d <URL> -w /directory/your/worslists´´´
El desgloce completo de dicho comando:
- ´´´gobuster dns´´´: Activa el modo de fuzzing enfocado a los DNS, dirigiendolo o centrandose en el descubrimiento de subdominios.
- ´´´-d <URL>´´´: Especifica el dominio objetivo para el cual se quiere hacer el descubrimiento de subdominios.
-´´´-w´´´: Esto no es mas que para indicar la ruta del diccionario a usar, por ejemplo, para el descubrimiento de DNS se usa la ruta de; ´´´/usr/share/seclists/Discovery/DNS/subdomains-top1millon-5000.txt´´´

El proceso interno de gobuster funciona generando nombres de subdominios basados en la lista de palabras, anexandolos al dominio objetivo y luego intentando resolver esos subdominios mediante consultas DNS. Si un subdominio se resuleve a una direccion IP, gobuster la considerara valida y se incluira en la salida. 

** Nota: ** En la ultima version de gobuster, la flag ´´´-d´´´ ahora establece el retardo entre solicitudes, no el dominio. Usa ´´´-do´´´ o ´´´--domain´´´ para especificar el dominio objetivo si se esta utilizando la ultima version.

## Fitrado de la Salida de las herramientas de fuzzing
Las herramientas que hemos estado usando en estas practicas, esan diseñadas para realizar un analisis esxhaustivo, generando a menudo una gran cantidad de datos. Revisar la salida que nos da para identificar los hallazgos mas relevanes puede ser una tarea abrumadora.

## Filtrado de Gobuster
Gobuster ofrece varias opciones de filtrado segun el modulo que se este ejecutando, para aguilizar el analisis. Hay una pequeña advertencia: las opciones ´´´-s´´´ y ´´´-b´´´ solo estan disponibles en el modo de fuzzing ´´´dir´´´
| Flag | Descripcion | Example uwu |
|----------|----------|----------|
| ```-s``` (include)    | Incluir solo respuestas con los codigos de estados especificacos, separado con comas   | En las redirecciones ***-s 301,302,307***  |
|  ```-b``` (exclude)   |  Exluir respuestas con los codigos de estado especificado (separado por coma)  | El servidor decuelve muchos errores 404. Exluyelos con ```-b 404```   |
| ```--exlude-length```    | Exluir respuestas con las longuitudes de contenidos especificas (separadas por comas, admite rangos).   | No te interesan las respuestad de 0 o 404 bytes, asi que usa ```--exlude-length0, 404```   |

## FFUF
FFUFofrece un sistema de filtrado mas personalizable, que permite un control mas preciso sobre la salida mostrada. Esto permite cribar eficientemente grandes cantidades de datos y centrarteen los hallazgos mas relevantes. Lasopciones de filtrado de **FFUF** se clasifican en multiples tipos que tienen un proposito especifico para refinar los resultados de salida.

| Flag | Descripción | Ejemplo de escenario |
|---|---|---|
| `-mc` (match code) | Incluir solo las respuestas que coincidan con los códigos de estado especificados. Puedes proporcionar un único código, múltiples códigos separados por comas o rangos de códigos separados por guiones (p. ej., `200,204,301,400-499`). El comportamiento por defecto es coincidir con los códigos `200-299`, `301`, `302`, `307`, `401`, `403`, `405` y `500`. | Después del fuzzing, notas muchas redirecciones `302 (Found)`, pero estás principalmente interesado en respuestas `200 (OK)`. Usa `-mc 200` para aislarlas. |
| `-fc` (filter code) | Excluir las respuestas que coincidan con los códigos de estado especificados, usando el mismo formato que `-mc`. Esto es útil para eliminar códigos de error comunes como `404 Not Found`. | Un análisis devuelve muchos errores `404`. Usa `-fc 404` para eliminarlos de la salida. |
| `-fs` (filter size) | Excluir respuestas con un tamaño o rango de tamaños específico. Puedes especificar tamaños únicos o rangos usando guiones (p. ej., `-fs 0` para respuestas vacías, `-fs 100-200` para respuestas de entre 100 y 200 bytes). | Sospechas que las respuestas interesantes serán mayores de 1 KB. Usa `-fs 0-1023` para filtrar las respuestas más pequeñas. |
| `-ms` (match size) | Incluir solo las respuestas que coincidan con un tamaño o rango de tamaños específico, usando el mismo formato que `-fs`. | Estás buscando un archivo de respaldo que sabes que tiene un tamaño exacto de 3456 bytes. Usa `-ms 3456` para encontrarlo. |
| `-fw` (filter out number of words in response) | Excluir respuestas que contengan el número especificado de palabras en la respuesta. | Estás filtrando un número específico de palabras de las respuestas. Usa `-fw 219` para filtrar las respuestas que contengan esa cantidad de palabras. |
| `-mw` (match word count) | Incluir solo respuestas que tengan la cantidad especificada de palabras en el cuerpo de la respuesta. | Estás buscando mensajes de error cortos y específicos. Usa `-mw 5-10` para filtrar respuestas con entre 5 y 10 palabras. |
| `-fl` (filter line) | Excluir respuestas con un número o rango de líneas específico. Por ejemplo, `-fl 5` filtrará las respuestas con 5 líneas. | Notas un patrón de mensajes de error de 10 líneas. Usa `-fl 10` para filtrarlos. |
| `-ml` (match line count) | Incluir solo respuestas que tengan la cantidad especificada de líneas en el cuerpo de la respuesta. | Estás buscando respuestas con un formato específico, como 20 líneas. Usa `-ml 20` para aislarlas. |
| `-mt` (match time) | Incluir solo las respuestas que cumplan una condición específica de tiempo hasta el primer byte (TTFB). Esto es útil para identificar respuestas inusualmente lentas o rápidas, lo que podría indicar un comportamiento interesante. | La aplicación responde lentamente al procesar ciertas entradas. Usa `-mt >500` para encontrar respuestas con un TTFB superior a 500 milisegundos. |


## Validar
El fuzzing es exxcelente para lanzar una red amplia y genera posibles pistas, pero no todos los hallazgos son una vulnerabilidad genuina. El proceso a meduno produce falsos positivos: anomalias inofensivas que activas los mecanismos de deteccion del fuzzer pero que no suponen una amenza real.

## Por que es importante validar?
- ´´´ Confirmar vulns´´´: Asegura que los problemas que se descubrieron son vulns reales y no falsas.
- ´´´ Comprender el impacto´´´:  Ayuda a evaluar la gravedad de la vuln y el impacto que este puede tener en la aplicacion web.
- ´´´ Recopilar Pruebas ´´´: Recopila pruebas de las vulns para comprartirlas con los devs o las partes de interes.

## Verificacion Manual
Aunque sea la manera mas tardada, esta misma suele implicar que se tenga que ´´´Reproducir la peticion´´´ con el uso de herramientas como ´´´curl´´´ o en el navegador web para analizar de manera mas exaustiva la misma peticios que provoco la respuesta inusual durante el ´´´fuzzing´´´.
Por su parte, la ´´´Explitacion´´´, es el hallazgo prometedor, si se intenta explotar la vuln en un entorno controlado para evaluar su impacto y gravedad. Este paso debe realizarse con precaucion y solo despues de obtener la autorizacion adecuada.

Para validad y explotar un hallzago de forma responsable, es crucial evitar acciones que puedan dañar el sistema de produccion o comprometer datos sensibles. En su lugar, se recomienda centrarse en crear una ´´´prueba de concepto (PoC)´´´ que demuestre la existencia de la vuln sin causar daños. Por ejemplo, si sospechas de una vuln de ´´´inyeccion SQL´´´ (´´´SQL Injeccion´´´), se podria elaborar una consulta SQL inofensiva que devuelva la cadena de version del servidor SQL en su lugar de intentar extraer o modificar datos sensibles.


## Api web
Una ´´´API web´´´ (o ´´´Web API´´´, del ingles ´´´Web Aplication Programming Interface´´´) es un conjunto de reglas y especificaciones que permiten a diferentes aplicaciones de software comunicarse a traver de la Web.
Esencialmente, una ´´´API web´´´ sirve como un puente entre un servidor (que loja los datos y la funcionalidad) y un cliente (como un navegador web, una aplicacion movil u otro servidor) que desea acceder o utilizar esos datos o funcionalidad.

## Transferencia de Estado Representacional (REST)
Las ´´´API REST´´´ son un estilo arquitectonico popular para construir servicios web. Utilizan un modelo de comunicacion cliente-servidor sin estado en el que los clientes envian solicitudes a los servidores para acceder o manipular recursos. Las API REST utilizan ´´´metodos HTTP´´´ estandar (´´´GET, POST, PUT, DELETE) para realizar operaciones ´´´CRUD´´´ (Crear, Leer, Actualizar, Borrar) en recursos identificados por URL unicas. Normalmente intercambian datos en formatos ligeros como ´´´JSON o XML´´´, lo que las hace faciles de integrar con diversas aplicaciones plataformas.

## Protocolo Simple de Acceso a Objetos (SOAP)
Las ´´´API SOAP´´´ siguen un protocolo mas formas y estandarizado para intercambiar informacion. Utilizan ´´´XML´´´ para definir mensajes, que luego se encapsulan en ´´´Sobres SOAP´´´ y se trensmiten a traver de protocolos de red como ´´´HTTP´´´ o ´´´SMTP´´´. Este tipo de API a menudo incluyen caracteristicas integradas de seguridad, fiabilidad y gestion de transacciones, las que las hace adecuadas para aplicaciones de un enfoque mas empresarial que requieren una estructura integrada de datos y manejo de errores.

**Consulta de ejemplo**: 
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
   <soapenv:Header/>
   <soapenv:Body>
      <tem:GetStockPrice>
         <tem:StockName>AAPL</tem:StockName>
      </tem:GetStockPrice>
   </soapenv:Body>
</soapenv:Envelope> 
```
## GraphQL
´´´GraphQL´´´ es un lenguaje de consulta y un entorno de ejecucion para API relativamente nuevo. A diferencia de las API REST, que exponen multiples endpints para diferentes recursos, este software propociona un unico endpoint donde los clientes pueden solicitar los datos que necesitan utilizando un lenguaje de consulta felxible. Esto elimina el problema el defecto de la obtencion de datos, que se comun en las API REST. Las fuertes capacidades de tipado e introspeccion de ´´´GraphQL´´´ que facilita la evolucion de las API a lo largo del tiempo sin romper los clientes existentes, lo que lo convierte en una mejor opcion para las aplicaciones web o moviles modernas.
```grapgql
query { 
    user(id: 123) {
           name
           email
       }
}
```
## Identifiacion de endpoints
### REST
Las API REST se basan en el concepto de recursos, que se identifican mediante URL unicas llamadas endpoints. Estos mismo son los objetivos de las solicitudes de los clientes y, a menudo, incluten parametros para proporcionar un contexto adicional o control sobre la operacion realizada.

Los endpoints en las API REST se estructuran como URL que representan los recursos a los que se desea acceder o manipular. POr ejemplo:

- ```/user``` -> Representa una coleccion de recursos de usuario.
- ```/user/123``` -> Representa un usuario especifico con el ID 123.
- ```/products``` -> Representa una coleccion de recursos de producto.
- ```/products/456``` -> Representa un producto especifiico con el ID 456.

Los parametros se utilizan para modificar el comportamiento de las solicitudes de la API o para proporcionar informacion adicional. En las API REST, existen varios tipos de parametros:
| Tipo de Parametro | Descripcion | Ejemplo |
| --- | --- | --- |
| Parametros de consulta | Se añaden a la URL del endpoint despues de un signo de interrogacion (```?```). Se utilizan para filtrar, ordenar o paginar. | ```/users?limit=10&sort=name``` |
| Parametros de ruta | Incrustacion directamente en la URL edl endpoint. Se utilizan para identificar recursos especificos. | ```/productos/{id}``` |
| Parametros del cuerpo de la solicitud | Se envian en el cuerpo de las solicitudes POST, PUT o PATCH. Se utilizan para crear o actualizar recursos. | ```{ "name": "New Product", "price": 99.99``` |

## Descubrimiento de endpoint y parametros REST
1.- ```Documentacion de la API```: La forma mas fiable de entender una API es consultar su documentacion oficial. Esta documentacion suele incluir unalista de los endpoints disponibles, sus parametros, los formatos de la solicitud/respuesta esperados y ejemplos de uso. Busque especificaciones como Swagger (OpenAPI) o RAML, que proporcionan descripciones de la API legible por maquina.
2.- ```Analisis de trafico de red```: Si la documentacion no esta disponible o es incompleta, puede analizar el trafico de red para observar como se utiliza la API. Herraminetas como Burp Suite o las de desarrollador del navegador le permiten interceptar e inspeccionar las solicitudes y respuestas de la API, revelando enpoints, parametros y formatos de datos.
3.- ```Fuzzing de nombres de parametros```: De forma similar el fuzzing de directorios y archivos, puede utilizar las mismas herrmientas y tecnicas para hacer ```fuzzing``` de nombres de parametros dentro de las solicitudes API. ```ffuf``` y ```wfuzz```, combinados con las wordlist adecuadas, pueden utilizarse para descubrir parametros ocultos o no dumentados.

## SOAP
Las API SOAP (Simple Object Access Protocol) tienen una estructura diferente a la de las API REST. Se basan en mensajes basados en XML y en archvios del Lenguaje de Descripcion de Servicios Web (WSDL, por sus siglas en ingles) para inferir sus interfaces y operaciones.

A diferencia de las API REST, que utilizan URL distintas para cada resurso, las API SOAP suelen exponer un unico endpoint. Este endpoint es una URL donde el servidor SOAP escucha las solicitudes entrantes. El contenido del propio mensaje SOAP determian la operacion especifica que se desea realizar.

## Descubrimiento de endpoints y parametros SOAP
Para identificar los endpoint (operacionales) y paramtros disponibles para una SOAP, se utilizan los siguientes metodos:

1.- ```Analisis del WSDL```: el archivo WSDL es el recurso mas valioso para entender una API SOAP. Describe:
- Operaciones disponibles (endpoints)
- Parametros de entrada para cada operacion (tipos de mensaje, elementos y atributos)
- Parametros de salida para cada operacion (tipos de mensaje de respuesta)
- Tipos de datos utilizados para los parametros (p. ej., cadenas, enteros, tipos completos)
- La ubicacion (URL) del SOAP
2.- ```Analisis de trafico de red```: De forma similiar a las API REST, se pueden interceptar y analizar el trafico SOAP para observar las solicitudes y respuestas entre los clientes y el servidor.
Herraminetas como Wbireshark o tcpdump pueden interceptar el trafico SOAP.
3.- ```Fuzzing de nombres y valores```:  Aunque las API SOAP suelen tener una estructira bien definida, el fuzzing puede ser util para descubrir operaciones o parametros ocultos o no documentados. Pueden utilizar herramientas de fuzzing para enviar valores malformados o inesperados dentro de las solicitudes SOAP y ver como responde el serv.

## Identificacion de endpiints y parametros de la API GraphQL
A diferencia de las API REST o SOAP, que qa menudo exponen multiples endpoints para diferenntes recursos, las API GraphQL suelen tener un unico endpoint. Este suele ser una URL como ```/graphql``` y sirve como punto de entrada para todas las consultas (queries) y mutaciones (mutations) enviadas a la API.

## Mutaciones (Mutations) de GraphQL
Las mutaciones son las contrapartes de las consultas, diseñadas para modificar datos en el servidor. 
Abarcan operaciones para crear, actualizar o eliminar datos. Al igual que las consultas, las mutaciones tambien pueden aceptar argumentos para definir los valores de entrada para estas operaciones.

| Componentes | Descripcion | Ejemplo | 
| --- | --- | --- | 
| Operacion | La accion a realizar (p. ej., createPost, updateUser, deleteComment) | ```createPost``` |
| Argumento | Datos de entrada necesarios para la operacion (p. ej., titulo y cuerpo para una nueva publicacion). | ```title: "New Post", body: "This is the content of the new posT"``` |
| Seleccion | Campos que desea recuperar en la respuesta una vez completada la mutacion (p. ej., id, titulo de la nueva publicacion). | ```id```, ```title``` | 

**Ejemplo:**
```graphql
mutation {
  createPost(title: "New Post", body: "This is the content of the new post") {
    id
    title
  }
}
```
