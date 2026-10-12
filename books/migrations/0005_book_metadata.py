import books.metadata
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_stable_cover'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='isbn',
            field=models.CharField(blank=True, max_length=13, null=True, unique=True, validators=[books.metadata.validate_isbn]),
        ),
        migrations.AddField(
            model_name='book',
            name='publication_text',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='book',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='page_count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='published_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='subtitle',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]