#include <pybind11/pybind11.h>

#include "stem.hpp"

#include <cctype>
#include <memory>
#include <string_view>

namespace py = pybind11;

std::string stem_word(std::string_view word)
{
    std::string alpha;
    alpha.reserve(word.size());

    for (auto& ch : word) {
        if (std::isalpha(ch)) {
            alpha.push_back(std::tolower(ch));
        }
    }

    auto* z = create_stemmer();
    auto new_end = stem(z, alpha.data(), alpha.size() - 1) + 1;

    return alpha.substr(0, new_end);
}

PYBIND11_MODULE(_core, m)
{
    m.doc() = "Porter stemmer";

    m.def("stem", &stem_word, R"pbdoc(
      Stems a given word, will ignore all non alphabetic characters, and return a lowercase string
    )pbdoc");
}
