from django.urls import reverse
from django.test import TestCase, Client


class StaticViewsTest(TestCase):

    def test_pages_use_correct_template(self):
        """Проверка шаблонов."""
        self.guest_user = Client()
        self.template_pages_name = {
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech")
        }

        for template, reverse_name in self.template_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_user.get(reverse_name)
                self.assertTemplateUsed(response, template)
