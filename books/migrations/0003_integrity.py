from django.db import migrations, models
import django.db.models.deletion

def preflight(apps,schema_editor):
    Copy=apps.get_model("books","Copy"); Event=apps.get_model("books","Event")
    alias=schema_editor.connection.alias
    copies=Copy.objects.using(alias); events=Event.objects.using(alias)
    if copies.filter(holder__isnull=False,reserved_for__isnull=False).exists():
        raise RuntimeError("Run audit_circulation and resolve borrowed/reserved conflicts.")
    duplicates=events.filter(return_date__isnull=True,borrowed_copy__isnull=False).values("borrowed_copy").annotate(n=models.Count("id")).filter(n__gt=1)
    if duplicates.exists():
        raise RuntimeError("Run audit_circulation and resolve duplicate open loans.")
    if events.filter(return_date__lt=models.F("borrow_date")).exists():
        raise RuntimeError("Resolve invalid historical dates before migration.")

class Migration(migrations.Migration):
    dependencies=[("books","0002_loan_operators")]
    operations=[
        migrations.RunPython(preflight,migrations.RunPython.noop),
        migrations.AlterField(model_name="copy",
                              name="book",
                              field=models.ForeignKey(to="books.book",on_delete=django.db.models.deletion.PROTECT)),
        migrations.AlterField(model_name="event",
                              name="borrowed_copy",
                              field=models.ForeignKey(to="books.copy",null=True,blank=True,related_name="borrowed_copy",
                                                      on_delete=django.db.models.deletion.PROTECT)),
        migrations.AddConstraint(model_name="copy",
                                 constraint=models.CheckConstraint(check=models.Q(holder__isnull=True)|models.Q(reserved_for__isnull=True),
                                                                   name="copy_not_both_borrowed_reserved")),
        migrations.AddConstraint(model_name="event",
                                 constraint=models.UniqueConstraint(fields=["borrowed_copy"],
                                                                    condition=models.Q(return_date__isnull=True,
                                                                                       borrowed_copy__isnull=False),
                                                                    name="one_open_loan_per_copy")),
        migrations.AddConstraint(model_name="event",
                                 constraint=models.CheckConstraint(check=models.Q(return_date__isnull=True)|models.Q(return_date__gte=models.F("borrow_date")),
                                                                   name="loan_dates_ordered")),
    ]