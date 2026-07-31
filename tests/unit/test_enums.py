"""
Tests des énumérations métier (app/enums.py).

Ces enums héritent à la fois de `str` et de `Enum`. Ce détail a deux
conséquences importantes qu'on vérifie explicitement ici :

1. Une valeur d'enum se compare directement à sa chaîne de caractères
   (`UserRole.ADMIN == "ADMIN"`), ce qui permet de les utiliser telles
   quelles dans du JSON ou une requête SQL sans conversion manuelle.
2. FastAPI/Pydantic peuvent sérialiser ces enums sans configuration
   particulière car elles sont aussi des `str`.
"""

import pytest

from app.enums import Item, Size, UserRole

pytestmark = pytest.mark.unit


class TestUserRole:
    def test_has_a_single_admin_role(self):
        """
        À ce jour, seul le rôle ADMIN existe (voir le commentaire dans
        app/models/user.py). Ce test documente cet état : s'il échoue après
        l'ajout d'un nouveau rôle, c'est le signal qu'il faut aussi mettre à
        jour app/deps/auth.require_admin et les tests associés.
        """
        assert [role.value for role in UserRole] == ["ADMIN"]

    def test_behaves_like_its_string_value(self):
        assert UserRole.ADMIN == "ADMIN"
        assert str(UserRole.ADMIN.value) == "ADMIN"


class TestItem:
    def test_contains_all_expected_categories(self):
        expected = {
            "T_SHIRT",
            "SWEATS",
            "JACKETS",
            "PANTS",
            "SHORTS",
            "UNDERWEAR",
            "ACCESSORIES",
        }
        assert {item.value for item in Item} == expected

    def test_behaves_like_its_string_value(self):
        assert Item.T_SHIRT == "T_SHIRT"


class TestSize:
    def test_contains_all_expected_sizes_in_order(self):
        # L'ordre de définition compte pour l'affichage (ex: sélecteurs de
        # taille côté front) : on le fige ici pour détecter tout réordonnancement
        # accidentel.
        assert [size.value for size in Size] == ["XS", "S", "M", "L", "XL", "XXL"]

    def test_behaves_like_its_string_value(self):
        assert Size.M == "M"

    def test_invalid_size_raises_value_error(self):
        with pytest.raises(ValueError):
            Size("TOO_BIG")
