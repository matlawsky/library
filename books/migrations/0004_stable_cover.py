from django.db import migrations,models
class Migration(migrations.Migration):
    dependencies=[("books","0003_integrity")]
    operations=[migrations.AlterField(model_name="book",
                                      name="image_url",
                                      field=models.URLField(blank=True,default=""))]