#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <bplustree.hpp>

namespace py = pybind11;

template<>
class BPlusTreeTraits<py::object, py::object> {
public:
    using Key = py::object;
    using FindBy = py::object;
    using Value = py::object;

    static FindBy to_find_by(Key key)
    {
        return key;
    }

    static std::size_t hash(FindBy value)
    {
        return py::hash(value);
    }
};

using PyBPlusTree = BPlusTree<py::object, py::object>;

PYBIND11_MODULE(_core, m)
{
    m.doc() = "Adds a B+ Tree data structure";

    py::class_<PyBPlusTree>(m, "BPlusTree")
        .def(py::init<>())
        .def("insert", &PyBPlusTree::insert)
        .def("find", &PyBPlusTree::find);
}
