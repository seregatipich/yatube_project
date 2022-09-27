from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.templates_url_name = {
            "about/author.html": "/about/author/",
            "about/tech.html": "/about/tech/",
        }

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов."""
        for address in self.templates_url_name.values():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, address in self.templates_url_name.items():
            with self.subTest(template=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
