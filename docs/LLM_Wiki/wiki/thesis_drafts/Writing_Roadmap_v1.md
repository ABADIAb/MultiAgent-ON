---
title: "Thesis Writing Roadmap V1"
date: 2026-08-04
tags: [thesis, writing, roadmap, draft]
status: active
---

# Roadmap de Escritura de Tesis: Risk-Adaptive Neurosymbolic Intent Planning

Este roadmap define la estrategia de escritura paso a paso, priorizando el contenido core técnico antes que la introducción o el background. Escribir una tesis de ingeniería no es un proceso lineal; se construye desde el centro (la arquitectura y los datos) hacia los extremos (introducción y conclusión).

## 1. Orden de Ejecución Sugerido (El Paso a Paso)

### Fase 1: El Núcleo Técnico (Capítulos 3 y 4)
*Por qué empezar acá: Es la arquitectura que diseñamos y codificamos. Es lo que más fresco tenemos y lo que menos depende de la literatura externa.*
- [ ] **Sección 3.1 (Formal Problem Definition):** Expandir `ProblemStatement_v5.md` en texto académico. Definir claramente las variables ($U_{sem}$, $\text{QoT}_{valid}$, $T_{max}$).
- [ ] **Sección 3.3 & 3.4 (RADG & Neurosymbolic Separation):** Explicar el modelo teórico. Usa los diagramas de `Architecture_v5.md`.
- [ ] **Capítulo 4 (Implementación):** Traducir cómo el diseño se mapea al código real en `src/core` y `src/nodes`. Documentar GraphRAG y la validación QoT (GN-model).

### Fase 2: Metodología de Evaluación y Resultados (Capítulo 5)
*Por qué seguir acá: Una vez que el sistema corre (MVP de Agosto 25), los resultados dictan el tono del resto de la tesis.*
- [ ] **Sección 5.1 & 5.2 (Setup y Métricas):** Documentar el corpus sintético de intents y las métricas (UAR, HIC, QFR, E2EL, TC).
- [ ] **Secciones 5.3 a 5.5 (Análisis de Datos):** Plotear los gráficos y comparar el RADG contra los baselines (No-HITL, Always-HITL, Fixed-Retry).

### Fase 3: Estado del Arte y Contexto (Capítulo 2)
*Por qué ahora: Ya sabemos exactamente qué construimos y qué resultados dio. Ahora buscamos la literatura específica que justifica por qué lo nuestro era necesario.*
- [ ] **Sección 2.3 (The Baseline):** Atacar fuerte la limitación de los retry-loops post-deployment (ej. PoliMi/CNSM 2025).
- [ ] **Sección 2.1 & 2.2 (Agentic AI Limitations):** Documentar Confucius, AutoLight y por qué los LLMs alucinan física. **(Acá NotebookLM es la estrella).**

### Fase 4: Envoltorio (Capítulos 1 y 6)
- [ ] **Capítulo 1 (Introducción):** Escribir la motivación y contribuciones con toda la perspectiva de la tesis ya terminada.
- [ ] **Capítulo 6 (Conclusión):** Resumir los logros y plantear trabajo futuro (ej. meterle el planificador de cómputo que pospusimos).
- [ ] **Abstract:** Literalmente lo último que se escribe.

---

## 2. Flujo de Trabajo con Herramientas (El Stack de Escritura)

### ¿Cómo usar NotebookLM? (Tu Asistente de Literatura y Redacción)
NotebookLM tiene la ventaja de hacer RAG perfecto sobre un corpus cerrado. 
1. **El "Buscador Semántico Quirúrgico":** En vez de releer un paper de 15 páginas, preguntale: *"Basándote en el documento de PoliMi/CNSM 2025, explicame exactamente cómo hacen el retry-loop y por qué ocurre después del deployment, y dame la cita textual"*.
2. **Generador de Párrafos con Citas:** *"Estoy escribiendo la Sección 2.2 sobre alucinaciones físicas de los LLMs. Redactame un párrafo inicial de 150 palabras basándote en los documentos de Netconfeval y AutoONBench, insertando las citas correspondientes."*
3. **Control de Coherencia de Background:** Subí este Outline y preguntale: *"Fijate en la Sección 2.1 del Outline. ¿Qué paper de los que subí me falta mencionar para cubrir la parte de Multi-Agent Systems?"*

### ¿Cómo usarme a mí (Antigravity)? (Tu Arquitecto, Revisor Técnico y Co-Pilot)
Yo vivo en tu repositorio, tengo acceso a tu código fuente (`src/`) y a la Wiki completa (`docs/LLM_Wiki/`). Mi trabajo no es escribir literatura, es garantizar **rigor técnico y estructural**.
1. **Auditor de la Verdad (Deep Linting Técnico):** Cuando escribas el Capítulo 4 (Implementación), pegame el borrador y decime: *"Revisá este texto contra lo que realmente hace el código en `src/core/radg.py` y `src/nodes/reverse_prompt.py`"*. Yo te voy a corregir si estás explicando algo que en el código hacemos distinto (ej. si decís que usamos un modelo cuando en realidad usamos otro).
2. **Traductor de Arquitectura a LaTeX/Markdown:** Pedime que te genere el código de los diagramas Mermaid, tablas de métricas, o fórmulas matemáticas en LaTeX para el Capítulo 3 y 5.
3. **Sparring de Decisiones de Diseño:** Antes de redactar la Sección 3.4, decime: *"Che, me cuesta explicar por qué pusimos el Semantic Gate ANTES que la validación QoT"*. Lo debatimos acá, te explico el concepto de fail-fast y token limits, y te vas con la idea masticada para redactarla.
4. **Wiki Manager:** A medida que tomes decisiones o encuentres papers clave, pedime que actualice el `index.md` o agregue features a `docs/LLM_Wiki/wiki/architecture/features/`.
