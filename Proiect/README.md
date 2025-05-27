## Proiect RI

![diagrama de servicii](./Service%20Diagram.drawio.png)

Notițe despre proiect:

- crawler-ul e paralelizat prin intermediul docker compose, care pornește mai multe instanțe ale containerului în același timp
- la nivel de indexer, construirea indecșilor direcți și celui indirect este realizată în thread-uri separate față de cel care monitorizează că o pagină nouă a fost accesată, ceea ce în momente de trafic intens ar duce la o procesare paralelă (totuși limitată la numărul de nuclee pe care rulează serviciul)
- proiectul nu prea respectă bunele practici de securitate: secretele (credențialele Mongo, secretul CSRF pentru Flask-WTF) sunt aruncate în repo, serverul de flask rulează pe dev server...
