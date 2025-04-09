#include <bplustree.hpp>
#include <iterator>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <tuple>

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
        auto eq = a.attr("__eq__");

        if (eq.is_none()) {
            return a.is(b);
        }

        return eq(b).cast<bool>();
    }
};

using PyBPlusTree = BPlusTree<py::object, py::object, BPlusTreeTraits<py::object, py::object>, 16>;

struct PyBPlusTreeIterator {
    // I'd love for this to be a member type of `BPlusTree` but I couldn't figure out how do that
    using RawIterator = decltype(std::declval<PyBPlusTree>().elements().begin());

    PyBPlusTreeIterator(PyBPlusTree const& tree, py::object ref)
        : generator { tree.elements() }
        , iterator { generator.begin() }
        , ref { ref }
    {
    }

    std::tuple<py::object, py::object> next()
    {
        if (iterator == std::default_sentinel) {
            throw py::stop_iteration();
        }

        auto next = *iterator;
        ++iterator;

        return next;
    }

    std::generator<PyBPlusTree::Entry> generator;
    RawIterator iterator;

    py::object ref; // keep the Python object alive
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
