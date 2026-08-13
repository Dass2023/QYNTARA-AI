#pragma once

#include <vector>
#include <cstdint>
#include <array>
#include <optional>

namespace q_nexus {

struct Vector3 {
    float x, y, z;
};

// Index-based ID to ensure cache locality (Avoids pointer chasing)
using Id = uint32_t;
static constexpr Id INVALID_ID = 0xFFFFFFFF;

struct Vertex {
    Vector3 position;
    Id half_edge = INVALID_ID;
};

struct HalfEdge {
    Id target_vertex = INVALID_ID;
    Id next = INVALID_ID;
    Id opposite = INVALID_ID;
    Id face = INVALID_ID;
};

struct Face {
    Id half_edge = INVALID_ID;
};

class Mesh {
public:
    std::vector<Vertex> vertices;
    std::vector<HalfEdge> half_edges;
    std::vector<Face> faces;

    // Core Mesh API
    Id add_vertex(float x, float y, float z);
    void add_triangle(Id v0, Id v1, Id v2);

    // Industrial Verification
    int calculate_euler_characteristic() const;
    bool is_manifold() const;

private:
    Id create_half_edge(Id target, Id next, Id opposite, Id face);
};

} // namespace q_nexus
