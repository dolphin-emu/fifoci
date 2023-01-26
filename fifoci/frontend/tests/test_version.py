from django.test import TestCase
from fifoci.frontend.models import FifoTest, Result, Type, Version


class JsonVersionTestCase(TestCase):
    def setUp(self):
        self.dff = FifoTest.objects.create(
            file="test.dff", name="Test", shortname="test", active=True, description=""
        )
        self.type = Type.objects.create(type="test")

    def test_json_no_diff(self):
        h1 = "a" * 40
        h2 = "b" * 40

        v1 = Version.objects.create(
            hash=h1, name="v1", parent=None, parent_hash="xxx", submitted=True
        )
        r1 = Result.objects.create(
            dff=self.dff,
            ver=v1,
            type=self.type,
            has_change=True,
            first_result=True,
            hashes="a,b,c,d",
        )

        v2 = Version.objects.create(
            hash=h2, name="v2", parent=v1, parent_hash=h1, submitted=True
        )
        r2 = Result.objects.create(
            dff=self.dff,
            ver=v2,
            type=self.type,
            has_change=False,
            first_result=False,
            hashes="a,b,c,d",
        )

        resp = self.client.get(f"/version/{h1}/json/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

        resp = self.client.get(f"/version/{h2}/json/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

    def test_json_diff(self):
        h1 = "a" * 40
        h2 = "b" * 40

        v1 = Version.objects.create(
            hash=h1, name="v1", parent=None, parent_hash="xxx", submitted=True
        )
        r1 = Result.objects.create(
            dff=self.dff,
            ver=v1,
            type=self.type,
            has_change=True,
            first_result=True,
            hashes="a,b,c,d",
        )

        v2 = Version.objects.create(
            hash=h2, name="v2", parent=v1, parent_hash=h1, submitted=True
        )
        r2 = Result.objects.create(
            dff=self.dff,
            ver=v2,
            type=self.type,
            has_change=True,
            first_result=False,
            hashes="a,x,c,d",
        )

        resp = self.client.get(f"/version/{h1}/json/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

        resp = self.client.get(f"/version/{h2}/json/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            [
                {
                    "type": self.type.type,
                    "dff": self.dff.shortname,
                    "failure": False,
                    "url": f"/compare/{r2.id}-{r1.id}/",
                }
            ],
        )

    def test_json_failure(self):
        h1 = "a" * 40
        h2 = "b" * 40

        v1 = Version.objects.create(
            hash=h1, name="v1", parent=None, parent_hash="xxx", submitted=True
        )
        r1 = Result.objects.create(
            dff=self.dff,
            ver=v1,
            type=self.type,
            has_change=True,
            first_result=True,
            hashes="a,b,c,d",
        )

        v2 = Version.objects.create(
            hash=h2, name="v2", parent=v1, parent_hash=h1, submitted=True
        )
        r2 = Result.objects.create(
            dff=self.dff,
            ver=v2,
            type=self.type,
            has_change=True,
            first_result=False,
            hashes="",
        )

        resp = self.client.get(f"/version/{h1}/json/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

        resp = self.client.get(f"/version/{h2}/json/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            [
                {
                    "type": self.type.type,
                    "dff": self.dff.shortname,
                    "failure": True,
                    "url": f"/compare/{r2.id}-{r1.id}/",
                }
            ],
        )
