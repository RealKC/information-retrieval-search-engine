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
public:
    BTree()
        : m_root {}
    {
    }

    void insert(fs::path const& path)
    {

        auto basename = path.stem().string();
        auto key = hash_str(basename.c_str());

        println("insert: {} -> {}", basename, key);

        fs::path p = path;
        auto path_info = new PathInfo { std::move(p), std::move(basename) };
        p = fs::path {};

        if (!m_root) {
            m_root = new Node;
            m_root->key_count = 1;
            m_root->keys[0] = key;
            m_root->leaf_data = new LeafData { path_info, nullptr };
        } else {
            Node* cursor = m_root;
            Node* parent = nullptr;

            while (!cursor->is_leaf()) {
                parent = cursor;

                for (usize i = 0; i < cursor->key_count; ++i) {
                    if (key < cursor->keys[i]) {
                        cursor = cursor->children[i];
                        break;
                    }

                    if (i == cursor->key_count - 1) {
                        cursor = cursor->children[i + 1];
                        break;
                    }
                }
            }

            if (cursor->key_count < MAX) {
                usize i = 0;
                while (key > cursor->keys[i] && i < cursor->key_count)
                    i++;
                for (usize j = cursor->key_count; j > i; j--) {
                    cursor->keys[j] = cursor->keys[j - 1];
                }
                for (usize j = cursor->key_count + 1; j > i + 1; j--) {
                    cursor->children[j] = cursor->children[j - 1];
                }
                cursor->keys[i] = key;
                cursor->key_count++;
                cursor->children[cursor->key_count] = cursor->children[cursor->key_count - 1];
                cursor->children[cursor->key_count - 1] = nullptr;
            } else {
                Node* new_leaf = new Node;
                usize virtual_node[MAX + 1];
                for (usize i = 0; i < MAX; i++) {
                    virtual_node[i] = cursor->keys[i];
                }
                usize i = 0, j;
                while (key > virtual_node[i] && i < MAX)
                    i++;
                for (usize j = MAX + 1; j > i; j--) {
                    virtual_node[j] = virtual_node[j - 1];
                }
                virtual_node[i] = key;
                new_leaf->leaf_data = new LeafData { path_info, nullptr };
                cursor->key_count = (MAX + 1) / 2;
                new_leaf->key_count = MAX + 1 - (MAX + 1) / 2;
                cursor->children[cursor->key_count] = new_leaf;
                new_leaf->children[new_leaf->key_count] = cursor->children[MAX];
                cursor->children[MAX] = NULL;
                for (i = 0; i < cursor->key_count; i++) {
                    cursor->keys[i] = virtual_node[i];
                }
                for (i = 0, j = cursor->key_count; i < new_leaf->key_count; i++, j++) {
                    new_leaf->keys[i] = virtual_node[j];
                }
                if (cursor == m_root) {
                    Node* new_root = new Node;
                    new_root->keys[0] = new_leaf->keys[0];
                    new_root->children[0] = cursor;
                    new_root->children[1] = new_leaf;
                    new_root->key_count = 1;
                    new_root->leaf_data = new LeafData { path_info, nullptr };
                    m_root = new_root;
                } else {
                    insert_internal(new_leaf->keys[0], path_info, parent, new_leaf);
                }
            }
        }
    }

    PathInfo* find(std::string_view basename)
    {
        auto key = hash_str(basename);
        println("find: {} -> {}", basename, key);

        if (!m_root) {
            return nullptr;
        } else {
            Node* cursor = m_root;
            while (!cursor->is_leaf()) {
                for (usize i = 0; i < cursor->key_count; i++) {
                    if (key < cursor->keys[i]) {
                        cursor = cursor->children[i];
                        break;
                    }
                    if (i == cursor->key_count - 1) {
                        cursor = cursor->children[i + 1];
                        break;
                    }
                }
            }
            for (usize i = 0; i < cursor->key_count; i++) {
                if (cursor->keys[i] == key) {
                    return cursor->leaf_data->path_info;
                }
            }
        }

        return nullptr;
    }

private:
    static constexpr usize MAX = 3;

    struct LeafData {
        PathInfo* path_info;
        LeafData* next;
    };

    struct Node {
        Node* children[MAX + 1];
        usize keys[MAX];
        usize key_count;

        // Only present for leaf nodes
        LeafData* leaf_data;

        [[nodiscard]] bool is_leaf() noexcept
        {
            return leaf_data != nullptr;
        }
    };

    Node* m_root;

    Node* search_tree(Node* node, usize key, std::string_view basename)
    {
        if (node->is_leaf()) {
            return node;
        }

        for (usize i = 0; i < node->key_count - 1; ++i) {
            if (key < node->keys[i]) {
                return search_tree(node->children[i], key, basename);
            }

            if (key == node->keys[i] && key < node->keys[key + 1]) {
                return search_tree(node->children[i + 1], key, basename);
            }
        }

        return search_tree(node->children[node->key_count - 1], key, basename);
    }

    void insert_internal(usize key, PathInfo* path_info, Node* cursor, Node* child)
    {
        if (cursor->key_count < MAX) {
            usize i = 0;
            while (key > cursor->keys[i] && i < cursor->key_count)
                i++;
            for (usize j = cursor->key_count; j > i; j--) {
                cursor->keys[j] = cursor->keys[j - 1];
            }
            for (usize j = cursor->key_count + 1; j > i + 1; j--) {
                cursor->children[j] = cursor->children[j - 1];
            }
            cursor->keys[i] = key;
            cursor->key_count++;
            cursor->children[i + 1] = child;
        } else {
            Node* new_internal = new Node;
            usize virtual_key[MAX + 1];
            Node* virtual_ptr[MAX + 2];
            for (usize i = 0; i < MAX; i++) {
                virtual_key[i] = cursor->keys[i];
            }
            for (usize i = 0; i < MAX + 1; i++) {
                virtual_ptr[i] = cursor->children[i];
            }
            usize i = 0, j;
            while (key > virtual_key[i] && i < MAX)
                i++;
            for (usize j = MAX + 1; j > i; j--) {
                virtual_key[j] = virtual_key[j - 1];
            }
            virtual_key[i] = key;
            for (usize j = MAX + 2; j > i + 1; j--) {
                virtual_ptr[j] = virtual_ptr[j - 1];
            }
            virtual_ptr[i + 1] = child;
            cursor->key_count = (MAX + 1) / 2;
            new_internal->key_count = MAX - (MAX + 1) / 2;
            for (i = 0, j = cursor->key_count + 1; i < new_internal->key_count; i++, j++) {
                new_internal->keys[i] = virtual_key[j];
            }
            for (i = 0, j = cursor->key_count + 1; i < new_internal->key_count + 1; i++, j++) {
                new_internal->children[i] = virtual_ptr[j];
            }
            if (cursor == m_root) {
                Node* new_root = new Node;
                new_root->keys[0] = virtual_key[cursor->key_count];
                new_root->children[0] = cursor;
                new_root->children[1] = new_internal;
                new_root->key_count = 1;
                new_root->leaf_data = nullptr;
                m_root = new_root;
            } else {
                insert_internal(cursor->keys[cursor->key_count], path_info, find_parent(m_root, cursor), new_internal);
            }
        }
    }

    Node* find_parent(Node* cursor, Node* child)
    {
        Node* parent = nullptr;
        if (cursor->is_leaf() || (cursor->children[0])->is_leaf()) {
            return nullptr;
        }

        for (usize i = 0; i < cursor->key_count + 1; i++) {
            if (cursor->children[i] == child) {
                parent = cursor;
                return parent;
            } else {
                parent = find_parent(cursor->children[i], child);
                if (parent != nullptr)
                    return parent;
            }
        }
        return parent;
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
        // std::println("Child: {}", child.path().c_str());
        tree.insert(child.path());
    }

    println("finding now...");

    auto path_info = tree.find(needle);
    println("{}: {}", path_info->basename, path_info->full_path.c_str());

    return 0;
}
