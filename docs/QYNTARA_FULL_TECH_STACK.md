# Qyntara AI: Full Technology Stack & Component Breakdown

This document provides a comprehensive list of all technologies, frameworks, libraries, and tools used in the Qyntara AI architecture.

---

## 1. Core Application Frameworks
The fundamental platforms the application runs on.

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **DCC Host** | Autodesk Maya | 2022 - 2025 | The main host application for the plugin. |
| **Language** | Python | 3.7 (Maya 22) / 3.9+ | Primary programming language for all logic. |
| **UI Framework** | PySide2 (Qt 5) | 5.15.x | Used for Maya 2022-2024 UI. |
| **UI Framework** | PySide6 (Qt 6) | 6.x | Future-proofing for Maya 2025+. |

---

## 2. Backend & Cloud Infrastructure
Technologies used for the "Cloud Validation" microservices.

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Gateway** | FastAPI | High-performance async web server for handling jobs. |
| **Server** | Uvicorn | ASGI server to run FastAPI. |
| **Message Broker** | Redis | In-memory queue for managing job distribution to workers. |
| **Worker Node** | Maya Standalone (mayapy) | Headless Maya instance for backend processing. |
| **Containerization** | Docker | Packaging the environment (API, Redis, Worker). |
| **Orchestration** | Docker Compose | Managing multi-container localized deployment. |
| **Base Image** | python:3.9-slim | Lightweight Linux base for API services. |

---

## 3. Geometric & Mathematical Engines
Libraries used for mesh calculation, analysis, and cleaning.

| Library | Role | Usage |
|---------|------|-------|
| **OpenMaya** | Low-Level API | Maya's native C++ wrapper for high-speed geometry access. |
| **maya.cmds** | Scripting API | Maya's high-level command wrapper for scene manipulation. |
| **NumPy** | Math Core | Vector math, matrix transformations, and fast array operations. |
| **Trimesh** | Geometry Proc. | Dealing with non-manifold geometry and "water-tight" checks off-line. |
| **Open3D** | Point Cloud | converting Meshes to Point Clouds for AI ingestion. |

---

## 4. Artificial Intelligence (AI) Stack
The "Brain" of the Qyntara anomaly detection system.

| Component | Technology | Details |
|-----------|------------|---------|
| **ML Framework** | PyTorch | Deep learning tensor library. |
| **Model Architecture** | Custom PointNet | Modified PointNet (Conv1d) for point cloud classification. |
| **Training Data** | Synthetic Generation | Custom scripts (`qyntara_ai/ai_assist/dataset`) generate training samples inside Maya. |
| **Inference** | CPU / CUDA | Can run on Artist CPU or Cloud GPU. |

---

## 5. Development & DevOps Tools
Tools used to build, test, and maintain the system.

| Tool | Purpose |
|------|---------|
| **Git** | Version Control. |
| **PyTest** | Unit Testing framework (mocking Maya environment). |
| **VS Code** | Recommended IDE with MayaCode extension. |
| **Mermaid** | Diagramming architecture in documentation. |

---

## 6. Detailed Data Flow Components

### A. Client-Server Communication
*   **Protocol**: HTTP/1.1 (REST)
*   **Data Format**: JSON (Rulesets, Reports)
*   **File Transfer**: Multipart/Form-Data (Binary .mb/.obj upload)

### B. Validation Ruleset
*   **Configuration**: `qyntara_ruleset.json`
*   **Structure**: JSON definition of ~40 rules with `severity`, `enabled`, and `function` mapping.

### C. Auto-Fix System
*   **Logic**: Deterministic Python Functions (`fixer.py`).
*   **State Management**: In-memory re-validation to prevent "fix-loops".
