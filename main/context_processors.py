def favorites_count(request):
    favs = request.session.get('favorites', [])
    return {'favorites_count': len(favs)}