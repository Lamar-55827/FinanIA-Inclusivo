# Kiki Pay – Inclusión y Autonomía Financiera

**Tu dinero, tus decisiones, tu futuro.**

Plataforma educativa para aprender a reconocer, comprender y administrar el dinero a tu propio ritmo, pensada para personas autistas, neurodivergentes y con necesidades de apoyo. Esta es la **Fase 3 corregida** (continuación de FinanIA Inclusivo 2.0 / propuesta Fase 3).

> ⚠️ Herramienta educativa con **datos de práctica**. No realiza operaciones financieras reales. **No escribas contraseñas, NIP, números de tarjeta ni datos bancarios.**

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `app.py` | Interfaz (Streamlit): navegación, formularios, módulos |
| `kiki_logica.py` | Lógica sin interfaz: validaciones, cambio, metas, retos, Kiki, respaldos |
| `requirements.txt` | Dependencias (`streamlit`, `pandas`) |
| `.streamlit/config.toml` | Opcional: tema claro fijo |
| `tests/` | Pruebas automáticas |

## Qué incluye (Fase 3)

- **Conozco el dinero**: ejercicios de monedas y billetes (dibujados con CSS, **no son fotografías**), tres modos de verlos (pictogramas / imagen y número / solo números) y tres dificultades. Práctica de sumas y restas.
- **Practico compras**: producto, dinero entregado, cambio con desglose en piezas, comparación de productos y registro opcional de la compra como gasto de práctica.
- **Organizo mi dinero**: formulario de ingresos y gastos (tipo, cantidad, categoría, descripción, fecha), totales, saldo, distribución de gastos, tabla, borrado y descarga CSV.
- **Mi ahorro**: varias metas, agregar cantidades, barra de progreso, cuánto falta, semanas estimadas y mensajes motivadores.
- **Retos**: preguntas generadas (resta, ahorro, comparar precios, gastar más de lo que recibes, ahorro semanal) con retroalimentación amable y nuevos intentos.
- **Pregúntale a Kiki**: ~25 temas (dinero, ahorro, cuentas, tarjetas, transferencias, comisiones, seguridad, créditos, historial crediticio…) con base local, sin APIs de pago. No da asesoría de inversión y avisa si se escriben datos sensibles.
- **Mi progreso** y **Mi experiencia** (tamaño de letra, alto contraste, pictogramas, instrucciones paso a paso, reducir estímulos).

## Qué se corrigió respecto a la versión anterior

1. **Error que rompía secciones:** `totals()` leía `"tipo"`/`"cantidad"` pero los movimientos se guardaban como `"Tipo"`/`"Cantidad"` → `KeyError` al guardar el primer movimiento. Ahora hay un solo formato y una prueba de regresión.
2. Las preferencias **ya no se aplican un clic tarde** (se guardan con `on_change` antes de dibujar la página).
3. Widgets con `key` y valores guardados en `st.session_state.prefs`, sin `value=` cambiante (evita reinicios).
4. El modo demo **ya no borra los datos de la persona** sin confirmación.
5. Las tarjetas de Inicio **ahora son botones que navegan**.
6. Los mensajes de retroalimentación **ya no desaparecen** al pulsar otro botón.
7. Eliminado `use_container_width` (obsoleto).

## Datos: qué es temporal y qué no

- **Temporal:** todo (movimientos, metas, progreso, preferencias) vive en la sesión del navegador. **Se pierde al recargar la página o reiniciar la app.**
- **Copia de seguridad (manual):** en *Mi experiencia* se puede descargar un archivo `.json` y restaurarlo después. Es responsabilidad de la persona guardarlo.
- **No existe todavía** almacenamiento permanente en servidor, cuentas de usuario ni panel familiar.

## Subir a GitHub

1. Entra a tu repositorio en github.com.
2. **Add file → Upload files** y arrastra: `app.py`, `kiki_logica.py`, `requirements.txt`, `README.md` y las carpetas `tests` y `.streamlit` (si no puedes subir carpetas, usa **Add file → Create new file** y escribe el nombre con la ruta, por ejemplo `tests/test_logica.py`, y pega el contenido).
3. Si ya existían `app.py`, `README.md` y `requirements.txt`, se reemplazarán al subirlos con el mismo nombre.
4. Escribe un mensaje (por ejemplo "Kiki Pay Fase 3 corregida") y pulsa **Commit changes**.

## Actualizar Streamlit Community Cloud

1. En [share.streamlit.io](https://share.streamlit.io) abre tu app. Debe apuntar a tu repositorio, rama principal y archivo `app.py`.
2. Al hacer commit, Streamlit suele actualizarse solo. Si no, en la app: **Manage app → ⋮ → Reboot app**.
3. Si aparece un error, abre **Manage app** y revisa los registros (logs); cópialos y compártelos para diagnosticar.

## Pruebas

```
pip install -r requirements.txt
python -m unittest discover -s tests -v
streamlit run app.py
```

Resultado de las pruebas en el entorno de desarrollo: 31 pruebas correctas (24 de lógica + 7 de humo con un Streamlit simulado). **Importante:** la app **no se ejecutó en un Streamlit real** en ese entorno (sin internet); la prueba de humo detecta errores de código y de flujo, no comportamientos visuales. Revisa la app desplegada y reporta cualquier cosa que no responda.

## Pendiente

- Fase 4: perfiles de usuario y tutor, permisos y consentimiento, panel familiar, reportes y almacenamiento persistente.
- Fase 5: cuentas, tarjetas, transferencias y pagos **simulados**; seguridad bancaria avanzada.
- Fase 6: análisis de alianzas con bancos y fintech, integraciones autorizadas, educación crediticia ampliada.
- Fotografías reales de monedas y billetes; pictogramas ARASAAC (verificar licencia); más retos y dificultad adaptativa automática.
- Revisión de accesibilidad con personas usuarias y profesionales; pruebas con lector de pantalla.
- Revisión legal de contenidos sobre crédito (México) antes de uso público.

## Limitaciones actuales

- Sin persistencia en servidor ni autenticación; no es un sistema seguro para datos personales reales.
- Kiki usa coincidencia de palabras clave: puede no entender preguntas muy distintas a sus temas.
- Los ejercicios usan pesos enteros; no incluyen centavos.
- El alto contraste y los colores se probaron solo por revisión de código, no visualmente.
