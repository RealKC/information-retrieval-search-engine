#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <tuple>

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

    static bool is_equal(FindBy a, FindBy b)
    {
        return a.is(b);
    }
};

using PyBPlusTree = BPlusTree<py::object, py::object>;

struct PyBPlusTreeIterator {
    PyBPlusTreeIterator(PyBPlusTree const& tree, py::object ref)
        : ref { ref }
    {
        tree.iterate([&](py::object key, py::object value) {
            leaf_data.push_back(std::tuple { key, value });
        });
    }

    std::tuple<py::object, py::object> next()
    {
        if (index == leaf_data.size()) {
            throw py::stop_iteration();
        }

        return leaf_data[index++];
    }

    std::vector<std::tuple<py::object, py::object>> leaf_data {};
    py::object ref; // keep the Python object alive
    std::size_t index = 0;
};

PYBIND11_MODULE(_core, m)
{
    m.doc() = "Adds a B+ Tree data structure";

    py::class_<PyBPlusTreeIterator>(m, "PyBPlusTreeIterator")
        .def("__iter__", [](PyBPlusTreeIterator& it) -> PyBPlusTreeIterator& { return it; })
        .def("__next__", &PyBPlusTreeIterator::next);

    auto cls = py::class_<PyBPlusTree>(m, "BPlusTree")
                   .def(py::init<>())
                   .def("__iter__", [](py::object obj) { return PyBPlusTreeIterator { obj.cast<PyBPlusTree const&>(), obj }; })
                   .def("insert", &PyBPlusTree::insert)
                   .def("find", &PyBPlusTree::find);

    auto generic_alias = py::module_::import("types").attr("GenericAlias");

    cls.def_static("__class_getitem__", [generic_alias, cls](py::args const& args) { return generic_alias(cls, args); });
}
