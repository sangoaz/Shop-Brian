# shop_brian — API e-commerce streetwear

Backend FastAPI (SQLModel + PostgreSQL) pour le lancement de la marque : catalogue de collections et vêtements, authentification admin par JWT.

## Stack

- FastAPI
- SQLModel / SQLAlchemy
- PostgreSQL (via Docker en local)
- Alembic pour les migrations
- JWT (python-jose) pour l'authentification

## Installation

1. Créer et activer un environnement virtuel, installer les dépendances :

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Lancer la base de données locale :

```
docker compose up -d
```

3. Créer un fichier `.env` à la racine (voir section Configuration).

4. Appliquer les migrations :

```
alembic upgrade head
```

5. Créer le compte admin :

```
python3 create_admin.py
```

6. Lancer l'API :

```
uvicorn app.main:app --reload
```

## Configuration (`.env`)

| Variable | Rôle | Obligatoire |
|---|---|---|
| `DATABASE_URL` | URL de connexion PostgreSQL | Oui, pour lancer l'API |
| `SECRET_KEY` | Clé de signature des JWT | Oui, pour lancer l'API |
| `ADMIN_EMAIL` | Email du compte admin créé par `create_admin.py` | Uniquement pour lancer `create_admin.py` |
| `ADMIN_PASSWORD` | Mot de passe du compte admin créé par `create_admin.py` | Uniquement pour lancer `create_admin.py` |

`.env` ne doit jamais être committé (il est exclu via `.gitignore`).

### À propos de `SECRET_KEY`

`SECRET_KEY` sert à signer et vérifier les tokens JWT utilisés pour l'authentification (algorithme HS256, symétrique : la même clé signe et vérifie un token). Quiconque connaît cette valeur peut fabriquer un token valide pour n'importe quel utilisateur, y compris un compte admin — ce n'est donc pas un simple paramètre de configuration, c'est ce qui protège l'accès à toute l'administration du site.

Ne jamais utiliser une valeur devinable ou un texte descriptif (par exemple `"une_valeur_secrete_aleatoire"` n'est pas une valeur aléatoire, c'est une description). Générer une vraie valeur aléatoire avec suffisamment d'entropie :

```
openssl rand -hex 32
```

Coller le résultat tel quel comme valeur de `SECRET_KEY` dans le `.env`.

Chaque environnement (développement local, staging, production) doit avoir sa **propre** valeur de `SECRET_KEY`, jamais partagée entre eux. Si la clé utilisée en développement venait à fuiter (commit accidentel, log, partage), une clé distincte en production limite le dégât à l'environnement compromis au lieu de compromettre le site en ligne.

## Tests

```
pytest
```
