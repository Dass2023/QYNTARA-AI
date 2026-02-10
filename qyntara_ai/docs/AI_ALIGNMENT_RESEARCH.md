# AI/ML Research: Geometry Snapping & Layout

## Overview
This document outlines research and integration strategies for incorporating AI-driven geometry snapping and layout correction into Qyntara AI. The goal is to move beyond heuristic bounding-box checks to intelligent, context-aware assembly.

## 1. Scene Graph Completion (Snap-by-Learning)
*   **Concept**: Predict object positions using learned layout constraints (e.g., "Chair goes in front of table").
*   **Relevance**: Train models on valid "Modular Kit" assemblies to learn how parts (walls, floors, props) typically connect.
*   **Technology**: Graph Neural Networks (GNNs), Conditional GANs.
*   **Reference**: "Learning to Reconstruct Indoor Scenes Using Generative Scene Graphs" (MIT/DeepMind).

## 2. Modular Assembly Agents
*   **Concept**: Use Reinforcement Learning (RL) agents in simulation to learn how to assemble kits.
*   **Relevance**: An agent can learn valid rotations and snap points for complex modular libraries where manual rule definition is tedious.
*   **Integration**: Train in NVIDIA Isaac Sim / Unity ML, deploy inference model to Maya.

## 3. Mesh Completion Models
*   **Concept**: Reconstruct full meshes from partial inputs.
*   **Relevance**: "Heal" gaps or suggest alignment by predicting the "whole" shape from two misaligned parts.
*   **Examples**: PointFlow, AtlasNet, PCN.

## 4. AI-Based Scan Alignment
*   **Concept**: Align geometry using Deep Learning registration (robust against noise).
*   **Relevance**: Aligning scanned assets or messy photogrammetry to clean CAD/Modular references.
*   **Tools**: Meshroom, Open3D + DL.

## Integration Strategy (Roadmap)

| Feature | AI Role | Integration Method |
| :--- | :--- | :--- |
| **Snap Detection** | Classify "Good" vs "Bad" alignment | Train GNN Classifier on dataset of pairs |
| **Auto-Snap Prediction** | Predict relative transform offset | Regression Model (Input: 2 BBoxes/PointClouds -> Output: Transform) |
| **Gap Filling** | Complete mesh geometry | Pre-process with Mesh Completion Network |
| **Layout Correction** | Suggest full layout fixes | Batch processing script calling inference server |

## Next Steps
1.  **Dataset Collection**: Build a dataset of "Perfectly Snapped" modular kits (Walls, Floors).
2.  **Prototype**: Train a simple binary classifier (Snap/No-Snap) using PointNet on edge data.
3.  **Deployment**: Wrap model in `qyntara_ai.ai_assist` and expose via Qyntara Server.
