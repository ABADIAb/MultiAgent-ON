---
title: "Session Summary: V5 Pivot & Risk-Adaptive Decision Gate"
date: 2026-07-17
tags: [session, debrief, pivot, radg, architecture-v5, sota]
status: active
---

# Session Summary: V5 Pivot & Risk-Adaptive Decision Gate

**Fecha:** 2026-07-17 | **Agente Principal:** Gemini 3.1 Pro

## 🎯 1. Objetivo de la Sesión
* Implementar el feedback del profesor respecto a la novedad de la tesis y la superposición con trabajos previos (PoliMi/CNSM 2025).
* Pivotar la arquitectura y el *Problem Statement* de la versión 4 (enfocada en convergencia HITL de múltiples turnos) a la versión 5, centrada en un mecanismo de pre-despliegue.

## 🧠 2. Decisiones Arquitectónicas y Conceptuales
* **Risk-Adaptive Decision Gate (RADG):** Se introdujo este nuevo componente crítico. El RADG es un filtro que evalúa conjuntamente la incertidumbre semántica ($U_{sem}$) en dos capas (validación estructural + similitud de embeddings) y el margen de riesgo físico QoT ($R_{qot}$).
* **Función de Decisión de 4 Salidas:** El sistema ahora clasifica la intención del operador antes del despliegue en:
  1. `Auto-Approve` (riesgo nulo)
  2. `Clarify` (incertidumbre semántica)
  3. `Suggest Replan` (riesgo físico marginal)
  4. `Reject` (riesgo físico inaceptable)
* **Diferenciación frente a PoliMi/CNSM 2025:** Mientras que el *state-of-the-art* basa su seguridad en un bucle de reintento post-despliegue (evaluando el fallo *después* de enviar al controlador), nuestra V5 previene configuraciones inseguras evaluando el riesgo *antes* del despliegue.

## 📝 3. Documentación y Wiki
* **Nuevos Documentos:**
  * [[Architecture_v5]]: Nuevo pipeline secuencial con el RADG.
  * [[ProblemStatement_v5]]: Nueva formulación del problema y marco formal de evaluación (UAR, HIC, QFR, E2EL, TC).
* **Documentos Modificados:**
  * [[Scope_Pivot_20260706]]: Actualizado con el tercer pivot (V4 → V5).
  * [[experiments/MVP_Roadmap]]: Añadidos experimentos 3.1 (RADG), 3.2 (HITL condicional) y 4.0 (Test Corpus).
  * [[literature/sota_gap_analysis]]: Añadido el paper PoliMi/CNSM 2025 y las columnas de Risk-Adaptive HITL y Pre-Deployment.
  * [[weekly_reports/Weekly_Report_20260720_Felipe_Abadia]]: Actualizado el progreso y redactada la pregunta al profesor sobre el proxy $U_{sem}$.
* **Archivados:** Todos los documentos de la V4 fueron movidos a la carpeta `archive/` y los links históricos en la wiki fueron corregidos (Deep Lint ejecutado).

## 🚀 4. Siguientes Pasos (Next Session)
1. **Implementación Exp 3.1:** Escribir el código del `radg.py` integrando la evaluación dual.
2. **Implementación Exp 4.0:** Crear el `test_corpus.json` con los 4 tipos de riesgo.
3. Esperar la respuesta del profesor sobre la métrica de $U_{sem}$ (Layer 2) para calibrar el umbral $\tau_{sem}$.
