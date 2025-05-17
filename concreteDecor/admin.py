from django.contrib import admin


class CustomAdminSite(admin.AdminSite):
    """
    Кастомная панель администратора с аналитикой заказов и клиентов.
    """
    site_header = "Административная панель"
    site_title = "Админ-панель"
    index_title = "Добро пожаловать в админ-панель"

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        allowed_apps = ['api', 'analytics']
        # app_list = [app for app in app_list if app['app_label'] in allowed_apps]
        filtered_app_list = []
        for app in app_list:
            if app['app_label'] not in allowed_apps:
                continue

            if app['app_label'] == 'api':
                filtered_models = [
                    model for model in app['models']
                    if model['object_name'] in ['Product', 'Order', 'CustomUser', 'PromoCode']  # здесь указываем нужные модели
                ]
                app['models'] = filtered_models

            # Исключаем приложения без моделей после фильтрации
            if len(app['models']) > 0:
                filtered_app_list.append(app)

        # Сортируем приложения так, чтобы первым шёл 'api', а потом 'analytics'
        def sort_key(app):
            return 0 if app['app_label'] == 'api' else 1

        app_list.sort(key=sort_key)
        return app_list


admin_site = CustomAdminSite(name="admin")
