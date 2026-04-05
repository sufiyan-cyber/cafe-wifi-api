import os
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['API_KEY'] = 'defaultkey'  # force test key before main.py loads

from main import app, db
import pytest


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app.test_client()


# ── Public Routes ────────────────────────────────────────────

def test_home(client):
    res = client.get('/')
    assert res.status_code == 200  # just checks page loads


def test_get_all_cafes_empty(client):
    res = client.get('/all')
    assert res.status_code == 200
    data = res.get_json()
    assert 'cafes' in data
    assert 'total' in data
    assert 'page' in data
    assert 'pages' in data


def test_get_all_cafes_pagination(client):
    res = client.get('/all?page=1&per_page=5')
    assert res.status_code == 200
    data = res.get_json()
    assert len(data['cafes']) <= 5


def test_random_cafe_empty_db(client):
    res = client.get('/random')
    assert res.status_code == 404


def test_search_no_results(client):
    res = client.get('/search?location=NonExistentPlace')
    assert res.status_code == 404


def test_locations_empty(client):
    res = client.get('/locations')
    assert res.status_code == 200
    data = res.get_json()
    assert 'locations' in data


# ── Auth Protection Tests ────────────────────────────────────

def test_add_cafe_no_auth(client):
    res = client.post('/add', json={
        'name': 'Test Cafe',
        'location': 'Koramangala'
    })
    assert res.status_code == 403


def test_delete_no_auth(client):
    res = client.delete('/report-closed/1')
    assert res.status_code == 403


def test_update_price_no_auth(client):
    res = client.patch('/update-price/1?new_cost=500')
    assert res.status_code == 403


# ── Admin Routes with valid key ──────────────────────────────

def test_add_cafe_with_auth(client):
    res = client.post('/add',
        json={
            'name': 'Test Cafe',
            'location': 'Koramangala',
            'online_order': True,
            'book_table': False,
            'rate': 4.3,
            'votes': 100,
            'rest_type': 'Cafe',
            'cuisines': 'Coffee, Continental',
            'dish_liked': 'Cold Brew',
            'approx_cost': 500,
            'listed_in_type': 'Cafes',
            'listed_in_city': 'Koramangala'
        },
        headers={'Authorization': 'Bearer defaultkey'}
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data['cafe']['name'] == 'Test Cafe'
    assert data['cafe']['location'] == 'Koramangala'


def test_delete_nonexistent_cafe(client):
    res = client.delete('/report-closed/9999',
        headers={'Authorization': 'Bearer defaultkey'}
    )
    assert res.status_code == 404


def test_update_price_nonexistent(client):
    res = client.patch('/update-price/9999?new_cost=500',
        headers={'Authorization': 'Bearer defaultkey'}
    )
    assert res.status_code == 404


def test_add_then_delete(client):
    res = client.post('/add',
        json={'name': 'Delete Me', 'location': 'HSR Layout'},
        headers={'Authorization': 'Bearer defaultkey'}
    )
    assert res.status_code == 201
    cafe_id = res.get_json()['cafe']['id']

    res = client.delete(f'/report-closed/{cafe_id}',
        headers={'Authorization': 'Bearer defaultkey'}
    )
    assert res.status_code == 200


def test_add_missing_required_fields(client):
    res = client.post('/add',
        json={'name': 'No Location Cafe'},
        headers={'Authorization': 'Bearer defaultkey'}
    )
    assert res.status_code == 400