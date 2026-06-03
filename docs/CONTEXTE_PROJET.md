# Contexte du projet — Smart Parking 2035

> Fichier mémoire : sert à retrouver tout le contexte du projet entre deux sessions
> (et entre deux comptes Claude Code). **Si tu reprends le projet : lis la section 0.**
> Dernière mise à jour : 2026-06-03.

---

## 0. À LIRE EN PREMIER — REPRISE RAPIDE (pour un nouveau compte/session)

> Ce projet a déjà été développé en grande partie. Un nouvel assistant doit lire
> CETTE section avant tout, puis le skill design `.claude/skills/ui-design/`.

### 0.1 En une phrase
Smart Parking 2035 : appli FastAPI + Jinja2 + PostgreSQL. **Admin = web** (gestion
parkings/comptes/stats), **Conducteur + Gardien = mobile PWA** (recherche/itinéraire/
réservation/QR). Algorithmes maison dans `app/graph/` (Dijkstra, Dijkstra+tas, A*,
glouton, table de hachage).

### 0.2 Comment lancer (Windows)
- Python du venv : `venv\Scripts\python.exe` (contient fastapi, sqlalchemy, bcrypt, qrcode, PIL, pytest).
- Lancer le serveur : `venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001`
  (⚠️ lancer depuis la RACINE du projet ; PAS de `--reload` sous Windows, il rate des fichiers — relancer à la main après un changement Python ; les templates .html se rechargent seuls).
- Créer un admin : `venv\Scripts\python.exe create_admin.py` (interactif). Admin existant : `admin@smartparking.mg` (mot de passe non stocké).
- Tests : `venv\Scripts\python.exe -m pytest` (14 tests verts). Benchmarks : `benchmarks/bench_*.py`.
- BD : PostgreSQL via `.env` (voir `.env.example`).

### 0.3 Tester sur téléphone (HTTPS obligatoire pour la PWA)
- **Tunnel FIXE ngrok** (domaine réservé, gratuit) : `https://acorn-popper-cavity.ngrok-free.dev`
- Relancer le tunnel (le PC doit faire tourner le serveur 8001) :
  `& "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe" http --domain=acorn-popper-cavity.ngrok-free.dev 8001`
  (ngrok gratuit affiche une page « Visit Site » au 1er accès → un clic, normal).
- Après tout changement de CSS/JS mobile : **bumper `NOM_CACHE` dans `app/static/sw.js`** (vN → vN+1) sinon le téléphone garde l'ancien.

### 0.4 RÈGLES À RESPECTER (consignes de l'étudiant, fermes)
1. **L2 débutant** : pas de syntaxe avancée/compliquée ; **expliquer simplement AVANT de coder**.
2. **Commits** : faire des **NOUVEAUX** commits, **jamais** `--amend`/écraser (pour voir les diffs).
   Trailer utilisé : `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>`.
   (Astuce : pour les messages multi-lignes, écrire un fichier puis `git commit -F fichier` ;
   le here-string inline `@'...'@` casse souvent dans ce PowerShell.)
3. **Périmètre VERROUILLÉ** : graphe = **52 nœuds / 128 arêtes orientées / 64 routes**, et les
   **Tableaux 5/6** (benchmarks) doivent rester reproductibles. NE PAS changer le graphe, les
   coordonnées, ni les modules d'algo. (Les distances/A* dépendent des coords.)
4. **Mobile = VRAIE app** : la PWA (manifest + service worker + installable + hors-ligne + splash)
   est OBLIGATOIRE (« juste responsive ne compte pas » — dit le prof).
5. **Monnaie = Ariary (Ar)**, pas d'euro, sans centimes.
6. **Design** : voir le skill `.claude/skills/ui-design/` (sobre, bleu `#2c5be0`, zéro emoji,
   pas de dégradé criard, cartes arrondies « bento », mobile = barre d'onglets en bas + splash SP).

### 0.5 CE QUI EST DÉJÀ FAIT (au 2026-06-03)
- **Sprints 1→11** terminés (voir §6 et §10) : CRUD utilisateurs/parkings, algos + 3 structures,
  benchmarks, ≥5 tests, QR entrée/sortie + montant, carte Leaflet, PWA, tableau de bord admin.
- **Refonte design + features hors-sprint** (toutes commitées) :
  - Mobile : design refait (barre d'onglets en bas, cartes arrondies), **splash SP** au lancement
    (1×/ouverture, y compris sur login en contexte mobile), grande **carte d'itinéraire plein écran
    + fiche du bas** (bottom sheet), couleur bleu `#2c5be0`.
  - Login/Signup : épurés, **logo centré**, **fond photo parking + carte glassmorphism**.
  - Admin web : **tableau de bord « bento »** + **donut taux d'occupation** (CSS pur), **sidebar
    bleue dégradée**, **déconnexion + profil + user EN BAS de la sidebar**, cartes arrondies partout,
    pages « Mon profil » et « formulaire utilisateur » **centrées**.
  - Sécurité rôles : modèle **« admins égaux »** (un admin crée/gère gardiens ET admins ; garde-fous :
    pas le dernier admin actif, pas soi-même ; email/mdp d'un autre admin non modifiables → via Mon profil).
    Conducteurs s'inscrivent seuls.
  - **Self-service « Mon profil »** (mdp actuel requis seulement si on change email/mdp).
  - **Prix parkings éditables** (hybride semaine/week-end, déplié sur 7 jours) + horaires ; **devise Ariary**.
  - **Pagination** « Précédent/Suivant » sur la liste Utilisateurs (10/page).
  - **Confirmation avant déconnexion** (web + mobile).
  - **Tableau de bord** : heures affichées à l'heure de **Madagascar (UTC+3)**.

### 0.6 CE QUI RESTE (à décider avec l'étudiant — il diffère souvent « pour ce soir/plus tard »)
- **Filtre multi-critères** côté conducteur (places min / prix max / ouvert maintenant / tri) — PROPOSÉ, pas fait.
- **Login : deux designs distincts web vs mobile** (détection appareil) — à trancher.
- **Prix des parkings DÉJÀ créés** : encore en ancienne valeur (ex. 2.0) → à re-saisir en Ariary.
- **Sprint 12 : README + réorg `/src`** — le prof a dit **non obligatoire** → en pause. (`/docs` et `/data` existent déjà.)
- Formulaire **Parkings** à centrer (cohérence, optionnel).
- **Pousser sur GitHub** : dépôt local prêt, `gh` (GitHub CLI) installé, `.env` retiré du
  suivi. Reste à faire `gh auth login` (côté étudiant, via navigateur) puis
  `gh repo create smart_parking_2035 --private --source=. --remote=origin --push`. PAS encore de remote.

### 0.7 Repères fichiers
`app/main.py` (routes racine + PWA + API reco/carte), `app/routes/` (auth, utilisateur, parking,
reservation, dashboard), `app/controllers/`, `app/graph/` (algos+structures), `app/templates/`
(base.html=layout admin ; conducteur/ gardien/ = mobile ; auth/ ; parkings/ ; utilisateurs/ ;
dashboard.html), `app/static/css/style.css` (admin) + `mobile.css` (mobile) + `sw.js` + `manifest.json`,
`data/` (graphe), `benchmarks/`, `tests/`. ⚠️ Le rapport `.docx` et le cahier des charges sont
**hors dépôt** (verrouillés, chez l'étudiant).

---

## 1. Identité du projet

- **Titre** : Smart Parking 2035 — Système de recommandation de stationnement basé sur des algorithmes de recherche de chemin.
- **Étudiant** : RANDRIAMORIA Sahiniaina Mathieu (NIE : SE20240206)
- **Cadre** : Projet transversal L2 — ESMIA INNOVATION, thème imposé « Imaginer le Numérique Malagasy de 2035 ».
- **Nature** : EXAMEN. L'étudiant est en L2 et débutant en programmation / structures de données / algorithmes avancés.
  → Toujours **expliquer simplement AVANT de coder**.

## 2. Problème traité

À Antananarivo, chercher une place de parking fait perdre du temps et crée des embouteillages.
Le système recommande au conducteur le parking le plus optimal (proche + places dispo) et calcule l'itinéraire.

**Question centrale** : comment recommander le parking le plus optimal pour un conducteur afin de réduire le temps de recherche ?

## 3. Acteurs et plateformes (2 livrables d'interface)

- **Administrateur** → interface **Web** (gestion parkings, comptes gardiens, statistiques, revenus).
- **Gardien** → interface **Mobile (PWA)** (scan QR, validation entrée/sortie, confirmation paiement espèce).
- **Conducteur** → interface **Mobile (PWA)** (recherche parking, recommandation, itinéraire, réservation, QR).

> Décision : Web pour l'admin, PWA mobile pour gardien + conducteur. La couche PWA (manifest + service worker + icônes + splash) est FAITE (cf. §0.5).
>
> ⚠️ IMPORTANT (consigne prof) : un livrable « juste responsive » NE COMPTE PAS. La partie mobile
> doit être une VRAIE app mobile. Choix retenu = PWA (alternative écartée = React Native).
> => La PWA (manifest + service worker + installable + hors-ligne) est OBLIGATOIRE, pas un bonus.

## 4. Stack technique réelle

- Backend : **FastAPI** + **Jinja2** (HTML rendu serveur)
- BDD : **PostgreSQL** via SQLAlchemy (psycopg)
- Auth : sessions + bcrypt, redirection par rôle
- Algorithmes maison : dossier `app/graph/`

## 5. Exigences du sujet ESMIA (ce qui donne les points)

Grille de notation (/100) :

| Critère | Points |
|---|---|
| Architecture + UML + BD + déploiement | 20 |
| Algorithmes avancés | 20 |
| Structures de données avancées | 15 |
| Optimisation mesurée (baseline vs optimisé) | 15 |
| Pertinence du problème "2035" | 15 |
| Qualité code + tests + doc | 10 |
| Pitch + démo | 5 |

**⚠️ ~60 points dépendent de DOCUMENTS/JUSTIFICATIONS, pas du code.**

Exigences obligatoires :
- **≥ 2 familles d'algorithmes** avancés (implémentés à la main, pas de boîte noire).
- **≥ 3 structures de données** avancées, justifiées.
- **Optimisation mesurée** : problème formalisé + baseline + version optimisée + mesures (temps/mémoire) + tableau.
- **≥ 3 contraintes "2035"** déclarées ET traduites en choix d'archi/algo.
- **≥ 5 tests unitaires** sur les modules algorithmiques.
- Dossiers : cahier des charges, dossier d'architecture (UML use-case + classes + séquence + schéma BD + déploiement), dossier algorithmique (plan imposé en 7 points).
- Dépôt Git : `/docs`, `/src`, `/data`, `README.md`.

**Critères de DISQUALIFICATION à éviter** : pas d'algos avancés / pas de structures avancées / proto non exécutable / dossier algo vide ou sans baseline-mesures / plagiat.

## 6. État du projet (au 2026-05-30)

### Fait ✅
- Sprint 1-2 : gestion utilisateurs + parkings (admin web), sécurisation des rôles.
- Sprint 3 : graphe routier, Dijkstra simple, Dijkstra + tas binaire, A*, glouton, recommandation, endpoint `/api/recommandation`.
- Modèles BD : Utilisateur, Role, Parking, HistoriquePlaces, Reservation.

### Familles d'algos couvertes
- Graphes/Réseaux : Dijkstra, Dijkstra+tas, A* ✅
- Optimisation : Glouton ✅
→ 2 familles : conforme.

### Structures de données
- Tas binaire ✅
- Graphe (listes d'adjacence) ✅
- **3ᵉ structure MANQUANTE** ❌ (piste : table de hachage avec collisions, ou Trie pour recherche par nom de parking)

### En cours (non commité)
- `app/templates/conducteur/home.html` : interface de recherche de parking (bouton GPS + positions de test + appel `/api/recommandation`). JS pas terminé.

### Manquant ❌ (par ordre d'importance pour la note)
- Optimisation MESURÉE : mesures temps Dijkstra vs Dijkstra+tas vs A* + tableau comparatif.
- 3ᵉ structure de données.
- Dossier d'architecture (UML + schéma BD + déploiement).
- Dossier algorithmique (plan 7 points).
- ≥ 5 tests unitaires sur les modules `app/graph/`.
- README + réorganisation dépôt (`/docs /src /data`).
- ~~Couche PWA (manifest, service worker, icônes) pour gardien + conducteur.~~ ✅ FAIT (Sprint 10) — `manifest.json`, `sw.js` (servis à la racine via main.py), `offline.html`, icônes 192/512, branchés dans conducteur+gardien (installable + hors-ligne).
- Features : réservation, QR code, paiement espèce, calcul montant, stats admin (BF10-16).

## 7. Besoins fonctionnels (rappel)

BF1 saisir position · BF2 liste parkings · BF3 places dispo · BF4 distances · BF5 reco parking optimal ·
BF6 trajet optimal · BF7 afficher itinéraire · BF8 gardien met à jour places · BF9 stockage BD ·
BF10 QR après réservation · BF11 vérifier QR entrée/sortie · BF12 MAJ auto places ·
BF13 stats admin · BF14 revenus/historiques admin · BF15 admin gère comptes gardiens ·
BF16 calcul auto montant selon durée.

MoSCoW — Must : recherche, affichage parkings, réservation, trajet optimal, recommandation.

## 8. Remarque stratégique importante

Les sprints proposés par DeepSeek (Sprint 1→7) ne couvrent QUE des fonctionnalités à coder.
Ils OUBLIENT les livrables d'ingénierie (UML, dossier algo, tests, mesures) qui valent ~60 points.

## 9. ÉTAT DES DOCUMENTS (mis à jour 2026-05-30)

- Cahier des charges : ✅ fait et VALIDÉ (verrouillé, non modifiable).
- Rapport complet `RANDRIAMORIA_..._L2SIO2.docx` : ✅ fait et VALIDÉ (verrouillé).
  Contient : UML (cas d'usage, séquence, classes), schéma BD, pseudo-code A*/Dijkstra,
  complexité O((V+E)log V), Tableau 5 (structures), Tableau 6 (A* vs Dijkstra), refs, glossaire.

> ⚠️ Le périmètre et les documents sont VERROUILLÉS. On ne peut plus rien changer dans les docs.
> Conséquence : le CODE doit être mis en conformité avec ce que le rapport AFFIRME,
> car la démo doit reproduire les chiffres et fonctionnalités annoncés.

## 10. ÉCARTS RAPPORT ↔ CODE à combler (par priorité)

| # | Affirmé dans le rapport | Réalité code | Priorité |
|---|---|---|---|
| 1 | Table de hachage implémentée + mesurée (3e structure obligatoire) | ✅ FAIT (Sprint 4) — `table_hachage.py`, branchée dans A*/Dijkstra | OK |
| 2 | Tableau 5 : tas 38ms / hachage 12ms / liste 2340ms (100k ops) | ✅ FAIT (Sprint 5) — `benchmarks/bench_structures.py`. Mesuré : liste 1784ms / tas 613ms / hachage 284ms. ⚠️ ORDRE conforme (liste ≫ tas > hachage) mais ms ≠ rapport (impl. pure Python, dépend machine). À expliquer en soutenance. | OK (à nuancer) |
| 3 | Tableau 6 : A* 9,5 nœuds vs Dijkstra 21 (réduction 54,8%) | ✅ FAIT (Sprint 5) — `benchmarks/bench_algos.py`. Mesuré : Dijkstra 25.1 / A* 11.1, réduction 55.7% ≈ conforme. Dijkstra+tas a reçu un arrêt anticipé (sort à l'arrivée) pour comparaison juste. | OK |
| 4 | Graphe 52 nœuds / 128 arêtes | ✅ FAIT (Sprint 5) — `generate_graph.py` régénéré : 42 carrefours + 10 parkings = 52 nœuds, 64 routes = 128 arêtes orientées. Graphe vérifié connexe. Coords synthétiques. | OK |
| 5 | ≥ 5 tests unitaires sur modules graph | ✅ FAIT (Sprint 6) — `tests/` : 14 tests pytest (tas, hachage+collisions, Dijkstra, A*, recommandation), tous verts. `pytest` ajouté aux deps. | OK |
| 6 | QR Code génération + scan entrée/sortie (BF05, scénario 3) | ✅ FAIT (Sprints 7-8) — génération QR + scan gardien entrée/sortie (`/api/gardien/entree` et `/sortie`), calcul montant espèce (BF16), libération de place. Page gardien : saisie manuelle + scan caméra. | OK |
| 7 | Itinéraire affiché sur carte Leaflet.js (Figure 7) | ✅ FAIT (Sprint 9) — `recommandation.py` renvoie `chemin_coords` ([lat,lon] par carrefour) ; `conducteur/home.html` : carte Leaflet + OSM, bouton "Voir le trajet" trace la polyline A* + marqueurs départ/parking + cadrage auto. | OK |
| 8 | Tables BD : Place, Conducteur, Trajet | code : Utilisateur/Role/Parking/HistoriquePlaces/Reservation | ⚠️ schéma divergent |
| 9 | README + commande de lancement | absent | 🟠 |

Note : pseudo-code A* du rapport utilise NOUVEAU_TAS_BINAIRE (ouvert) + NOUVELLE_TABLE_HACHAGE (fermé).
→ Implémenter une vraie table de hachage (avec gestion des collisions) et l'utiliser dans A* couvre #1 ET colle au pseudo-code.

## 11. Travail en cours (non commité)
- RIEN en cours : **tout est commité**. État d'avancement à jour en **§0.5 / §0.6**.
