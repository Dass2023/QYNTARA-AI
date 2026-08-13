#include "q_nexus/core/baker.hpp"
#include <iostream>
#include <cmath>

namespace q_nexus {

// Möller–Trumbore ray-triangle intersection
Hit intersect_triangle(const Ray& ray, const Vector3& v0, const Vector3& v1, const Vector3& v2) {
    Hit hit;
    Vector3 edge1 = {v1.x - v0.x, v1.y - v0.y, v1.z - v0.z};
    Vector3 edge2 = {v2.x - v0.x, v2.y - v0.y, v2.z - v0.z};
    
    // Cross product (h = d x e2)
    Vector3 h = {
        ray.direction.y * edge2.z - ray.direction.z * edge2.y,
        ray.direction.z * edge2.x - ray.direction.x * edge2.z,
        ray.direction.x * edge2.y - ray.direction.y * edge2.x
    };
    
    // Dot product (a = e1 . h)
    float a = edge1.x * h.x + edge1.y * h.y + edge1.z * h.z;
    if (a > -1e-6f && a < 1e-6f) return hit; // Parallel
    
    float f = 1.0f / a;
    Vector3 s = {ray.origin.x - v0.x, ray.origin.y - v0.y, ray.origin.z - v0.z};
    float u = f * (s.x * h.x + s.y * h.y + s.z * h.z);
    if (u < 0.0f || u > 1.0f) return hit;
    
    // q = s x e1
    Vector3 q = {
        s.y * edge1.z - s.z * edge1.y,
        s.z * edge1.x - s.x * edge1.z,
        s.x * edge1.y - s.y * edge1.x
    };
    
    float v = f * (ray.direction.x * q.x + ray.direction.y * q.y + ray.direction.z * q.z);
    if (v < 0.0f || u + v > 1.0f) return hit;
    
    float t = f * (edge2.x * q.x + edge2.y * q.y + edge2.z * q.z);
    if (t > 1e-6f) {
        hit.hit = true;
        hit.distance = t;
        // Normal (Cross e1, e2)
        hit.surface_normal = {
            edge1.y * edge2.z - edge1.z * edge2.y,
            edge1.z * edge2.x - edge1.x * edge2.z,
            edge1.x * edge2.y - edge1.y * edge2.x
        };
        // Normalize
        float len = std::sqrt(hit.surface_normal.x * hit.surface_normal.x + 
                              hit.surface_normal.y * hit.surface_normal.y + 
                              hit.surface_normal.z * hit.surface_normal.z);
        if (len > 0) {
            hit.surface_normal.x /= len; hit.surface_normal.y /= len; hit.surface_normal.z /= len;
        }
    }
    
    return hit;
}

void Baker::bake_normals_to_vertices() {
    std::cout << "[Q-Nexus] Baking High-Poly Detail to Low-Poly..." << std::endl;
    // Iterate over low-poly vertices and cast rays to high-poly
}

Hit Baker::intersect_high_poly(const Ray& ray) const {
    Hit closest_hit;
    
    // Simple brute-force for R&D (Replacement for Embree BVH)
    for (const auto& face : high_poly_.faces) {
        Id h0 = face.half_edge;
        Id h1 = high_poly_.half_edges[h0].next;
        Id h2 = high_poly_.half_edges[h1].next;
        
        const auto& v0 = high_poly_.vertices[high_poly_.half_edges[h2].target_vertex].position;
        const auto& v1 = high_poly_.vertices[high_poly_.half_edges[h0].target_vertex].position;
        const auto& v2 = high_poly_.vertices[high_poly_.half_edges[h1].target_vertex].position;
        
        Hit hit = intersect_triangle(ray, v0, v1, v2);
        if (hit.hit && hit.distance < closest_hit.distance) {
            closest_hit = hit;
        }
    }
    
    return closest_hit;
}

} // namespace q_nexus
