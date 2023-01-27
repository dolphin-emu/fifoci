from django.conf import settings
from django.test.runner import DiscoverRunner


class TestRunner(DiscoverRunner):
    def setup_test_environment(self):
        super().setup_test_environment()

        settings.DEFAULT_FILE_STORAGE = "inmemorystorage.InMemoryStorage"
