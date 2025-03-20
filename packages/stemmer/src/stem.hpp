#pragma once

extern "C" {

struct stemmer;

struct stemmer* create_stemmer(void);
void free_stemmer(struct stemmer* z);

int stem(struct stemmer* z, char* b, int k);
}
