# Especificación Técnica: Sistema Multiplataforma de Gestión de Dependencias para md2tex

**Versión:** 1.0  
**Estado:** Propuesta de implementación  
**Prioridad:** Alta

---

# Objetivo General

Desarrollar un sistema de gestión de dependencias completamente automatizado que permita ejecutar **md2tex** en:

- Windows
- Linux
- macOS

sin que el usuario tenga que realizar configuraciones manuales.

El sistema deberá detectar, instalar (cuando sea posible), validar y reparar automáticamente el entorno necesario para la generación de documentos PDF mediante LaTeX.

---

# Objetivos Específicos

- Detectar automáticamente el sistema operativo.
- Detectar las dependencias necesarias.
- Instalar dependencias automáticamente cuando el sistema lo permita.
- Guiar al usuario cuando la instalación automática no sea viable.
- Validar completamente el entorno antes de generar un PDF.
- Reparar automáticamente configuraciones dañadas.
- Mostrar diagnósticos claros y comprensibles.
- Mantener una única arquitectura para los tres sistemas operativos.

---

# Arquitectura General

```text
                    md2tex
                       │
                       ▼
             Environment Manager
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
   Windows          Linux          macOS
       │               │               │
       ▼               ▼               ▼
 Dependency     Dependency      Dependency
   Manager         Manager         Manager
       │               │               │
       └───────────────┼───────────────┘
                       ▼
              Environment Validator
                       ▼
              Test Compilation
                       ▼
                 Ready to Use
```

---

# Nueva Estructura del Proyecto

```text
md2tex/

environment/
│
├── base.py
├── checker.py
├── installer.py
├── validator.py
├── compiler.py
├── repair.py
├── report.py
│
├── windows.py
├── linux.py
└── macos.py
```

---

# Responsabilidades de Cada Módulo

## base.py

Clase base para todos los sistemas operativos.

Debe definir:

- detectar dependencias
- instalar dependencias
- validar entorno
- generar reporte
- ejecutar compilación de prueba

---

## checker.py

Debe detectar:

- Sistema operativo
- Arquitectura
- PATH
- Versiones
- Variables de entorno
- Compiladores disponibles

---

## installer.py

Encargado de:

- instalar dependencias
- actualizar componentes
- descargar recursos oficiales
- ejecutar instalaciones silenciosas

---

## validator.py

Debe comprobar:

- existencia de ejecutables
- compilación de prueba
- plantillas
- recursos
- paquetes LaTeX

---

## compiler.py

Debe decidir automáticamente cuál compilador utilizar.

Orden recomendado:

```text
latexmk

↓

xelatex

↓

lualatex

↓

pdflatex
```

Si uno falla:

continuar con el siguiente.

---

## repair.py

Encargado de reparar el entorno.

Ejemplos:

- reconstruir PATH
- actualizar MiKTeX
- instalar paquetes faltantes
- regenerar configuración

---

## report.py

Genera un informe completo del entorno.

Ejemplo:

```text
Sistema

✓ Windows 11

Compiladores

✓ latexmk

✓ pdflatex

✓ xelatex

✓ perl

Paquetes

✓ moderncv

✓ hyperref

✓ geometry

Resultado

Entorno listo.
```

---

# Gestión por Sistema Operativo

# Windows

## Detectar

- MiKTeX
- Perl
- latexmk
- pdflatex
- xelatex
- PATH

---

## Si falta MiKTeX

Descargar automáticamente.

Instalar silenciosamente.

Actualizar paquetes.

---

## Si falta Perl

Descargar Strawberry Perl.

Instalar silenciosamente.

Actualizar PATH.

---

## Verificar

```text
perl --version

latexmk --version

pdflatex --version
```

---

## Compilar documento de prueba

Si genera PDF:

```text
Entorno listo.
```

---

# Linux

## Detectar distribución

- Ubuntu
- Debian
- Fedora
- Arch
- openSUSE
- Otras

---

## Detectar gestor

- apt
- dnf
- pacman
- zypper

---

## Verificar

- texlive
- latexmk
- perl
- xelatex
- pdflatex

---

## Si falta una dependencia

Mostrar exactamente el comando correspondiente.

Ejemplo Ubuntu

```bash
sudo apt install texlive-full latexmk perl
```

Ejemplo Fedora

```bash
sudo dnf install texlive latexmk perl
```

Ejemplo Arch

```bash
sudo pacman -S texlive-most perl
```

La aplicación también puede ofrecer una opción para ejecutar estos comandos automáticamente si el usuario concede permisos de administrador.

---

# macOS

## Detectar

- Homebrew
- MacTeX
- Perl

---

## Si Homebrew no existe

Mostrar instrucciones para instalarlo.

---

## Si MacTeX no existe

Instalar mediante:

```bash
brew install --cask mactex
```

---

## Si falta Perl

```bash
brew install perl
```

---

# Detección de Dependencias

El sistema deberá comprobar:

```text
latexmk

pdflatex

xelatex

lualatex

perl

kpsewhich
```

También:

```text
PATH

Variables de entorno

Permisos

Espacio disponible
```

---

# Detección de Paquetes LaTeX

Comprobar automáticamente la existencia de:

- moderncv
- hyperref
- geometry
- fontawesome
- babel
- xcolor
- graphicx
- fancyhdr
- tcolorbox

Utilizar:

```text
kpsewhich
```

para verificar si un paquete está instalado.

---

# Motor Inteligente de Compilación

La aplicación nunca deberá depender exclusivamente de un compilador.

Debe seguir este flujo:

```text
latexmk

↓

¿Disponible?

↓

Sí

↓

Compilar

↓

Si falla

↓

xelatex

↓

Si falla

↓

lualatex

↓

Si falla

↓

pdflatex

↓

Si falla

↓

Mostrar diagnóstico
```

---

# Sistema de Diagnóstico

Agregar una ventana:

```text
Herramientas

↓

Diagnóstico del entorno
```

Debe mostrar:

```text
Sistema

Compiladores

Dependencias

Paquetes

Plantillas

PATH

Permisos

Resultado final
```

---

# Sistema de Reparación

Agregar:

```text
Herramientas

↓

Reparar entorno
```

Debe poder:

- actualizar PATH
- actualizar MiKTeX
- instalar paquetes
- regenerar configuración
- limpiar temporales
- verificar recursos

---

# Compilación de Prueba

Después de instalar dependencias.

Generar automáticamente:

```latex
\documentclass{article}

\begin{document}

Test

\end{document}
```

Compilar.

Verificar existencia del PDF.

---

# Logs

Guardar:

```text
Sistema operativo

Versión

Compilador utilizado

stdout

stderr

Código de salida

Tiempo de compilación

Paquetes cargados

Errores
```

Nunca registrar únicamente:

```text
Compilación fallida.
```

Siempre registrar la salida completa.

---

# Interfaz

Agregar una sección:

```text
Estado del entorno
```

Ejemplo:

```text
Sistema

✓ Windows 11

Compiladores

✓ latexmk

✓ xelatex

✓ pdflatex

✓ perl

Paquetes

✓ moderncv

✓ hyperref

✓ geometry

Configuración

✓ PATH

✓ Plantillas

Resultado

🟢 Entorno completamente funcional
```

---

# Flujo Completo de Instalación

```text
Ejecutar Setup

↓

Detectar SO

↓

Instalar aplicación

↓

Instalar dependencias específicas del SO

↓

Actualizar entorno

↓

Actualizar PATH

↓

Actualizar paquetes LaTeX

↓

Validar compiladores

↓

Validar plantillas

↓

Compilar documento de prueba

↓

Guardar reporte

↓

Instalación finalizada
```

---

# Flujo de Inicio de la Aplicación

```text
Abrir md2tex

↓

Comprobar entorno

↓

¿Todo correcto?

↓

Sí

↓

Abrir aplicación

↓

No

↓

Mostrar diagnóstico

↓

Ofrecer reparación automática
```

---

# Requisitos de Calidad

La implementación deberá cumplir los siguientes criterios:

- Compatibilidad con Windows, Linux y macOS.
- Detección automática del sistema operativo.
- Gestión independiente de dependencias por plataforma.
- Validación del entorno antes de cada compilación.
- Captura completa de errores y generación de logs detallados.
- Interfaz clara para diagnóstico y reparación.
- Arquitectura modular y extensible para incorporar nuevos compiladores o distribuciones de LaTeX en el futuro.

---

# Resultado Esperado

Al finalizar la implementación:

- El usuario instala **md2tex** sin preocuparse por dependencias.
- La aplicación detecta automáticamente el sistema operativo.
- Se prepara o valida el entorno de compilación correspondiente.
- Los errores se presentan de forma clara y con acciones concretas para resolverlos.
- La generación de PDF funciona de manera consistente en Windows, Linux y macOS.
- La lógica de gestión del entorno queda centralizada en un único módulo reutilizable, facilitando el mantenimiento y la evolución del proyecto.
