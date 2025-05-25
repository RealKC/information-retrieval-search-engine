## robotstxt

In principiu acest pachet poate fi tratat ca o librarie externa.

Am vrut un parser de robots.txt caruia ii pot serializa starea interna, pentru a o stoca intr-o baza de date, si dupa, modulele care au nevoie sa inspecteze robots.txt a unui domeniu, sa-l poata lua din baza de date.

P.S.: Stiu ca Rust nu era printre limbajele care s-au mentionat ca permise pentru proiect, dar nu am gasit nimic care sa-mi placa in Python, si am considerat ca asta nu e un component critic sau cu destula logica in el cat sa conteze limbajul cat timp puteam sa ii fac bind usor in Python.
