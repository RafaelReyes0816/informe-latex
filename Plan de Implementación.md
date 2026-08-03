# Plan de Implementación Definitivo para la Gestión de Dependencias de LaTeX

## Objetivo

Eliminar por completo la necesidad de que el usuario instale o configure manualmente herramientas externas para generar documentos PDF.

Al finalizar la instalación de la aplicación, el entorno debe quedar completamente preparado para compilar documentos LaTeX desde el primer uso.

---

# Problema Actual

Actualmente la aplicación depende del entorno del sistema operativo.

Esto provoca que la compilación falle cuando falta alguna dependencia, por ejemplo:

- MiKTeX no instalado.
- Perl no instalado.
- MiKTeX sin actualizar.
- Paquetes LaTeX faltantes.
- Variables PATH incorrectas.

Aunque la aplicación detecta correctamente estas situaciones, sigue dependiendo de que el usuario las resuelva manualmente.

---

# Objetivo Final

El usuario únicamente debe ejecutar:

```text
Setup.exe
```

y al finalizar podrá generar PDFs inmediatamente.

No deberá instalar manualmente:

- MiKTeX
- Strawberry Perl
- Paquetes LaTeX
- Variables PATH
- Actualizaciones

---

# Arquitectura Recomendada

```text
                 Setup.exe
                      │
                      ▼
        Instalación de la aplicación
                      │
                      ▼
          Verificación del entorno
                      │
      ┌───────────────┼────────────────┐
      ▼               ▼                ▼
   MiKTeX         Strawberry Perl     PATH
      │               │                │
      └───────────────┼────────────────┘
                      ▼
        Actualizar MiKTeX
                      ▼
 Instalar paquetes LaTeX requeridos
                      ▼
      Compilación de documento prueba
                      ▼
             Instalación completada
```

---

# Paso 1 - Detectar Dependencias

Antes de instalar cualquier componente, verificar:

## MiKTeX

Buscar:

```text
pdflatex.exe
```

o

```text
miktex-console.exe
```

---

## Perl

Buscar:

```text
perl.exe
```

---

## latexmk

Buscar:

```text
latexmk.exe
```

---

## Variables PATH

Comprobar que Windows puede ejecutar:

```text
pdflatex

latexmk

perl
```

sin indicar una ruta completa.

---

# Paso 2 - Instalar MiKTeX

Si MiKTeX no existe:

- Descargar automáticamente el instalador oficial.
- Ejecutar instalación silenciosa.
- Esperar a que finalice.

Una vez instalado:

Actualizar la base de datos.

Ejecutar:

```cmd
mpm --update
```

> **Nota:** Las opciones `--update` y `--update-db` aparecen marcadas como obsoletas en versiones recientes de MiKTeX. Conviene revisar la documentación de la versión utilizada y, si es posible, utilizar la interfaz de MiKTeX Console o el comando recomendado para esa versión. La lógica del instalador debe adaptarse a la versión detectada.

---

# Paso 3 - Instalar Strawberry Perl

Si:

```text
perl --version
```

falla,

instalar automáticamente Strawberry Perl.

Después:

Actualizar PATH.

Verificar:

```cmd
perl --version
```

Debe devolver la versión instalada.

---

# Paso 4 - Actualizar PATH

Después de instalar:

- MiKTeX
- Perl

Actualizar las variables de entorno.

Verificar:

```cmd
where perl

where pdflatex

where latexmk
```

Los tres comandos deben localizar los ejecutables correctamente.

---

# Paso 5 - Instalar Paquetes LaTeX

Realizar una compilación automática de prueba.

Documento:

```latex
\documentclass{article}

\begin{document}

Instalación correcta

\end{document}
```

Si MiKTeX detecta paquetes faltantes:

Permitir su instalación automática.

---

# Paso 6 - Verificar Plantillas del Proyecto

Antes de finalizar la instalación:

Verificar que existan:

- Templates
- Logos
- Archivos `.cls`
- Archivos `.sty`
- Recursos del proyecto

---

# Paso 7 - Diagnóstico del Entorno

Crear un módulo que genere un informe similar a:

```text
Estado del entorno

✓ Aplicación

✓ MiKTeX

✓ Perl

✓ latexmk

✓ pdflatex

✓ PATH

✓ Templates

✓ Compilación de prueba
```

Si alguna dependencia falla:

Mostrar exactamente cuál.

---

# Paso 8 - Compilación de Prueba

Generar automáticamente:

```text
test.tex
```

Compilar:

```text
pdflatex test.tex
```

o

```text
latexmk test.tex
```

Verificar:

```text
test.pdf
```

Si existe:

```text
✓ Instalación validada correctamente
```

---

# Paso 9 - Manejo Inteligente de Errores

En lugar de mostrar únicamente:

```text
Compilación fallida
```

Mostrar:

```text
Dependencia faltante:

✗ Perl

Solución:

Instalar Strawberry Perl.
```

o

```text
Paquete LaTeX faltante:

moderncv.cls
```

o

```text
No se encontró pdflatex.
```

---

# Paso 10 - Captura Completa del Log

Actualmente el log únicamente muestra advertencias.

Debe registrar completamente:

- stdout
- stderr
- Código de salida
- Archivo `.log`

Ejemplo:

```text
========== PDFLATEX ==========
...

! LaTeX Error: File 'moderncv.cls' not found.

...

Exit Code: 1
```

Esto permitirá identificar el error real sin necesidad de reproducir el problema manualmente.

---

# Orden de Implementación

## Fase 1

- [ ] Detectar MiKTeX.
- [ ] Detectar Perl.
- [ ] Detectar PATH.
- [ ] Detectar latexmk.

---

## Fase 2

- [ ] Instalar MiKTeX automáticamente.
- [ ] Instalar Strawberry Perl automáticamente.
- [ ] Actualizar PATH.

---

## Fase 3

- [ ] Actualizar MiKTeX.
- [ ] Instalar paquetes LaTeX.
- [ ] Ejecutar compilación de prueba.

---

## Fase 4

- [ ] Capturar logs completos.
- [ ] Mostrar mensajes amigables.
- [ ] Crear pantalla de diagnóstico.

---

# Recomendaciones de Arquitectura

## No depender del entorno del usuario

Toda dependencia necesaria para generar documentos debe quedar instalada durante el proceso de instalación de la aplicación.

---

## Centralizar las verificaciones

Crear una clase dedicada exclusivamente al diagnóstico del entorno.

Ejemplo:

```text
EnvironmentChecker
```

Responsabilidades:

- Detectar herramientas.
- Verificar PATH.
- Comprobar versiones.
- Validar compiladores.
- Generar reportes.

---

## Centralizar el proceso de compilación

Crear una clase:

```text
LatexCompiler
```

Responsabilidades:

- Elegir automáticamente entre `latexmk` y `pdflatex`.
- Capturar errores.
- Registrar logs.
- Informar el motivo exacto de una falla.

---

# Resultado Esperado

Después de ejecutar el instalador:

```text
✓ Aplicación instalada

✓ MiKTeX instalado

✓ Strawberry Perl instalado

✓ PATH configurado

✓ Paquetes LaTeX instalados

✓ Documento de prueba compilado

✓ Entorno validado
```

A partir de ese momento, cualquier documento generado por la aplicación deberá poder convertirse a PDF sin requerir configuraciones manuales adicionales.

---

# Conclusión

La solución definitiva no consiste únicamente en detectar dependencias faltantes, sino en **automatizar completamente la preparación del entorno**. El instalador debe asumir la responsabilidad de instalar, configurar y validar todas las herramientas necesarias antes de dar por finalizada la instalación. Con este enfoque se obtiene una experiencia consistente para todos los usuarios y se reducen considerablemente los errores de soporte relacionados con la configuración del sistema.
