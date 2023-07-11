# Generated by Django 4.2.1 on 2023-05-27 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ceng', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('username', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='GraphUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('graph', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ceng.graph')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ceng.user')),
            ],
        ),
    ]