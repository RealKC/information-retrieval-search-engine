#include <bitset>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <print>
#include <string>

template<typename K>
class HashTable {
public:
    using Hasher = std::size_t (*)(K const&);

    HashTable(Hasher hash)
        : m_hash(hash)
        , m_collisions(0)
    {
        m_nodes = new Node[MAX_CAPACITY];
    }

    void insert(K const& k)
    {
        auto hash = m_hash(k);
        auto index = hash % MAX_CAPACITY;

        if (m_occupations[index]) {
            if (m_nodes[index].value == k) {
                return;
            }

            m_collisions++;
            auto* new_node = new Node(k, nullptr);
            auto* p = &m_nodes[index];

            while (p->next) {
                p = p->next;
            }

            p->next = new_node;
        } else {
            m_nodes[index].value = k;
            m_nodes[index].next = nullptr;
            m_occupations[index] = true;
        }
    }

    bool has(K const& k)
    {
        auto hash = m_hash(k);
        auto index = hash % MAX_CAPACITY;

        if (!m_occupations[index]) {
            return false;
        }

        for (auto p = &m_nodes[index]; p; p = p->next) {
            if (p->value == k) {
                return true;
            }
        }

        return false;
    }

    void dump_stats()
    {
        std::println("collisions: {}", m_collisions);
        std::println("nodes occupied: {}", m_occupations.count());
    }

private:
    // static constexpr std::size_t MAX_CAPACITY = 1223;
    static constexpr std::size_t MAX_CAPACITY = 11;

    struct Node {
        K value;
        Node* next;
    };

    Hasher m_hash;
    Node* m_nodes;
    std::bitset<MAX_CAPACITY> m_occupations;

    std::size_t m_collisions;
};

// Taken from <https://stackoverflow.com/a/12996028>
std::size_t hash_int(int const& x)
{
    std::size_t xu = x;
    xu = ((xu >> 16) ^ xu) * 0x45d9f3b;
    xu = ((xu >> 16) ^ xu) * 0x45d9f3b;
    xu = (xu >> 16) ^ xu;
    return xu;
}

// Taken from lab :)
std::size_t hash_str(std::string const& s)
{
    std::size_t hcode = 0;
    std::size_t R = 31;
    std::size_t N = 7727;

    for (char ch : s) {
        hcode = (R * hcode + ch) % N;
    }

    return hcode;
}

static constexpr std::size_t ELEMENT_COUNT = 10'000;

template<typename Callback>
void benchmark(char const* description, Callback callback)
{
    using namespace std::chrono;

    auto start = high_resolution_clock::now();
    callback();
    auto end = high_resolution_clock::now();

    auto duration = end - start;

    auto us = duration_cast<microseconds>(duration);

    std::println("{} -> duration = {} µs ({} ms)", description, us.count(), us.count() / 1000);
}

void int_tests()
{

    HashTable<int> table(hash_int);
    int needle = 2123;
    table.insert(needle);

    benchmark("HashTable<int>: before inserting 10k", [&]() {
        table.has(needle);
    });

    int last;
    for (std::size_t i = 0; i < ELEMENT_COUNT; ++i) {
        table.insert(last = std::rand());
    }

    benchmark("HashTable<int>: after inserting 10k", [&]() {
        table.has(last);
    });

    std::println("HashTable<int> stats: ");
    table.dump_stats();
}

std::string random_string()
{
    static constexpr char charset[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";

    std::size_t length = std::rand() % 20 + 10;

    std::string result;
    result.resize(length);

    for (std::size_t i = 0; i < length; ++i) {
        result[i] = charset[std::rand() % std::size(charset)];
    }

    return result;
}

void string_tests()
{
    using namespace std::string_literals;

    HashTable<std::string> table(hash_str);
    auto needle = "hello world"s;
    table.insert(needle);

    benchmark("HashTable<string> before inserting 10k", [&]() {
        table.has(needle);
    });

    std::string last;
    for (std::size_t i = 0; i < ELEMENT_COUNT; ++i) {
        table.insert(last = random_string());
    }

    benchmark("HashTable<string> before inserting 10k", [&]() {
        table.has(last);
    });

    std::println("HashTable<string> stats: ");
    table.dump_stats();
}

int main()
{
    int_tests();
    string_tests();

    return 0;
}
