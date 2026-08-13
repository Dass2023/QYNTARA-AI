#include "q_nexus/core/half_edge.hpp"
#include <iostream>
#include <cassert>

int main() {
    q_nexus::Mesh mesh;

    // Create a single triangle
    auto v0 = mesh.add_vertex(0, 0, 0);
    auto v1 = mesh.add_vertex(1, 0, 0);
    auto v2 = mesh.add_vertex(0, 1, 0);

    mesh.add_triangle(v0, v1, v2);

    int chi = mesh.calculate_euler_characteristic();
    
    std::cout << "[Q-Nexus Test] Vertices: " << mesh.vertices.size() << std::endl;
    std::cout << "[Q-Nexus Test] Half-Edges: " << mesh.half_edges.size() << std::endl;
    std::cout << "[Q-Nexus Test] Faces: " << mesh.faces.size() << std::endl;
    std::cout << "[Q-Nexus Test] Euler Characteristic: " << chi << std::endl;

    // For a single planar triangle: V=3, E=3, F=1. V - E + F = 3 - 3 + 1 = 1.
    if (chi == 1) {
        std::cout << "[Q-Nexus Test] PASSED: Topological integrity verified." << std::endl;
        return 0;
    } else {
        std::cout << "[Q-Nexus Test] FAILED: Topological deviation detected!" << std::endl;
        return 1;
    }
}
