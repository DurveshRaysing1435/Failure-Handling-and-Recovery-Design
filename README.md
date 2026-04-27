# 🛡️ Phase 1 – Reliability Layer: Failure Handling & Recovery Design

**Project:** AI Interview and Assessment Monitoring System
**Task:** Task 17 — Failure Handling Design
**Difficulty:** High

## 📌 Overview
In real-world assessment environments, external APIs drop, networks disconnect, and candidates act unpredictably (e.g., remaining silent or giving invalid answers). If not handled properly, these edge cases cause system crashes and poor user experiences. 

This repository contains the **Failure Handling & Recovery Engine**. It acts as an independent middleware layer designed to intercept system failures and user errors, apply strategic retry mechanisms (like exponential backoff), and generate graceful fallback responses without crashing the core assessment engine.

---

## 🧩 Core Modules

### 1. `error_handler.py` (The Reliability Middleware)
This is the core, API-first engine containing the failure logic. It avoids tight coupling with the main assessment system and utilizes strict `Pydantic` schemas for data validation.
* **`ErrorLogSchema`**: Standardizes error logging for database insertion (timestamps, incident IDs, severity).
* **`UIResponseSchema`**: Formats the fallback text and action commands sent back to the frontend.
* **`FailureHandler` (Class)**: Tracks session retries and executes the specific recovery strategy:
  * `handle_user_silence()`: Prompts the user up to 2 times before skipping the question with 0 points.
  * `handle_llm_timeout()`: Applies exponential backoff (2s, 4s) to retry AI calls before gracefully failing and moving on.

### 2. `main.py` (FastAPI Implementation)
A lightweight FastAPI server built to demonstrate the integration of the `error_handler.py` module. It exposes a testing endpoint (`/api/evaluate_answer`) to simulate LLM timeouts and user silence.

---

## ⚙️ How to Run & Test Locally

### Prerequisites
Ensure you have Python 3.8+ installed. Install the required libraries using pip:
```bash
pip install fastapi uvicorn pydantic
