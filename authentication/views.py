from django.http import JsonResponse
from django.views import View
import secrets
import json

# Хранилище в памяти (вместо БД)
users_db = {}
sessions_db = {}
projects = {
    1: {
        'name': 'Проект А', 'text': 'Текст А',
        'notes': 'text_note C', 'author': 'moderator@mail.ru'
        },
    2: {
        'name': 'Проект Б', 'text': 'Текст Б',
        'notes': 'text_note Б', 'author': 'user@mail.ru'},
    3: {
        'name': 'Проект В', 'text': 'Текст Б',
        'notes': 'text_note В', 'author': 'user@mail.ru'},
}


def init_data():
    """Инициализация тестовых данных."""

    # Тестовые пользователи
    users_db['admin@mail.ru'] = {
        'email': 'admin@mail.ru',
        'password': 'admin123',
        'first_name': 'Иван',
        'last_name': 'Иванов',
        'role': 'admin',
        'is_active': True
    }
    users_db['moderator@mail.ru'] = {
        'email': 'moderator@mail.ru',
        'password': 'moderator123',
        'first_name': 'Василий',
        'last_name': 'Сидоров',
        'role': 'moderator',
        'is_active': True
    }
    users_db['user@mail.ru'] = {
        'email': 'user@mail.ru',
        'password': 'user123',
        'first_name': 'Петр',
        'last_name': 'Петров',
        'role': 'user',
        'is_active': True
    }


init_data()


def get_json_data(request):
    """Функция для получения JSON данных из request."""

    try:
        return json.loads(request.body)
    except:
        return None


class RegisterView(View):
    """Регистрация."""

    def post(self, request):
        data = get_json_data(request)
        email = data.get('email')
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        if not all([email, password, password_confirm]):
            return JsonResponse({'error': 'Все поля обязательны'}, status=400)

        if password != password_confirm:
            return JsonResponse({'error': 'Пароли не совпадают'}, status=400)

        if email in users_db:
            return JsonResponse(
                {'error': 'Пользователь уже существует'}, status=400
                )

        users_db[email] = {
            'email': email, 'password': password,
            'first_name': first_name, 'last_name': last_name,
            'role': 'user', 'is_active': True
        }
        return JsonResponse({'message': 'Регистрация успешна'})


class LoginView(View):
    """Вход."""

    def post(self, request):
        data = get_json_data(request)

        email = data.get('email')
        password = data.get('password')

        user = users_db.get(email)
        for token, email_db in sessions_db.items():
            if email_db == email:
                return JsonResponse(
                    {'error': 'Пользователь уже аутентифицирован'},
                    status=403)
        if not user or not user['is_active']:
            return JsonResponse(
                {'error': 'Пользователь не найден'}, status=401
                )

        if user['password'] != password:
            return JsonResponse({'error': 'Неверный пароль'}, status=400)

        # Генерируем токен
        token = secrets.token_hex(16)
        sessions_db[token] = email

        return JsonResponse({
            'message': 'Вход успешен',
            'user': {
                'email': user['email'],
                'first_name': user['first_name'],
                'token': token,  # Копируем токен в Postman Authorization
                'last_name': user['last_name'],
                'role': user['role']
            }
        })


class LogoutView(View):
    """Выход."""

    def post(self, request):
        if request.token in sessions_db:
            del sessions_db[request.token]
            return JsonResponse({'message': 'Выход успешен'})
        else:
            return JsonResponse(
                {'message': 'Для данного запроса требуется аутентификация'}
                )


class ProfileView(View):
    """Информация о текущем пользователе."""

    def get(self, request, profile_slug):
        print("GET_LOGIN", profile_slug)
        if request.token not in sessions_db:
            return JsonResponse({'error': 'Требуется вход'}, status=401)

        user = users_db.get(profile_slug)
        if user:
            return JsonResponse({
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': user['role']
            })
        else:
            return JsonResponse(
                {'error': 'Пользователь не найден'}, status=401
                )

    def post(self, request, profile_slug):

        if request.token not in sessions_db:
            return JsonResponse({'error': 'Требуется вход'}, status=401)
        data = get_json_data(request)
        user = users_db.get(profile_slug)
        # Обновляем данные

        if request.user['role'] == 'admin':

            if data.get('first_name'):
                user['first_name'] = data['first_name']
            if data.get('last_name'):
                user['last_name'] = data['last_name']
            if data.get('email'):
                user['email'] = data['email']
            if data.get('role'):
                user['role'] = data['role']
            if data.get('is_active'):
                user['is_active'] = data['is_active']
            if data.get('password'):
                user['is_active'] = data['is_active']
            return JsonResponse({'message': 'Профиль обновлен',
                                 'email': user['email'],
                                 'first_name': user['first_name'],
                                 'last_name': user['last_name'],
                                 'role': user['role'],
                                 })

        if any(key in data for key in [
            'email', 'password', 'role', 'is_active'
                ]):
            return JsonResponse({'message': 'У вас нет прав'}, status=403)
        if 'first_name' in data:
            user['first_name'] = data['first_name']
        if 'last_name' in request.POST:
            user['last_name'] = data['last_name']
        return JsonResponse({'message': 'Профиль обновлен',
                             'email': user['email'],
                             'first_name': user['first_name'],
                             'last_name': user['last_name'],
                             'role': user['role']})


class DeleteAccountView(View):
    """Удаление аккаунта."""

    def post(self, request):
        if request.token not in sessions_db:
            return JsonResponse({'error': 'Требуется вход'}, status=401)

        # Мягкое удаление
        request.user['is_active'] = False
        # Выход из системы
        del sessions_db[request.token]
        return JsonResponse({'message': 'Аккаунт удален'})


class ProjectsView(View):
    """Все проекты."""

    def get(self, request):
        return JsonResponse({'projects': projects})


class ProjectDetailView(View):
    """Данные проекта."""

    def get(self, request, project_id):
        """Смотреть проекты могут все пользователи."""

        project = projects.get(project_id)
        return JsonResponse(project, safe=False)

    def post(self, request, project_id):
        """Изменять проект могут пользователи с определенными правами."""

        if request.token not in sessions_db:
            return JsonResponse({'error': 'Требуется вход'}, status=401)

        data = get_json_data(request)

        #  Администратор имеет права на все.
        if users_db.get(sessions_db.get(request.token))['role'] == 'admin':
            if 'name' in data:
                projects.get(project_id)['name'] = data.get('name')
            if 'notes' in data:
                projects.get(project_id)['notes'] = data.get('notes')
            if 'text' in data:
                projects.get(project_id)['text'] = data.get('text')
            return JsonResponse(projects.get(project_id), safe=False)

        #  Модератор может оставлять заметки на постах.
        if users_db.get(sessions_db.get(request.token))['role'] == 'moderator':
            if any(key in data for key in ['text', 'author', 'name']):
                return JsonResponse({'message': 'У вас нет прав'}, status=403)
            projects.get(project_id)['notes'] = data.get('notes')
            return JsonResponse(projects.get(project_id), safe=False)

        #  Пользователь может изменять только свои посты.
        if users_db.get(sessions_db.get(request.token))['role'] == 'user':
            if any(key in data for key in ['author', 'notes']):
                return JsonResponse({'message': 'У вас нет прав'}, status=403)
            elif 'user@mail.ru' == projects.get(project_id)['author']:
                if 'name' in data:
                    projects.get(project_id)['name'] = data.get('name')
                if 'text' in data:
                    projects.get(project_id)['text'] = data.get('text')
                return JsonResponse(projects.get(project_id), safe=False)
            else:
                return JsonResponse({'message': 'У вас нет прав'}, status=403)
