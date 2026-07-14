---
title: "Session Summary: 2026-07-14"
date: 2026-07-14
tags: [session-summary, sprint-2, pddl, hitl, orchestrator, langgraph]
status: active
---

# Session Summary: Sprint 2 PDDL & HITL Implementations

## 1. Datos de la Sesión
* **Fecha:** 2026-07-14
* **Objetivo:** Ejecutar Exp 2.1 (PDDL Intent Parser) y Exp 2.2 (Reverse Prompting HITL Node) según el [[MVP_Roadmap]].
* **Resultado:** ÉXITO. La pipeline neurosimbólica (según [[Architecture_v4]]) ahora traduce intents en PDDL con validación CFG (Regex) e incorpora convergencia HITL interactiva, manejando iterativamente el feedback del operador mediante el uso de LangGraph `interrupt()`.

## 2. Decisiones Arquitectónicas y de Código

Se reemplazaron los stubs de la sesión anterior por implementaciones robustas en `src/agents/pddl_parser.py` y `src/agents/reverse_prompt.py`.

* **PDDL Simplificado:** Decidimos utilizar un subconjunto minimalista de PDDL adaptado a la red óptica (`define`, `problem`, `:domain`, `:objects`, `:init`, `:goal`). 
* **Validador CFG Determinístico (`src/core/pddl_validator.py`):** Antes de continuar el pipeline, se verifica la estructura del PDDL usando un script Regex. Si hay alucinación estructural (faltan secciones o paréntesis desbalanceados), se rechaza.
* **Mecanismo Anti-Drift Semántico (Reverse Prompting):** En lugar de mostrar el PDDL crudo al operador (que es difícil de leer y aprobar), el sistema realiza un call inverso al LLM para traducir el PDDL generado a lenguaje natural ("Reconstrucción"). El usuario aprueba la reconstrucción, forzando la convergencia semántica de su intent inicial y el constraint code final (ver [[ProblemStatement_v4]]).
* **Feedback Loop del Operador:** Se identificó y resolvió un bug donde el `pddl_parser` original ignoraba el feedback de la iteración HITL. Se modificó el parser para que detecte la presencia de `pddl_constraints` y `error_context` previos en el `AgentState` y lo envíe al LLM para refinamiento.

## 3. Estado del Código (`src/`)

El código fuente actual de la aplicación se encuentra estructurado y operando de la siguiente manera:
* **`src/core/`**: Contiene la lógica base (grafos, estados, validación). 
  * `llm.py` (Conexión configurada con Kimi).
  * `state.py` (Definición del AgentState).
  * `graph.py` (Configuración de LangGraph).
  * `pddl_validator.py` (Validador CFG funcional con 20/20 tests en verde).
* **`src/agents/`**: Nodos de comportamiento del orchestrator.
  * `intent_ingest.py` (Procesa el lenguaje natural inicial).
  * `pddl_parser.py` (Llamado al LLM con prompt dinámico y feedback iterativo).
  * `reverse_prompt.py` (Traducción inversa e interrupción HITL).
* **`src/tools/`**: Herramientas determinísticas y de validación física.
  * `qot_tool.py` (Cálculo de Quality of Transmission traducido 100% a Python).
* **`src/services/`**: 
  * `testbed_client.py` (Actualmente tiene el stub y los mocks de RESTConf a la espera de la API real).

## 4. Aspectos a tener en cuenta (Handover for Future Agents)

* **Strict TDD Mode activo:** Toda lógica nueva en los nodos debe ser escrita usando pruebas automatizadas y mockeando las llamadas al LLM (`patch("src.core.llm.get_llm")`). El set actual de pruebas (126) es 100% verde (`uv run pytest tests/`).
* **Interrupt de LangGraph:** El nodo `reverse_prompt_node` pausa la ejecución con `interrupt(...)`. El input del usuario se inyecta mediante el `Command(resume=...)` ejecutado desde `main.py`.
* **Estado del Pipeline:** El feedback de refinamiento (almacenado como un string bajo la key `error_context` del `AgentState`) viaja directo del `reverse_prompt` al `pddl_parser` a través de la función `hitl_route(state)`.

## 4. Siguientes Pasos
- [ ] Obtener la API del testbed virtual del profesor e implementar el código real en `RESTConfTestbedClient` para el Exp 1.3. **(Bloqueante prioritario antes del despliegue E2E).**
- [ ] Avanzar con el Exp 2.3: `Symbolic Solver` & `Mock GraphRAG`.
