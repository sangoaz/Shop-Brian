"""
Tests de app/main.py : câblage de l'application FastAPI.

On ne re-teste pas la logique métier des routes ici (déjà couverte dans les
autres fichiers de tests/integration/), seulement que l'application démarre
et que les bons routeurs sont bien montés. On vérifie le montage via le
schéma OpenAPI (`/openapi.json`) plutôt qu'en inspectant `app.routes`
directement : la structure interne de `app.routes` dépend de la version de
FastAPI (les routeurs inclus via `include_router` n'y apparaissent pas
toujours comme une liste plate de routes), alors que le schéma OpenAPI
expose une liste de chemins stable et publique.
"""

import pytest

pytestmark = pytest.mark.integration


def test_app_starts_without_error(client):
    # La fixture `client` entre dans le `TestClient` en context manager, ce
    # qui déclenche le `lifespan` défini dans main.py. Si celui-ci levait
    # une exception, ce test échouerait avant même d'atteindre l'assertion.
    response = client.get("/does-not-exist")
    assert response.status_code == 404


def test_auth_router_is_mounted(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/auth/login" in paths
    assert "/auth/me" in paths


def test_admin_collections_router_is_mounted(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/admin/collections" in paths
    assert "/admin/collections/{collection_id}" in paths


def test_admin_clothes_router_is_mounted(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/admin/collections/{collection_id}/clothing" in paths
    assert "/admin/collections/{collection_id}/clothing/{clothing_id}" in paths


def test_public_collections_router_is_mounted(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/collections" in paths
    assert "/collections/{collection_id}" in paths


def test_public_clothes_router_is_mounted(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/clothes" in paths


def test_public_clothes_in_collection_router_is_mounted(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/collections/{collection_id}/clothes" in paths
    assert "/collections/{collection_id}/clothing/{clothing_id}" in paths
