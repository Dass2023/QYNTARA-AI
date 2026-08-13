#pragma once

#include "q_nexus/core/half_edge.hpp"
#include <vector>

namespace q_nexus {

struct Ray {
    Vector3 origin;
    Vector3 direction;
};

struct Hit {
    bool hit = false;
    float distance = 1e30f;
    Vector3 surface_normal;
};

class Baker {
public:
    Baker(const Mesh& high_poly, const Mesh& low_poly)
        : high_poly_(high_poly), low_poly_(low_poly) {}

    // Phase 4: Normal Transfer & Baking
    
    // Transfoms high-poly geometric detail to low-poly vertex normals
    // or generates a normal map (Mock).
    void bake_normals_to_vertices();

    // BVH Ray-casting (Embree-style)
    Hit intersect_high_poly(const Ray& ray) const;

private:
    const Mesh& high_poly_;
    const Mesh& low_poly_;
};

} // namespace q_nexus
