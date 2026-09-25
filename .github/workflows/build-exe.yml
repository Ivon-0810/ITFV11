name: Construire IrwaneTraceForest.exe

# Se déclenche automatiquement à chaque envoi de fichiers sur GitHub,
# et peut aussi être relancé manuellement depuis l'onglet "Actions".
on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    # Machine Windows fournie gratuitement par GitHub — c'est elle qui compile,
    # pas votre PC de bureau. Aucune installation locale n'est nécessaire.
    runs-on: windows-latest

    steps:
      - name: Récupérer le code
        uses: actions/checkout@v4

      - name: Installer Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Installer les dépendances (Flask, pywebview, reportlab, openpyxl, PyInstaller)
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Initialiser la base de données locale
        run: python database.py

      - name: Compiler l'exécutable avec PyInstaller
        run: pyinstaller itf.spec --noconfirm

      - name: Mettre l'exécutable à disposition au téléchargement
        uses: actions/upload-artifact@v4
        with:
          name: IrwaneTraceForest-exe
          path: dist/IrwaneTraceForest.exe
