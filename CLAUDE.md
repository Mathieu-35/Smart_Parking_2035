# CLAUDE.md — Smart Parking 2035 (à lire à chaque démarrage)

> Projet d'EXAMEN L2 (ESMIA) de RANDRIAMORIA Sahiniaina Mathieu.
> **AVANT TOUTE CHOSE : lis `docs/CONTEXTE_PROJET.md` (section 0 « À LIRE EN PREMIER »)**
> qui contient l'état d'avancement complet, comment lancer, ce qui reste à faire.
> Le skill `.claude/skills/ui-design/` (chargé automatiquement) porte les goûts de design.

## En une phrase
FastAPI + Jinja2 + PostgreSQL. **Admin = web** (gestion parkings/comptes/stats),
**Conducteur + Gardien = mobile PWA** (recherche/itinéraire/réservation/QR).
Algorithmes maison dans `app/graph/` (Dijkstra, Dijkstra+tas, A*, glouton, table de hachage).

## Règles fermes (consignes de l'étudiant)
1. **L2 débutant** : pas de syntaxe avancée ; **expliquer simplement AVANT de coder**.
2. **Commits** : toujours de NOUVEAUX commits, **jamais `--amend`/écraser**.
   Trailer : `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>`.
   (Messages multi-lignes : écrire un fichier puis `git commit -F fichier` ; le here-string
   inline `@'...'@` casse souvent dans ce PowerShell Windows.)
3. **Périmètre VERROUILLÉ** : graphe = 52 nœuds / 128 arêtes / 64 routes ; benchmarks
   (Tableaux 5/6) reproductibles. NE PAS toucher au graphe, aux coordonnées, ni aux modules d'algo.
4. **Mobile = vraie PWA** (manifest + service worker + installable + hors-ligne + splash) : OBLIGATOIRE.
5. **Monnaie = Ariary (Ar)**, sans centimes.
6. **Design** : sobre, **palette bleu/navy** (accent `#2F2FE4`, navy `#1A1953` pour
   sidebar/splash/barre de statut, appui `#162E93`), zéro emoji, aplats (pas de dégradé),
   cartes arrondies « bento », mobile = barre d'onglets en bas + splash SP. Bouton CTA
   « Ajouter » = macro `components/boutons.html` (classe `.btn-cta`, voile jaune `#ffd401`
   au survol). Détails : skill `ui-design`. (Anciennes couleurs `#2c5be0` puis indigo
   `#4B5694` remplacées le 2026-06-03 ; le rapport écrit peut encore citer `#2c5be0`.)

## Lancer le projet (Windows)
- Serveur : `venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001`
  (depuis la RACINE ; PAS de `--reload` ; relancer à la main après un changement Python).
- Créer un admin : `venv\Scripts\python.exe create_admin.py`.
- Tests : `venv\Scripts\python.exe -m pytest`.
- Après changement CSS/JS mobile : **bumper `NOM_CACHE` dans `app/static/sw.js`**.

## Test mobile (PWA) — tunnel FIXE ngrok
`https://acorn-popper-cavity.ngrok-free.dev` →
`& "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe" http --domain=acorn-popper-cavity.ngrok-free.dev 8001`

## Tâches en attente (au 2026-06-03)
Voir `docs/CONTEXTE_PROJET.md` §0.6. En résumé : filtre multi-critères (conducteur),
login web vs mobile, prix Ariary des parkings déjà créés, README + `/src` (prof a dit non
obligatoire), **push GitHub** (gh installé ; reste `gh auth login` puis `gh repo create
smart_parking_2035 --private --source=. --remote=origin --push`).
