from django.contrib import admin


class CustomAdminSite(admin.AdminSite):
    """
    Кастомная панель администратора с аналитикой заказов и клиентов.
    """
    site_header = "Административная панель"
    site_title = "Админ-панель"
    index_title = "Добро пожаловать в админ-панель"

    def get_app_list(self, request, app_label=None):
        # Получаем стандартный список приложений
        app_list = super().get_app_list(request, app_label)
        # Список разрешённых приложений (app_label)
        allowed_apps = ['api', 'analytics']
        # Фильтруем приложения: оставляем только те, что входят в allowed_apps
        app_list = [app for app in app_list if app['app_label'] in allowed_apps]

        # Сортируем приложения так, чтобы первым шёл 'api', а потом 'analytics'
        def sort_key(app):
            return 0 if app['app_label'] == 'api' else 1

        app_list.sort(key=sort_key)
        return app_list


admin_site = CustomAdminSite(name="admin")
