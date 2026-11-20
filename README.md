# FinanIA Inclusivo – Fase 4

Aplicación educativa de finanzas personales con Python y Streamlit.

## Novedades de esta fase
- **Botones de voz 🔊** en títulos, instrucciones, tarjetas, preguntas y resultados. Leen con voz en español de México (la del navegador/dispositivo).
- **Retos en mapa de niveles**: 16 retos en 5 niveles (🌱 Muy fácil → 🏆 Experto) sobre un camino con estrellas, puntos, una mascota que avanza y una corona final.
- **Diseño más colorido**: fondo degradado, barra lateral de colores, tarjetas con iconos grandes.
- Interruptor para ocultar los botones de voz y botón "Probar la voz" en Mi experiencia.
- Corrección: los totales de ingresos y gastos ya no fallan al registrar movimientos.

## Funciones
- Conocer el dinero: reconocimiento de cantidades y sumas.
- Practicar compras: precios y cálculo de cambio.
- Organizar mi dinero: formulario para ingresos y gastos.
- Mi ahorro: meta y barra de progreso.
- Retos y juegos con mapa, pistas y estrellas.
- Ayuda FinanIA con explicaciones educativas preparadas (sin API).
- Preferencias: tamaño de letra, alto contraste, instrucciones paso a paso y voz.
- Modo demostración con movimientos ficticios.

## Publicar en GitHub y Streamlit Community Cloud
1. Descomprime este ZIP.
2. Abre tu repositorio `FinanIA-Inclusivo` en GitHub.
3. Selecciona **Add file → Upload files**.
4. Sube `app.py`, `requirements.txt` y `README.md`, reemplazando los anteriores.
5. Pulsa **Commit changes**.
6. En Streamlit Community Cloud espera a que detecte los cambios. Si no se actualiza, entra a **Manage app → Reboot**.

Conserva la aplicación anterior hasta comprobar que la nueva funciona.

## Sobre la voz
- Usa la síntesis de voz del navegador: no requiere API ni costo.
- Elige una voz femenina en español de México si el dispositivo la tiene (Edge, Chrome, Android y iPhone suelen tenerla). Si no, usa otra voz en español.
- Toca 🔊 para escuchar y vuelve a tocarlo para detener.
- Si no suena, revisa el volumen y que el navegador no tenga la pestaña silenciada.

## Importante
- No requiere claves API ni servicios de pago.
- No conecta con bancos ni procesa pagos.
- Los datos y preferencias se guardan en la sesión de Streamlit y pueden perderse al reiniciar o volver a publicar.
- No introduzcas contraseñas, datos bancarios ni información personal sensible.
- Es una herramienta educativa, no asesoría financiera ni herramienta clínica.
- Antes de usarla con participantes, realiza pruebas con consentimiento y permite que cada persona ajuste sus preferencias.
