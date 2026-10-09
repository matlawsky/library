from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("books","0001_initial"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField(model_name="event",
                            name=name,
                            field=models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                                    null=True,
                                                    blank=True,
                                                    on_delete=django.db.models.deletion.SET_NULL,
                                                    related_name=related)
                                                    ) for name,related in [
                                                        ("issued_by","issued_loans"),
                                                        ("received_by","received_loans")
                                                        ]
                                                        ]