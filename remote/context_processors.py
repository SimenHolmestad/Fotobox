from .models import Settings


def contact_information_processor(request):
    settings = Settings.get_or_create_settings()
    return {"contact_first_name": settings.contact_first_name,
            "contact_phone_number": settings.contact_phone_number}
