#pragma once

#include "q_nexus/core/half_edge.hpp"
#include <vector>

namespace q_nexus {

struct FieldVector {
    float x, y, z;
};

class Remesher {
public:
    Remesher(Mesh& mesh) : mesh_(mesh) {}

    // Phase 3: Field-Aligned Pipeline
    
    // Step 1: Orientation Field Optimization
    // Initializes and smooths a 4-RoSy orientation field across the mesh.
    // stiffness_weight: Higher values enforce straighter, more parallel quad flow.
    void optimize_orientation_field(float stiffness_weight = 1.0f, int iterations = 10);

    // Step 2: Position Field Optimization
    // Solves for local (u,v) parameterization aligned with the orientation field.
    void optimize_position_field(int iterations = 10);

    // Step 3: Mesh Extraction
    // Generates the final quad-dominant mesh.
    void extract_mesh();

private:
    Mesh& mesh_;
    std::vector<FieldVector> orientation_field_;
    std::vector<Vector3> position_field_; // Local parameterization coords
};

} // namespace q_nexus
