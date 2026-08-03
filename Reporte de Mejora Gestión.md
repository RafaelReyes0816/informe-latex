# Reporte de Mejora: Gestión Automática de Dependencias para la Generación de PDF

## Objetivo

Garantizar que la aplicación quede completamente funcional después de su instalación, evitando que el usuario tenga que instalar manualmente herramientas adicionales para generar documentos PDF.

El objetivo final es que el instalador (`Setup`) prepare el entorno automáticamente y verifique que todas las dependencias necesarias estén disponibles antes de utilizar la aplicación.

---

# Problema Detectado

Durante la generación del PDF se obtuvo el siguiente resultado:

```text
Estado del entorno:
✓ latexmk: encontrado
✗ perl: no encontrado
✓ pdflatex: encontrado

⚠ Compilación fallida (usando pdflatex (perl no disponible)).

pdflatex: major issue: So far, you have not checked for MiKTeX updates.
```

El sistema detectó correctamente que:

- `latexmk` está instalado.
- `pdflatex` está disponible.
- `Perl` no está instalado.

Como consecuencia, la aplicación intentó utilizar `pdflatex` como método alternativo, pero la compilación tampoco pudo completarse.

---

# Análisis del Problema

Actualmente la aplicación depende de herramientas externas instaladas en el sistema operativo.

Entre ellas:

- MiKTeX
- latexmk
- pdflatex
- Perl
- Paquetes de LaTeX
- Variables PATH correctamente configuradas

Si alguna de estas dependencias falta o está incompleta, la generación del PDF falla.

---

# Dependencias Necesarias

## Requeridas

- MiKTeX
- Perl (para latexmk)
- latexmk
- pdflatex
- Variables PATH

## Recomendadas

- Actualización de paquetes MiKTeX
- Instalación automática de paquetes faltantes
- Actualización periódica de MiKTeX

---

# Problemas Actuales

## 1. Dependencias externas

Actualmente el usuario debe instalar manualmente:

- MiKTeX
- Perl

Esto genera una mala experiencia de usuario.

---

## 2. Configuración manual

Después de instalar MiKTeX todavía pueden faltar:

- paquetes
- fuentes
- estilos (.sty)
- clases (.cls)

que únicamente se descargan durante la primera compilación.

---

## 3. Dependencia de Perl

`latexmk` requiere Perl para funcionar.

Si Perl no está instalado:

```text
latexmk
        ↓
No puede ejecutarse
```

---

## 4. Inconsistencia del entorno

Dos usuarios con la misma versión de la aplicación pueden obtener resultados diferentes dependiendo de las herramientas instaladas en Windows.

---

# Solución Propuesta

## Objetivo

Que el instalador configure automáticamente el entorno necesario para generar documentos PDF.

El usuario únicamente debería ejecutar:

```text
Setup.exe
```

y comenzar a utilizar la aplicación.

---

# Flujo Propuesto

```text
Ejecutar Setup
        │
        ▼
Instalar aplicación
        │
        ▼
Verificar MiKTeX
        │
        ▼
¿Está instalado?
      │
 ┌────┴────┐
 │         │
No        Sí
 │         │
 ▼         ▼
Instalar   Verificar versión
MiKTeX
        │
        ▼
Verificar Perl
        │
        ▼
¿Existe?
      │
 ┌────┴────┐
 │         │
No        Sí
 │         │
 ▼         ▼
Instalar   Continuar
Perl
        │
        ▼
Actualizar PATH
        │
        ▼
Verificar latexmk
        │
        ▼
Verificar pdflatex
        │
        ▼
Verificar paquetes LaTeX
        │
        ▼
Realizar prueba de compilación
        │
        ▼
Instalación finalizada
```

---

# Mejoras Recomendadas

## 1. Instalación Automática de MiKTeX

Si MiKTeX no existe:

- descargar instalador
- instalar silenciosamente
- configurar instalación para todos los usuarios

---

## 2. Instalación Automática de Perl

Si Perl no existe:

Instalar automáticamente Strawberry Perl.

Esto permitirá utilizar:

```text
latexmk
```

sin intervención del usuario.

---

## 3. Actualización Automática de MiKTeX

Después de instalar MiKTeX ejecutar:

```text
mpm --update-db
mpm --update
```

para garantizar que los paquetes estén actualizados.

---

## 4. Instalación Automática de Paquetes LaTeX

Durante la primera instalación realizar una compilación de prueba.

Si faltan paquetes:

```text
moderncv

fontawesome5

geometry

babel

xcolor

hyperref
```

MiKTeX podrá instalarlos automáticamente.

---

## 5. Verificación de Dependencias

Crear un módulo interno que valide:

```text
✓ MiKTeX

✓ Perl

✓ latexmk

✓ pdflatex

✓ PATH

✓ Paquetes LaTeX
```

Si alguna dependencia falta, informar claramente al usuario antes de intentar compilar.

---

## 6. Compilación de Diagnóstico

Después de instalar todas las dependencias:

Generar automáticamente un documento LaTeX mínimo.

Ejemplo:

```latex
\documentclass{article}

\begin{document}

Prueba de instalación

\end{document}
```

Compilarlo.

Si genera correctamente el PDF:

```text
✓ Entorno listo para utilizar.
```

---

# Mejoras para el Instalador

El instalador debería ofrecer un proceso similar a:

```text
Instalando aplicación...

✔ Aplicación

✔ MiKTeX

✔ Perl

✔ Configuración PATH

✔ Paquetes LaTeX

✔ Verificación del entorno

✔ Compilación de prueba

Instalación completada correctamente.
```

---

# Beneficios

- El usuario no instala herramientas manualmente.
- Se reducen errores de configuración.
- El entorno queda completamente preparado.
- La generación de PDF funciona desde la primera ejecución.
- Menor cantidad de incidencias reportadas.
- Instalación más profesional y robusta.

---

# Prioridad de Implementación

## Alta

- [ ] Detectar dependencias automáticamente.
- [ ] Instalar Perl si no existe.
- [ ] Instalar MiKTeX si no existe.
- [ ] Configurar variables PATH.

## Media

- [ ] Actualizar automáticamente MiKTeX.
- [ ] Verificar paquetes LaTeX necesarios.
- [ ] Ejecutar compilación de prueba.

## Baja

- [ ] Implementar un asistente de diagnóstico del entorno.
- [ ] Permitir reparar automáticamente dependencias desde la aplicación.

---

# Resultado Esperado

Al finalizar la instalación, el usuario no debería realizar ninguna configuración adicional.

La aplicación deberá contar con un entorno completamente funcional para generar documentos PDF, incluyendo todas las herramientas, motores de compilación y dependencias necesarias, reduciendo al mínimo los errores relacionados con la configuración del sistema.
