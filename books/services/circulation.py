from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.utils import timezone
from books.models import Copy, Event

def require_staff(actor):
    if not actor.is_authenticated or not actor.is_active or not actor.is_staff:
        raise PermissionDenied

@transaction.atomic
def transition(copy_id, actor, action, state=None):
    if not actor.is_authenticated or not actor.is_active:
        raise PermissionDenied
    copy = Copy.objects.select_for_update().get(pk=copy_id)
    if action in {"borrow", "return"} or state is not None:
        require_staff(actor)
    if action == "reserve":
        if copy.holder_id or copy.reserved_for_id:
            raise ValidationError("This copy is unavailable.")
        copy.reserved_for = actor
    elif action == "cancel":
        if not copy.reserved_for_id:
            raise ValidationError("No active reservation.")
        if copy.reserved_for_id != actor.pk and not actor.is_staff:
            raise PermissionDenied
        copy.reserved_for = None
    elif action == "borrow":
        if copy.holder_id or not copy.reserved_for_id:
            raise ValidationError("An available reservation is required.")
        if not copy.reserved_for.is_active:
            raise ValidationError("Reader account is inactive.")
        Event.objects.create(borrowed_copy=copy,borrower=copy.reserved_for,issued_by=actor)
        copy.holder = copy.reserved_for
        copy.reserved_for = None
    elif action == "return":
        loan = Event.objects.filter(borrowed_copy=copy,return_date__isnull=True).first()
        if not copy.holder_id or not loan or loan.borrower_id != copy.holder_id:
            raise ValidationError("No consistent active loan. Ask staff to audit this copy.")
        loan.return_date = timezone.localdate()
        loan.received_by = actor
        loan.save(update_fields=["return_date","received_by"])
        copy.holder = None
    else:
        raise ValidationError("Unknown action.")
    if state is not None:
        copy.state = state
    copy.save()
    return copy