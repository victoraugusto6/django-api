# Generated by Django 4.2 on 2023-04-30 18:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_alter_book_edition_alter_book_publication_year"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="book",
            options={"ordering": ("name",)},
        ),
    ]
