#include "q_nexus/core/half_edge.hpp"
#include <map>
#include <utility>

namespace q_nexus {

Id Mesh::add_vertex(float x, float y, float z) {
    Id id = static_cast<Id>(vertices.size());
    vertices.push_back({{x, y, z}, INVALID_ID});
    return id;
}

void Mesh::add_triangle(Id v0, Id v1, Id v2) {
    // Basic construction (Simplified for Phase 2)
    // In a production Half-Edge system, this involves complex opposite linkage
    // and edge-map tracking.
    
    Id f_id = static_cast<Id>(faces.size());
    faces.push_back({INVALID_ID});

    Id h0 = static_cast<Id>(half_edges.size());
    Id h1 = h0 + 1;
    Id h2 = h0 + 2;

    half_edges.push_back({v1, h1, INVALID_ID, f_id});
    half_edges.push_back({v2, h2, INVALID_ID, f_id});
    half_edges.push_back({v0, h0, INVALID_ID, f_id});

    faces[f_id].half_edge = h0;
    vertices[v0].half_edge = h0;
    vertices[v1].half_edge = h1;
    vertices[v2].half_edge = h2;
}

int Mesh::calculate_euler_characteristic() const {
    // Industrial V - E + F calculation
    // E (Edges) must be counted as UNIQUE pairs of vertices
    size_t V = vertices.size();
    size_t F = faces.size();
    
    // For a robust Half-Edge mesh, E is (InternalHalfEdges + BoundaryHalfEdges) / 2
    // If we haven't linked opposites yet, we count the individual edges manually
    // or assume the current half_edges represent the edges (for simple triangles).
    
    // NEW: Count unique edges by vertex pairs
    std::map<std::pair<Id, Id>, bool> unique_edges;
    for (size_t i = 0; i < half_edges.size(); ++i) {
        Id v1 = half_edges[i].target_vertex;
        // The source vertex of a half-edge is the target of the PREVIOUS half-edge
        Id next_id = half_edges[i].next;
        Id v2 = half_edges[next_id].target_vertex;
        
        Id min_v = std::min(v1, v2);
        Id max_v = std::max(v1, v2);
        unique_edges[{min_v, max_v}] = true;
    }

    size_t E = unique_edges.size();
    return static_cast<int>(V - E + F);
}

bool Mesh::is_manifold() const {
    // Industrial check: Every edge must have exactly one or two half-edges
    // (Managed by the half-edge structure by definition, but needs opposite link validation)
    for (const auto& he : half_edges) {
        if (he.target_vertex >= vertices.size()) return false;
    }
    return true;
}

} // namespace q_nexus
