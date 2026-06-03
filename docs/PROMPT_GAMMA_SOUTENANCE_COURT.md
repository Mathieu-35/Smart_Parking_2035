# Prompt Gamma — VERSION COURTE (10 min, démo incluse)

> Version réduite à 8 slides pour une soutenance de 10 minutes AVEC démonstration.
> L'autre fichier (PROMPT_GAMMA_SOUTENANCE.md) garde la version longue de 17 slides.
>
> MODE D'EMPLOI :
> 1. Gamma → "Créer AI" → "Coller du texte".
> 2. Colle TOUT le bloc entre les lignes ===.
> 3. Format "Présentation", langue Français, thème bleu sobre.
>
> Minutage conseillé : ~5 min de parole + ~4 min de démo + marge.
> Soit environ 45 secondes par slide de contenu.

=== DÉBUT DU PROMPT À COLLER ===

Crée une présentation de soutenance académique courte (8 diapositives), sobre et professionnelle, couleur dominante bleu (#2c5be0), fond clair, sans emoji, coins arrondis. Public : un jury universitaire (L2, ESMIA). Sujet : "Smart Parking 2035". Une diapositive par section ci-dessous, avec une icône ou un visuel simple par slide. Garde les titres et les puces tels quels.

Slide 1 — Page de titre
Titre : Smart Parking 2035
Sous-titre : Plateforme intelligente de gestion et de recherche de parkings
Présenté par : RANDRIAMORIA Sahiniaina Mathieu
Niveau : Licence 2 — ESMIA
Contexte : Antananarivo, Madagascar

Slide 2 — Problème et solution
- Problème : trouver une place de parking fait perdre du temps et du carburant ; on ne sait pas où il reste de la place ni quel chemin prendre.
- Solution : une application qui trouve le parking le plus proche ayant de la place et calcule le meilleur itinéraire.
- Adaptée au contexte local : monnaie en Ariary (Ar), heure de Madagascar (UTC+3).

Slide 3 — Les trois rôles
- Administrateur (sur le web) : gère les parkings, les comptes et consulte les statistiques.
- Conducteur (sur mobile) : cherche un parking, voit l'itinéraire, réserve une place, reçoit un QR code.
- Gardien (sur mobile) : scanne le QR code pour valider l'entrée et la sortie, et encaisse le paiement.

Slide 4 — Architecture technique
- Backend : Python avec le framework FastAPI.
- Pages web : moteur de templates Jinja2 (HTML rendu côté serveur).
- Base de données : PostgreSQL via SQLAlchemy.
- Sécurité : authentification par session et mots de passe chiffrés (bcrypt).
- Organisation claire du code : routes, contrôleurs, modèles, et un module dédié aux algorithmes.

Slide 5 — Le cœur du projet : trouver le meilleur chemin
- Le plan de la ville est transformé en une carte de points reliés par des rues (un graphe) : 52 points, 128 rues, 64 trajets possibles.
- Pour guider le conducteur vers un parking, j'ai écrit moi-même les méthodes de calcul, sans outil tout fait :
  - une méthode classique de plus court chemin (Dijkstra), et une version plus rapide
  - une méthode plus maligne qui vise directement la destination (A*)
  - une méthode simple qui choisit le parking le plus proche disponible
- J'ai ensuite comparé ces méthodes pour voir laquelle est la plus rapide : les résultats sont fiables et reproductibles.

Slide 6 — Une vraie application mobile (PWA)
- La partie mobile est une Progressive Web App, pas un simple site responsive.
- Installable sur le téléphone, avec un écran de démarrage et une barre d'onglets en bas.
- Fonctionne hors-ligne grâce à un service worker (mise en cache des pages).
- Expérience proche d'une application native.

Slide 7 — Démonstration
- Conducteur : recherche d'un parking, itinéraire sur la carte, réservation et QR code.
- Gardien : scan du QR code, validation de l'entrée et de la sortie, montant en Ariary.
- Administrateur : tableau de bord (occupation, revenus) et gestion des parkings et comptes.

Slide 8 — Conclusion et merci
- Une application complète : recherche, itinéraire, réservation, paiement, statistiques.
- Des algorithmes de plus court chemin implémentés et comparés à la main.
- Perspectives : filtres multi-critères, paiement mobile, données de trafic en temps réel.
- Merci de votre attention — Questions et réponses.

=== FIN DU PROMPT À COLLER ===
