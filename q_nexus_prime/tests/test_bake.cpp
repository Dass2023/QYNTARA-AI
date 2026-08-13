#include "q_nexus/core/half_edge.hpp"
#include "q_nexus/core/baker.hpp"
#include <iostream>

int main() {
    q_nexus::Mesh high_poly;
    q_nexus::Mesh low_poly;

    // Create a high-poly triangle (Source)
    auto v0 = high_poly.add_vertex(0, 0, 10);
    auto v1 = high_poly.add_vertex(1, 0, 10);
    auto v2 = high_poly.add_vertex(0, 1, 10);
    high_poly.add_triangle(v0, v1, v2);

    q_nexus::Baker baker(high_poly, low_poly);

    std::cout << "[Q-Nexus Test] Starting Ray-Casting Bake Verification..." << std::endl;
    
    // Cast a ray from origin up towards the triangle
    q_nexus::Ray ray = {{0.2f, 0.2f, 0.0f}, {0.0f, 0.0f, 1.0f}};
    auto hit = baker.intersect_high_poly(ray);
    
    if (hit.hit) {
        std::cout << "[Q-Nexus Test] Hit Detected at distance: " << hit.distance << std::endl;
        std::cout << "[Q-Nexus Test] Surface Normal: (" << hit.surface_normal.x << ", " << hit.surface_normal.y << ", " << hit.surface_normal.z << ")" << std::endl;
        
        // Expected distance: 10
        // Expected normal: (0, 0, 1) or (0, 0, -1) depending on winding
        if (hit.distance > 9.9f && hit.distance < 10.1f) {
             std::cout << "[Q-Nexus Test] PASSED: Ray-casting fidelity verified." << std::endl;
             return 0;
        }
    }

    std::cout << "[Q-Nexus Test] FAILED: Ray-casting deviation detected!" << std::endl;
    return 1;
}
