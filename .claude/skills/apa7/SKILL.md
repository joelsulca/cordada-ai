---
name: apa7
description: Citas en el texto y lista de referencias en APA 7.ª edición (estándar de la American Psychological Association), con las diferencias de la guía de la universidad si el perfil las registra. Cubre cita narrativa y entre paréntesis, citas textuales cortas y largas, paráfrasis, y referencias de libros, capítulos, artículos, sitios web, tesis, ponencias, normas técnicas, software y herramientas de IA. Actívalo cuando el usuario mencione APA, bibliografía, referencias, cómo citar, cita textual, paráfrasis, formato de referencias, o pida revisar o generar la lista de referencias de un trabajo. No lo uses para verificar si una referencia existe o cumple criterios del curso (eso es verificar-referencias).
---

# APA 7 — Citas y referencias

## Fuentes y precedencia

- **Estándar**: American Psychological Association. (2020). *Publication manual of the American Psychological Association* (7th ed.). https://doi.org/10.1037/0000165-000. Ejemplos oficiales: https://apastyle.apa.org/style-grammar-guidelines/references/examples
- **Guía de la universidad**: si `perfil/perfil.md` indica una guía de biblioteca, sus diferencias están en `perfil/citacion-local.md`. **Prevalecen sobre este archivo** (`AGENTS.md`, sección 1).
- **Reglas del docente**: el `CLAUDE.md` del curso. Prevalecen sobre las dos anteriores.

Antes de dar formato, lee `perfil/citacion-local.md` si existe y el apartado de reglas del `CLAUDE.md` del curso.

**Idioma.** El manual original está en inglés. En trabajos en español, los elementos fijos se traducen según la guía de cada institución:

| Elemento | Inglés (APA) | Español (forma habitual) |
|---|---|---|
| Conector de autores en el texto | `and` (narrativa), `&` (paréntesis) | `y` (narrativa); en paréntesis, `&` o `y` según la guía |
| Edición | `(2nd ed.)` | `(2.ª ed.)` o `(2a ed.)` |
| Página | `p.` / `pp.` | `p.` / `pp.` |
| Sin fecha | `n.d.` | `s.f.` |
| Recuperado | `Retrieved Month Day, Year, from` | `Recuperado el día de mes de año, de` |
| Párrafo | `para.` | `párr.` |

Si el perfil no fija la variante, usa la del idioma del trabajo y sé consistente en todo el documento.

## 1. Citas en el texto

Toda cita lleva **autor y año**. Las textuales llevan también la **página** (o el párrafo, si no hay páginas).

| Tipo | Ejemplo |
|---|---|
| Entre paréntesis | …el modelo mejora la precisión (Rodríguez, 2023). |
| Narrativa | Rodríguez (2023) sostiene que… |

| Autores | Forma |
|---|---|
| 1 | (Pérez, 2024) |
| 2 | (Pérez & García, 2024) / Pérez y García (2024) |
| 3 o más | (Pérez et al., 2024) desde la **primera** cita |
| Institución con sigla | Primera vez: (Organización Mundial de la Salud [OMS], 2023); luego: (OMS, 2023) |

- **Varias obras en un mismo paréntesis**: en orden alfabético, separadas por punto y coma: (García, 2022; Pérez, 2024).
- **Mismo autor y año**: se agrega una letra: (Pérez, 2024a, 2024b).
- **Dos primeros autores con el mismo apellido**: se agregan las iniciales para distinguirlos.

## 2. Citas textuales

**Corta (menos de 40 palabras)**: entre comillas, dentro del párrafo, con la página.
> …"los mercados son lugares donde se reúnen compradores y vendedores" (Parkin, 2018, p. 56).

**Larga (40 palabras o más)**: bloque aparte, sin comillas, con sangría de 1,27 cm (0,5 in). El paréntesis va **después** del punto final: `…exhibir. (p. 497)`.

| Ubicación | Notación |
|---|---|
| Una página | p. 25 |
| Rango | pp. 25–27 |
| Sin paginación | párr. 13, o el nombre de la sección |

## 3. Paráfrasis

La idea se reformula con palabras propias. Basta autor y año; APA recomienda agregar la página cuando ayuda a ubicar la idea.

## 4. Lista de referencias

**Reglas generales**
1. Orden alfabético por el apellido del primer autor.
2. Sangría francesa de 1,27 cm (0,5 in).
3. **Todo lo citado está en la lista y todo lo de la lista está citado.** Excepción: las comunicaciones personales se citan solo en el texto.
4. Hasta **20 autores** se listan todos. Con 21 o más: los primeros 19, puntos suspensivos y el último.
5. Cursiva para el título de la obra independiente (libro, revista y su volumen, informe, sitio, norma). El título del artículo o capítulo va sin cursiva.
6. El DOI se escribe como URL (`https://doi.org/…`), al final y sin punto después.
7. Los libros ya no llevan la ciudad de la editorial.
8. Si el autor y la editorial son el mismo, se omite la editorial.

### 4.1 Libros

```
Apellido, I. I. (Año). Título en cursiva (2.ª ed.). Editorial. https://doi.org/…
```

**Capítulo de libro editado**
```
Apellido, I. (Año). Título del capítulo. En I. Editor (Ed.), Título del libro en cursiva
    (pp. 45–67). Editorial. https://doi.org/…
```

La edición se indica desde la segunda.

### 4.2 Artículos de revista

```
Apellido, I., Apellido, I., & Apellido, I. (Año). Título del artículo. Nombre de la Revista,
    volumen(número), páginas. https://doi.org/…
```

- La revista y el volumen van en cursiva; el número no.
- Si el artículo tiene número en lugar de páginas, se escribe "Artículo e0209899".

### 4.3 Sitios web y páginas

```
Autor o Institución. (Año, día de mes). Título de la página en cursiva. Nombre del sitio. URL
```

- Si el autor y el sitio coinciden, se omite el sitio.
- Sin fecha: `(s.f.)` / `(n.d.)`.
- **Fecha de consulta** solo si el contenido cambia con el tiempo y no está archivado:
  `Recuperado el 3 de octubre de 2026, de URL`.

### 4.4 Tesis

```
Apellido, I. (Año). Título en cursiva [Tesis de maestría, Universidad]. Nombre del repositorio. URL
```

Para una tesis no publicada: `[Tesis de maestría no publicada]. Universidad.`

### 4.5 Ponencias en congresos

```
Apellido, I. (Año, día–día de mes). Título de la ponencia en cursiva [Tipo de presentación].
    Nombre del evento, Ciudad, País. URL
```

Si la ponencia se publicó en actas (*proceedings*), se cita como capítulo de libro o como artículo de revista, según cómo se publicaron.

### 4.6 Normas técnicas y estándares

```
Organismo. (Año). Título de la norma en cursiva (Norma No. XXX:AAAA). URL
```

Ejemplo:
```
International Organization for Standardization. (2023). Systems and software engineering —
    Systems and software Quality Requirements and Evaluation (SQuaRE) — Product quality model
    (ISO/IEC Standard No. 25010:2023). https://www.iso.org/standard/78176.html
```

Antes de usar el título, verifícalo en la página oficial de la norma.

### 4.7 Software y aplicaciones

```
Autor o Empresa. (Año). Nombre del software en cursiva (Versión X) [Software]. URL
```

El software de uso común (procesadores de texto, hojas de cálculo, herramientas de diagramas) no se referencia si solo se menciona. Se referencia cuando se cita o parafrasea su contenido, o cuando es un software especializado clave para el método.

### 4.8 Herramientas de IA generativa

Formato que publicó el blog de APA Style en 2023 y que reproducen la mayoría de las guías de biblioteca:

```
Empresa. (Año). Nombre del modelo en cursiva (versión o fecha) [Large language model]. URL
```

```
OpenAI. (2023). ChatGPT (Mar 14 version) [Large language model]. https://chat.openai.com/chat
```

- En el texto: (OpenAI, 2023).
- Lo que se recomienda declarar: **cómo** se usó la herramienta (en la metodología o en una nota), el **prompt** y la respuesta relevante. La respuesta completa va en un anexo o en material complementario.
- **Atención**: APA podría haber actualizado esta guía después de 2023. Algunas fuentes secundarias mencionan un formato de 2025 que cita la conversación concreta. Antes de entregar, confirma el formato vigente en apastyle.apa.org (blog "How to cite ChatGPT") o en la guía de tu biblioteca. Si la guía de tu universidad trae su propio formato, ese prevalece.

## 5. Figuras y tablas tomadas de otra fuente

Debajo de la figura o la tabla va una nota:
- *Nota.* Adaptado de "Título", por I. Apellido, Año, *Revista*, *volumen*(número), p. X.
- *Nota.* Tomado de…, si se copia sin cambios.

La fuente va también en la lista de referencias.

## 6. Qué entregar

- Si el usuario pide formatear: la referencia o la lista lista para pegar, con la cursiva en Markdown (`*…*`).
- Si pide revisar: una tabla con cada problema (cita sin referencia o al revés, autores, año, cursiva, DOI) y su corrección.
- **No inventes datos que falten** (volumen, páginas, DOI): márcalos como pendientes o verifícalos con el skill `verificar-referencias`.
