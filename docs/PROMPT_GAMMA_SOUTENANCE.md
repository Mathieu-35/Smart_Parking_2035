# Prompt à coller dans Gamma — Soutenance Smart Parking 2035

> MODE D'EMPLOI :
> 1. Va sur https://gamma.app → "Create new" → "Paste in text" (Coller du texte).
> 2. Colle TOUT le bloc ci-dessous (entre les lignes ===).
> 3. Choisis le format "Présentation", langue Français, puis génère.
> 4. Choisis un thème sobre (bleu), puis ajuste si besoin.
>
> Astuce : si Gamma te demande un style, écris « sobre, professionnel, bleu #2c5be0, sans emoji ».

=== DÉBUT DU PROMPT À COLLER ===

Crée une présentation de soutenance académique, sobre et professionnelle, couleur dominante bleu (#2c5be0), fond clair, sans emoji, coins arrondis. Public : un jury universitaire (L2, ESMIA). Sujet : un projet logiciel nommé "Smart Parking 2035". Génère une diapositive par section ci-dessous, en gardant les titres et les puces tels quels, avec un visuel ou une icône simple par slide.

Slide 1 — Page de titre
Titre : Smart Parking 2035
Sous-titre : Plateforme intelligente de gestion et de recherche de parkings
Présenté par : RANDRIAMORIA Sahiniaina Mathieu
Niveau : Licence 2 — ESMIA
Contexte : Antananarivo, Madagascar

Slide 2 — Le problème
- Trouver une place de parking en ville fait perdre du temps et du carburant.
- Les conducteurs ne savent pas où il reste de la place, ni le chemin le plus court.
- Les gestionnaires de parkings manquent d'outils pour suivre l'occupation en temps réel.

Slide 3 — La solution proposée
- Une application qui trouve le parking le plus proche ayant de la place.
- Elle calcule le meilleur itinéraire grâce à des algorithmes de plus court chemin.
- Trois profils d'utilisateurs : Administrateur, Conducteur, Gardien.

Slide 4 — Les trois rôles
- Administrateur (sur le web) : gère les parkings, les comptes et consulte les statistiques.
- Conducteur (sur mobile) : cherche un parking, voit l'itinéraire, réserve une place, reçoit un QR code.
- Gardien (sur mobile) : scanne le QR code pour valider l'entrée et la sortie, encaisse le paiement.

Slide 5 — Architecture technique
- Backend : Python avec le framework FastAPI.
- Pages web : moteur de templates Jinja2 (HTML rendu côté serveur).
- Base de données : PostgreSQL (via SQLAlchemy).
- Sécurité : authentification par session et mots de passe chiffrés (bcrypt).

Slide 6 — Le cœur du projet : les algorithmes maison
- Le plan de la ville est modélisé en graphe : 52 nœuds, 128 arêtes orientées, 64 trajets.
- Algorithmes implémentés à la main (sans bibliothèque externe) :
  - Dijkstra (plus court chemin)
  - Dijkstra optimisé avec un tas binaire (file de priorité)
  - A* (recherche guidée par une heuristique de distance)
  - Algorithme glouton (recherche du parking le plus proche)
- Structures de données maison : tas minimal (TasMin), table de hachage, listes d'adjacence.

Slide 7 — Pourquoi plusieurs algorithmes ?
- Montrer que l'on comprend les différences de performance entre les approches.
- Comparer le nombre d'opérations et le temps de calcul sur le même graphe.
- Justifier le choix de l'algorithme le plus efficace pour l'application.

Slide 8 — Résultats : comparaison des algorithmes
- Présenter un tableau comparatif (Tableaux 5 et 6 du rapport) : temps de calcul et nombre de nœuds explorés.
- A* explore moins de nœuds que Dijkstra grâce à son heuristique.
- Le tas binaire accélère Dijkstra sur les graphes plus grands.
- Conclusion : les résultats sont reproductibles et cohérents avec la théorie.

Slide 9 — Une vraie application mobile (PWA)
- La partie mobile est une Progressive Web App, pas un simple site responsive.
- Installable sur le téléphone (icône sur l'écran d'accueil).
- Fonctionne hors-ligne grâce à un service worker (mise en cache).
- Écran de démarrage (splash), barre d'onglets en bas, expérience proche d'une vraie app.

Slide 10 — Le parcours du conducteur
- Recherche du parking le plus proche avec de la place.
- Affichage de l'itinéraire sur une carte plein écran (Leaflet).
- Fiche du parking en bas de l'écran : distance, places, tarif.
- Réservation d'une place et génération d'un QR code.

Slide 11 — Le parcours du gardien
- Le gardien ouvre la caméra et scanne le QR code du conducteur.
- Validation de l'entrée puis de la sortie du véhicule.
- Calcul automatique du montant à payer, en Ariary (Ar).

Slide 12 — Le tableau de bord administrateur
- Vue d'ensemble : taux d'occupation, revenus, nombre de réservations.
- Gestion des parkings : tarifs (semaine/week-end) et horaires d'ouverture modifiables.
- Gestion des comptes : création de gardiens et d'autres administrateurs, avec pagination.
- Statistiques affichées à l'heure locale de Madagascar (UTC+3).

Slide 13 — Choix d'adaptation au contexte local
- Monnaie : Ariary (Ar), sans centimes.
- Fuseau horaire : Madagascar (UTC+3).
- Tarification hybride : un prix en semaine et un prix le week-end.

Slide 14 — Démonstration
- Connexion en tant que conducteur : recherche et itinéraire.
- Réservation et obtention du QR code.
- Connexion en tant que gardien : scan et validation.
- Connexion en tant qu'administrateur : tableau de bord et gestion.

Slide 15 — Difficultés rencontrées et solutions
- Affichage de la fiche par-dessus la carte : résolu avec la gestion des couches (z-index).
- Heure décalée de 3 heures : corrigée en tenant compte du fuseau de Madagascar.
- Faire une vraie PWA installable et hors-ligne : manifeste + service worker.

Slide 16 — Conclusion et perspectives
- Une application complète : recherche, itinéraire, réservation, paiement, statistiques.
- Des algorithmes de plus court chemin implémentés et comparés à la main.
- Perspectives : filtres multi-critères, paiement mobile, données de trafic en temps réel.

Slide 17 — Merci
Titre : Merci de votre attention
Sous-titre : Questions et réponses
RANDRIAMORIA Sahiniaina Mathieu — L2 ESMIA — Smart Parking 2035

=== FIN DU PROMPT À COLLER ===
