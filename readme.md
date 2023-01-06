# SETUP

- HTTP
  SETUP<br>`git clone https://github.com/JHostalek/hostaja1_LE_Bully_Python-sockets_dist-computation.git && cd hostaja1_LE_Bully_Python-sockets_dist-computation && /bin/bash setup.sh`
- (if private repo) SSH
  SETUP<br>`git clone git@github.com:JHostalek/hostaja1_LE_Bully_Python-sockets_dist-computation.git && cd hostaja1_LE_Bully_Python-sockets_dist-computation && /bin/bash setup.sh`

# ZADÁNÍ

- [x] Programy musí podporovat interaktivní i dávkové řízení (např. přidání a odebrání procesu).
- [x] Kromě správnosti algoritmu se zaměřte i na prezentaci výsledků. Cílem je aby bylo poznat co Váš program právě dělá.
- [ ] Srozumitelné výpisy logujte na konzoli i do souboru/ů. Výpisy budou opatřeny časovým razítkem logického času.
- [x] Každý uzel bude mít jednoznačnou identifikaci. Doporučená je kombinace IP adresy a portu.
- [x] Je doporučeno mít implementovanou možnost zpožďovat odeslání/příjem zprávy. Vhodné pro generování souběžných situací.
- [x] Implementujte program detekující ukončení distribuovaného výpočtu. Výpočet může být spuštěn na kterémkoliv uzlu, jednotlivé uzly budou schopny práci předávat dál a také budou
  schopné si o práci zažádat.

# TODO

- [x] Zpoždění odeslání/příjem zprávy
- [x] Detekce ukončení distribuovaného výpočtu
- [ ] Logování do souboru
- [x] Časové razítko logického času
- [x] Ukladani progresu do DataStorage

