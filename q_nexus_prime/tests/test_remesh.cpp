#include "q_nexus/core/half_edge.hpp"
#include "q_nexus/core/remesher.hpp"
#include <iostream>

int main() {
    q_nexus::Mesh mesh;

    // Create a simple planar patch (2 triangles)
    auto v0 = mesh.add_vertex(0, 0, 0);
    auto v1 = mesh.add_vertex(1, 0, 0);
    auto v2 = mesh.add_vertex(0, 1, 0);
    auto v3 = mesh.add_vertex(1, 1, 0);

    mesh.add_triangle(v0, v1, v2);
    mesh.add_triangle(v1, v3, v2);

    q_nexus::Remesher remesher(mesh);

    std::cout << "[Q-Nexus Test] Starting Field Alignment R&D..." << std::endl;
    
    // Test Orientation Field solver with Stiffness Weight
    remesher.optimize_orientation_field(5.0f, 5); // Stiffness = 5.0
    
    std::cout << "[Q-Nexus Test] PASSED: Field Alignment initialized successfully." << std::endl;
    return 0;
}
