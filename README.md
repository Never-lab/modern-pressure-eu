# Modern Pressure EU / Pressione Moderna UE

Democracy 4 mod — hardcore **EU pressure pack**: climate, housing, migration, tech/AI, health.  
Mod per Democracy 4 — pack di pressione **UE** hardcore: clima, casa, migrazione, tech/IA, salute.

| | |
|---|---|
| **Author / Autore** | [JustNever_](https://steamcommunity.com/id/JustNever_/) |
| **Repo** | https://github.com/Never-lab/modern-pressure-eu |
| **Game** | [Democracy 4](https://store.steampowered.com/app/1410710/Democracy_4/) (Positech) |

---

## English

### What it is

Additive content pack (not a full economy overhaul):

- **32 policies** (English + Italian)
- **20 crisis events** with burst pacing and mutual exclusion
- Gated to **EU missions** via vanilla `_prereq_eu`
- Themes: climate & energy, housing & cost of living, migration, tech/AI, health

Design: high costs, painful side effects, slow inertia, calm stretches then crisis waves.

### Install (Windows)

1. Copy `ModernPressureEU/` to:  
   `%USERPROFILE%\Documents\My Games\Democracy4\mods\ModernPressureEU`
2. Or from this repo:  
   `powershell -NoProfile -File tools/install-to-documents.ps1`
3. Enable **Modern Pressure EU** in the Democracy 4 Mods panel.
4. Start an **EU** mission (Italy, France, Germany, Spain, Greece, Ireland, Poland, …).

### Steam Workshop

Upload from the in-game Mods UI. Use:

- Preview: `ModernPressureEU/preview.jpg`
- Full description: [`docs/workshop/STEAM_WORKSHOP_DESCRIPTION.txt`](docs/workshop/STEAM_WORKSHOP_DESCRIPTION.txt)
- Steps: [`docs/workshop/PUBLISH_STEPS.txt`](docs/workshop/PUBLISH_STEPS.txt)

### Develop / validate

```powershell
powershell -NoProfile -File tools/validate-mod.ps1
python tools/check-effect-targets.py
python tools/simulate-balance.py --runs 50 --seed 123
```

Specs & plans: `docs/superpowers/`

### Compatibility

- EU / Country Pack missions that set `_prereq_eu`
- Non-EU missions (USA, UK, …): mod policies/events should not appear
- Additive files — usually fine with other content packs; heavy overhauls may conflict

### Feedback

Bugs and balance reports: [GitHub Issues](https://github.com/Never-lab/modern-pressure-eu/issues)

---

## Italiano

### Cos’è

Pack di contenuti aggiuntivi (non un overhaul economico completo):

- **32 politiche** (italiano + inglese)
- **20 eventi di crisi** con ritmo a ondate ed esclusione reciproca
- Attivo sulle **missioni UE** tramite `_prereq_eu` vanilla
- Temi: clima ed energia, casa e costo della vita, migrazione, tech/IA, salute

Design: costi alti, effetti collaterali dolorosi, inerzia lenta, periodi calmi poi ondate di crisi.

### Installazione (Windows)

1. Copia `ModernPressureEU/` in:  
   `%USERPROFILE%\Documents\My Games\Democracy4\mods\ModernPressureEU`
2. Oppure dal repo:  
   `powershell -NoProfile -File tools/install-to-documents.ps1`
3. Abilita **Modern Pressure EU** nel pannello Mod di Democracy 4.
4. Avvia una missione **UE** (Italia, Francia, Germania, Spagna, Grecia, Irlanda, Polonia, …).

### Steam Workshop

Carica dall’interfaccia Mod del gioco. Usa:

- Anteprima: `ModernPressureEU/preview.jpg`
- Descrizione completa: [`docs/workshop/STEAM_WORKSHOP_DESCRIPTION.txt`](docs/workshop/STEAM_WORKSHOP_DESCRIPTION.txt)
- Passi: [`docs/workshop/PUBLISH_STEPS.txt`](docs/workshop/PUBLISH_STEPS.txt)

### Sviluppo / validazione

```powershell
powershell -NoProfile -File tools/validate-mod.ps1
python tools/check-effect-targets.py
python tools/simulate-balance.py --runs 50 --seed 123
```

Spec e piani: `docs/superpowers/`

### Compatibilità

- Missioni UE / Country Pack con `_prereq_eu`
- Missioni non-UE (USA, UK, …): le policy/eventi della mod non dovrebbero comparire
- File additivi — di solito ok con altri pack; overhaul pesanti possono confliggere

### Feedback

Bug e bilanciamento: [GitHub Issues](https://github.com/Never-lab/modern-pressure-eu/issues)

---

## License / Licenza

Mod content in this repository: see repo license if present; Democracy 4 belongs to Positech Games.  
Contenuti della mod in questo repository: vedi la license del repo se presente; Democracy 4 è di Positech Games.
