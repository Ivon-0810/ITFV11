# -*- coding: utf-8 -*-
"""
IrwaneTraceForest (ITF) - Serveur central de synchronisation
À déployer séparément, sur une machine avec accès Internet permanent,
par Gauthier MBILI (Super-Admin). Chaque installation ITF (par société ou
console Super-Admin), une fois une connexion détectée, pousse ses données
locales vers ce serveur via POST /api/sync/push.

Lancement : python sync_server.py   -> http://0.0.0.0:6000
Ce script est indépendant de app.py : il peut tourner sur un serveur
distinct de celui utilisé pour les installations locales des sociétés.

--- V11 : stockage PostgreSQL persistant (au lieu de SQLite) --------------
Sur Render (et la plupart des hébergeurs gratuits), le disque local d'un
service web n'est PAS garanti persistant entre deux redémarrages : un
fichier sqlite3 comme "sync_central.db" peut donc disparaître silencieusement
(redéploiement, redémarrage après inactivité, migration de conteneur), ce
qui aurait fait perdre TOUTES les synchronisations déjà reçues.

Ce module utilise désormais une vraie base PostgreSQL externe, désignée par
la variable d'environnement DATABASE_URL (format standard
"postgresql://user:password@host:port/dbname", fourni tel quel par Neon,
Supabase, Render Postgres payant, etc.). Voir MIGRATION_POSTGRESQL.md pour
la marche à suivre (création d'une base Neon gratuite en 5 minutes).

Si DATABASE_URL n'est pas définie, le module retombe automatiquement sur
l'ancien comportement SQLite local — pratique pour tester sur ton PC sans
dépendre d'une base distante, mais À NE JAMAIS UTILISER EN PRODUCTION.
"""

import json
import os
import sqlite3
import datetime

from flask import Flask, request, jsonify, render_template_string

DATABASE_URL = os.environ.get("DATABASE_URL")
MODE_POSTGRES = bool(DATABASE_URL)

if MODE_POSTGRES:
    import psycopg2
    import psycopg2.extras
    # Render/Neon fournissent parfois une URL "postgres://" (ancien schéma) ;
    # psycopg2 exige "postgresql://".
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    DB_CENTRAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sync_central.db")

app = Flask(__name__)


def get_connection():
    if MODE_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    conn = sqlite3.connect(DB_CENTRAL)
    conn.row_factory = sqlite3.Row
    return conn


def init_central_db():
    conn = get_connection()
    if MODE_POSTGRES:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS receptions (
                    id SERIAL PRIMARY KEY,
                    tenant_code TEXT NOT NULL,
                    tenant_id INTEGER,
                    nb_enregistrements INTEGER DEFAULT 0,
                    paquet_json TEXT NOT NULL,
                    adresse_ip TEXT,
                    recu_le TIMESTAMP DEFAULT NOW()
                );
                """
            )
        conn.commit()
    else:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS receptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_code TEXT NOT NULL,
                tenant_id INTEGER,
                nb_enregistrements INTEGER DEFAULT 0,
                paquet_json TEXT NOT NULL,
                adresse_ip TEXT,
                recu_le TEXT DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()
    conn.close()


# Appelée immédiatement à l'import du module (et pas seulement dans le bloc
# __main__) : sous gunicorn — la commande de démarrage réelle utilisée par
# Render en production — le bloc `if __name__ == "__main__"` ne s'exécute
# JAMAIS, puisque gunicorn importe l'objet `app` sans lancer le script en
# tant que programme principal. Sans cet appel ici, la table `receptions`
# ne serait jamais créée en production et /api/sync/push échouerait dès la
# première requête. CREATE TABLE IF NOT EXISTS rend cet appel sûr à rejouer.
init_central_db()


@app.route("/api/sync/push", methods=["POST"])
def sync_push():
    """Reçoit un paquet JSON {tenant_code, tenant_id, donnees, envoye_le}
    envoyé par sync.synchroniser() depuis une installation locale ITF."""
    try:
        paquet = request.get_json(force=True)
    except Exception:
        return jsonify({"ok": False, "message": "JSON invalide."}), 400

    if not paquet or "donnees" not in paquet:
        return jsonify({"ok": False, "message": "Paquet incomplet."}), 400

    tenant_code = paquet.get("tenant_code") or "INCONNU"
    tenant_id = paquet.get("tenant_id")
    donnees = paquet["donnees"]

    if tenant_code == "GLOBAL_SUPER_ADMIN":
        nb = sum(len(v2) for v1 in donnees.values() for v2 in v1.values())
    else:
        nb = sum(len(v) for v in donnees.values())

    conn = get_connection()
    try:
        if MODE_POSTGRES:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO receptions (tenant_code, tenant_id, nb_enregistrements, paquet_json, adresse_ip) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (tenant_code, tenant_id, nb, json.dumps(donnees, default=str), request.remote_addr),
                )
        else:
            conn.execute(
                "INSERT INTO receptions (tenant_code, tenant_id, nb_enregistrements, paquet_json, adresse_ip) "
                "VALUES (?,?,?,?,?)",
                (tenant_code, tenant_id, nb, json.dumps(donnees, default=str), request.remote_addr),
            )
        conn.commit()
    finally:
        conn.close()
    return jsonify({"ok": True, "message": f"{nb} enregistrement(s) reçus.", "recu_le": datetime.datetime.now().isoformat()})


@app.route("/api/sync/health")
def sync_health():
    return jsonify({
        "ok": True,
        "service": "IrwaneTraceForest - Serveur central de synchronisation",
        "stockage": "PostgreSQL" if MODE_POSTGRES else "SQLite local (DEV UNIQUEMENT)",
    })


@app.route("/")
def tableau_bord_central():
    conn = get_connection()
    if MODE_POSTGRES:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, tenant_code, nb_enregistrements, adresse_ip, recu_le FROM receptions "
                "ORDER BY id DESC LIMIT 200"
            )
            receptions = cur.fetchall()
    else:
        receptions = conn.execute(
            "SELECT id, tenant_code, nb_enregistrements, adresse_ip, recu_le FROM receptions "
            "ORDER BY id DESC LIMIT 200"
        ).fetchall()
    conn.close()
    return render_template_string(
        """
        <!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
        <title>ITF — Serveur central de synchronisation</title>
        <style>
          body { font-family: Segoe UI, sans-serif; background:#0f172a; color:#e2e8f0; padding:30px; }
          h1 { color:#34d399; }
          .badge { display:inline-block; padding:2px 10px; border-radius:12px; font-size:12px; margin-left:10px; }
          .badge-ok { background:#065f46; color:#6ee7b7; }
          .badge-warn { background:#7c2d12; color:#fdba74; }
          table { width:100%; border-collapse: collapse; margin-top:20px; }
          th, td { padding:8px 12px; border-bottom:1px solid #334155; text-align:left; font-size:13px; }
          th { color:#94a3b8; text-transform:uppercase; font-size:11px; }
        </style></head><body>
        <h1>IrwaneTraceForest — Serveur central de synchronisation
          {% if mode_postgres %}
          <span class="badge badge-ok">PostgreSQL — persistant</span>
          {% else %}
          <span class="badge badge-warn">SQLite local — DEV UNIQUEMENT, non persistant en production</span>
          {% endif %}
        </h1>
        <p style="color:#94a3b8">Réceptions envoyées par les installations locales, une fois connectées à Internet.</p>
        <table>
          <tr><th>#</th><th>Société</th><th>Enregistrements</th><th>IP</th><th>Reçu le</th></tr>
          {% for r in receptions %}
          <tr><td>{{ r.id }}</td><td>{{ r.tenant_code }}</td><td>{{ r.nb_enregistrements }}</td>
              <td>{{ r.adresse_ip }}</td><td>{{ r.recu_le }}</td></tr>
          {% endfor %}
        </table>
        </body></html>
        """,
        receptions=receptions,
        mode_postgres=MODE_POSTGRES,
    )


if __name__ == "__main__":
    init_central_db()
    port = int(os.environ.get("PORT", 6000))
    app.run(host="0.0.0.0", port=port, debug=False)
