---
name: uml-architecture
description: >
  Modela, genera o evalúa diagramas UML de arquitectura — Componentes, Paquetes y
  Despliegue — con semántica UML estándar por defecto. Es agnóstico a dominio, curso,
  herramienta y organización; perfiles locales pueden simplificar la representación solo
  cuando estén documentados o sean solicitados explícitamente. Activar ante UML, diagramas
  de componentes, paquetes, capas, despliegue, artifact, deploy, node, interfaz provista o
  requerida, lollipop, socket, puertos o dependencias UML.
---

# UML Architecture — núcleo estándar y agnóstico

## 1. Alcance, autoridad y orden de decisión

Este skill modela vistas arquitectónicas UML, no impone una arquitectura, dominio,
herramienta, número de capas ni estilo gráfico. Cubre principalmente diagramas de
**Componentes**, **Paquetes** y **Despliegue**. UML tiene más diagramas; usar otro tipo
solo cuando la pregunta lo requiera.

Base normativa externa: OMG, *Unified Modeling Language (UML) 2.5.1*, especificación
formal, diciembre de 2017: <https://www.omg.org/spec/UML/2.5.1/About-UML/>. La semántica
del modelo prevalece sobre la disponibilidad de un shape en una herramienta.

Orden de decisión:

1. Requisito explícito del usuario, contrato, norma o enunciado.
2. Perfil documentado de curso, organización o cliente, declarado como perfil.
3. UML estándar (`strict-uml`), que es el valor por defecto.
4. Supuestos mínimos, declarados antes de incorporarlos al diagrama.

Un ejemplo anterior, un archivo de un proyecto o una apariencia de draw.io no crea por sí
solo una convención universal. Si contradice una regla formal o un perfil, documentar la
divergencia en vez de atribuirla silenciosamente a UML.

## 2. Contrato de modelado antes de dibujar

Antes de generar XML, obtener o declarar estos datos:

| Dato | Pregunta que debe resolverse |
|---|---|
| Objetivo | ¿Qué decisión, responsabilidad o topología debe comunicar la vista? |
| Tipo de diagrama | ¿Componentes, Paquetes, Despliegue u otro solicitado? |
| Alcance | ¿Qué sistema, límite y nivel de detalle incluye y excluye? |
| Elementos | ¿Qué componentes, paquetes, nodos, artifacts, interfaces o actores existen? |
| Relaciones | ¿Qué semántica tiene cada relación y cuál es su dirección? |
| Perfil | ¿`strict-uml`, simplificado documentado, curso o perfil organizacional? |
| Supuestos | ¿Qué información no entrega el caso y afecta el modelo? |

No elegir los elementos porque “se ven bien” ni inventar capas, protocolos, estereotipos o
infraestructura. Si una vista es solo un inventario modular, puede no tener conexiones;
debe titularse o anotarse como inventario, no insinuar relaciones inexistentes.

## 3. Perfil por defecto: `strict-uml`

`strict-uml` conserva la semántica UML y usa notación reconocible. Puede adaptar el layout
para legibilidad, pero no sustituye relaciones o elementos por cajas genéricas.

### 3.1 Diagrama de Componentes

| Elemento/relación | Uso correcto |
|---|---|
| Component | Unidad modular y reemplazable con responsabilidades o servicios definidos. Usar el símbolo UML de componente o una representación equivalente identificada inequívocamente. |
| Interfaz provista | Servicio que el componente ofrece; se representa como lollipop o con la notación de interfaz equivalente. |
| Interfaz requerida | Servicio que el componente necesita; se representa como socket o notación equivalente. |
| Assembly connector | Une una interfaz requerida con una provista compatible. |
| Delegation connector | Delega una interacción entre el borde de un componente estructurado y una parte interna. |
| Dependency | Flecha punteada abierta desde el cliente que depende hacia el proveedor. |

No usar una flecha sólida genérica para llamar “dependencia”, “interfaz” e “integración” a
la vez. Si se opta por una relación simplificada, la leyenda debe decir qué relación UML
representa o debe declararse como relación informal de la vista.

### 3.2 Diagrama de Paquetes

| Elemento/relación | Uso correcto |
|---|---|
| Package | Espacio de nombres que agrupa elementos del modelo; usar el símbolo de paquete. |
| Anidamiento | Un paquete contiene a otro dentro de su espacio de nombres. |
| Dependency | Flecha punteada abierta del paquete cliente al paquete proveedor. |
| `«import»` | Importa miembros públicos del paquete proveedor al espacio de nombres del cliente. |
| `«merge»` | Combina o expande contenido de paquetes; no equivale a una dependencia común. |

Una capa arquitectónica puede representarse con paquetes y una convención o estereotipo de
capas, pero UML no obliga a “Presentación → Negocio → Datos” ni a tres niveles. Derivar
el número, nombres y direcciones de dependencia del caso.

### 3.3 Diagrama de Despliegue

| Elemento/relación | Uso correcto |
|---|---|
| Node | Recurso computacional físico o lógico; distinguir `«device»` y `«executionEnvironment»` cuando sea relevante. |
| Artifact | Pieza física de información o software desplegable. Puede manifestar un componente, pero no es automáticamente un componente. |
| Deployment | Un artifact se despliega en un deployment target; usar `«deploy»` cuando se dibuje como relación explícita. |
| Communication path | Conexión entre nodos que pueden intercambiar señales; anotar protocolo, puerto o multiplicidad solo si el caso lo sustenta. |

No usar componentes dentro de nodos como reemplazo silencioso de artifacts. Si se muestra
un componente para dar contexto, indicar qué artifact lo manifiesta o declarar en la
leyenda que es una simplificación del perfil activo.

## 4. Perfiles y extensiones controladas

Un perfil modifica la presentación o añade vocabulario sin ocultar su procedencia.

| Perfil | Cuándo usarlo | Requisito |
|---|---|---|
| `strict-uml` | No existe instrucción local o se pide UML estándar. | Default. |
| `simplified-uml` | Se pide una vista rápida, pedagógica o de alto nivel. | Declarar la equivalencia entre la caja o flecha simplificada y el concepto UML. |
| `course-profile` | Existe una regla documentada del profesor. | Citar archivo y página/sección; nunca aplicarlo a otro curso automáticamente. |
| `organization-profile` | Cliente o equipo tiene estándares propios. | Adjuntar o citar la convención, leyenda y versión. |

Los estereotipos no estándar —por ejemplo `«AD»`, `«BD»`, `«Negocio»` o siglas propias—
solo se usan con una leyenda o perfil que defina su significado. No presentarlos como
estereotipos UML estándar.

## 5. Generación independiente de herramienta

La herramienta representa el modelo; no lo sustituye. Para draw.io, generar el XML de
forma programática y mapear, cuando estén disponibles:

| Concepto UML | Shape draw.io orientativo |
|---|---|
| Component | `shape=mxgraph.uml.component` |
| Interfaz provista/requerida | `shape=mxgraph.uml.providedRequiredInterface` o símbolos separados equivalentes |
| Package | `shape=folder` |
| Node | `shape=cube` o símbolo UML equivalente |
| Artifact | `shape=mxgraph.uml.artifact` |

Estos son mapeos de renderizado, no reglas semánticas. Si se usa una caja simple por una
limitación de herramienta, conservar estereotipo, leyenda y relaciones correctas. Mantener
las etiquetas de relaciones como elementos de texto separados si la herramienta lo exige;
no dejar que el auto-layout cambie su asociación semántica.

## 6. Validación antes de entregar

Comprobar, en este orden:

1. La vista responde al objetivo y al alcance declarados.
2. Cada elemento tiene el tipo UML correcto y una responsabilidad o rol entendible.
3. Cada flecha tiene un significado, dirección y etiqueta coherentes; no hay flechas
   decorativas.
4. Interfaces, artifacts, nodos y paquetes no se confunden entre sí.
5. Todo estereotipo o simplificación está definido en la leyenda o perfil.
6. Las relaciones no inventan datos, protocolos, puertos o topologías ausentes del caso.
7. La geometría es legible: sin solapes, etiquetas asociadas a la flecha correcta y sin
   cruces evitables.
8. La salida identifica el perfil usado y separa hechos, convenciones locales y supuestos.

## 7. Salida mínima del skill

Entregar junto al diagrama:

```text
Tipo de diagrama: <Componentes | Paquetes | Despliegue>
Perfil aplicado: <strict-uml | nombre del perfil>
Alcance: <incluye / excluye>
Supuestos: <solo los necesarios>
Leyenda: <estereotipos y simplificaciones no estándar>
```

Si un perfil local contradice o simplifica UML estándar, conservar la convención solicitada
pero anotarla como tal. Nunca “corregir” silenciosamente un formato que el usuario o el
profesor haya exigido.
