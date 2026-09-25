# Déployer le serveur central de synchronisation en ligne
## (application web réelle, gratuite, 100% navigateur — aucune installation)

Ce guide déploie `sync_server.py` sur **Render.com**, un hébergeur qui offre un
plan gratuit adapté à cet usage. Une fois en ligne, chaque installation ITF
(le `.exe` de chaque société ou de votre console Super-Admin) pourra s'y
synchroniser automatiquement dès qu'une connexion Internet est détectée —
via le bouton « Synchroniser maintenant » déjà présent dans l'application.

---

## Étape 1 — Avoir le code sur GitHub

Si vous avez déjà suivi le guide `OBTENIR_LE_EXE_SANS_RIEN_INSTALLER.md` pour
compiler le `.exe`, **vous avez déjà un dépôt GitHub** avec tout le code —
passez directement à l'étape 2. Sinon, reportez-vous à ce guide pour créer
votre dépôt et y envoyer le contenu du dossier `itf`.

## Étape 2 — Créer un compte Render (gratuit)

1. Allez sur https://render.com
2. Cliquez sur **"Get Started"**, puis **"Sign up with GitHub"** (le plus
   simple — connecte directement votre dépôt)
3. Autorisez Render à accéder à vos dépôts GitHub

## Étape 3 — Créer le service web

1. Sur le tableau de bord Render, cliquez sur **"New +"** → **"Blueprint"**
2. Sélectionnez votre dépôt `irwanetraceforest` (ou le nom que vous avez
   choisi)
3. Render détecte automatiquement le fichier `render.yaml` déjà présent
   dans le projet et propose de créer le service **irwanetraceforest-sync**
4. Cliquez sur **"Apply"**

## Étape 4 — Attendre le déploiement

1. Render installe les dépendances et démarre le serveur — comptez 2 à 5
   minutes pour le tout premier déploiement
2. Une fois prêt, un statut **"Live"** (point vert) apparaît
3. Notez l'URL fournie en haut de la page, du type :
   ```
   https://irwanetraceforest-sync.onrender.com
   ```

## Étape 5 — Vérifier que ça répond

Ouvrez cette URL dans votre navigateur — vous devez voir le tableau de bord
**« IrwaneTraceForest — Serveur central de synchronisation »**, vide pour
l'instant (aucune réception encore reçue).

## Étape 6 — Connecter votre application ITF à ce serveur

1. Ouvrez votre application ITF, connectez-vous en Super-Admin
2. Allez dans **Paramètres** → section **Synchronisation & mode hors-ligne**
   (ou directement le menu **🔄 Synchronisation**)
3. Dans le champ **URL du serveur central**, collez l'adresse notée à
   l'étape 4 (ex : `https://irwanetraceforest-sync.onrender.com`)
4. Cochez éventuellement « Proposer la synchronisation automatiquement »
5. Enregistrez

## Étape 7 — Tester

Cliquez sur **« Synchroniser maintenant »** dans l'application. Si tout
fonctionne, un message de succès s'affiche, et le tableau de bord du
serveur central (l'URL de l'étape 4) affiche la réception correspondante.

---

## Point d'attention — plan gratuit Render

Le plan gratuit met le service en veille après 15 minutes sans requête : la
toute première synchronisation après une période d'inactivité peut prendre
30 à 60 secondes de plus le temps que le service se réveille — c'est normal,
pas une panne. Les synchronisations suivantes sont rapides tant que le
service reste actif.

## Pour les mises à jour futures

Si `sync_server.py` évolue, il suffit de renvoyer les fichiers mis à jour
vers votre dépôt GitHub (comme pour le `.exe`) — Render redéploie
automatiquement la nouvelle version en quelques minutes.

## Sécurité — à faire évoluer avant un usage à grande échelle

La version actuelle du serveur central accepte les envois sans clé
d'authentification (pratique pour démarrer rapidement). Si vous exposez ce
serveur publiquement sur Internet de façon durable, il est recommandé
d'ajouter une clé secrète partagée (vérifiée dans l'en-tête de chaque
requête) avant que d'autres sociétés que les vôtres n'y aient accès —
dites-le-moi quand vous serez prêt pour cette étape et je l'ajoute.
