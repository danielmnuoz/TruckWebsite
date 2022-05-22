# import pytest_django
import pytest

from django.contrib.auth.models import User


@pytest.fixture
def fixture_1():
    return 1


def test_1(fixture_1):
    assert fixture_1 == 1


@pytest.mark.django_db
def test_database():
    User.objects.create_user('test', 'test@test.com', 'test')
    print('work')
    assert User.objects.count() == 1
