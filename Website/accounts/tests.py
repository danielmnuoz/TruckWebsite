from django.test import TestCase
from django.urls import reverse

from login.models import GeneralUser, Sponsor, Driver


class GeneralUserTest(TestCase):
    @classmethod
    def create_general_user(cls):
        GeneralUser.objects.create(user_id=123, email="email1", password="password", user_type=1)

    def test_user_creation(self):
        user = GeneralUser.objects.get(user_id=123)
        field_label = user._meta.get_field('user_id').verbose_name
        self.assertEqual(field_label, 'user_id')


# TODO Fill in
class SponsorTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Sponsor ")
        return Sponsor.objects.create(sponsor_id=123, org_id=123)

    def setUp(self):
        print("setUp: Setup clean data ")
        sponsor = self.setUpTestData()
        self.assertTrue(isinstance(sponsor, Sponsor))

    def test_false_is_false(self):
        print("Method: test_false_is_false.")
        self.assertFalse(False)

    def test_false_is_true(self):
        print("Method: test_false_is_true.")
        self.assertTrue(False)

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)


# TODO Fill in

class SponsorOrg(TestCase):
    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Admin ")

    # return Sponsor.objects.create(sponsor_id=123, org_id=123)

    def setUp(self):
        print("setUp: Setup clean data ")
        sponsorOrg = self.setUpTestData()
        # self.assertTrue(isinstance(admin, Admin))

    def test_false_is_false(self):
        print("Method: test_false_is_false.")
        self.assertFalse(False)

    def test_false_is_true(self):
        print("Method: test_false_is_true.")
        self.assertTrue(False)

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)


# Reference to how class structures can be tested

# class Author(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     date_of_birth = models.DateField(null=True, blank=True)
#     date_of_death = models.DateField('Died', null=True, blank=True)
#
#     def get_absolute_url(self):
#         return reverse('author-detail', args=[str(self.id)])
#
#     def __str__(self):
#         return f'{self.last_name}, {self.first_name}'

# class Driver(models.Model):
#     driver_id = models.IntegerField(db_column='DRIVER_ID', primary_key=True)  # Field name made lowercase.
#     points = models.IntegerField(db_column='POINTS', blank=True, null=True)  # Field name made lowercase.
#     application_id = models.IntegerField(db_column='APPLICATION_ID', blank=True,
#                                          null=True)  # Field name made lowercase.
#     user_id = models.IntegerField(db_column='USER_ID', blank=True, null=True)  # Field name made lowercase.
#
#     class Meta:
#         managed = False
#         db_table = 'DRIVER'

class DriverTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        # ID, Points, Application ID, User ID
        Driver.objects.create(driver_id=1, points=5, application_id=1, user_id=1)

    @classmethod
    def test_first_name_label(self):
        author = Driver.objects.get(user_id=1)
        field_label = author._meta.get_field('driver_id').verbose_name
        self.assertEqual(field_label, 'first name')

    @classmethod
    def test_date_of_death_label(self):
        author = Driver.objects.get(user_id=1)
        field_label = author._meta.get_field('points').verbose_name
        self.assertEqual(field_label, 'died')

    @classmethod
    def test_first_name_max_length(self):
        author = Driver.objects.get(user_id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)

    @classmethod
    def test_object_name_is_last_name_comma_first_name(self):
        author = Driver.objects.get(user_id=1)
        expected_object_name = f'{author.last_name}, {author.first_name}'
        self.assertEqual(str(author), expected_object_name)

    @classmethod
    def test_get_absolute_url(self):
        author = Driver.objects.get(user_id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(author.get_absolute_url(), '/catalog/author/1')


class SignupPageTest(TestCase):

    def setUp(self) -> None:
        self.username = 'testuser'
        self.email = 'testuser@email.com'
        self.age = 20
        self.password = 'somePassword'

    def test_signup_page_status_code(self):
        response = self.client.get('/accounts/signup/')
        self.assertEquals(response.status_code, 200)

    def test_view_url_by_name(self):
        response = self.client.get(reverse('signup'), follow=True)
        self.assertEquals(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('signup'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_signup_form(self):
        response = self.client.post(reverse('signup'), data={
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'password1': self.password,
            'password2': self.password
        })
        self.assertEqual(response.status_code, 302)
