# SETUP

- git clone https://github.com/JHostalek/hostaja1_LE_Bully_Python-sockets_dist-computation.git && cd hostaja1_LE_Bully_Python-sockets_dist-computation && chmod +x setup.sh && chmod
  +x run.sh && ./setup.sh && ./run.sh

# ZADANI

- [ ] Programy musí podporovat interaktivní i dávkové řízení (např. přidání a odebrání procesu).
- [ ] Kromě správnosti algoritmu se zaměřte i na prezentaci výsledků. Cílem je aby bylo poznat co Váš program právě dělá.
- [ ] Srozumitelné výpisy logujte na konzoli i do souboru/ů. Výpisy budou opatřeny časovým razítkem logického času.
- [ ] Každý uzel bude mít jednoznačnou identifikaci. Doporučená je kombinace IP adresy a portu.
- [ ] Je doporučeno mít implementovanou možnost zpožďovat odeslání/příjem zprávy. Vhodné pro generování souběžných situací.
- [ ] Implementujte program detekující ukončení distribuovaného výpočtu. Výpočet může být spuštěn na kterémkoliv uzlu, jednotlivé uzly budou schopny práci předávat dál a také budou
  schopné si o práci zažádat.

# TODO

- [ ] Zpoždění odeslání/příjem zprávy
- [ ] Detekce ukončení distribuovaného výpočtu
- [ ] Logování do souboru
- [ ] Časové razítko logického času