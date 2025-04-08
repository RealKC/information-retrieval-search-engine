#include <pybind11/pybind11.h>

#include "stem.hpp"

#include <cctype>
#include <memory>
#include <string_view>

std::string stem_word(std::string_view word)
{
    using stemmer_ptr = std::unique_ptr<stemmer, decltype(&free_stemmer)>;

    std::string alpha;
    alpha.reserve(word.size());

    for (auto& ch : word) {
        if (std::isalpha(ch)) {
            alpha.push_back(std::tolower(ch));
        }
    }

    stemmer_ptr z(create_stemmer(), &free_stemmer);

    if (!z) {
        throw std::bad_alloc();
    }

    auto new_end = stem(z.get(), alpha.data(), alpha.size() - 1) + 1;

    return alpha.substr(0, new_end);
}

PYBIND11_MODULE(_core, m)
{
    m.doc() = "Porter stemmer";

    m.def("stem", &stem_word, R"pbdoc(
      Stems a given word, will ignore all non alphabetic characters, and return a lowercase string
    )pbdoc");
}
