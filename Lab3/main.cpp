#include <filesystem>
#include <optional>
#include <print>
#include <string>
#include <string_view>

namespace fs = std::filesystem;

using usize = std::size_t;
using std::println;

struct PathInfo {
    fs::path full_path;
    std::string basename;
};

class BTree {
    // Implementation based on https://www.geeksforgeeks.org/implementation-of-b-plus-tree-in-c/
public:
    BTree()
        : m_root { create_node(true) }
    {
        m_root->is_leaf = true;
    }

    void insert(fs::path const& path, PathInfo info)
    {
        auto key = hash_str(info.basename);
        auto* root = m_root;
        if (root->n == 2 * BRANCHING_FACTOR - 1) {
            auto* new_root = create_node(false);
            new_root->children[0] = root;
            split_node(new_root, 0, root);
            insert_non_full(new_root, key, info);
            m_root = new_root;
        } else {
            insert_non_full(root, key, info);
        }
    }

    std::optional<PathInfo> find(std::string_view basename)
    {
        auto key = hash_str(basename);
        return search_recursive(m_root, key);
    }

private:
    static constexpr usize BRANCHING_FACTOR = 3;

    struct Node {
        Node* children[2 * BRANCHING_FACTOR];
        usize keys[2 * BRANCHING_FACTOR - 1];
        usize n;

        std::optional<PathInfo> data[2 * BRANCHING_FACTOR - 1];

        bool is_leaf;
    };

    Node* m_root;

    Node* create_node(bool is_leaf)
    {
        auto* node = new Node;
        node->is_leaf = is_leaf;
        for (int i = 0; i < std::size(node->children); ++i) {
            node->children[i] = new Node;
        }
        node->n = 0;
        return node;
    }

    void insert_non_full(Node* node, usize key, PathInfo value)
    {
        int i = node->n - 1;

        if (node->is_leaf) {
            while (i >= 0 && node->keys[i] > key) {
                node->keys[i + 1] = node->keys[i];
                if (node->data[i].has_value()) {
                    node->data[i + 1] = node->data[i];
                }
                i--;
            }

            node->keys[i + 1] = key;
            node->data[i + 1] = value;
            node->n++;
        } else {
            while (i >= 0 && node->keys[i] > key) {
                i--;
            }
            i++;

            if (node->children[i]->n == 2 * BRANCHING_FACTOR - 1) {
                split_node(node, i, node->children[i]);
                if (node->keys[i] < key) {
                    i++;
                }
            }
            insert_non_full(node->children[i], key, value);
        }
    }

    void split_node(Node* parent, int i, Node* child)
    {
        auto* new_child = create_node(child->is_leaf);
        new_child->n = BRANCHING_FACTOR - 1;

        for (int j = 0; j < BRANCHING_FACTOR - 1; ++j) {
            new_child->keys[j] = child->keys[j + BRANCHING_FACTOR];
            if (new_child->is_leaf) {
                new_child->data[j] = child->data[j + BRANCHING_FACTOR];
            }
        }

        if (!child->is_leaf) {
            for (int j = 0; j < BRANCHING_FACTOR; ++j) {
                new_child->children[j] = child->children[j + BRANCHING_FACTOR];
            }
        }

        child->n = BRANCHING_FACTOR - 1;

        for (int j = parent->n; j >= i + 1; --j) {
            parent->children[j + 1] = parent->children[j];
        }
        parent->children[i + 1] = new_child;

        for (int j = parent->n - 1; j >= i; --j) {
            parent->keys[j + 1] = parent->keys[j];
        }
        parent->keys[i] = child->keys[BRANCHING_FACTOR - 1];
        parent->n++;
    }

    std::optional<PathInfo> search_recursive(Node* node, usize key)
    {
        int i = 0;

        while (i < node->n && key > node->keys[i]) {
            i++;
        }

        if (i < node->n && key == node->keys[i]) {
            return node->data[i];
        }

        if (node->is_leaf) {
            return std::nullopt;
        }

        return search_recursive(node->children[i], key);
    }

    // Taken from lab :)
    usize hash_str(std::string_view s)
    {
        usize hcode = 0;
        usize R = 31;
        usize N = 7727;

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

    println("To explore: {}", to_explore.c_str());

    auto iterator = fs::recursive_directory_iterator { to_explore };
    BTree tree;

    for (auto& child : iterator) {
        std::println("Child: {}", child.path().c_str());
        tree.insert(child.path(), PathInfo { child.path(), child.path().filename().string() });
    }

    println("finding now...");

    auto path_info = tree.find(needle);
    if (path_info.has_value()) {
        println("{}: {}", path_info->basename, path_info->full_path.c_str());
    } else {
        println("Could not find {}", needle);
    }

    return 0;
}
