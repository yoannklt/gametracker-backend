# 🎮 GameTracker Backend

Backend du projet GameTracker, une application web de suivi personnalisé des performances sur **Teamfight Tactics (TFT)**, basée sur les données de l’**API Riot Games**.

---

## 🚀 Fonctionnalités principales

- 🔐 **Authentification sécurisée** (bcrypt + JWT)
- 🧠 **Lien avec un compte Riot** (gameName, tagLine, région)
- 🧩 **Récupération des derniers matchs TFT** via l'API officielle Riot
- 📊 **Analyse et stockage** des données match (traits, unités, résultats...)
- 📈 **Statistiques dynamiques**
  - Winrate par composition
  - Top traits et unités joués
- 🔄 **Unlink** d’un compte Riot
- ✅ Compatible avec un frontend React/Next.js (à venir)

---

## 🛠️ Stack Technique

- **Langage** : Python 3.11
- **Framework** : FastAPI
- **Base de données** : PostgreSQL (via SQLAlchemy)
- **ORM** : SQLAlchemy 2.0
- **Auth** : JWT (access_token)
- **API externe** : [Riot Games API](https://developer.riotgames.com/)
- **Librairies principales** :
  - `requests`, `passlib[bcrypt]`, `python-jose`, `pydantic`, `fastapi`, `uvicorn`, etc.

---

## 📦 Installation & Lancement

### 1. Cloner le repo

```bash
git clone https://github.com/yoannklt/gametracker-backend.git
cd gametracker-backend
```

### 2. Créer et activer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer le serveur

```bash
uvicorn app.main:app --reload
```

---

## 🔐 Variables d’environnement

Créer un fichier `.env` à la racine avec le contenu suivant :

```
DATABASE_URL=postgresql://<username>:<password>@localhost/<dbname>
RIOT_API_KEY=<ta_clé_riot>
SECRET_KEY=<clé_secrète>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 📂 Arborescence du projet

```
app/
├── core/        # Configuration, sécurité
├── models/      # Modèles SQLAlchemy (User, Match)
├── routers/     # Endpoints FastAPI (auth, riot, games)
├── schemas/     # Schémas Pydantic
├── services/    # Fonctions métiers (API Riot, stats...)
└── main.py      # Entrée principale de l’app
```

---

## 📌 À venir

- ✅ Frontend React / Next.js (dashboard utilisateur)
- 📉 Analyse avancée des performances
- 🧪 Tests unitaires
- 🌐 Déploiement complet (VPS / Docker / CI/CD)
