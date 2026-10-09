from books.models import Copy, Event

def issues():
    for copy in Copy.objects.all().iterator():
        loans=list(Event.objects.filter(borrowed_copy=copy,return_date__isnull=True))
        if len(loans)>1: yield f"Copy {copy.pk}: multiple open loans"
        if copy.holder_id and copy.reserved_for_id: yield f"Copy {copy.pk}: borrowed and reserved"
        if bool(copy.holder_id) != bool(loans): yield f"Copy {copy.pk}: holder/open loan mismatch"
        if loans and (not copy.holder_id or loans[0].borrower_id != copy.holder_id): yield f"Copy {copy.pk}: borrower mismatch"
    for loan in Event.objects.filter(borrowed_copy__isnull=True): yield f"Event {loan.pk}: missing copy"
    for loan in Event.objects.filter(borrower__isnull=True,return_date__isnull=True): yield f"Event {loan.pk}: open loan without borrower"