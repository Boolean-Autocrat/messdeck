# Generated by Django 4.2.7 on 2024-01-07 08:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff_dashboard', '0007_remove_menu_breakfast_remove_menu_dinner_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='food',
            name='rating',
        ),
    ]