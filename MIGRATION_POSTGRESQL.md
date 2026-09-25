# Migration du serveur central vers PostgreSQL (V11)

## Pourquoi ce changement ?

Le serveur central de synchronisation (`sync_server.py`, déployé sur Render)
stockait ses données reçues dans un simple fichier SQLite sur le disque du
serveur. Problème : sur l'offre gratuite de Render, ce disque n'est pas
garanti persistant — un redéploiement, une mise à jour, ou une simple
inactivité prolongée peut effacer ce fichier **sans avertissement**. Toutes
les données déjà synchronisées par les sociétés auraient alors été perdues
définitivement.

La solution : utiliser une vraie base de données PostgreSQL, hébergée à part,
qui survit aux redémarrages du serveur web. Ce guide utilise **Neon**, qui
propose une offre gratuite **permanente** (contrairement à la base Postgres
gratuite de Render elle-même, qui s'auto-détruit 30 jours après sa création
— à éviter absolument pour cet usage).

Durée estimée : 10 minutes. Aucune carte bancaire requise.

---

## Étape 1 — Créer un compte Neon (2 minutes)

1. Allez sur https://neon.tech
2. Cliquez sur **"Sign up"**, connectez-vous avec votre compte GitHub ou
   Google (le plus rapide) ou votre e-mail
3. Confirmez votre e-mail si demandé

## Étape 2 — Créer un projet (2 minutes)

1. Une fois connecté, cliquez sur **"Create a project"**
2. Nom du projet : `irwanetraceforest` (ou ce que vous voulez)
3. Région : choisissez la plus proche de votre serveur Render (Europe si
   votre service Render est en Europe — vérifiez dans le tableau de bord
   Render, section "Region")
4. Cliquez sur **"Create project"**

## Étape 3 — Copier l'URL de connexion (1 minute)

1. Une fois le projet créé, Neon affiche directement une **"Connection
   string"** — une ligne qui commence par `postgresql://...`
2. Cliquez sur l'icône de copie à côté de cette ligne
3. **Gardez-la de côté** (collez-la temporairement dans un fichier texte) —
   c'est votre `DATABASE_URL`, elle contient un mot de passe, ne la partagez
   avec personne d'autre que vous-même

## Étape 4 — Coller l'URL dans Render (3 minutes)

1. Allez sur https://dashboard.render.com et ouvrez votre service
   `irwanetraceforest-sync`
2. Dans le menu de gauche, cliquez sur **"Environment"**
3. Cliquez sur **"Add Environment Variable"**
4. Key : `DATABASE_URL`
5. Value : collez la ligne copiée à l'étape 3
6. Cliquez sur **"Save Changes"** — Render redéploie automatiquement le
   service avec la nouvelle configuration

## Étape 5 — Vérifier que ça fonctionne (2 minutes)

1. Une fois le redéploiement terminé (statut "Live" sur Render), ouvrez
   l'URL de votre serveur central dans un navigateur
   (`https://irwanetraceforest-sync.onrender.com` ou votre URL personnalisée)
2. En haut de la page, vous devez voir un badge vert **"PostgreSQL —
   persistant"** au lieu du badge orange "SQLite local"
3. Vous pouvez aussi vérifier `/api/sync/health` : le champ `"stockage"`
   doit afficher `"PostgreSQL"`

Si le badge reste orange, vérifiez que `DATABASE_URL` est bien enregistrée
dans Render (étape 4) et que le service a bien redémarré.

---

## Ce qui NE change PAS

- Les installations locales (`.exe` de chaque société) continuent de
  fonctionner exactement comme avant, en SQLite local — ce n'est PAS elles
  qui sont concernées par cette migration.
- Le bouton "Synchroniser" et son comportement (hors-ligne, non configuré,
  échec réseau) restent identiques.
- Aucune donnée locale n'est affectée, quoi qu'il arrive côté serveur
  central.

## Limite de l'offre gratuite Neon à connaître

0,5 Go de stockage inclus — largement suffisant pour démarrer (les paquets
JSON reçus sont compacts), mais à surveiller si le nombre de sociétés
synchronisées augmente fortement. Le tableau de bord Neon affiche l'usage
en temps réel. Si besoin plus tard, l'upgrade vers un plan payant Neon se
fait sans migration (même URL de connexion).
