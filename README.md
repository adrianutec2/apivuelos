# Parte 1:Infraestructura e IaC

1. Identificar la infraestructura necesaria para ingestar, almacenar y exponer datos:
a. Utilizar el esquema Pub/Sub (no confundir con servicio Pub/Sub de Google) para ingesta de datos
b. Base de datos para el almacenamiento enfocado en analítica de datos
c. Endpoint HTTP para servir parte de los datos almacenados
2. (Opcional) Deployar infraestructura mediante Terraform de la manera que más te acomode. Incluir código fuente Terraform. No requiere pipeline CI/CD

#### Para el desarrollo de la API se utilizo python con Flask, SQLAlchemy y SQLite. Para BD de analitica se podria utilizar BigQuery, dejo un link para referencia: https://www.cdata.com/kb/tech/bigquery-python-sqlalchemy.rst


# Parte 2: Aplicaciones y flujo CI/CD
1. API HTTP: Levantar un endpoint HTTP con lógica que lea datos de base de datos y los exponga al recibir una petición GET
2. Deployar API HTTP en la nube mediante CI/CD a tu elección. Flujo CI/CD y ejecuciones deben estar visibles en el repositorio git.
3. (Opcional) Ingesta: Agregar suscripción al sistema Pub/Sub con lógica para ingresar los datos recibidos a la base de datos. El objetivo es que los mensajes recibidos en un tópico se guarden en la base de datos. No requiere CI/CD.
4. Incluye un diagrama de arquitectura con la infraestructura del punto 1.1 y su interacción con los servicios/aplicaciones que demuestra el proceso end-to-end de ingesta hasta el consumo por la API HTTP

#### Para despliegue se utilizó tanto terraform como cloud build desde consola de GCP. Ver capturas de pantalla en carpeta CapturasEvidencia

Paso a paso para despliegue dcon terraform:
00) Crear proyecto en GCP
01) gcloud auth application-default login --project [nombredelproyectocreado]
02) Modificar ambos archivos variables.tf con el [nombredelproyectocreado]
03) gcloud config set project [nombredelproyectocreado]
04) gcloud init
05) gcloud config list para verificar
06) gcloud config configurations list para chequear si ya existe configuracion docker-push y en ese caso eliminar con gcloud config configurations delete docker-pusher
07) inicializar terraform en backend, terraform -chdir=backend init
08) validar, terraform -chdir=backend validate
09) terraform -chdir=backend apply para crear el bucket para usar de backend
10) inicializar el main, terraform -chdir=main init
11) verificar valor de variable first_time = true, validar terraform -chdir=main validate
12) desplegar infra terraform -chdir=main apply
13) gcloud config configurations create docker-pusher
14) gcloud config set project [nombredelproyectocreado]
15) gcloud auth activate-service-account --key-file=docker_service_account.json
16) gcloud config list para verificar que este activa la config docker-pusher
17) gcloud auth configure-docker us-central1-docker.pkg.dev
18) docker tag api-vuelos-2023 us-central1-docker.pkg.dev/challengesep2023/docker-repository/api-vuelos
19) docker push us-central1-docker.pkg.dev/challengesep2023/docker-repository/api-vuelos
20) cambiar valor de variable first_time a false 
21) terraform -chdir=main apply para desplegar e cloud run y copiar cloud_run_instance_url = "https://..."
	Outputs:
		cloud_run_instance_url = "https://api-test-73yvk6u7aq-uc.a.run.app"


# Parte 3: Pruebas de Integración y Puntos Críticos de Calidad
1. Implementa en el flujo CI/CD en test de integración que verifique que la API efectivamente está exponiendo los datos de la base de datos. Argumenta.
2. Proponer otras pruebas de integración que validen que el sistema está funcionando correctamente y cómo se implementarían.
3. Identificar posibles puntos críticos del sistema (a nivel de fallo o performance) diferentes al punto anterior y proponer formas de testearlos o medirlos (no implementar)
4. Proponer cómo robustecer técnicamente el sistema para compensar o solucionar dichos puntos críticos

#### Para otro momento.

# Parte 4: Métricas y Monitoreo
1. Proponer 3 métricas (además de las básicas CPU/RAM/DISK USAGE) críticas para entender la salud y rendimiento del sistema end-to-end
2. Proponer una herramienta de visualización y describe textualmente qué métricas mostraría, y cómo esta información nos permitiría entender la salud del sistema para tomar decisiones estratégicas
3. Describe a grandes rasgos cómo sería la implementación de esta herramienta en la nube y cómo esta recolectaría las métricas del sistema
4. Describe cómo cambiará la visualización si escalamos la solución a 50 sistemas similares y qué otras métricas o formas de visualización nos permite desbloquear este escalamiento.
5. Comenta qué dificultades o limitaciones podrían surgir a nivel de observabilidad de los sistemas de no abordarse correctamente el problema de escalabilidad

#### Para metricas se utilizan las propias generadas por el servicio de Cloud Run. Para referencia considerar las 4 golden signals  (latency, traffic, saturation, errors).
1. Latency: # requests waiting for a thread, Query duration, Service response time, Transaction duration, Time until first response, Time until complete data return
2. Traffic: # HTTP requests per second, # retrievals per second, # active requests, # write ops, # read ops, # active connections
3. Saturation: Disk quota, Memory quota, # available connections, # users on the system
4. Errors: Wrong answer/content, # 400/500 HTTP codes, # failed requests, # exceptions, # stack traces, Server fails liveness check, # dropped connections

Estas herramientos a de monitoreo y obserbavilidad ya se encuentran impolementadas en GCP y se disponen de mas de 1500 mertricas inteligentes generadas por la plataforma. Incluso sepuden definir metricas personalizadas en caso de ser necesario.
En cuanto a escala bilidad el servico de Cloud Run es autoescalable con lo cual se absorben los picos de traficos y se mantiene la facturacion ajustada segun consumo.


# Parte 5: Alertas y SRE (Opcional)
1. Define específicamente qué reglas o umbrales utilizarías para las métricas propuestas, de manera que se disparan alertas al equipo al decaer la performance del sistema. Argumenta.
2. Define métricas SLIs para los servicios del sistema y un SLO para cada uno de los SLIs. Argumenta por qué escogiste esos SLIs/SLOs y por qué desechaste otras métricas para utilizarlas dentro de la definición de SLIs.

#### Aplicar los principios de Error budget (100%-SLO) para las metricas acordadas y gestionar cliclo de DevOps segun estos presupuestos. 

Especificar los SLI en base al recorrido del usuario (user journey). 
ref.: Descripción general de la observabilidad de los microservicios
https://cloud.google.com/stackdriver/docs/solutions/grpc?hl=es-419

Configura la observabilidad de microservicios https://cloud.google.com/stackdriver/docs/solutions/grpc/set-up-observability?hl=es-419#before-begin

Availability: SLI: The proportion of HTTP GET requests that have 2XX, 3XX or 4XX (excl. 429) status measured at the load balancer. SLO: 99.95% successful in previous 28d

Latency: SLI: The proportion of HTTP GET requests served within X ms measured at the load balancer. SLO: 90% of requests < 500ms in previous 28d

If Errors Over Time/Events Over Time > Error Budget, Alert!
If the SLO is 99.9%/30 days, the error budget is .1%/30 days.

Small windows: Faster alert detection, Shorter reset time, Poor precision
Longer windows: Better precision, Longer reset and detection times, Spend more error budget before alert

See the SRE Workbook for more information:
https://landing.google.com/sre/workbook/chapters/alerting-on-slos/

Prioritize alerts based on customer impact and SLA. Involve humans only for critical alerts! Log low-priority alerts for later analysis: Ticket/Email