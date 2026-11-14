from django.contrib.staticfiles import finders
from django.http import FileResponse, Http404


def manifest(request):
    """Serve the same valid PWA manifest from the root URL."""
    path = finders.find('manifest.json')
    if not path:
        raise Http404('manifest.json topilmadi')

    return FileResponse(
        open(path, 'rb'),
        content_type='application/manifest+json',
    )
