# Generated by Django 4.2.7 on 2023-12-26 08:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('staff_dashboard', '0004_alter_menu_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foodrating',
            name='ratings',
        ),
        migrations.AddField(
            model_name='foodrating',
            name='rating',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='foodrating',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='foodrating',
            constraint=models.CheckConstraint(check=models.Q(('rating__gte', 1), ('rating__lte', 5)), name='rating_range'),
        ),
    ]
