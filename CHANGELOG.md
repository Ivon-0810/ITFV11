# CHANGELOG — IrwaneTraceForest (ITF)

## V11 — Stockage PostgreSQL persistant pour le serveur central

Le serveur central de synchronisation (`sync_server.py`) stockait ses
réceptions dans un fichier SQLite local (`sync_central.db`). Sur l'offre
gratuite de Render, ce disque n'est pas garanti persistant entre deux
redémarrages : un redéploiement ou une inactivité prolongée pouvait effacer
silencieusement toutes les données déjà synchronisées par les sociétés.

Corrigé : le serveur utilise désormais PostgreSQL via la variable
d'environnement `DATABASE_URL` (compatible Neon, Supabase, ou toute base
Postgres standard). Important : la base Postgres gratuite fournie
directement par Render s'auto-détruit 30 jours après sa création — le guide
`MIGRATION_POSTGRESQL.md` recommande donc Neon (offre gratuite permanente)
plutôt que Render Postgres pour cet usage précis.

Repli automatique : si `DATABASE_URL` n'est pas définie, le serveur retombe
sur l'ancien comportement SQLite local — pratique pour tester en local, à
ne jamais utiliser en production. Le tableau de bord du serveur central
affiche désormais un badge indiquant le mode actif (PostgreSQL / SQLite
local).

Aucun changement côté installations locales (`.exe` de chaque société) :
elles continuent de fonctionner en SQLite local, ce qui reste le bon choix
pour préserver le fonctionnement hors-ligne sans installation. Testé :
health check, réception d'un paquet, affichage du tableau de bord — les
trois passent en mode repli SQLite (le mode PostgreSQL nécessite une base
distante réelle pour être testé en conditions de production).

## Correctif critique — serveur central de synchronisation

`sync_server.py` n'initialisait la base centrale (table `receptions`) que
dans le bloc `if __name__ == "__main__"`. Or la commande de démarrage réelle
utilisée en production sur Render (`gunicorn sync_server:app`) **n'exécute
jamais ce bloc** — elle importe simplement l'objet `app`. Résultat : la
première synchronisation reçue en production aurait échoué avec une erreur
« table receptions introuvable ». Corrigé : l'initialisation s'exécute
désormais à l'import du module, donc aussi bien en local qu'en production.

## V10 — Modules scierie détaillés, catalogue d'essences extensible, postes personnalisés, synchronisation web déployable

### Nouveaux modules scierie (d'après les fichiers réels de production fournis)
Chaîne complète désormais tracée, distincte du module « Transformation » générique :
- **Tronçonnage scierie** (`/tronconnage-scierie`) — arrivée LVG, dimensions grume,
  volume calculé automatiquement (même formule officielle que le DF10).
- **Billonnage** (`/billonnage`) — numérotation des billons, cubage automatique.
- **Sciage de tête** (`/sciage-tete`) — passage billon → coursons.
- **Stock coursons** (`/stock-coursons`) — inventaire des coursons, diamètre
  moyen et volume calculés automatiquement à partir des mesures gros/petit bout.
- **Production débitée journalière** (`/production-debitee`) — colisage fin par
  dimension/qualité, volume calculé automatiquement (pièces × L × l × ép.).

Chacun dispose de son propre export Excel, import Excel (avec résolution des
essences par nom et des grumes par numéro DF10) et modèle vierge téléchargeable.
Testé : 17 vérifications (création, calculs automatiques, imports) — 0 échec.

### Catalogue d'essences extensible
Nouvelle page `/essences` : n'importe quel utilisateur de terrain peut ajouter
une essence manquante (nom, masse volumique, DME), immédiatement disponible
dans toutes les listes déroulantes. Une essence ajoutée par une société reste
strictement invisible aux autres sociétés (testé) ; le catalogue global reste
partagé par tous.

### Postes & métiers personnalisés
Nouvelle page `/parametres/postes` (Super-Admin) : définir des intitulés de
poste (« Opérateur Massicot », « Chef Séchoir »...) sélectionnables à la
création de n'importe quel compte, en plus du rôle système qui continue seul
de gouverner les permissions. Purement informatif — n'élargit aucun droit.

### Synchronisation — serveur central déployable en ligne
`sync_server.py` accepte désormais un port dynamique (`$PORT`), avec
`render.yaml` et `requirements-sync.txt` pour un déploiement en un clic sur
Render.com (plan gratuit, 100% navigateur, aucune commande à taper). Guide
complet dans `DEPLOIEMENT_SYNC_WEB.md`.

### Logo
Nouveau fichier `.ico` fourni, recadré (emblème carré sans texte) et régénéré
dans toutes les tailles (favicon, barre latérale, icône `.exe` Windows).

## V9 — Icône du logo dans la barre des tâches Windows

Sur Windows, pywebview (via WebView2/WinForms) affiche parfois une icône
générique dans la barre des tâches et le bandeau de la fenêtre, même quand
l'exécutable `.exe` a bien sa propre icône embarquée. Corrigé :
- `desktop_launcher.py` force désormais explicitement l'icône du logo
  IrwaneTraceForest (`static/img/itf.ico`) sur la fenêtre, via un message
  Windows natif (`WM_SETICON`) envoyé juste après l'ouverture de la fenêtre.
- Ce mécanisme est spécifique à Windows et **sans aucun effet** ailleurs
  (Linux/Mac) ou si `pywin32` n'est pas installé — l'application continue de
  fonctionner normalement dans tous les cas, l'icône de l'exécutable restant
  le repli par défaut.
- Nouvelle dépendance `pywin32` (Windows uniquement, via un marqueur
  d'environnement dans `requirements.txt` — n'affecte pas les autres OS).
- `itf.spec` déclare les imports cachés `win32gui`, `win32con`, `win32api`
  nécessaires à PyInstaller pour les inclure dans le build Windows.

## V8 — Récupération d'urgence du mot de passe Super-Admin

Nouvelle route `/recuperation-urgence`, désactivée par défaut (404). Elle ne
s'active que si un fichier `RESET_SUPER_ADMIN.txt` est créé à la main dans le
dossier de la base de données (preuve d'accès physique à la machine) : le
mot de passe du compte Super-Admin est alors régénéré, affiché une seule
fois, et le fichier déclencheur est supprimé automatiquement (usage unique).
Aucune faille exploitable à distance — testé (8 vérifications).

## V5 — Import/Export Excel complet, module par module

Auparavant, l'export Excel n'existait que pour l'inventaire, le registre DF10,
la production scierie, le stock usine et l'audit — et l'import Excel n'existait
que pour l'inventaire. Toutes les étapes disposent désormais des deux sens :

| Module | Export Excel | Import Excel | Modèle vierge téléchargeable |
|---|---|---|---|
| Inventaire forestier | ✅ | ✅ | ✅ |
| Registre DF10 | ✅ | ✅ (nouveau) | ✅ |
| Transport (LV grumes/bois débité) | ✅ (nouveau) | ✅ (nouveau) | ✅ |
| Parc usine (CEU / stock) | ✅ | ✅ (nouveau) | ✅ |
| Transformation | ✅ (nouveau) | ✅ (nouveau) | ✅ |
| Scierie (production) | ✅ | ✅ (nouveau) | ✅ |
| Contrats & exports | ✅ (nouveau) | ✅ (nouveau) | ✅ |
| Journal d'audit | ✅ | — (lecture seule par nature) | — |

Points de conception :
- Chaque import résout les références croisées à partir de numéros métier
  lisibles (N° DF10, N° CEU, N° Lot) plutôt que d'identifiants techniques —
  cohérent avec ce qu'un utilisateur peut effectivement saisir dans un tableur.
- L'import Transport recalcule automatiquement le contrôle de charge à l'essieu
  quand les poids sont fournis, exactement comme la saisie manuelle.
- Toute ligne invalide (essence inconnue, référence introuvable, valeur non
  numérique) est ignorée avec un compte-rendu — jamais bloquant pour le reste
  du fichier ni pour l'application.
- L'isolation multi-tenant s'applique aussi aux imports : impossible de
  référencer, même par erreur, une donnée d'une autre société (testé).
- Chaque page d'import propose un lien « Télécharger le modèle vierge »
  (fichier `.xlsx` avec les bons en-têtes) pour éviter les erreurs de format.

Testé : 40 vérifications automatisées (accès, imports réels avec liaison
relationnelle, robustesse sur données invalides, isolation tenant, restriction
de rôle) — 0 échec.

## V4 — Gouvernance des comptes : Super-Admin unique & nomination des Admins

### Un seul compte Super-Admin, garanti au niveau base de données
- Index unique SQLite `idx_super_admin_unique` sur `users(role)` filtré sur
  `role = 'SUPER_ADMIN'` : même une tentative de contournement applicatif ne
  peut pas créer un second compte Super-Admin. Testé explicitement.
- Toute route de création d'utilisateur refuse explicitement `role=SUPER_ADMIN`
  avant même d'atteindre la base (message clair à l'utilisateur).

### Nomination des Admins de société — exclusive au Super-Admin
- Nouvelle page `/super-admin/utilisateurs` : vue sur **tous** les utilisateurs
  de **toutes** les sociétés (seule vue de ce type dans l'application), création
  d'un compte ADMIN (ou d'un rôle opérationnel directement) pour n'importe
  quelle société, activation/désactivation, réinitialisation de mot de passe.
- Nouvelle page `/utilisateurs` (« Mon équipe ») réservée à chaque ADMIN : gère
  uniquement les collaborateurs opérationnels de sa propre société — impossible
  d'y créer un compte ADMIN ou SUPER_ADMIN, et aucune visibilité sur les autres
  sociétés (testé explicitement).

### Mot de passe personnel obligatoire à la première connexion
- Tout compte créé (par le Super-Admin ou un Admin) reçoit un mot de passe
  temporaire affiché une seule fois à son créateur. À la première connexion,
  l'utilisateur est redirigé de force vers `/changer-mot-de-passe` et ne peut
  accéder à aucune autre page tant qu'il n'a pas défini son propre mot de passe.

### Documentation du déploiement .exe
- Nouveau `construire_exe.bat` : script Windows à double-cliquer qui installe
  les dépendances et lance PyInstaller automatiquement, en une seule action.
- `DEPLOIEMENT_EXE.md` précise désormais explicitement pourquoi le `.exe` ne
  peut être compilé qu'à partir d'un poste Windows (PyInstaller ne fait pas de
  compilation croisée), et comment tester l'application immédiatement via
  `python app.py` en attendant.

## V3 — Logo, interface exclusive par société, hors-ligne & synchronisation

### Identité visuelle
- Intégration du logo officiel IrwaneTraceForest (fourni par Gauthier MBILI) :
  favicon web, icône de la barre latérale, icône `.exe` Windows (`static/img/itf.ico`).

### Interface exclusive par société
- Bannière « Interface exclusive — [Société] » affichée en permanence dans la barre
  latérale pour tout utilisateur rattaché à un tenant, rappelant que l'isolation
  multi-tenant (déjà vérifiée par tests en V1/V2) est stricte et systématique.

### Mode hors-ligne & synchronisation
- Nouveau module `sync.py` : détection réelle de connexion Internet (test de
  connexion TCP vers des DNS publics, jamais de faux positif sur un simple réseau
  local), envoi des données de la société (ou de toutes les sociétés pour le
  Super-Admin) vers un serveur central configurable, historique complet des
  tentatives (`sync_log`), jamais de perte de données locale en cas d'échec réseau.
- Nouveau script indépendant `sync_server.py` : récepteur central minimal à
  déployer par le Super-Admin, avec tableau de bord de suivi des réceptions.
- Nouvelle page `/sync` : pastille d'état (en ligne/hors ligne) rafraîchie
  automatiquement toutes les 20 secondes, bouton « Synchroniser maintenant »
  activé uniquement quand une connexion est réellement détectée, historique des
  synchronisations, configuration du serveur central réservée au Super-Admin.
- Nouvelles tables `parametres_sync` (config globale, Super-Admin exclusif) et
  `sync_log` (historique), colonne `dernier_sync_le` sur `tenants` — toutes
  additives, sans impact sur les données existantes.

## V2 — Évolution structurée (2026)

Toutes les modifications ci-dessous sont **additives** : aucune table, colonne,
route ou template existant n'a été supprimé ou renommé. Une base V1 en
production peut être mise à jour vers V2 sans perte de données — les
migrations (`database._migrer_colonnes_additionnelles`) s'exécutent
automatiquement et sans risque à chaque démarrage.

### 1. Étapes de transformation (nouveau module `/transformation`)
- Nouvelle table `etapes_transformation` : Écorçage, Tronçonnage, Sciage
  primaire, Séchage, Rabotage/Finition.
- Rattachement **optionnel** à une grume DF10 et/ou à une réception usine
  (CEU), ou saisie libre par référence de lot si aucune référence amont
  n'est encore disponible — aucun blocage du flux terrain.
- Calcul automatique du taux de perte quand les deux volumes sont saisis.

### 2. Documents officiels & PDF / code-barres
- `lettres_voiture` : nouvelle colonne `type_lv` (GRUMES / BOIS_DEBITE),
  nouvelle colonne `scierie_lot_ids` pour les LV bois débité.
- `parc_usine_receptions` : nouvelle colonne `numero_ceu` (numérotation
  officielle du Carnet Entrée Usine).
- Nouveau module `pdf_documents.py` : PDF avec code-barres Code128 pour
  DF10 (`/df10/<id>/pdf`), Lettre de Voiture Grumes/Bois débité
  (`/transport/<id>/pdf`), Carnet Entrée Usine (`/parc-usine/<id>/pdf`).

### 3. Contrôle de charge à l'essieu
- Nouveau module `charge_essieu.py` (seuils PMA standard 44t / renforcé 50t).
- Nouvelle table `controle_charge_essieu`, rattachée à la lettre de voiture.
- Intégré à l'émission de la LV : **facultatif**, n'empêche jamais l'édition
  du document — signale simplement une non-conformité (badge + alerte).

### 4. Généalogie & Module 8
- Généalogie étendue : Grume → LV grumes → Réception (CEU) → Étapes de
  transformation → Lot de sciage → LV bois débité, avec liste consolidée
  des intervenants terrain et bureau à chaque étape.
- Nouveau module `core_export.py` (Module 8, suite Python autonome
  `irwanetrace_core.py`) : accessible uniquement via `/module8`, protégé
  par le décorateur `@super_admin_requis` (vérification serveur, jamais
  contournable depuis le template). Journalisation dédiée dans
  `exports_module8`.

### 5. Excel
- Nouveau module `excel_io.py` : export générique (inventaire, registre
  DF10, production scierie, stock usine, journal d'audit) et import pour
  l'inventaire forestier (lignes invalides ignorées avec compte-rendu,
  jamais bloquant pour le reste du fichier).

### 6. Thème
- Commutateur Émeraude / Sombre dans le pied de la barre latérale,
  mémorisé en session (`session["theme"]`), sans rechargement de logique
  métier — uniquement une bascule de variables CSS.

### Correctifs
- Ajout de l'import manquant `import io` dans `app.py` (nécessaire aux
  exports PDF/Excel via `send_file`).
