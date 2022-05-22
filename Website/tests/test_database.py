import pytest
from django.contrib.auth.models import User

from login.models import GeneralUser


@pytest.fixture
def user_1(db):
    return User.objects.create_user('gav', 'gav@gav.com', 'gav')


@pytest.mark.django_db
def test_pass(user_1):
    user_1.set_password('New password')
    assert user_1.check_password('New password') is True


@pytest.mark.djang_db
def test_general_user(db):
    user = GeneralUser.objects.create(user_id='1', email='test@gmail.com', password='password', user_type='1',
                                      points=10)
