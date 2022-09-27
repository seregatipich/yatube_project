from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.templates_url_name = (
            reverse('about:author'),
            reverse('about:tech'),
        )

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов."""
        for address in self.templates_url_name:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
