from authentication.views import sessions_db, users_db


class GetUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_email = sessions_db.get(token)
        if user_email in users_db and users_db[user_email]['is_active']:
            request.user = users_db[user_email]
            request.token = token
        else:
            request.user = None
            request.token = token

        return self.get_response(request)
