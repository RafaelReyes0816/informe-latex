# Implementación de Conversión de Documentos a Markdown Conservando Imágenes

## Objetivo

Permitir que el usuario importe documentos (principalmente DOCX y posteriormente PDF) y generar automáticamente un archivo Markdown sin perder las imágenes originales.

Las imágenes deberán extraerse automáticamente, almacenarse en una carpeta asociada al documento y referenciarse correctamente dentro del Markdown generado.

---

## Problema Actual

Actualmente, cuando un documento contiene imágenes, estas deben añadirse manualmente al archivo Markdown, lo que implica:

- Trabajo adicional para el usuario.
- Riesgo de olvidar imágenes importantes.
- Pérdida de la estructura original del documento.
- Menor automatización del flujo de trabajo.

---

## Solución Propuesta

Implementar un sistema de extracción automática de imágenes durante la conversión del documento.

### Flujo General

```text
Documento (DOCX/PDF)
        │
        ▼
Extracción de contenido
        │
 ┌──────┴──────┐
 │             │
Texto      Imágenes
 │             │
 └──────┬──────┘
        ▼
Generación Markdown
        ▼
Referencias automáticas
        ▼
Resultado final
```

---

## Estructura de Salida

### Entrada

```text
Informe.docx
```

### Salida

```text
output/
├── informe.md
└── images/
    ├── image1.png
    ├── image2.jpg
    └── image3.png
```

---

## Resultado Esperado

Markdown generado:

```md
# Introducción

Texto introductorio.

![Imagen 1](images/image1.png)

Más contenido.

![Imagen 2](images/image2.jpg)
```

Las rutas deberán generarse automáticamente sin intervención del usuario.

---

## Implementación para DOCX

### Opción Recomendada: Pandoc

Pandoc permite convertir documentos Word a Markdown y extraer imágenes automáticamente.

Comando de referencia:

```bash
pandoc informe.docx \
-o informe.md \
--extract-media=images
```

Resultado:

```text
informe.md
images/
├── image1.png
├── image2.jpg
└── image3.png
```

Las referencias a imágenes se insertan automáticamente en el Markdown.

---

## Implementación con Python

Si se desea realizar la conversión directamente desde la aplicación:

### Librerías Evaluadas

#### Mammoth

Ventajas:

- Excelente conversión DOCX → HTML.
- Conserva estructura del documento.
- Fácil integración.

Ejemplo:

```python
import mammoth

with open("documento.docx", "rb") as docx_file:
    result = mammoth.convert_to_html(docx_file)

html = result.value
```

Posteriormente:

```text
DOCX
  ↓
HTML
  ↓
Markdown
```

---

#### python-docx

Ventajas:

- Acceso completo al contenido del documento.
- Permite localizar imágenes manualmente.

Desventajas:

- Requiere más código.
- Conversión menos automática.

---

## Implementación para PDF

### Consideraciones

Los PDF presentan una dificultad adicional:

- No poseen una estructura semántica tan clara como DOCX.
- Las imágenes no siempre tienen una posición fácilmente recuperable.
- Algunas páginas pueden contener imágenes incrustadas como parte de un único gráfico.

---

### Librerías Evaluadas

#### PyMuPDF (fitz)

Permite:

- Extraer texto.
- Extraer imágenes.
- Obtener metadatos.

#### pdfplumber

Permite:

- Extraer texto.
- Analizar contenido visual.

---

## Limitaciones de PDF

Aunque las imágenes pueden extraerse correctamente, no siempre será posible reconstruir exactamente la posición original dentro del documento.

Por esta razón:

```text
DOCX → Markdown
```

ofrece resultados considerablemente mejores que:

```text
PDF → Markdown
```

---

## Arquitectura Propuesta

Para mantener el proyecto escalable se recomienda separar los conversores por tipo de documento.

```text
md2tex/
├── converters/
│   ├── docx_converter.py
│   ├── pdf_converter.py
│   ├── markdown_converter.py
│   └── base_converter.py
```

---

## Interfaz de Conversión

Flujo para el usuario:

```text
Seleccionar documento
        │
        ▼
Detectar formato
        │
        ▼
Convertir contenido
        │
        ▼
Extraer imágenes
        │
        ▼
Generar Markdown
        │
        ▼
Guardar proyecto
```

---

## Mejoras Futuras

### Soporte para formatos adicionales

- ODT
- RTF
- HTML
- EPUB

### Gestión de imágenes

- Renombrado automático.
- Compresión opcional.
- Conversión automática a PNG o JPG.
- Eliminación de duplicados.

### Integración con Plantillas

Permitir que el Markdown generado pueda utilizarse inmediatamente dentro del flujo actual:

```text
DOCX
  ↓
Markdown
  ↓
Plantilla LaTeX
  ↓
PDF Final
```

---

## Recomendación Final

La solución más robusta y con menor mantenimiento consiste en utilizar Pandoc como motor de conversión para documentos DOCX, aprovechando su capacidad nativa para:

- Extraer imágenes.
- Mantener referencias automáticas.
- Preservar encabezados.
- Preservar tablas.
- Preservar listas.
- Generar Markdown limpio.

Esto permite concentrar el desarrollo del proyecto en la generación de informes y plantillas LaTeX, evitando implementar y mantener un conversor complejo desde cero.
