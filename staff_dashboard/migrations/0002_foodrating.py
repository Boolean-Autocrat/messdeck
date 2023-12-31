# Generated by Django 4.2.7 on 2023-11-24 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff_dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=255)),
                ('rating', models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff_dashboard.menu')),
            ],
            options={
                'unique_together': {('menu', 'item')},
            },
        ),
    ]
