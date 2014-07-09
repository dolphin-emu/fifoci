from django.contrib import admin
from fifoci.models import FifoTest, Result, Version

admin.site.register(FifoTest)
admin.site.register(Result)
admin.site.register(Version)
