# FinanIA Inclusivo — prototipo gratuito

## Qué incluye
- Registro local de ingresos y gastos.
- Clasificación experimental de descripciones con un modelo de aprendizaje automático (TF-IDF + Naive Bayes).
- Confirmación/corrección manual de la categoría sugerida.
- Resumen y gráfica de gastos.
- Ejercicio educativo de cambio y meta visual de ahorro.
- Ajuste básico del tamaño de texto.
- Base de datos SQLite local.

## Requisitos
- Python 3.10 o posterior.
- Conexión a internet solo para instalar las bibliotecas la primera vez.

## Cómo ejecutarlo
1. Descarga y descomprime el proyecto.
2. Abre una terminal dentro de la carpeta `finania_inclusivo`.
3. (Opcional pero recomendado) crea un entorno virtual:
   - Windows: `python -m venv .venv` y `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` y `source .venv/bin/activate`
4. Instala dependencias: `pip install -r requirements.txt`
5. Inicia la aplicación: `streamlit run app.py`
6. Se abrirá en el navegador, normalmente en `http://localhost:8501`.

## Importante
- No se conecta a bancos ni procesa pagos.
- Los datos se guardan en `finania.db` en la computadora donde se ejecuta.
- El modelo de IA es una demostración pequeña: puede clasificar mal. La persona debe poder confirmar o corregir la categoría.
- Antes de probar con personas, solicita consentimiento, evita recopilar datos sensibles y realiza pruebas de accesibilidad con personas autistas y profesionales/asesores relevantes.
- No asumas que una misma interfaz sirve para todas las edades o necesidades. Permite personalizarla.
