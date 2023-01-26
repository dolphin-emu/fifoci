from django.test import Client, TestCase


class StaticTestCase(TestCase):
    def test_home(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_dff(self):
        resp = self.client.get("/dff/")
        self.assertEqual(resp.status_code, 200)

    def test_existing_images(self):
        resp = self.client.get("/existing-images/")
        self.assertEqual(resp.status_code, 200)

    def test_about(self):
        resp = self.client.get("/about/")
        self.assertEqual(resp.status_code, 200)
