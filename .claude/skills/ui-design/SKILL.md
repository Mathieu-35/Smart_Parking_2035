---
name: ui-design
description: Règles et goûts de design UI pour le projet Smart Parking 2035. À utiliser DÈS QU'ON TOUCHE à l'apparence — CSS, templates HTML, couleurs, espacements, composants (pages mobiles conducteur/gardien ET admin web). Consulter aussi les captures dans references/ pour s'aligner sur les inspirations de l'étudiant.
---

# Design UI — Smart Parking 2035

Ce Skill capture les goûts de l'étudiant (RANDRIAMORIA Mathieu, L2) pour
que l'interface reste cohérente d'une session à l'autre. À relire avant
toute modification visuelle.

## 0. Règle d'or
Avant de coder du CSS, **regarder les images dans `references/`** (les
inspirations déposées par l'étudiant) et **expliquer simplement le plan
AVANT de coder** (l'étudiant est débutant, pas de syntaxe avancée).

## 1. Ce que l'étudiant N'AIME PAS (à éviter absolument)
Retours explicites donnés pendant le projet :
- ❌ Le look « **IA generated** » : dégradés tape-à-l'œil, emojis partout,
  coins ultra-arrondis, ombres colorées.
- ❌ Les **emojis** dans les boutons/titres (📍 📷 🚗 🅿️ ✅…). **Zéro emoji.**
- ❌ Les **dégradés**. On utilise des **aplats** (couleurs plates).
- ❌ Les blocs qui « **prennent trop de place** » et **ne respirent pas** :
  en-têtes géants, paddings énormes qui écrasent la zone de saisie.
- ❌ Une sidebar large qui mange l'écran sur mobile.

## 2. Ce qu'il AIME (direction validée)
- ✅ **Sobre et pro**, épuré.
- ✅ **Bleu plat `#1e3a8a`** comme couleur principale.
- ✅ **Coins discrets** : 10–12px (pas 20–26px).
- ✅ **Ombres grises légères** (`0 1px 2px rgba(16,24,40,.06)`), pas bleutées.
- ✅ Contenu **aéré** : marges/espaces généreux, surtout autour des champs
  de saisie.
- ✅ Sur mobile : **barre d'onglets en BAS** (tab bar, style app classique,
  icônes + petit label), décidé le 2026-06-02 d'après l'inspiration #1
  (remplace l'ancien rail d'icônes à gauche).
- ✅ **Bleu royal vif `#2c5be0`** (décidé 2026-06-02, remplace le marine).
- ✅ Pour l'itinéraire : **carte plein écran + fiche qui remonte du bas**
  (bottom sheet) — l'étudiant tient à une GRANDE carte pour voir le trajet.

## 3. Palette (mobile)
| Rôle | Couleur |
|---|---|
| Bleu principal | `#1e3a8a` |
| Bleu foncé (appui) | `#172e6e` |
| Fond | `#f5f6f8` |
| Surface (cartes) | `#ffffff` |
| Texte | `#1f2533` |
| Texte doux | `#687087` |
| Vert succès | `#157347` / fond `#e7f4ec` |
| Rouge erreur | `#b42318` / fond `#fdeceb` |
| Bord | `#e7e9ee` |
| Rayon cartes | `12px` · boutons `10px` |

## 4. Architecture des styles (à respecter)
- **`app/static/css/mobile.css`** = pages MOBILES uniquement (conducteur +
  gardien). Classes préfixées `m-`.
- **`app/static/css/style.css`** = ADMIN web. **NE PAS** y mettre du style
  mobile, et inversement. Les deux mondes restent séparés.
- Le PWA met les fichiers en cache : après tout changement CSS, **bumper
  `NOM_CACHE` dans `app/static/sw.js`** (v6 → v7…) sinon le téléphone
  garde l'ancien design.

## 5. Composants mobiles existants (classes `m-`)
`m-screen` (écran), `m-rail` + `m-rail-link` (sidebar icônes),
`m-content` (zone de contenu), `m-intro` (Bonjour + sous-titre),
`m-card`, `m-btn` (`m-btn-primary` / `m-btn-secondary`),
`m-field` + `m-label`, `m-row` (boutons côte à côte), `m-or` (séparateur),
`m-result` (carte parking) + `m-badge` + `m-chip` + `m-route` + `m-explore`,
`m-alert` (`m-alert-success` / `m-alert-error`), `m-map`, `m-camera`.

> ⚠️ Côté gardien, ne pas réintroduire la classe `alert-error` (n'existe
> que `m-alert-error`).

## 6. Inspirations
Les captures d'écran d'apps que l'étudiant aime sont dans **`references/`**.
Pour chaque image, il indique ce qu'il aime (ex. « les cartes épurées »).
S'aligner sur ces images en priorité ; mettre à jour ce fichier quand de
nouvelles inspirations arrivent.

### Inspiration #1 — UI kit "app de parking" bleu & blanc (2026-06-02)
Planche de maquettes d'une app de parking (onboarding, login, liste de
parkings, carte, réservation, ticket QR, profil). Ce que l'étudiant aime :
- **Bleu & blanc franc, très épuré**, beaucoup de blanc → ça respire.
  (Leur bleu est plus VIF/royal que notre `#1e3a8a` marine — possibilité de
  l'éclaircir si l'étudiant valide.)
- **Cartes de parking riches** : vignette/photo + nom + note (étoiles) +
  prix + distance, empilées en liste.
- **GRANDE carte plein écran** avec une fiche qui remonte du bas
  (« bottom sheet ») → idéal pour voir l'itinéraire en grand. Point
  explicitement apprécié : « la carte est grande pour voir l'itinéraire ».
- Navigation par **barre d'onglets en bas** (tab bar) dans la maquette.
  ⚠️ Mais l'étudiant avait demandé un **rail d'icônes à gauche** : à
  reconfirmer avec lui avant de basculer en tab bar.
- Écrans profil et ticket QR épurés.
> Pour garder l'image : déposer le PNG dans `references/` (le chat ne la
> persiste pas tout seul).
