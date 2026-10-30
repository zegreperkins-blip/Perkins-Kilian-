# Perkins & Kilian — site web complet

Site vitrine responsive pour un service d'aide à la vente destiné aux marchands de vêtements et de chaussures. Il inclut une zone client, une administration et une base de données SQLite.

## Fonctionnalités
- Accueil commercial, services, contact et mentions légales à compléter.
- Inscription client et connexion sécurisée (mots de passe hachés).
- Espace client pour envoyer une demande de service et suivre son statut.
- Espace admin : consulter les clients, demandes et messages de contact ; modifier les statuts.
- Base de données SQLite créée automatiquement au premier lancement.

## Installation (Windows)
1. Installez Python 3.10 ou plus récent.
2. Décompressez le projet et ouvrez un terminal dans le dossier `perkins_kilian`.
3. Créez un environnement virtuel :
   `python -m venv .venv`
4. Activez-le :
   PowerShell : `.venv\\Scripts\\Activate.ps1`
   CMD : `.venv\\Scripts\\activate.bat`
5. Installez les dépendances :
   `pip install -r requirements.txt`
6. Lancez le site :
   `python app.py`
7. Ouvrez `http://127.0.0.1:5000` dans votre navigateur.

## Connexion administrateur initiale
- E-mail : `admin@perkinskilian.ci`
- Mot de passe temporaire : `ChangeMe123!`

**Sécurité obligatoire avant publication :** connectez-vous en local et modifiez ce mot de passe (dans la base de données ou en ajoutant une fonction de changement de mot de passe), définissez une variable d'environnement `SECRET_KEY` longue et aléatoire, désactivez le mode debug, activez HTTPS et configurez sauvegardes, limitation des tentatives de connexion et politique de confidentialité. Les identifiants ci-dessus sont des identifiants de démonstration et ne doivent jamais être conservés en production.

## Publication
Le backend Flask et SQLite ne peuvent pas fonctionner sur un hébergement statique comme GitHub Pages. Il faut un hébergement qui exécute Python (par exemple un hébergeur d'applications Python) et un stockage persistant pour la base de données. Pour une utilisation multi-clients en production, préférez PostgreSQL et configurez les sauvegardes.

## Personnalisation
Les textes sont rédigés en français et orientés vers les vendeurs de vêtements et chaussures. Remplacez les coordonnées fictives, précisez vos tarifs, vos conditions, vos horaires et vos canaux de contact avant mise en ligne.
