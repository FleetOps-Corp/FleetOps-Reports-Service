## 29 de mayo de 2026 Sample Software Architecture [2026] Document 

Este documento establece las bases fundamentales a nivel arquitectural del servicio de Reportes en el sistema de FleetOps. Incluye decisiones arquitecturales, patrones de diseño, atributos de calidad 

Yummy Inc 

## **Control de Cambios** 

||**Creación del documento**|**Creación del documento**|**Creación del documento**|**Creación del documento**|**Creación del documento**|||
|---|---|---|---|---|---|---|---|
|**Autor**||Adolfo Andrey Quiceno Cabrera|||**Fecha**||29/05/2026|
|**Revisado**<br>**por**||**Nombre**|Hector Carabalí||**Fecha**||29/05/2026|
|||**Cargo**||||||
|**Aprobado**<br>**por**||**Nombre**|Juan Francesco García||**Fecha**||29/05/2026|
|||**Cargo**||||||
|**Versión**||**Descripción**|**Autor**|**Aprobado Por**|**Fecha Aprobación**|||
|1.0.1||Segunda versión<br>alineada al formato y<br>cambios<br>arquitecturales|Andrey<br>Quiceno||Seleccione una Fecha|||
|||||||||



## **TABLA DE CONTENIDO** 

|**1.**|**INTRODUCCIÓN**|**3**|
|---|---|---|
|1.1|PROPÓSITO|3|
|1.2|ALCANCE|3|
|1.3|DEFINICIONES,SIGLAS Y ABREVIATURAS|3|
|1.4|REFERENCIAS|3|
|1.5|VISTAGLOBAL|3|
|**2.**|**MACRO ARQUITECTURA**|**3**|
|2.1|METAS YRESTRICCIONESARQUITECTÓNICAS|3|
|**3.**|**VISTA FÍSICA**|**6**|
|**4.**|**VISTA FUNCIONAL O LÓGICA**|**6**|
|**5.**|**VISTA DE DESPLIEGUE**|**7**|



## **1. Introducción** 

El presente Documento de Arquitectura de Software (DAS) describe la arquitectura del sistema FleetOps Reports, un microservicio analítico encargado de consolidar información proveniente de los servicios de Vehículos, Asignaciones, Incidentes y Mantenimientos para generar indicadores operativos, visualizaciones estadísticas y reportes ejecutivos. 

La solución se integra con los sistemas operacionales mediante gRPC, almacena información analítica en MongoDB Atlas y gestiona recursos documentales en MinIO. La arquitectura se diseña bajo principios de desacoplamiento, mantenibilidad y escalabilidad, permitiendo la generación de información estratégica sin afectar los sistemas transaccionales del ecosistema FleetOps. 

Este documento presenta las decisiones arquitectónicas, atributos de calidad, patrones de diseño y vistas UML-Kruchten que describen la solución desde diferentes perspectivas. 

|**Categoría**|**Tecnología**|
|---|---|
|Lenguaje|Python 3.12|
|Framework|FastAPI|
|Comunicación|gRPC|
|Serialización|Protocol Buffers|
|Persistencia|MongoDB Atlas|
|ODM|Beanie|
|Almacenamiento|MinIO|
|Reportes PDF|WeasyPrint|
|Templates|Jinja2|
|Observabilidad|Prometheus|
|Dashboards|Grafana|
|Logs|Loki|
|Contenedores|Docker|



## **2. Propósito** 

El propósito de este Documento de Arquitectura de Software es definir y comunicar la arquitectura del 

sistema FleetOps Reports, estableciendo los componentes, responsabilidades, restricciones, decisiones arquitectónicas y tecnologías que guían su construcción y evolución. además está dirigido a arquitectos de software, desarrolladores, evaluadores académicos, personal de pruebas y responsables de infraestructura, y tiene como propósito servir de referencia para las actividades de diseño, desarrollo, validación, despliegue y mantenimiento de la solución. Su contenido se organiza en torno a las decisiones arquitectónicas adoptadas, los módulos y funcionalidades del sistema, los atributos de calidad, los patrones de diseño y su relación con dichos atributos, las restricciones y consideraciones técnicas, y las diferentes vistas arquitectónicas basadas en el modelo UML-Kruchten, incluyendo la vista física de la solución, la vista funcional o lógica de los procesos principales y la vista de despliegue e infraestructura tecnológica. 

La audiencia objetivo de este documento incluye arquitectos de software, desarrolladores, evaluadores académicos, personal de pruebas, responsables de infraestructura y demás interesados que requieran comprender la arquitectura de la solución. Se espera que este documento sea utilizado como guía para el desarrollo, validación, mantenimiento y futuras extensiones del sistema, garantizando que las decisiones de implementación permanezcan alineadas con la arquitectura definida. 

## **3. Alcance** 

Se define la arquitectura del sistema analítico de FleetCorp S.A., cuya finalidad es centralizar información operacional proveniente de los sistemas de Vehículos, Incidentes, Asignaciones y Mantenimientos 

para generar indicadores de gestión, métricas operativas, estadísticas, gráficas y reportes ejecutivos que apoyen la toma de decisiones organizacionales. 

Este documento establece las directrices arquitectónicas que deben seguirse durante el diseño, desarrollo, despliegue y mantenimiento de la solución, sirviendo como referencia para todos los actores involucrados en el proyecto. El DAS influye directamente en los siguientes artefactos del proyecto: 

- Product Backlog. 

- Historias de Usuario. 

- Diagramas UML de diseño. 

- Diagramas de componentes y despliegue. 

- Modelo de datos analítico. 

- Estrategia de pruebas. 

- Configuración de infraestructura y despliegue. 

- Documentación técnica de desarrollo. 

## _**Decisiones Arquitectónicas**_ 

|**_Decisiones Arquitectónicas_**|**_Decisiones Arquitectónicas_**|
|---|---|
|**ADR-001: Uso de gRPC para Integración entre Servicios**||
|**Elemento**|**Descripción**|
|Contexto|La solución requiere consumir información proveniente de múltiples servicios<br>internos con baja latencia, contratos consistentes y tipado fuerte.|
|Decisión|Utilizar gRPC y Protocol Buffers para la comunicación con los servicios de<br>Vehículos, Incidentes, Mantenimientos y Asignaciones.|
|Consecuencias Positivas|Menor latencia, contratos tipados, serialización eficiente, mejor rendimiento que<br>REST para comunicación interna.|
|Consecuencias Negativas|Mayor complejidad de depuración y pruebas manuales frente a APIs REST.|



|**ADR-002: Uso de MongoDB Atlas para Persistencia Analítica**|**ADR-002: Uso de MongoDB Atlas para Persistencia Analítica**|**ADR-002: Uso de MongoDB Atlas para Persistencia Analítica**|
|---|---|---|
|**Elemento**|**Descripción**||
|Contexto|La información consolidada contiene indicadores, snapshots históricos, métricas y<br>estructuras documentales con evolución frecuente.||
|Decisión|Utilizar MongoDB Atlas como repositorio principal para la persistencia analítica.||
|Consecuencias Positivas|Flexibilidad de esquema, evolución sencilla de modelos analíticos, escalabilidad<br>horizontal.||
|Consecuencias Negativas|Menor capacidad para consultas relacionales complejas y agregaciones altamente<br>normalizadas.||
||||
|**ADR-003: Uso de MinIO para Almacenamiento Documental**|||
|**Elemento**||**Descripción**|
|Contexto<br> <br>||Las gráficas y reportes PDF son artefactos binarios que no deben almacenarse<br>dentro de la base analítica.|
|Decisión<br>||Utilizar MinIO como plataforma de almacenamiento de objetos.|
|Consecuencias Positivas<br> <br>||Separación entre datos analíticos y documentos, escalabilidad para archivos,<br>compatibilidad S3.|
|Consecuencias Negativas||Introduce una dependencia adicional de infraestructura.|



|**ADR-005: Uso de Circuit Breaker para Integraciones gRPC**|**ADR-005: Uso de Circuit Breaker para Integraciones gRPC**|**ADR-005: Uso de Circuit Breaker para Integraciones gRPC**|**ADR-005: Uso de Circuit Breaker para Integraciones gRPC**|
|---|---|---|---|
|**Elemento**||**Descripción**||
|Contexto||La disponibilidad de la plataforma depende de servicios externos que pueden<br>presentar fallas temporales o degradación de rendimiento.||
|Decisión||Implementar Circuit Breaker en las llamadas gRPC hacia servicios operacionales.||
|Consecuencias Positivas||Evita fallas en cascada, mejora la resiliencia y protege recursos internos del sistema.||
|Consecuencias Negativas||Incrementa la complejidad de configuración y monitoreo.||
|||||
|**ADR-006: Separación Interna por Servicios Lógicos**||||
|**Elemento**|**Descripción**|||
|Contexto|El<br>microservicio<br>analítico<br>concentra<br>múltiples<br>responsabilidades<br>funcionales<br>relacionadas con cálculo de indicadores, generación de visualizaciones y construcción<br>documental.|||
|Decisión|Organizar el microservicio mediante componentes internos especializados (Servicios<br>Lógicos) sin desplegarlos como microservicios independientes.|||
|Consecuencias Positivas|Mayor mantenibilidad, menor acoplamiento interno, facilidad para extender nuevos<br>indicadores., evolución independiente de módulos analíticos.|||
|Consecuencias Negativas|Mayor cantidad de componentes internos y necesidad de coordinación entre servicios<br>lógicos.|||
|**_Módulos y Funcionalidades_**<br>**Módulo Funcional**<br>**Funcionalidad**<br>Disponibilidad de Flota<br>Consultar y analizar la disponibilidad operativa de los vehículos.<br>Gestión de Incidentes<br>Analizar recurrencia, severidad y criticidad de incidentes.<br>Gestión de Mantenimientos<br>Calcular indicadores de mantenimiento preventivo y correctivo.<br>Trazabilidad Vehicular<br>Consolidar el historial operativo de un vehículo.<br>Analítica Operacional<br>Generar KPIs, métricas y estadísticas para la toma de decisiones.<br>Visualización de Datos<br>Construir gráficas, rankings y representaciones analíticas.<br>Generación de Reportes<br>Crear reportes ejecutivos en formato PDF.<br>Gestión Documental<br>Almacenar y recuperar reportes históricos y recursos asociados.||||
|**Módulo Funcional**|||**Funcionalidad**|
|Disponibilidad de Flota|||Consultar y analizar la disponibilidad operativa de los vehículos.|
|Gestión de Incidentes|||Analizar recurrencia, severidad y criticidad de incidentes.|
|Gestión de Mantenimientos|||Calcular indicadores de mantenimiento preventivo y correctivo.|
|Trazabilidad Vehicular|||Consolidar el historial operativo de un vehículo.|
|Analítica Operacional|||Generar KPIs, métricas y estadísticas para la toma de decisiones.|
|Visualización de Datos|||Construir gráficas, rankings y representaciones analíticas.|
|Generación de Reportes|||Crear reportes ejecutivos en formato PDF.|
|Gestión Documental|||Almacenar y recuperar reportes históricos y recursos asociados.|



## _**Atributos de Calidad**_ 

|**Categoría**|**Atributo**|**Prioridad**|
|---|---|---|
|Observable|Disponibilidad|Alta|
|Observable|Confiabilidad|Alta|
|Observable|Rendimiento|Media|
|Observable|Integración|Alta|
|Observable|Trazabilidad|Media|
|No Observable|Mantenibilidad|Alta|
|No Observable|Modificabilidad|Media|
|No Observable|Escalabilidad|Media|
|No Observable|Extensibilidad|Media|
|No Observable|Observabilidad|Media|



## _**Patrones de Diseño**_ 

|**Patrón**|**Propósito**|
|---|---|
|Microservice Architecture|Implementar la solución como un microservicio analítico independiente.|
|Aggregator Pattern|Consolidar información proveniente de múltiples servicios operacionales.|
|API Composition Pattern|Construir respuestas analíticas a partir de varias fuentes de información.|
|Repository Pattern|Abstraer el acceso a MongoDB Atlas.|
|DTO Pattern|Transferir información entre capas y servicios.|
|Adapter Pattern|Adaptar modelos externos al dominio analítico interno.|
|Builder Pattern|Construir visualizaciones estadísticas de forma modular.|
|Template View Pattern|Generar reportes PDF a partir de plantillas HTML/Jinja2.|
|Circuit Breaker Pattern|Proteger las integraciones gRPC frente a fallos externos.|
|Observability Pattern|Facilitar monitoreo, métricas y trazabilidad operacional.|



## **4. Definiciones, siglas y abreviaturas** 

|**Término / Sigla**|**Definición**|
|---|---|
|API<br> <br>|Application Programming Interface. Conjunto de mecanismos que permiten la<br>comunicación entre componentes de software.|
|gRPC<br> <br> <br>|Google Remote Procedure Call. Framework de comunicación de alto rendimiento<br>basado en HTTP/2 y Protocol Buffers utilizado para la integración entre servicios<br>distribuidos.|
|Protocol Buffers<br>(Protobuf)<br> <br>|Mecanismo de serialización de datos utilizado por gRPC para definir contratos y<br>estructuras de mensajes.|
|FastAPI<br> <br>|Framework de desarrollo para Python utilizado para la implementación del<br>microservicio analítico y la gestión de su ciclo de vida.|
|MongoDB Atlas<br> <br>|Servicio administrado de MongoDB utilizado como base de datos analítica de la<br>solución.|
|ODM<br> <br>|Object Document Mapper. Herramienta que permite mapear documentos de<br>MongoDB a objetos del lenguaje de programación.|



|Beanie ODM|ODM utilizado para la interacción entre la aplicación desarrollada en Python y<br>MongoDB Atlas.|
|---|---|
|MinIO|Plataforma de almacenamiento de objetos compatible con Amazon S3 utilizada para<br>almacenar reportes generados por el sistema.|
|KPI|Key Performance Indicator. Indicador utilizado para medir el desempeño de un<br>proceso o actividad.|
|MTTR|Mean Time To Repair. Tiempo promedio requerido para restaurar un activo después<br>de una falla.|
|Disponibilidad|Porcentaje de tiempo durante el cual un vehículo o conjunto de vehículos se<br>encuentra operativo y disponible para su utilización.|
|Trazabilidad|Capacidad de reconstruir el historial completo de un vehículo a partir de sus<br>asignaciones, incidentes y mantenimientos registrados.|
|Snapshot|Registro histórico que representa el estado de una entidad en un momento específico<br>del tiempo.|
|Microservicio|Unidad de software autónoma que encapsula una funcionalidad específica y puede<br>evolucionar de manera independiente.|
|Aggregator Pattern|Patrón arquitectónico utilizado para consolidar información proveniente de múltiples<br>sistemas en una única respuesta o modelo de negocio.|
|API Composition Pattern|Patrón utilizado para construir respuestas complejas mediante la combinación de<br>información obtenida de diferentes fuentes.|
|Repository Pattern|Patrón de diseño que abstrae el acceso a la capa de persistencia y desacopla la<br>lógica de negocio de la tecnología de almacenamiento.|
|DTO|Data Transfer Object. Objeto utilizado para transportar información entre componentes<br>o servicios sin exponer detalles internos de implementación.|
|Adapter Pattern|Patrón utilizado para transformar estructuras de datos externas al modelo interno de la<br>aplicación.|
|Template View|Este patrón sugiere crear páginas web estáticas (por ejemplo, en HTML) que sirven<br>como una "plantilla" base. Esta plantilla contiene marcadores o etiquetas especiales<br>en los lugares donde se debe mostrar información dinámica.|
|Builder Pattern|Patrón utilizado para construir objetos complejos de manera incremental y controlada.|
|Circuit Breaker Pattern|Patrón utilizado para evitar fallas en cascada cuando una dependencia externa<br>presenta indisponibilidad.|
|Observability|Capacidad del sistema para exponer información que permita monitorear, diagnosticar<br>y analizar su comportamiento interno.|
|Prometheus|Plataforma de monitoreo utilizada para la recolección de métricas operativas.|
|Grafana|Herramienta utilizada para la visualización de métricas y construcción de tableros de<br>monitoreo.|
|Loki|Sistema de agregación y consulta centralizada de logs.|
|Docker|Plataforma de contenedorización utilizada para empaquetar y desplegar la solución.|
|API Gateway|Componente externo encargado de centralizar el acceso a los servicios del<br>ecosistema y gestionar aspectos transversales como autenticación y enrutamiento.|



|Vehículos|Sistema externo responsable de la administración de los activos vehiculares de la<br>organización.|
|---|---|
|Incidentes|Sistema externo responsable de la gestión de eventos, fallas e incidentes asociados a<br>los vehículos.|
|Mantenimientos|Sistema externo responsable del control y seguimiento de mantenimientos preventivos<br>y correctivos.|



## **5. Referencias** 

|**Referencias**|||
|---|---|---|
|**Documento**|**Versión**|**Fecha de la versión**|
|Diagrama de Arquitectura de Componentes (Visual Paradigm)|1.0|29/05/2026|
|Diagrama UML del Sistema Analítico|1.0|29/05/2026|
|Prompt de Generación del Arquetipo Inicial del Proyecto|1.0|29/05/2026|
|FleetOps contexto de negocio|1.0|29/05/2026|
|FleetOps Procesos|1.0|29/05/2026|
|FleetOps Problemas|1.0|29/05/2026|
|FleetOps Final|1.0|29/05/2026|



Al momento de la elaboración de este documento, el Product Backlog se encuentra en construcción 

como parte de la fase de planeación del proyecto. Una vez sea aprobado, deberá incorporarse como referencia formal y utilizarse como fuente principal de trazabilidad entre requerimientos funcionales y decisiones arquitectónicas. 

## **6. Vista Global** 

La solución se organiza mediante una arquitectura en capas que separa las responsabilidades de presentación, procesamiento analítico y acceso a datos, favoreciendo la mantenibilidad, escalabilidad y desacoplamiento de la solución. 

## _**Capa de Presentación**_ 

Responsable de exponer las capacidades del sistema mediante endpoints de consulta y generación de reportes. Recibe solicitudes, valida parámetros de entrada y delega el procesamiento a la capa de lógica de negocio. 

## _**Capa de Lógica de Negocio**_ 

|**_Capa de Lógica de Negocio_**||
|---|---|
|**Componente Interno**|**Responsabilidad**|
|Disponibilidad Service|Calcula disponibilidad global, por sede y estado operativo de la flota.|
|Maintenance Analytics Service|Calcula MTTR, relación preventivo/correctivo y métricas de<br>mantenimiento.|
|Incident Analytics Service|Analiza recurrencia, severidad e identifica vehículos críticos.|
|Traceability Service|Construye el historial consolidado y la trazabilidad de los vehículos.|
|Calculus Service|Centraliza reglas de negocio, fórmulas, indicadores y cálculos<br>analíticos.|
|Graph Service|Genera gráficas, rankings y visualizaciones estadísticas.|
|Template Service|Construye plantillas documentales HTML/Jinja2 para reportes.|
|Report Service|Orquesta la generación y almacenamiento de reportes PDF.|



## _**Capa de Acceso a Datos**_ 

Gestiona la interacción con los mecanismos de persistencia y almacenamiento del sistema. Esta capa abstrae el acceso a: 

- MongoDB Atlas para el almacenamiento de snapshots, métricas históricas, indicadores y trazabilidad consolidada. 

- MinIO para el almacenamiento de reportes ejecutivos en formato PDF. 

- Clientes gRPC utilizados para la obtención de información desde los sistemas operacionales externos. 

La interacción entre estas capas sigue el principio de separación de responsabilidades, permitiendo mantener una arquitectura modular, escalable, mantenible y alineada con los atributos de calidad definidos para la solución. 

## **7. Marco Arquitectura** 

La solución se implementa como un único microservicio analítico desacoplado de los sistemas transaccionales, encargado de consolidar información proveniente de los servicios de Vehículos, Incidentes, Mantenimientos y Asignaciones para generar indicadores operativos, métricas históricas, visualizaciones estadísticas y reportes ejecutivos. La arquitectura se organiza en tres capas principales: 

## **Capas Arquitectónicas** 

La arquitectura se organiza bajo un modelo en capas compuesto por: 

- Capa de Presentación, encargada de exponer los servicios analíticos y recibir las solicitudes de los consumidores. 

- Capa de Lógica de Negocio, responsable del procesamiento analítico, cálculo de indicadores, generación de visualizaciones y construcción de reportes. 

- Capa de Acceso a Datos, encargada de la persistencia analítica, el almacenamiento documental y la integración con servicios externos. 

La arquitectura es representada mediante las siguientes vistas arquitectónicas: 

|Vista|Contenido|
|---|---|
|Vista Física|Componentes físicos de la solución, mecanismos de persistencia, almacenamiento,<br>observabilidad e integraciones externas.|
|Vista Funcional o Lógica|Procesos analíticos principales, flujo de información y comportamiento de los servicios<br>internos.|
|Vista de Despliegue|Nodos físicos, topología de red, protocolos de comunicación e infraestructura<br>tecnológica utilizada.|



## _**Comunicación entre Capas**_ 

La comunicación sigue un flujo unidireccional controlado, donde cada capa interactúa únicamente con la capa inmediatamente inferior. 

## None 

Presentación -> Lógica de Negocio -> Acceso a Datos 

## _**Integraciones Externas**_ 

|**_graciones Externas_**||
|---|---|
|Sistema|Propósito|
|Servicio de Vehículos|Proveer información vehicular y estado operativo.|
|Servicio de Asignaciones|Proveer información de asignación de vehículos.|
|Servicio de Incidentes|Proveer historial y severidad de incidentes.|
|Servicio de Mantenimientos|Proveer información de mantenimientos preventivos y correctivos.|



|MongoDB Atlas|Persistencia de métricas e información analítica.|
|---|---|
|MinIO|Almacenamiento de recursos gráficos y reportes PDF.|
|Prometheus|Recolección de métricas operativas.|
|Grafana|Visualización de métricas y dashboards.|
|Loki|Centralización y consulta de logs.|



## **8. Metas y Restricciones Arquitectónicas** 

La arquitectura propuesta busca proporcionar una plataforma analítica centralizada para FleetCorp S.A. que permita consolidar información operacional proveniente de múltiples dominios del negocio y transformarla en indicadores, estadísticas y reportes ejecutivos para la toma de decisiones. 

## **Metas Arquitectónicas** 

- Centralizar la información analítica de la flota en una única fuente de verdad. 

- Eliminar la dependencia de procesos manuales y hojas de cálculo dispersas. 

- Facilitar la generación de indicadores operativos y métricas históricas. 

- Permitir la trazabilidad completa de los vehículos durante su ciclo de vida. 

- Generar reportes ejecutivos automatizados con soporte visual. 

- Garantizar escalabilidad y mantenibilidad mediante una arquitectura desacoplada. 

- Proporcionar observabilidad integral del sistema mediante monitoreo y trazabilidad técnica. 

## **Restricciones Arquitectónicas** 

- La comunicación con los sistemas operacionales debe realizarse exclusivamente mediante gRPC. 

- El sistema debe implementarse utilizando Python 3.12 y FastAPI. 

- MongoDB Atlas será la única base de datos utilizada para la persistencia analítica. 

- MinIO será utilizado para el almacenamiento de gráficas y reportes PDF. 

- Los datos operacionales no podrán modificarse desde el microservicio analítico. 

- La observabilidad mediante Prometheus, Grafana y Loki es obligatoria. 

- La arquitectura debe mantener independencia respecto a los sistemas de Vehículos, Incidentes, Mantenimientos y Asignaciones. 

- La autenticación y autorización de las solicitudes son gestionadas por la plataforma corporativa de API Gateway, la cual se considera una dependencia transversal externa al alcance de esta solución. 

|**Atributos de Calidad “Observables”**|**Atributos de Calidad “Observables”**|**Atributos de Calidad “Observables”**|**Atributos de Calidad “Observables”**|
|---|---|---|---|
|**Atributo de Calidad**|**Descripción**|**Tácticas / Patrón de Diseño**|**Dónde se aplica**|
|Disponibilidad|Capacidad del sistema para<br>permanecer<br>operativo<br>y<br>continuar<br>prestando<br>sus<br>servicios analíticos cuando<br>sea requerido.|Circuit<br>Breaker<br>Pattern<br>y<br>monitoreo continuo mediante<br>Prometheus y Grafana.|Comunicación gRPC con<br>los servicios de Vehículos,<br>Incidentes, Mantenimientos<br>y Asignaciones.|
|Confiabilidad|Capacidad del sistema para<br>producir<br>resultados<br>analíticos<br>consistentes y<br>correctos<br>durante<br>su<br>operación.|Aggregator<br>Pattern,<br>API<br>Composition<br>Pattern<br>y<br>persistencia<br>histórica<br>de<br>snapshots analíticos.|Consolidación<br>de<br>información operacional y<br>cálculo de KPIs.|



|Desempeño|Capacidad<br>de<br>generar<br>métricas,<br>estadísticas<br>y<br>reportes dentro de tiempos<br>aceptables<br>para<br>los<br>usuarios.|gRPC Communication Pattern,<br>procesamiento<br>analítico<br>optimizado y almacenamiento<br>documental desacoplado.|Consultas<br>analíticas,<br>generación de gráficas y<br>construcción de reportes<br>PDF.|
|---|---|---|---|
|Observabilidad|Capacidad de monitorear el<br>estado interno del sistema y<br>diagnosticar<br>problemas<br>operativos.|Observability Pattern mediante<br>Prometheus, Grafana y Loki.|Monitoreo<br>de<br>latencia,<br>errores,<br>consumo<br>de<br>recursos<br>y<br>tiempos<br>de<br>procesamiento.|
|Trazabilidad|Capacidad de reconstruir el<br>historial completo de un<br>vehículo<br>y sus eventos<br>asociados.|Aggregator<br>Pattern<br>y<br>API<br>Composition Pattern.|Consolidación<br>de<br>vehículos,<br>incidentes,<br>mantenimientos<br>y<br>asignaciones.|
|Integridad<br>de<br>la<br>Información|Garantiza que los datos<br>analíticos reflejen fielmente<br>la información obtenida de<br>los sistemas operacionales.|DTO Pattern y Adapter Pattern<br>para<br>normalización<br>y<br>transformación<br>de<br>datos<br>externos.|Procesamiento<br>y<br>consolidación<br>de<br>información operacional.|



## **Atributos de Calidad “No observables”** 

|**Atributos de Calidad “No observables”**|**Atributos de Calidad “No observables”**|**Atributos de Calidad “No observables”**|**Atributos de Calidad “No observables”**|
|---|---|---|---|
|**Atributo**|**Descripción**|**Tácticas / Patrón de**<br>**Arquitectura**|**Dónde se aplica**|
|Modificabilidad|Capacidad de incorporar<br>nuevos indicadores,<br>reportes o fuentes de<br>información con bajo<br>impacto sobre el sistema<br>existente.|Arquitectura por capas,<br>Repository Pattern y Template<br>View Pattern.|Servicios analíticos,<br>cálculo de KPIs y<br>generación de reportes.|
|Mantenibilidad|Capacidad de realizar<br>correcciones y evoluciones<br>de forma controlada y con<br>bajo costo de<br>mantenimiento.|Separación de<br>responsabilidades,<br>arquitectura por capas, DTO<br>Pattern y Repository Pattern.|Toda la arquitectura del<br>microservicio.|
|Escalabilidad|Capacidad de incrementar<br>recursos para soportar<br>mayores volúmenes de<br>procesamiento analítico.|Microservice Architecture y<br>desacoplamiento de<br>persistencia mediante<br>MongoDB Atlas y MinIO.|Procesamiento de<br>métricas, generación de<br>gráficas y reportes.|



|Extensibilidad|Capacidad de incorporar<br>nuevos tipos de análisis,<br>visualizaciones o formatos<br>de reporte sin modificar la<br>arquitectura base.|Arquitectura por capas,<br>desacoplamiento de casos de<br>uso analíticos y Builder<br>Pattern para la construcción<br>progresiva y extensible de<br>visualizaciones estadísticas.|Generación de<br>indicadores, gráficas,<br>visualizaciones<br>estadísticas y reportes<br>PDF.|
|---|---|---|---|
|Portabilidad|Capacidad de desplegar el<br>sistema en distintos<br>entornos sin cambios<br>significativos en el código.|Docker, configuración<br>externalizada mediante<br>variables de entorno y<br>tecnologías multiplataforma.|Despliegue y operación<br>del sistema.|
|Reusabilidad|Capacidad de reutilizar<br>componentes analíticos y<br>servicios de negocio en<br>diferentes funcionalidades<br>del sistema.|DTO Pattern y Repository<br>Pattern.|Casos de uso analíticos y<br>generación de reportes.|
|Interoperabilidad|Capacidad del sistema para<br>intercambiar información de<br>forma consistente con otros<br>sistemas y plataformas.|gRPC Communication<br>Pattern, Protocol Buffers, DTO<br>Pattern y Adapter Pattern.|Integración con los<br>servicios de Vehículos,<br>Incidentes,<br>Mantenimientos y<br>Asignaciones.|
|Integración|Capacidad de incorporar<br>nuevas fuentes de datos o<br>servicios externos con<br>cambios mínimos en la<br>arquitectura existente.|API Composition Pattern,<br>Aggregator Pattern y contratos<br>gRPC desacoplados.|Integraciones actuales y<br>futuras del ecosistema<br>FleetCorp.|



## **9. Vista Física** 

La solución se implementa como un microservicio analítico independiente encargado de consumir información operacional, consolidar métricas de negocio y generar reportes ejecutivos. Para su funcionamiento interactúa con servicios externos, mecanismos de persistencia, almacenamiento documental y componentes de observabilidad. 

## **Componentes Físicos de la Solución** 

|**Componente**|**Tecnología /**<br>**Plataforma**|**Responsabilidad**|
|---|---|---|
|Microservicio Analítico|FastAPI + Python 3.12<br> <br>|Consolidación de datos, cálculo de KPIs, generación de<br>gráficas y construcción de reportes PDF.|
|API Gateway Corporativo|Plataforma Externa<br> <br>|Gestión centralizada de autenticación, autorización y<br>control de acceso.|
|Servicio de Vehículos|Microservicio Externo<br> <br>|Proporciona información del inventario y estado operativo<br>de los vehículos.|



|Servicio de Incidentes|Microservicio Externo|Proporciona información de incidentes y eventos asociados<br>a los vehículos.|
|---|---|---|
|Servicio de<br>Mantenimientos|Microservicio Externo|Proporciona información de mantenimientos preventivos y<br>correctivos.|
|Servicio de Asignaciones|Microservicio Externo|Proporciona información de asignaciones históricas y<br>actuales de vehículos.|
|MongoDB Atlas|Base de Datos<br>Documental|Almacenamiento de métricas, snapshots históricos y<br>trazabilidad consolidada.|
|MinIO - Recursos Gráficos|Object Storage|Almacenamiento de imágenes estadísticas generadas por<br>el sistema.|
|MinIO - Reportes<br>Ejecutivos|Object Storage|Almacenamiento de reportes PDF generados.|
|Prometheus|Monitoreo|Recolección de métricas operativas.|
|Grafana|Visualización|Construcción de dashboards de monitoreo.|
|Loki|Logging|Centralización y consulta de logs.|



## _**Interacción Entre Componentes**_ 

1. El consumidor accede al sistema a través del API Gateway corporativo. 

2. El microservicio analítico consulta información de los servicios de Vehículos, Incidentes, Mantenimientos y Asignaciones mediante gRPC protegido por Circuit Breaker. 

3. La información obtenida es consolidada y procesada para generar indicadores operativos y métricas analíticas. 

4. Los resultados consolidados son almacenados en MongoDB Atlas. 

5. Para la generación de reportes, el sistema consulta la información analítica almacenada y genera las visualizaciones estadísticas correspondientes. 

6. Las gráficas se almacenan en la instancia de MinIO destinada a recursos gráficos. 

7. El reporte PDF es generado y almacenado en la instancia de MinIO destinada a reportes ejecutivos. 

8. El sistema retorna al consumidor el resultado analítico solicitado o la referencia del reporte generado. 

9. Prometheus, Grafana y Loki monitorean continuamente la operación del sistema. 

## _**Representación Física**_ 

La distribución física de la solución se representa mediante el Diagrama de Componentes de Arquitectura, en el cual se identifican: 

   - API Gateway corporativo. 

   - Servicios operacionales externos. 

   - Microservicio analítico. 

   - MongoDB Atlas. 

   - Instancia MinIO para recursos gráficos. 

   - Instancia MinIO para reportes ejecutivos. 

   - Componentes de observabilidad (Prometheus, Grafana y Loki). 

   - Canales de comunicación HTTP/REST y gRPC. 

   - Aplicación del patrón Circuit Breaker sobre las integraciones externas. 

**10. Vista Funcional o Lógica** 

## **10.1 Proceso de Cálculo de Disponibilidad Operativa** 

## _**Objetivo**_ 

Determinar el porcentaje real de disponibilidad de la flota mediante la correlación de información operacional proveniente de múltiples fuentes. 

## _**Procesos involucrados**_ 

- Cliente solicitante 

- Servicio Analítico de Reportes 

- Servicio de Vehículos 

- Servicio de Asignaciones 

- Servicio de Incidentes 

- Servicio de Mantenimientos 

- MongoDB Atlas 

## _**Comportamiento**_ 

Este proceso consolida la información de inventario, asignaciones, incidentes y mantenimientos para 

determinar cuántos vehículos se encuentran realmente disponibles para operación. 

La disponibilidad no se obtiene directamente de una fuente única, sino que es calculada a partir de reglas de negocio que relacionan múltiples dominios operacionales. 

## _**Interacciones**_ 

1. El cliente solicita la disponibilidad de la flota. 

2. El servicio consulta el inventario total de vehículos. 

3. Consulta los vehículos actualmente asignados. 

4. Consulta los vehículos con mantenimientos activos. 

5. Consulta los vehículos afectados por incidentes críticos. 

6. Consolida la información obtenida. 

7. Aplica las reglas de negocio de disponibilidad. 

8. Calcula indicadores globales y por sede. 

9. Persiste los resultados analíticos. 

10. Retorna la información calculada. 

## _**Ciclo de Vida**_ 

1. Recepción de solicitud. 

2. Consulta de fuentes operacionales. 

3. Consolidación de información. 

4. Aplicación de reglas de negocio. 

5. Persistencia analítica. 

6. Respuesta al consumidor. 

7. Finalización del proceso. 

## _**Características de Comunicación**_ 

- Comunicación síncrona mediante gRPC. 

- Patrón Request-Response. 

- Manejo de errores mediante excepciones controladas. 

- Persistencia mediante operaciones CRUD sobre MongoDB Atlas. 

- Consistencia basada en la información disponible al momento de la consulta. 

## _**Operaciones Funcionales**_ 

|**_peraciones Funcionales_**|||
|---|---|---|
|**Tipo de Acción**|**Recurso Consumido**|**Procesamiento**|
|Consulta Externa|Vehículos|Obtención del inventario total de vehículos.|
|Consulta Externa|Asignaciones|Obtención de vehículos actualmente asignados.|



|Consulta Externa|Mantenimientos|Obtención de vehículos en mantenimiento activo.|
|---|---|---|
|Consulta Externa|Incidentes|Obtención de vehículos con incidentes críticos abiertos.|
|Procesamiento Interno|Datos Consolidados|Aplicación de reglas de disponibilidad.|
|Persistencia|MongoDB Atlas|Almacenamiento de indicadores históricos.|



## _**Resultado**_ 

- Disponibilidad global de la flota. 

- Disponibilidad por sede. 

- Disponibilidad por categoría. 

- Históricos de disponibilidad. 

## **10.2 Proceso de Cálculo de Eficiencia de Mantenimiento** 

## _**Objetivo**_ 

Evaluar la efectividad de las actividades de mantenimiento mediante indicadores operativos y temporales. 

## _**Procesos involucrados**_ 

- Servicio Analítico de Reportes 

- Servicio de Mantenimientos 

- MongoDB Atlas 

## _**Comportamiento**_ 

Este proceso analiza el historial de mantenimientos para identificar tendencias operativas, calcular 

indicadores de desempeño y determinar la eficiencia de las estrategias de mantenimiento implementadas. 

## _**Interacciones**_ 

1. Consulta los mantenimientos registrados. 

2. Clasifica los mantenimientos como preventivos o correctivos. 

3. Obtiene fechas de inicio y finalización. 

4. Calcula tiempos de reparación. 

5. Calcula el MTTR. 

6. Calcula el ratio preventivo/correctivo. 

7. Persiste los resultados obtenidos. 

8. Retorna los indicadores calculados. 

## _**Ciclo de Vida**_ 

1. Obtención de registros de mantenimiento. 

2. Clasificación de eventos. 

3. Cálculo de indicadores. 

4. Persistencia de resultados. 

5. Respuesta al consumidor. 

## _**Características de Comunicación**_ 

- Comunicación síncrona mediante gRPC. 

- Operaciones analíticas internas sobre datos consolidados. 

- Persistencia en MongoDB Atlas. 

- Procesamiento estadístico de datos históricos. 

## _**Operaciones Funcionales**_ 

|**_raciones Funcionales_**|||
|---|---|---|
|**Tipo de Acción**|**Recurso Consumido**|**Procesamiento**|
|Consulta Externa|Mantenimientos|Obtención del historial de mantenimientos.|



|Procesamiento Interno|Datos históricos|Clasificación preventivo/correctivo.|
|---|---|---|
|Procesamiento Interno|Fechas de mantenimiento|Cálculo de MTTR.|
|Procesamiento Interno|Datos consolidados|Cálculo de indicadores de eficiencia.|
|Persistencia|MongoDB Atlas|Almacenamiento de métricas históricas.|



## _**Resultado**_ 

- Tiempo medio de reparación (MTTR). 

- Ratio preventivo/correctivo. 

- Indicadores históricos de mantenimiento. 

- Tendencias operativas. 

## **10.3 Proceso de Identificación de Vehículos Críticos** 

## _**Objetivo**_ 

Detectar vehículos que presentan comportamientos operativos anómalos o riesgos elevados para la operación. 

## _**Procesos involucrados**_ 

- Servicio Analítico de Reportes 

- Servicio de Incidentes 

- Servicio de Mantenimientos 

- MongoDB Atlas 

## _**Comportamiento**_ 

El proceso analiza la recurrencia de incidentes y mantenimientos para identificar activos con comportamiento problemático y priorizar acciones correctivas. 

## _**Interacciones**_ 

1. Consulta incidentes históricos. 

2. Consulta mantenimientos históricos. 

3. Calcula frecuencia de incidentes. 

4. Calcula recurrencia de fallas. 

5. Evalúa niveles de criticidad. 

6. Genera clasificación de vehículos críticos. 

7. Persiste los resultados. 

8. Retorna los indicadores generados. 

## _**Ciclo de Vida**_ 

1. Recolección de información histórica. 

2. Consolidación de eventos. 

3. Cálculo de recurrencias. 

4. Clasificación de criticidad. 

5. Persistencia de resultados. 

6. Publicación de indicadores. 

## _**Características de Comunicación**_ 

- Comunicación síncrona mediante gRPC. 

- Procesamiento analítico interno. 

- Persistencia histórica en MongoDB Atlas. 

- Cálculo de métricas derivadas de múltiples fuentes. 

## _**Operaciones Funcionales**_ 

|**Tipo de Acción**|**Recurso Consumido**|**Procesamiento**|
|---|---|---|
|Consulta Externa|Incidentes|Obtención de historial de incidentes.|
|Consulta Externa|Mantenimientos|Obtención de historial de mantenimientos.|
|Procesamiento Interno|Datos consolidados|Cálculo de recurrencia.|
|Procesamiento Interno|Datos consolidados|Determinación de criticidad.|
|Persistencia|MongoDB Atlas|Almacenamiento de indicadores.|



## _**Resultado**_ 

- Ranking de vehículos críticos. 

- Frecuencia de incidentes por vehículo. 

- Tendencias históricas de criticidad. 

- Activos prioritarios para intervención. 

## **10.4 Proceso de Trazabilidad Histórica del Vehículo** 

## _**Objetivo**_ 

Construir una vista integral del historial operativo de un vehículo específico mediante la consolidación de información proveniente de los diferentes dominios operacionales del ecosistema. 

## **Procesos involucrados** 

- Cliente solicitante 

- Servicio Analítico de Reportes 

- Servicio de Vehículos 

- Servicio de Asignaciones 

- Servicio de Incidentes 

- Servicio de Mantenimientos 

- MongoDB Atlas 

## _**Comportamiento**_ 

Este proceso recopila y correlaciona la información histórica asociada a un vehículo determinado, 

permitiendo reconstruir su comportamiento operativo a lo largo del tiempo. La información consolidada incluye datos maestros del vehículo, historial de asignaciones, incidentes registrados y actividades de mantenimiento ejecutadas. 

## _**Interacciones**_ 

1. El cliente solicita la trazabilidad de un vehículo. 

2. El servicio consulta la información maestra del vehículo. 

3. Consulta el historial de asignaciones. 

4. Consulta el historial de incidentes. 

5. Consulta el historial de mantenimientos. 

6. Consolida toda la información obtenida. 

7. Organiza los eventos cronológicamente. 

8. Construye una línea temporal unificada. 

9. Almacena la información consolidada para futuras consultas. 

10. Retorna la trazabilidad completa del vehículo. 

## _**Ciclo de Vida**_ 

1. Recepción de solicitud. 

2. Consulta de fuentes operacionales. 

3. Consolidación de información. 

4. Construcción de línea temporal. 

5. Persistencia analítica. 

6. Entrega de resultados. 

7. Finalización del proceso. 

## _**Características de Comunicación**_ 

- Comunicación síncrona mediante gRPC. 

- Patrón Request-Response. 

- Agregación de información proveniente de múltiples servicios. 

- Persistencia de resultados en MongoDB Atlas. 

- Procesamiento orientado a consultas históricas. 

## _**Operaciones Funcionales**_ 

|**Tipo de Acción**|**Recurso Consumido**|**Procesamiento**|
|---|---|---|
|Consulta Externa|Vehículos|Obtención de información maestra del vehículo.|
|Consulta Externa|Asignaciones|Obtención del historial operativo del vehículo.|
|Consulta Externa|Incidentes|Obtención de incidentes asociados al vehículo.|
|Consulta Externa|Mantenimientos|Obtención del historial de mantenimiento.|
|Procesamiento Interno|Datos consolidados|Construcción de línea temporal unificada.|
|Persistencia|MongoDB Atlas|Almacenamiento de trazabilidad histórica.|



## _**Resultado**_ 

- Historial completo del vehículo. 

- Línea temporal consolidada. 

- Vista 360° del activo. 

- Información histórica para análisis y auditoría. 

## _**10.5. Proceso de Generación de Visualizaciones Estadísticas**_ 

## _**Objetivo**_ 

Transformar los indicadores analíticos almacenados en representaciones visuales que faciliten la 

interpretación de la información y la toma de decisiones. 

## _**Procesos involucrados**_ 

- Servicio Analítico de Reportes 

- MongoDB Atlas 

- MinIO 

## _**Comportamiento**_ 

Este proceso obtiene métricas previamente consolidadas y genera visualizaciones estadísticas con Builder Pattern, permitiendo generar de forma incremental las distintas secciones del reporte que representan el comportamiento de la flota y sus indicadores operativos. 

Las gráficas generadas son almacenadas en MinIO para su posterior utilización en reportes ejecutivos. 

## _**Interacciones**_ 

1. Se consultan las métricas analíticas almacenadas. 

2. Se obtienen los datasets requeridos. 

3. Se generan las visualizaciones estadísticas. 

4. Se almacenan las imágenes generadas en MinIO. 

5. Se registran las rutas de acceso correspondientes. 

6. Se ponen a disposición para la generación de reportes. 

## _**Ciclo de Vida**_ 

1. Recuperación de datos analíticos. 

2. Construcción de datasets. 

3. Generación de visualizaciones. 

4. Almacenamiento de imágenes. 

5. Registro de metadatos. 

6. Finalización del proceso. 

## _**Características de Comunicación**_ 

- Comunicación interna con MongoDB Atlas. 

- Comunicación mediante API de almacenamiento con MinIO. 

- Procesamiento estadístico local. 

- Operaciones de lectura y escritura de objetos. 

## _**Operaciones Funcionales**_ 

|**_Operaciones Funcionales_**|||
|---|---|---|
|**Tipo de Acción**|**Fuente**|**Procesamiento**|
|Consulta Interna|MongoDB Atlas|Obtención de métricas históricas.|
|Generación Estadística|Disponibilidad|Construcción de gráficas de disponibilidad.|
|Generación Estadística|Incidentes|Construcción de gráficas de recurrencia y severidad.|
|Generación Estadística|Mantenimientos|Construcción de gráficas de mantenimiento.|
|Generación Estadística|MTTR|Construcción de gráficas de desempeño técnico.|
|Generación Estadística|Trazabilidad|Construcción de visualizaciones históricas.|
|Almacenamiento|MinIO|Persistencia de imágenes generadas.|



## _**Resultado**_ 

- Gráficas estadísticas. 

- Visualizaciones analíticas. 

- Recursos gráficos reutilizables. 

- URLs de acceso a imágenes almacenadas. 

## **10.6 Proceso de Generación de Reportes Ejecutivos** 

## _**Objetivo**_ 

Construir documentos PDF ejecutivos que consoliden indicadores, métricas, tablas y visualizaciones estadísticas en un único artefacto documental. 

## _**Procesos involucrados**_ 

- Cliente solicitante 

- Servicio Analítico de Reportes 

- MongoDB Atlas 

- MinIO (Gráficas) 

- MinIO (Reportes) 

## _**Comportamiento**_ 

Este proceso integra la información analítica consolidada con las visualizaciones previamente generadas para construir reportes ejecutivos destinados a la toma de decisiones. A diferencia de la generación de gráficas, este proceso utiliza las imágenes previamente almacenadas en MinIO para incorporarlas en una plantilla documental antes de generar el PDF final. 

La construcción del documento se realiza siguiendo el Template View Pattern, permitiendo ensamblar 

de forma las distintas secciones del reporte (indicadores, métricas, tablas, gráficos y conclusiones) sin acoplar la lógica de generación a una estructura documental específica. 

## _**Interacciones**_ 

1. El cliente solicita la generación de un reporte a través del API Gateway. 

2. Se consultan las métricas, KPIs y textos de resumen almacenados en MongoDB Atlas. 

3. Se generan las URLs firmadas temporalmente (Pre Signed URLs) de las gráficas estadísticas almacenadas en MinIO. 

4. Se construye el modelo de datos unificado del reporte (combinando los datos planos de MongoDB y las URLs efímeras de MinIO). 

5. Se ensamblan las diferentes secciones del documento de forma estructurada mediante el Template View Pattern. 

6. Se completa y procesa la plantilla documental en formato HTML/CSS mediante Jinja2. 

7. Se genera el documento PDF final utilizando el motor de renderizado WeasyPrint. 

8. El archivo PDF ejecutivo es almacenado de forma segura en el bucket de reportes de MinIO. 

9. Se registra el identificador del reporte y se retorna la referencia de su ubicación al cliente. 

10. Se retorna la referencia del documento generado. 

## _**Ciclo de Vida**_ 

1. Recepción de solicitud. 

2. Recuperación de información analítica. 

3. Recuperación de recursos visuales. 

4. Construcción de plantilla. 

5. Generación de PDF. 

6. Almacenamiento documental. 

7. Publicación del resultado. 

8. Finalización del proceso. 

## _**Características de Comunicación**_ 

- Comunicación interna con MongoDB Atlas. 

- Comunicación con MinIO para recuperación de imágenes. 

- Comunicación con MinIO para almacenamiento documental. 

- Procesamiento síncrono de construcción documental. 

- Persistencia de artefactos binarios. 

## _**Operaciones Funcionales**_ 

|**_aciones Funcionales_**|||
|---|---|---|
|**Tipo de Acción**|**Recurso**|**Procesamiento**|
|Consulta Interna|MongoDB Atlas|Obtención<br>de<br>KPIs<br>y<br>métricas<br>consolidadas.|
|Consulta Interna|MinIO (Gráficas)|Recuperación de URLs de imágenes.|
|Construcción de Documento|Template View|Ensamblaje<br>de<br>métricas,<br>tablas,<br>indicadores y visualizaciones.|
|Construcción de Documento|Plantilla Jinja2|Integración de métricas, tablas y gráficas.|
|Generación PDF|WeasyPrint|Construcción del documento final.|
|Almacenamiento|MinIO (Reportes)|Persistencia del PDF generado.|
|Consulta|MinIO (Reportes)|Recuperación de reportes históricos.|



## _**Resultado**_ 

- Reportes PDF ejecutivos. 

- Reportes históricos almacenados. 

- Documentación consolidada de indicadores. 

- Distribución centralizada de información analítica. 

## **10.7 Proceso de Observabilidad y Monitoreo** 

## _**Objetivo**_ 

Garantizar la supervisión continua del comportamiento operativo y técnico del sistema mediante la recopilación y visualización de métricas. 

## _**Procesos involucrados**_ 

- Servicio Analítico de Reportes 

- Prometheus 

- Grafana 

## _**Comportamiento**_ 

Este proceso recopila métricas técnicas relacionadas con las comunicaciones gRPC, consultas a bases de datos, generación de visualizaciones y construcción de reportes PDF. 

La información recolectada permite detectar fallos, cuellos de botella y oportunidades de optimización. 

## _**Interacciones**_ 

1. El servicio expone métricas internas. 

2. Prometheus realiza la recolección periódica. 

3. Las métricas son almacenadas por Prometheus. 

4. Grafana consulta las métricas recopiladas. 

5. Se construyen dashboards operativos y técnicos. 

6. Los responsables del sistema monitorean el comportamiento de la plataforma. 

## _**Ciclo de Vida**_ 

1. Exposición de métricas. 

2. Recolección automática. 

3. Almacenamiento temporal. 

4. Visualización. 

5. Análisis operativo. 

6. Detección de anomalías. 

7. Mejora continua. 

## _**Características de Comunicación**_ 

- Comunicación basada en recolección periódica de métricas. 

- Exposición mediante endpoint de monitoreo. 

- Comunicación entre Prometheus y Grafana. 

- Procesamiento orientado a observabilidad. 

## _**Operaciones Funcionales**_ 

|**_raciones Funcionales_**|||
|---|---|---|
|**Tipo de Acción**|**Herramienta**|**Información Monitoreada**|
|Métricas de comunicación|Prometheus|Latencia y errores de llamadas gRPC.|
|Métricas de persistencia|Prometheus|Consultas y tiempos de respuesta de MongoDB.|
|Métricas de almacenamiento|Prometheus|Operaciones sobre MinIO.|
|Métricas de visualización|Prometheus|Tiempo de generación de gráficas.|
|Métricas documentales|Prometheus|Tiempo de generación y almacenamiento de PDF.|
|Visualización|Grafana|Dashboards operativos y técnicos.|



## _**Resultado**_ 

- Monitoreo en tiempo real. 

- Detección temprana de fallos. 

- Diagnóstico de problemas. 

- Métricas de rendimiento histórico. 

- Soporte para mejora continua y capacidad operativa. 

## **11. Vista de Despliegue** 

## **11.1 Configuración Física: Plataforma Analítica FleetOps Reports** 

La solución se despliega como un microservicio especializado en analítica y generación documental, encargado de consumir información operativa mediante gRPC desde los servicios del ecosistema FleetOps, consolidar métricas analíticas, generar visualizaciones estadísticas y construir reportes ejecutivos en formato PDF.  El servicio expone su API de consumo mediante HTTP/REST a través de FastAPI, mientras que la comunicación interna con servicios operacionales se realiza mediante gRPC. 

## **11.2 Topología de Red Física** 

## _**Interconexiones de Red**_ 

|**_nexiones de Red_**|||
|---|---|---|
|**Origen**|**Destino**|**Protocolo**|
|Cliente Consumidor|API Gateway|HTTP/REST|
|API Gateway|FleetOps Reports Service|HTTP/REST|
|FleetOps Reports Service|Servicio de Vehículos|gRPC|
|FleetOps Reports Service|Servicio de Asignaciones|gRPC|
|FleetOps Reports Service|Servicio de Incidentes|gRPC|
|FleetOps Reports Service|Servicio de Mantenimientos|gRPC|
|FleetOps Reports Service|MongoDB Atlas|MongoDB Driver + TLS|
|FleetOps Reports Service|MinIO|S3 API (HTTPS)|
|Prometheus|FleetOps Reports Service|HTTP|
|Grafana|Prometheus|HTTP|



## **Nodos Físicos de la Solución** 

|**Nodo**|**Software Ejecutado**|**Responsabilidad**|
|---|---|---|
|Cliente Consumidor|Cliente web o aplicación externa|Solicitar generación y consulta de reportes|
|API Gateway|Gateway HTTP (routing, auth, rate limiting)|Punto único de entrada al ecosistema|
|FleetOps Reports Service|FastAPI, servicios gRPC client, motor<br>analítico, generador de gráficas y PDF|Consolidación analítica y generación<br>documental|
|MongoDB Atlas|MongoDB Atlas|Persistencia de métricas, KPIs y metadatos de<br>reportes|
|MinIO|MinIO Object Storage|Almacenamiento de imágenes estadísticas y<br>reportes PDF|
|Servicios Operacionales<br>FleetCorp|Servicios de Vehículos, Asignaciones,<br>Incidentes y Mantenimientos|Proveer información operacional|
|Observabilidad|Prometheus y Grafana|Monitoreo y visualización de métricas|



**11.4 Mapa de Procesos por Nodo** 

|**Nodo**|**Procesos Principales**|**Nodo**|
|---|---|---|
|FleetOps Reports<br>Service|Consolidación analítica, cálculo de KPIs,<br>generación de visualizaciones y generación<br>de reportes PDF|<br>FleetOps Reports Service|
|MongoDB Atlas|Persistencia y consulta de métricas, KPIs y<br>snapshots históricos|MongoDB Atlas|
|MinIO – Recursos<br>Gráficos|Almacenamiento y recuperación de<br>imágenes y visualizaciones estadísticas|MinIO – Recursos Gráficos|
|MinIO – Reportes<br>Ejecutivos|Almacenamiento y recuperación de<br>reportes PDF generados|MinIO – Reportes Ejecutivos|
|Servicios Operacionales<br>FleetCorp|Gestión de vehículos, asignaciones,<br>incidentes y mantenimientos|Servicios Operacionales FleetCorp|
|Observabilidad|Recolección de métricas, monitoreo y<br>centralización de logs|Observabilidad|



## **11.5 Flujo General de Despliegue** 

|**Paso**|**Acción**|
|---|---|
|1|El cliente solicita la generación de un reporte a través del API Gateway|
|2|El API Gateway enruta la solicitud hacia FleetOps Reports Service|
|3|FleetOps Reports Service consulta los servicios operacionales vía gRPC|
|4|Se consolidan y calculan los indicadores de negocio|
|5|Los resultados se almacenan en MongoDB Atlas|
|6|Se generan las gráficas estadísticas|
|7|Las imágenes son almacenadas en MinIO|
|8|las URLs recuperadas de MinIO no son enlaces públicos directos, sino URLs firmadas<br>temporalmente (Presigned URLs) con un tiempo de expiración corto (por ejemplo, 5 o 10<br>minutos). Esto garantiza que WeasyPrint pueda descargar los gráficos mediante HTTP<br>de forma segura, sin exponer públicamente el bucket de MinIO.|
|9|Se construye la plantilla documental|
|10|Se genera el documento PDF|
|11|El PDF es almacenado en MinIO|
|12|Se retorna el identificador del reporte generado al cliente|
|13|Prometheus y Grafana monitorean la ejecución del sistema|



