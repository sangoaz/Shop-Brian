"""
Ce fichier force l'import RÉEL de tous les modèles SQLModel.

Pourquoi c'est nécessaire :
Certains modèles se référencent mutuellement (ex: Clothing <-> Collection).
Pour éviter un import circulaire, ces références croisées sont déclarées
uniquement sous `TYPE_CHECKING` dans chaque fichier de modèle -- ce qui
veut dire qu'elles ne sont JAMAIS exécutées par Python normalement,
seulement lues par les outils de typage (mypy, autocomplétion).

Conséquence : si rien d'autre n'importe ces fichiers, les classes ne sont
jamais réellement définies en mémoire, et n'apparaissent donc jamais dans
SQLModel.metadata (le registre que create_all() et Alembic autogenerate
utilisent pour savoir quelles tables doivent exister).

Ce fichier existe donc uniquement pour déclencher un vrai `import` de
chaque modèle, une seule fois, au démarrage de l'appli -- pour que le
registre SQLModel.metadata soit toujours complet.
"""

from app.models.user import User
from app.models.collections import Collection, CollectionImage
from app.models.clothes import Clothing, ClothingImage

