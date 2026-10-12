import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from books.metadata import normalize_isbn, parse_publication


class MetadataUnavailable(Exception):
    pass

def lookup_isbn(value):
    isbn=normalize_isbn(value)
    if not isbn: raise MetadataUnavailable("ISBN is required.")
    if not settings.GOOGLE_BOOKS_API_KEY:
        raise MetadataUnavailable("Google Books is not configured. Use manual entry.")
    try:
        with requests.Session() as session:
            session.mount("https://",HTTPAdapter(max_retries=Retry(total=2,backoff_factor=0.3,status_forcelist=[429,500,502,503,504],allowed_methods=["GET"],respect_retry_after_header=False)))
            response=session.get("https://www.googleapis.com/books/v1/volumes",params={"q":"isbn:"+isbn,"key":settings.GOOGLE_BOOKS_API_KEY,"maxResults":5},timeout=(3,8))
            response.raise_for_status(); payload=response.json()
    except (requests.RequestException,ValueError) as exc:
        raise MetadataUnavailable("Metadata provider unavailable. Use manual entry or retry later.") from exc
    for item in payload.get("items",[]) if isinstance(payload,dict) else []:
        info=item.get("volumeInfo",{})
        matches=False
        for identifier in info.get("industryIdentifiers",[]):
            try:
                matches |= normalize_isbn(identifier.get("identifier")) == isbn
            except ValidationError:
                pass
        if not matches:
            continue
        try: 
            publication, full_date=parse_publication(info.get("publishedDate"))
        except ValidationError:
            publication,full_date="",None
        
        pages=info.get("pageCount")
        image=info.get("imageLinks",{}).get("thumbnail","")
        if image.startswith("http://"):
            image="https://"+image[7:]
        if not image.startswith("https://"):
            image=""
        return {"isbn":isbn,"title":info.get("title","")[:250],"subtitle":info.get("subtitle","")[:250],"authors":"; ".join(info.get("authors") or ["Unknown"]),"description":strip_tags(info.get("description", "")),"publication_text":publication,"published_date":full_date,"page_count":pages if isinstance(pages,int) and pages>0 else None,"image_url":image,"number_of_copies":1}
    raise MetadataUnavailable("No matching ISBN found. Use manual entry.")