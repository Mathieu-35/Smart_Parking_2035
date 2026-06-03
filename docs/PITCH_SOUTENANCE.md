# Pitch et déroulé oral — Soutenance Smart Parking 2035

> À réviser avant le jour J. Ordre imposé : 1) pitch d'accroche, 2) salutation, 3) slides.
> Présenté par : RANDRIAMORIA Sahiniaina Mathieu — L2 ESMIA.
> Durée totale visée : 10 minutes, démonstration incluse.

---

## 1) LE PITCH D'ACCROCHE (en tout premier, ~45 secondes)

> « Imaginez : vous êtes en voiture, en plein centre d'Antananarivo. Vous êtes
> en retard. Et là, vous tournez… vous tournez encore… à la recherche d'une
> seule place de parking libre. Du temps perdu, du carburant gaspillé, et un
> stress que nous connaissons tous.
>
> Et si votre téléphone pouvait, en quelques secondes, vous dire où se trouve
> la place la plus proche encore libre, et vous montrer le chemin le plus court
> pour y arriver ?
>
> C'est précisément ce que résout mon projet : Smart Parking 2035. »

(Petite pause. Lever les yeux vers le jury.)

---

## 2) LA SALUTATION (juste après l'accroche, ~20 secondes)

> « Bonjour à tous. Je remercie les membres du jury ainsi que toutes les
> personnes présentes. Je m'appelle RANDRIAMORIA Sahiniaina Mathieu, je suis en
> deuxième année à l'ESMIA, et je vais vous présenter ce projet ainsi qu'une
> démonstration en direct. »

---

## 3) LA PRÉSENTATION → afficher la slide 1 et enchaîner.

---

## Conseils pour bien le dire
- Respirer après l'accroche, ne pas se précipiter.
- Dire « Et si votre téléphone pouvait… » plus doucement : c'est le moment clé.
- Terminer sur « ce que j'ai programmé moi-même » avec un peu de fierté quand
  on arrivera à la slide des algorithmes.
- Minutage : accroche (~45 s) + salutation (~20 s) = ~1 minute.

---

## Rappel du minutage global (10 min)
- Pitch + salutation : ~1 min
- Slides 1 à 6 et 8 (parole) : ~5 min (environ 45 s par slide)
- Slide 7 = démonstration en direct : ~3 à 4 min
- Garder une petite marge de sécurité.

---

## NOTES À DIRE SOUS CHAQUE SLIDE (version courte 8 slides)

### Slide 1 — Titre
« Voici donc Smart Parking 2035, une plateforme intelligente de gestion et de
recherche de parkings, que j'ai développée dans le contexte d'Antananarivo. »
(Court — la slide parle d'elle-même.)

### Slide 2 — Problème et solution
« Le problème, je viens de vous le décrire : on perd du temps à chercher une
place. Ma solution est une application qui trouve le parking le plus proche
ayant de la place, et qui calcule le meilleur chemin pour y aller. J'ai adapté
le projet à notre réalité : les prix sont en Ariary, et l'heure est celle de
Madagascar. »

### Slide 3 — Les trois rôles
« L'application réunit trois personnes. Le conducteur, sur son téléphone,
cherche et réserve une place. Le gardien, lui aussi sur mobile, scanne un QR
code pour valider l'entrée et la sortie. Et l'administrateur, sur le web, gère
les parkings, les comptes et suit les statistiques. »

### Slide 4 — Architecture technique
« Côté technique, le programme est écrit en Python avec le framework FastAPI.
Les pages sont générées avec Jinja2, et les données sont stockées dans une base
PostgreSQL. La connexion est sécurisée : les mots de passe sont chiffrés. J'ai
organisé mon code proprement, en séparant les routes, les contrôleurs, les
modèles, et un module à part pour les algorithmes. »

### Slide 5 — Le cœur du projet (algorithmes)  [SLIDE LA PLUS IMPORTANTE]
« Et voici le cœur de mon travail. J'ai transformé le plan de la ville en une
carte de points reliés par des rues — ce qu'on appelle un graphe : 52 points et
128 rues. Pour guider le conducteur, j'ai écrit moi-même, sans outil tout fait,
plusieurs méthodes de calcul du meilleur chemin : Dijkstra, une version plus
rapide, A* qui vise directement la destination, et une méthode simple qui prend
le parking le plus proche. Je les ai ensuite comparées pour voir laquelle est la
plus rapide. »
(Ralentir, et dire « moi-même » avec fierté.)

### Slide 6 — La PWA
« La partie mobile n'est pas un simple site internet : c'est une vraie
application installable sur le téléphone, avec un écran de démarrage, et qui
fonctionne même sans connexion grâce à une mise en cache. L'expérience est
proche d'une application native. »

### Slide 7 — Démonstration
« Je vais maintenant vous montrer tout cela en direct. »
(Ordre : conducteur -> réservation + QR -> gardien scanne -> admin dashboard.)

### Slide 8 — Conclusion et merci
« Pour conclure : Smart Parking 2035 est une application complète, de la
recherche jusqu'au paiement, avec des algorithmes que j'ai programmés et
comparés moi-même. Plus tard, on pourrait y ajouter des filtres de recherche et
le paiement mobile. Je vous remercie de votre attention, et je suis prêt à
répondre à vos questions. »
