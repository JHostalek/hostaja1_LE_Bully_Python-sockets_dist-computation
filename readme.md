# SETUP

`git clone https://github.com/JHostalek/hostaja1_LE_Bully_Python-sockets_dist-computation.git && cd hostaja1_LE_Bully_Python-sockets_dist-computation && /bin/bash setup.sh`

# RUN

Start the data center:<br>
`/bin/bash runDataCenterNode.sh` nebo `python3 MainDataCenter`<br>
Start the node:<br>
`/bin/bash runNode.sh` - default data ceter ip 115<br>
`python3 MainNode.py --data_center_ip 192.168.56.XXX`

# HELP

```
usage: MainNode.py [-h] [--real_audio REAL_AUDIO] [--tasks TASKS]
                   [--data_center_ip DATA_CENTER_IP]
                   [--message_delay MESSAGE_DELAY]
                   [--hold_each_message HOLD_EACH_MESSAGE]
                   [--bully_timeout BULLY_TIMEOUT]

optional arguments:
  -h, --help            show this help message and exit
  --real_audio REAL_AUDIO
                        Use real audio
  --tasks TASKS         How many tasks to generate
  --data_center_ip DATA_CENTER_IP
                        IP of the data center
  --message_delay MESSAGE_DELAY
                        Delay between all messages
  --hold_each_message HOLD_EACH_MESSAGE
                        Hold on to each message until key is pressed. Cancel
                        by CTRL+E
  --bully_timeout BULLY_TIMEOUT
                        Time limit for the bully algorithm. Node claims to be
                        the coordinator (leader) if neighbors with higher id
                        do not respond until this timeout expires.
```

# ZADÁNÍ

- [x] Programy musí podporovat interaktivní i dávkové řízení (např. přidání a odebrání procesu).
- [x] Kromě správnosti algoritmu se zaměřte i na prezentaci výsledků. Cílem je aby bylo poznat co Váš program právě dělá.
- [x] Srozumitelné výpisy logujte na konzoli i do souboru/ů. Výpisy budou opatřeny časovým razítkem logického času.
- [x] Každý uzel bude mít jednoznačnou identifikaci. Doporučená je kombinace IP adresy a portu.
- [x] Je doporučeno mít implementovanou možnost zpožďovat odeslání/příjem zprávy. Vhodné pro generování souběžných situací.
- [x] Implementujte program detekující ukončení distribuovaného výpočtu. Výpočet může být spuštěn na kterémkoliv uzlu, jednotlivé uzly budou schopny práci předávat dál a také budou
  schopné si o práci zažádat.
