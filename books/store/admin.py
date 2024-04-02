from django.contrib import admin

from store.models import Book

# Register your models here.
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass

