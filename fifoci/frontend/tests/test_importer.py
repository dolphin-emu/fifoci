from django.core.files.storage import default_storage
from django.test import TestCase
from fifoci.frontend import importer
from fifoci.frontend.models import FifoTest, Result, Type, Version

import io


class FindFirstParentTestCase(TestCase):
    def setUp(self):
        hashes = ["1" * 40, "2" * 40, "3" * 40, "4" * 40]

        parent = None
        parent_hash = "0" * 40
        for i, h in enumerate(hashes):
            v = Version.objects.create(
                hash=h,
                name=f"v{i+1}",
                parent=parent,
                parent_hash=parent_hash,
                submitted=True,
            )
            parent = v
            parent_hash = h

    def test_no_parent(self):
        parent, parent_hash = importer.find_first_parent(["6" * 40, "5" * 40])
        self.assertIsNone(parent)
        self.assertEqual(parent_hash, "6" * 40)

    def test_one_parent(self):
        parent, parent_hash = importer.find_first_parent(["6" * 40, "3" * 40])
        self.assertEqual(parent.name, "v3")
        self.assertEqual(parent_hash, parent.hash)
        self.assertEqual(parent_hash, "3" * 40)

    def test_first_parent(self):
        parent, parent_hash = importer.find_first_parent(["6" * 40, "3" * 40, "2" * 40])
        self.assertEqual(parent.name, "v3")
        self.assertEqual(parent_hash, parent.hash)
        self.assertEqual(parent_hash, "3" * 40)


class GetOrCreateVerTestCase(TestCase):
    def test_create_dup(self):
        rev = {
            "hash": "a" * 40,
            "name": "test",
            "submitted": True,
            "parents": ["0" * 40],
        }
        v1, _ = importer.get_or_create_ver(rev)
        v2, _ = importer.get_or_create_ver(rev)
        self.assertEqual(v1.id, v2.id)

        self.assertEqual(v1.hash, "a" * 40)
        self.assertEqual(v1.name, "test")
        self.assertEqual(v1.submitted, True)

    def test_finds_parent(self):
        r1 = {
            "hash": "a" * 40,
            "name": "test",
            "submitted": True,
            "parents": ["0" * 40],
        }
        r2 = {
            "hash": "b" * 40,
            "name": "test 2",
            "submitted": True,
            "parents": ["a" * 40],
        }

        v1, v1p = importer.get_or_create_ver(r1)
        v2, v2p = importer.get_or_create_ver(r2)

        self.assertIsNone(v1p)
        self.assertNotEqual(v1.id, v2.id)
        self.assertEqual(v2p.id, v1.id)


class ImportResultTestCase(TestCase):
    def setUp(self):
        self.dff = FifoTest.objects.create(
            file="test.dff", name="Test", shortname="test", active=True, description=""
        )
        self.type = Type.objects.create(type="test")

        self.parent, _ = importer.get_or_create_ver(
            {
                "hash": "a" * 40,
                "name": "parent",
                "submitted": True,
                "parents": ["0" * 40],
            }
        )
        self.ver, _ = importer.get_or_create_ver(
            {
                "hash": "b" * 40,
                "name": "testver",
                "submitted": True,
                "parents": ["a" * 40],
            }
        )

    def test_import_new(self):
        meta = {"failure": False, "hashes": ["0" * 40, "1" * 40]}
        images = {"0" * 40: io.BytesIO(b"img0"), "1" * 40: io.BytesIO(b"img1")}
        res = importer.import_result(
            self.dff, self.type, self.ver, self.parent, meta, images
        )

        self.assertEqual(res.dff.id, self.dff.id)
        self.assertEqual(res.type.id, self.type.id)
        self.assertEqual(res.ver.id, self.ver.id)
        self.assertEqual(res.first_result, True)
        self.assertEqual(res.has_change, False)
        self.assertEqual(res.hashes, f"{'0'*40},{'1'*40}")

        with default_storage.open(f"/results/{'0'*40}.png") as fp:
            self.assertEqual(fp.read(), b"img0")

        with default_storage.open(f"/results/{'1'*40}.png") as fp:
            self.assertEqual(fp.read(), b"img1")

    def test_import_failure(self):
        meta = {"failure": True, "hashes": []}
        images = {}
        res = importer.import_result(
            self.dff, self.type, self.ver, self.parent, meta, images
        )

        self.assertEqual(res.first_result, True)
        self.assertEqual(res.has_change, False)
        self.assertEqual(res.hashes, "")

    def test_import_dupe(self):
        meta = {"failure": False, "hashes": ["0" * 40, "1" * 40]}
        images = {"0" * 40: io.BytesIO(b"img0"), "1" * 40: io.BytesIO(b"img1")}
        res1 = importer.import_result(
            self.dff, self.type, self.ver, self.parent, meta, images
        )

        res2 = importer.import_result(
            self.dff, self.type, self.ver, self.parent, meta, images
        )

        self.assertEqual(res1.id, res2.id)

    def test_import_skip_known_images(self):
        meta = {"failure": False, "hashes": ["0" * 40, "1" * 40]}
        images = {"0" * 40: io.BytesIO(b"img0"), "1" * 40: io.BytesIO(b"img1")}
        res1 = importer.import_result(
            self.dff, self.type, self.ver, self.parent, meta, images
        )

        res2 = importer.import_result(
            self.dff, self.type, self.ver, self.parent, meta, {}
        )

        self.assertEqual(res1.id, res2.id)

    def test_import_no_change(self):
        meta = {"failure": False, "hashes": ["0" * 40, "1" * 40]}
        images = {"0" * 40: io.BytesIO(b"img0"), "1" * 40: io.BytesIO(b"img1")}
        res1 = importer.import_result(
            self.dff, self.type, self.parent, None, meta, images
        )
        self.assertEqual(res1.first_result, True)
        self.assertEqual(res1.has_change, False)

        res2 = importer.import_result(
            self.dff, self.type, self.ver, self.parent, meta, images
        )
        self.assertEqual(res2.first_result, False)
        self.assertEqual(res2.has_change, False)

    def test_import_has_change(self):
        meta = {"failure": False, "hashes": ["0" * 40, "1" * 40]}
        images = {"0" * 40: io.BytesIO(b"img0"), "1" * 40: io.BytesIO(b"img1")}
        res1 = importer.import_result(
            self.dff, self.type, self.parent, None, meta, images
        )
        self.assertEqual(res1.first_result, True)
        self.assertEqual(res1.has_change, False)

        meta["hashes"][0] = "2" * 40
        images["2" * 40] = io.BytesIO(b"img2")
        res2 = importer.import_result(
            self.dff, self.type, self.ver, self.parent, meta, images
        )
        self.assertEqual(res2.first_result, False)
        self.assertEqual(res2.has_change, True)
