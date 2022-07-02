# Generated by Django 4.0.5 on 2022-07-02 23:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project_management', '0003_issue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributor',
            name='permission',
            field=models.CharField(choices=[('Créateur', 'Creator'), ('Contributeur', 'Contributor')], default='Contributeur', max_length=50),
        ),
        migrations.AlterField(
            model_name='issue',
            name='priority',
            field=models.CharField(choices=[('Faible', 'Low'), ('Moyenne', 'Medium'), ('Élevée', 'High')], max_length=50),
        ),
        migrations.AlterField(
            model_name='issue',
            name='status',
            field=models.CharField(choices=[('À faire', 'To Do'), ('En cours', 'In Progress'), ('Terminé', 'Done')], max_length=50),
        ),
        migrations.AlterField(
            model_name='issue',
            name='tag',
            field=models.CharField(choices=[('Bug', 'Bug'), ('Tâche', 'Task'), ('Amélioration', 'Upgrade')], max_length=50),
        ),
        migrations.AlterField(
            model_name='project',
            name='type',
            field=models.CharField(choices=[('Back-end', 'Back End'), ('Front-end', 'Front End'), ('iOS', 'Ios'), ('Android', 'Android')], max_length=50),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=2048)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_management.issue')),
            ],
        ),
    ]