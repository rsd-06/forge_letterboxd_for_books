from .gemini_service import is_gemini_configured
from .models import ReadList


def global_context(request):
    context = {
        'is_gemini_configured': is_gemini_configured(),
        'app_name': 'Bookboxd',
    }
    if request.user.is_authenticated:
        # Preload user's shelves for rapid header/modal access
        context['user_shelves'] = ReadList.objects.filter(user=request.user)
    return context
