from django.test import TestCase
from fifoci.frontend.models import FifoTest


class DffApiTestCase(TestCase):
    def test_empty(self):
        resp = self.client.get("/dff/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

    def test_filled(self):
        FifoTest.objects.create(
            file="test1.dff",
            name="Test 1",
            shortname="test1",
            active=True,
            description="",
        )

        FifoTest.objects.create(
            file="test2.dff",
            name="Test 2",
            shortname="test2",
            active=True,
            description="",
        )

        resp = self.client.get("/dff/")
        self.assertEqual(resp.status_code, 200)

        l = resp.json()

        self.assertTrue(all("url" in e for e in l))
        for e in l:
            del e["url"]

        self.assertCountEqual(
            l,
            (
                {"shortname": "test1", "filename": "test1.dff"},
                {"shortname": "test2", "filename": "test2.dff"},
            ),
        )

    def test_inactive(self):
        FifoTest.objects.create(
            file="inactive.dff",
            name="Inactive",
            shortname="inactive",
            active=False,
            description="",
        )

        resp = self.client.get("/dff/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])
