#include "q_nexus/core/half_edge.hpp"
#include <iostream>

int main() {
    q_nexus::Mesh mesh;

    // Create a Tetrahedron (4 vertices, 6 edges, 4 faces)
    auto v0 = mesh.add_vertex(0, 0, 0);
    auto v1 = mesh.add_vertex(1, 0, 0);
    auto v2 = mesh.add_vertex(0.5f, 1, 0);
    auto v3 = mesh.add_vertex(0.5f, 0.5f, 1);

    mesh.add_triangle(v0, v1, v2); // Base
    mesh.add_triangle(v0, v1, v3); // Side 1
    mesh.add_triangle(v1, v2, v3); // Side 2
    mesh.add_triangle(v2, v0, v3); // Side 3

    int chi = mesh.calculate_euler_characteristic();
    
    std::cout << "[Q-Nexus Industrial] Vertices: " << mesh.vertices.size() << std::endl;
    std::cout << "[Q-Nexus Industrial] Half-Edges: " << mesh.half_edges.size() << std::endl;
    std::cout << "[Q-Nexus Industrial] Faces: " << mesh.faces.size() << std::endl;
    std::cout << "[Q-Nexus Industrial] Euler Characteristic: " << chi << std::endl;

    // For a tetrahedron (closed manifold, genus 0): V - E + F = 4 - 6 + 4 = 2.
    if (chi == 2) {
        std::cout << "[Q-Nexus Industrial] PASSED: Closed manifold integrity verified (V-E+F=2)." << std::endl;
        return 0;
    } else {
        std::cout << "[Q-Nexus Industrial] FAILED: Topological deviation in closed manifold!" << std::endl;
        return 1;
    }
}
