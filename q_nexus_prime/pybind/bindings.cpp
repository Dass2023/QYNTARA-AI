#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "q_nexus/core/half_edge.hpp"
#include "q_nexus/core/remesher.hpp"
#include "q_nexus/core/baker.hpp"

namespace py = pybind11;
using namespace q_nexus;

PYBIND11_MODULE(q_nexus_prime, m) {
    m.doc() = "Q-Nexus Prime: High-Performance C++20 Mesh Processing Engine";

    py::class_<Vertex>(m, "Vertex")
        .def_readwrite("position", &Vertex::position);

    py::class_<Mesh>(m, "Mesh")
        .def(py::init<>())
        .def("add_vertex", &Mesh::add_vertex)
        .def("add_triangle", &Mesh::add_triangle)
        .def("calculate_euler_characteristic", &Mesh::calculate_euler_characteristic)
        .def("is_manifold", &Mesh::is_manifold);

    py::class_<Remesher>(m, "Remesher")
        .def(py::init<Mesh&>())
        .def("optimize_orientation_field", &Remesher::optimize_orientation_field, 
             py::arg("stiffness_weight") = 1.0f, py::arg("iterations") = 10)
        .def("optimize_position_field", &Remesher::optimize_position_field)
        .def("extract_mesh", &Remesher::extract_mesh);

    py::class_<Baker>(m, "Baker")
        .def(py::init<const Mesh&, const Mesh&>())
        .def("bake_normals_to_vertices", &Baker::bake_normals_to_vertices);
}
