# Reporte de Incidencia: Error al Inicializar la Barra de Menú (CTkMenuBar)

**Versión:** Pendiente de corrección  
**Prioridad:** Alta  
**Estado:** Bloqueante

---

# Resumen

Después de instalar la nueva versión de **md2tex**, la aplicación no logra iniciar.

El ejecutable se cierra inmediatamente mostrando una excepción no controlada relacionada con `CustomTkinter`.

---

# Error Registrado

```text
Failed to execute script '__main__' due to unhandled exception:

AttributeError:
module 'customtkinter' has no attribute 'CTkMenuBar'
```

---

# Traceback

```text
Traceback (most recent call last):

File "__main__.py", line 14

File "__main__.py", line 10

File "md2tex/gui.py", line 521

File "md2tex/gui.py", line 429

File "md2tex/gui.py", line 440, in _setup_menubar

AttributeError:
module 'customtkinter' has no attribute 'CTkMenuBar'
```

---

# Impacto

La aplicación no llega a mostrar la ventana principal.

El fallo ocurre durante la inicialización de la interfaz gráfica, por lo que el usuario no puede utilizar ninguna funcionalidad.

Este error es crítico ya que impide completamente el uso del programa.

---

# Análisis

El método:

```text
_setup_menubar()
```

está intentando crear un componente llamado:

```python
customtkinter.CTkMenuBar
```

Sin embargo, la biblioteca oficial **CustomTkinter** no incluye un widget llamado `CTkMenuBar`.

Como resultado Python lanza:

```text
AttributeError
```

antes de que termine la construcción de la ventana principal.

---

# Posibles Causas

## Caso 1 (Más probable)

Se asumió que `CTkMenuBar` pertenece a CustomTkinter.

Ejemplo incorrecto:

```python
import customtkinter as ctk

menubar = ctk.CTkMenuBar(...)
```

Esta clase no existe en la API oficial.

---

## Caso 2

Se utilizó una librería externa llamada:

```text
CTkMenuBar
```

durante el desarrollo,

pero:

- no se instaló correctamente
- no se incluyó en PyInstaller
- no se importó correctamente

---

## Caso 3

El código fue modificado recientemente y se cambió accidentalmente:

```python
from CTkMenuBar import CTkMenuBar
```

por

```python
customtkinter.CTkMenuBar
```

---

## Caso 4

La dependencia existe únicamente en el entorno de desarrollo.

Durante la generación del ejecutable:

PyInstaller no la incluyó.

---

# Objetivos de la Corrección

- Permitir que la aplicación inicie correctamente.
- Eliminar dependencias innecesarias.
- Mejorar la compatibilidad multiplataforma.
- Evitar errores durante el empaquetado.

---

# Solución Recomendada

## Opción A (Recomendada)

Eliminar completamente la dependencia de `CTkMenuBar`.

Crear la barra superior utilizando únicamente componentes oficiales de CustomTkinter.

Ejemplo de estructura:

```text
┌────────────────────────────────────────────┐
│ Archivo │ Editar │ Herramientas │ Ayuda │
└────────────────────────────────────────────┘
```

Implementación sugerida:

- CTkFrame
- CTkButton
- CTkOptionMenu
- CTkLabel

Ventajas:

- Sin dependencias externas.
- Compatible con Windows.
- Compatible con Linux.
- Compatible con macOS.
- Compatible con PyInstaller.

---

## Opción B

Si realmente se desea utilizar `CTkMenuBar`:

Verificar que:

- la librería esté instalada
- la importación sea correcta
- PyInstaller la incluya durante el empaquetado

Ejemplo:

```python
from CTkMenuBar import CTkMenuBar
```

No utilizar:

```python
customtkinter.CTkMenuBar
```

---

# Validaciones a Realizar

Antes de crear la barra de menú:

Comprobar:

- existencia de la librería
- importación correcta
- compatibilidad con la versión instalada de CustomTkinter

Si falla:

Registrar el error y continuar utilizando un menú alternativo.

Nunca detener completamente la aplicación.

---

# Mejora de Arquitectura

Crear un componente independiente:

```text
ui/

menu.py
```

Responsabilidades:

- construir la barra de menú
- registrar eventos
- cargar iconos
- crear submenús

La ventana principal únicamente deberá llamar:

```python
setup_menu()
```

De esta forma el código queda desacoplado.

---

# Manejo de Errores

Actualmente:

```text
Error

↓

Aplicación termina
```

Se propone:

```text
Intentar crear menú

↓

¿Correcto?

↓

Sí

↓

Continuar

↓

No

↓

Registrar excepción

↓

Crear menú básico

↓

Continuar cargando la aplicación
```

Esto evita que un error secundario impida abrir toda la aplicación.

---

# Compatibilidad Multiplataforma

La solución deberá funcionar en:

- Windows
- Linux
- macOS

sin depender de widgets no oficiales.

Se recomienda utilizar únicamente componentes soportados por la API oficial de CustomTkinter o widgets estándar de Tkinter cuando sea necesario.

---

# Tareas de Implementación

## Prioridad Alta

- [ ] Revisar `_setup_menubar()`.
- [ ] Identificar el uso de `CTkMenuBar`.
- [ ] Sustituir componentes no oficiales.
- [ ] Verificar compatibilidad con la versión actual de CustomTkinter.

---

## Prioridad Media

- [ ] Crear un módulo independiente para la barra de menú.
- [ ] Agregar manejo de excepciones durante la inicialización.
- [ ] Registrar el error completo en el log.

---

## Prioridad Baja

- [ ] Implementar un menú adaptable para Windows, Linux y macOS.
- [ ] Agregar pruebas automatizadas para validar la inicialización de la interfaz.

---

# Resultado Esperado

Después de la corrección:

- La aplicación inicia correctamente.
- La barra de menú se construye utilizando componentes compatibles.
- El ejecutable generado con PyInstaller funciona sin errores.
- La interfaz mantiene compatibilidad en Windows, Linux y macOS.
- Un fallo en el menú no impide que el resto de la aplicación se ejecute.

---

# Conclusión

La causa del problema es el uso de un componente (`CTkMenuBar`) que no forma parte de la API oficial de CustomTkinter o cuya dependencia no está siendo gestionada correctamente durante el empaquetado. La solución más robusta consiste en reemplazar esta dependencia por componentes oficiales de CustomTkinter o de Tkinter, encapsular la lógica del menú en un módulo independiente y añadir manejo de errores para evitar que un fallo en la interfaz bloquee completamente la aplicación.
