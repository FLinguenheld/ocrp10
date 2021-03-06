# Generated by Django 4.0.5 on 2022-07-02 23:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project_management', '0002_contributor_contributor_unique_contributor'),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('description', models.CharField(blank=True, max_length=2048)),
                ('priority', models.CharField(choices=[('Faible', 'Low'), ('Moyenne', 'Medium'), ('Élevée', 'High')], max_length=25)),
                ('status', models.CharField(choices=[('À faire', 'To Do'), ('En cours', 'In Progress'), ('Terminé', 'Done')], max_length=25)),
                ('tag', models.CharField(choices=[('Bug', 'Bug'), ('Tâche', 'Task'), ('Amélioration', 'Upgrade')], max_length=25)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('assigned_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_to_user', to=settings.AUTH_USER_MODEL)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_creator', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_management.project')),
            ],
        ),
    ]
