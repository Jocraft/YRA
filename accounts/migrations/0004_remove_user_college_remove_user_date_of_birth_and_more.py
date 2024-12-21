# Generated by Django 4.0.8 on 2024-12-21 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_college_user_date_of_birth_user_enrollment_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='college',
        ),
        migrations.RemoveField(
            model_name='user',
            name='date_of_birth',
        ),
        migrations.RemoveField(
            model_name='user',
            name='program',
        ),
        migrations.AlterField(
            model_name='user',
            name='enrollment_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='ethnicity',
            field=models.CharField(blank=True, choices=[('asian', 'Asian'), ('black', 'Black'), ('hispanic', 'Hispanic'), ('white', 'White'), ('other', 'Other')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='expected_graduation_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='languages_spoken',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='national_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='nationality',
            field=models.CharField(blank=True, choices=[('american', 'American'), ('british', 'British'), ('canadian', 'Canadian'), ('other', 'Other')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='religion',
            field=models.CharField(blank=True, choices=[('christian', 'Christianity'), ('muslim', 'Islam'), ('jewish', 'Judaism'), ('hindu', 'Hinduism'), ('buddhist', 'Buddhism'), ('other', 'Other / Prefer not to say')], max_length=100, null=True),
        ),
    ]