#include <bplustree.hpp>
#include <filesystem>
#include <optional>
#include <print>
#include <string>
#include <string_view>

namespace fs = std::filesystem;

struct PathInfo {
    fs::path full_path;
    std::string basename;
};

template<>
class BPlusTreeTraits<fs::path, PathInfo> {
public:
    using Key = fs::path;
    using FindBy = std::string_view;
    using Value = PathInfo;

    // Taken from lab :)
    static std::size_t hash(FindBy s)
    {
        std::size_t hcode = 0;
        std::size_t R = 31;
        std::size_t N = 7727;

        for (char ch : s) {
            hcode = (R * hcode + ch) % N;
        }

        return hcode;
    }
};

int main(int argc, char* argv[])
{
    if (argc != 3) {
        std::println("Usage: program <path> <needle>");
        return 1;
    }

    auto to_explore = fs::canonical(fs::path { std::string { argv[1] } });
    auto needle = std::string { argv[2] };

    std::println("To explore: {}", to_explore.c_str());

    auto iterator = fs::recursive_directory_iterator { to_explore };
    BPlusTree<fs::path, PathInfo> tree;

    for (auto& child : iterator) {
        std::println("Child: {}", child.path().c_str());
        tree.insert(child.path(), PathInfo { child.path(), child.path().filename().string() });
    }

    std::println("finding now...");

    auto path_info = tree.find(needle);
    if (path_info.has_value()) {
        std::println("{}: {}", path_info->basename, path_info->full_path.c_str());
    } else {
        std::println("Could not find {}", needle);
    }

    return 0;
}
