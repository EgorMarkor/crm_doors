from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.models import DeliveryRequest, InstallationRequest, User


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    user: User = request.user
    now = timezone.now()
    upcoming_installations = (
        InstallationRequest.objects.filter(scheduled_for__gte=now).order_by('scheduled_for')[:5]
    )
    upcoming_deliveries = (
        DeliveryRequest.objects.filter(scheduled_for__gte=now).order_by('scheduled_for')[:5]
    )
    context = {
        'upcoming_installations': upcoming_installations,
        'upcoming_deliveries': upcoming_deliveries,
        'soon_window': now + timedelta(days=7),
    }
    if user.is_owner():
        return render(request, 'core/dashboard_owner.html', context)
    if user.is_manager():
        return render(request, 'core/dashboard_manager.html', context)
    if user.is_installer():
        my_installations = (
            InstallationRequest.objects.filter(installer=user, scheduled_for__gte=now)
            .order_by('scheduled_for')[:5]
        )
        context.update({'my_installations': my_installations})
        return render(request, 'core/dashboard_installer.html', context)
    if user.is_delivery():
        my_deliveries = (
            DeliveryRequest.objects.filter(courier=user, scheduled_for__gte=now).order_by('scheduled_for')[:5]
        )
        context.update({'my_deliveries': my_deliveries})
        return render(request, 'core/dashboard_delivery.html', context)
    return render(request, 'core/dashboard_owner.html', context)


@login_required
def installation_requests(request: HttpRequest) -> HttpResponse:
    user: User = request.user
    if user.is_manager():
        qs = InstallationRequest.objects.filter(manager=user)
    elif user.is_installer():
        qs = InstallationRequest.objects.filter(installer=user)
    elif user.is_owner():
        qs = InstallationRequest.objects.all()
    else:
        return redirect('dashboard')
    return render(request, 'core/installation_requests.html', {'requests': qs})


@login_required
def delivery_requests(request: HttpRequest) -> HttpResponse:
    user: User = request.user
    if user.is_manager():
        qs = DeliveryRequest.objects.filter(manager=user)
    elif user.is_delivery():
        qs = DeliveryRequest.objects.filter(courier=user)
    elif user.is_owner():
        qs = DeliveryRequest.objects.all()
    else:
        return redirect('dashboard')
    return render(request, 'core/delivery_requests.html', {'requests': qs})


@login_required
def free_installation_requests(request: HttpRequest) -> HttpResponse:
    user: User = request.user
    if not (user.is_installer() or user.is_owner()):
        return redirect('dashboard')
    qs = InstallationRequest.objects.filter(installer__isnull=True)
    return render(request, 'core/free_requests.html', {'requests': qs, 'type': 'installation'})


@login_required
def free_delivery_requests(request: HttpRequest) -> HttpResponse:
    user: User = request.user
    if not (user.is_delivery() or user.is_owner()):
        return redirect('dashboard')
    qs = DeliveryRequest.objects.filter(courier__isnull=True)
    return render(request, 'core/free_requests.html', {'requests': qs, 'type': 'delivery'})


@login_required
def claim_installation(request: HttpRequest, request_id: int) -> HttpResponse:
    user: User = request.user
    if not (user.is_installer() or user.is_owner()):
        return redirect('free_installation_requests')
    installation_request = get_object_or_404(InstallationRequest, pk=request_id, installer__isnull=True)
    installation_request.installer = user
    installation_request.status = 'Назначен установщик'
    installation_request.save()
    return redirect('installation_requests')


@login_required
def claim_delivery(request: HttpRequest, request_id: int) -> HttpResponse:
    user: User = request.user
    if not (user.is_delivery() or user.is_owner()):
        return redirect('free_delivery_requests')
    delivery_request = get_object_or_404(DeliveryRequest, pk=request_id, courier__isnull=True)
    delivery_request.courier = user
    delivery_request.status = 'Назначен доставщик'
    delivery_request.save()
    return redirect('delivery_requests')


@login_required
def placeholder_section(request: HttpRequest, section: str) -> HttpResponse:
    user: User = request.user
    if user.is_owner():
        allowed_sections = {'leads', 'managers', 'sales', 'site', 'production', 'finance'}
    elif user.is_manager():
        allowed_sections = {'leads', 'sales'}
    else:
        return redirect('dashboard')
    if section not in allowed_sections:
        return redirect('dashboard')
    sections = {
        'leads': {
            'title': 'Лиды',
            'subtitle': 'Статистика по новым обращениям и скорости обработки.',
            'period': 'Последние 30 дней',
            'kpis': [
                {'title': 'Новые лиды', 'value': '248', 'note': '+18% к прошлому месяцу'},
                {'title': 'Конверсия в сделку', 'value': '24%', 'note': 'Рост на 3 п.п.'},
                {'title': 'Среднее время ответа', 'value': '12 мин', 'note': 'SLA < 15 мин'},
                {'title': 'Стоимость лида', 'value': '820 ₽', 'note': '−6% за неделю'},
            ],
            'table_title': 'Последние лиды',
            'table_headers': ['Клиент', 'Канал', 'Статус', 'Ответственный'],
            'table_rows': [
                ['Ирина Власова', 'Сайт', 'В работе', 'Виктор С.'],
                ['ООО «Гарден»', 'Реклама', 'Назначена встреча', 'Мария К.'],
                ['Максим Павлов', 'Рекомендация', 'Договор', 'Артем И.'],
                ['Анна Литвинова', 'Колл-центр', 'Нужен звонок', 'Светлана М.'],
            ],
            'insight_title': 'Фокусы команды',
            'insights': [
                {'title': 'Реклама', 'value': '72 лида / 2,1% конверсия'},
                {'title': 'Рекомендации', 'value': '18 лидов / 41% конверсия'},
                {'title': 'Колл-центр', 'value': '53 лида / 19% конверсия'},
                {'title': 'Партнеры', 'value': '12 лидов / 33% конверсия'},
            ],
            'list_title': '',
            'list_items': [],
        },
        'managers': {
            'title': 'Менеджеры',
            'subtitle': 'Загрузка и эффективность менеджерского состава.',
            'period': 'Текущая неделя',
            'kpis': [
                {'title': 'Активные менеджеры', 'value': '12', 'note': '2 новых сотрудника'},
                {'title': 'Средний чек', 'value': '48 000 ₽', 'note': 'План 45 000 ₽'},
                {'title': 'Встречи запланированы', 'value': '31', 'note': '60% от цели'},
                {'title': 'Закрыто сделок', 'value': '14', 'note': 'Рекорд недели'},
            ],
            'table_title': 'Рейтинг по продажам',
            'table_headers': ['Менеджер', 'Сделки', 'Выручка', 'Конверсия'],
            'table_rows': [
                ['Мария К.', '7', '312 000 ₽', '29%'],
                ['Артем И.', '5', '224 000 ₽', '25%'],
                ['Виктор С.', '4', '198 000 ₽', '22%'],
                ['Светлана М.', '3', '156 000 ₽', '19%'],
            ],
            'insight_title': 'Статусы нагрузки',
            'insights': [
                {'title': 'Пиковая загрузка', 'value': 'Мария К. — 9 сделок'},
                {'title': 'Нужна поддержка', 'value': 'Светлана М. — 2 сделки'},
                {'title': 'Лучший SLA', 'value': 'Виктор С. — 7 мин'},
                {'title': 'Обучение', 'value': '2 новых менеджера'},
            ],
            'list_title': '',
            'list_items': [],
        },
        'sales': {
            'title': 'Продажи',
            'subtitle': 'Актуальные показатели воронки и выручки.',
            'period': 'Март 2024',
            'kpis': [
                {'title': 'Выручка месяца', 'value': '4,2 млн ₽', 'note': '+12% к февралю'},
                {'title': 'Средний цикл сделки', 'value': '9 дней', 'note': 'Цель 10 дней'},
                {'title': 'Коммерческих предложений', 'value': '52', 'note': '18 на подписи'},
                {'title': 'Потеряно сделок', 'value': '8', 'note': 'Основная причина — цена'},
            ],
            'table_title': 'Воронка продаж',
            'table_headers': ['Этап', 'Кол-во', 'Сумма', 'Конверсия'],
            'table_rows': [
                ['Новые лиды', '248', '—', '100%'],
                ['Квалификация', '120', '—', '48%'],
                ['Замер', '64', '2,1 млн ₽', '53%'],
                ['Договор', '32', '1,4 млн ₽', '50%'],
            ],
            'insight_title': 'Заметки аналитики',
            'insights': [
                {'title': 'Лучший канал', 'value': 'Сайт — 1,7 млн ₽'},
                {'title': 'Причина потерь', 'value': 'Цена — 5 сделок'},
                {'title': 'Upsell', 'value': '+12% к среднему чеку'},
                {'title': 'Ожидаемые поступления', 'value': '1,1 млн ₽'},
            ],
            'list_title': '',
            'list_items': [],
        },
        'site': {
            'title': 'Сайт и ИИ',
            'subtitle': 'Привлечение трафика и эффективность автоответов.',
            'period': 'Последние 7 дней',
            'kpis': [
                {'title': 'Посещения сайта', 'value': '18 420', 'note': '+9%'},
                {'title': 'Лидов с сайта', 'value': '136', 'note': 'Конверсия 0,74%'},
                {'title': 'Чат-ботов', 'value': '82', 'note': '87% автоответов'},
                {'title': 'Рейтинг контента', 'value': '4,7', 'note': 'Отзывы клиентов'},
            ],
            'table_title': 'Источники трафика',
            'table_headers': ['Источник', 'Сеансы', 'Конверсия', 'Лиды'],
            'table_rows': [
                ['Органика', '7 840', '0,9%', '71'],
                ['Реклама', '6 120', '0,6%', '37'],
                ['Соцсети', '2 340', '0,4%', '10'],
                ['Партнеры', '1 120', '1,6%', '18'],
            ],
            'insight_title': 'ИИ-метрики',
            'insights': [
                {'title': 'Сценарии в топе', 'value': 'Доставка / Установка'},
                {'title': 'Среднее время ответа', 'value': '8 сек'},
                {'title': 'Нераспознанные запросы', 'value': '6%'},
                {'title': 'Удовлетворенность', 'value': '92%'},
            ],
            'list_title': '',
            'list_items': [],
        },
        'production': {
            'title': 'Производство и 1С',
            'subtitle': 'Контроль заказов, закупок и складских остатков.',
            'period': 'На сегодня',
            'kpis': [
                {'title': 'Заказы в производстве', 'value': '34', 'note': '7 на запуске'},
                {'title': 'Средний срок', 'value': '4 дня', 'note': 'Цель 5 дней'},
                {'title': 'Брак', 'value': '1,2%', 'note': 'Норма 1,5%'},
                {'title': 'Остатки склада', 'value': '2,8 млн ₽', 'note': '−4%'},
            ],
            'table_title': 'План производства',
            'table_headers': ['Заказ', 'Статус', 'Срок', 'Ответственный'],
            'table_rows': [
                ['№1245/К', 'В раскрое', '12.03', 'Смена 2'],
                ['№1249/А', 'Сборка', '13.03', 'Смена 1'],
                ['№1251/Б', 'Покраска', '14.03', 'Смена 3'],
                ['№1253/К', 'Контроль', '14.03', 'ОТК'],
            ],
            'insight_title': 'Сводка 1С',
            'insights': [
                {'title': 'Закупки на неделе', 'value': '640 000 ₽'},
                {'title': 'Материалы критично', 'value': 'Петли, пена'},
                {'title': 'Выпуск вчера', 'value': '12 изделий'},
                {'title': 'Заявки отгрузки', 'value': '9'},
            ],
            'list_title': '',
            'list_items': [],
        },
        'finance': {
            'title': 'Финансы',
            'subtitle': 'Основные расходы и баланс компании.',
            'period': 'Февраль 2024',
            'kpis': [
                {'title': 'Выручка', 'value': '5,1 млн ₽', 'note': '+8% к январю'},
                {'title': 'Расходы', 'value': '2,4 млн ₽', 'note': '62% от выручки'},
                {'title': 'Маржа', 'value': '2,7 млн ₽', 'note': 'Цель 2,5 млн ₽'},
                {'title': 'Операционный запас', 'value': '3,2 месяца', 'note': 'Норма 3 месяца'},
            ],
            'list_title': 'Расходы по категориям',
            'list_items': [
                {'title': 'Закупка', 'subtitle': '1 транзакция', 'value': '380 000 ₽'},
                {'title': 'Зарплаты', 'subtitle': '1 транзакция', 'value': '320 000 ₽'},
                {'title': 'Логистика', 'subtitle': '2 транзакции', 'value': '157 000 ₽'},
                {'title': 'Аренда', 'subtitle': '1 транзакция', 'value': '150 000 ₽'},
                {'title': 'Таргет', 'subtitle': '3 транзакции', 'value': '105 000 ₽'},
                {'title': 'Коммунальные', 'subtitle': '1 транзакция', 'value': '25 000 ₽'},
                {'title': 'Эквайринг', 'subtitle': '1 транзакция', 'value': '12 500 ₽'},
                {'title': 'Связь', 'subtitle': '1 транзакция', 'value': '8 000 ₽'},
            ],
            'table_title': 'Потоки по неделям',
            'table_headers': ['Неделя', 'Поступления', 'Расходы', 'Баланс'],
            'table_rows': [
                ['1-7 фев', '1,3 млн ₽', '620 000 ₽', '680 000 ₽'],
                ['8-14 фев', '1,1 млн ₽', '540 000 ₽', '560 000 ₽'],
                ['15-21 фев', '1,4 млн ₽', '680 000 ₽', '720 000 ₽'],
                ['22-28 фев', '1,3 млн ₽', '560 000 ₽', '740 000 ₽'],
            ],
            'insight_title': 'Финансовые заметки',
            'insights': [
                {'title': 'Главный драйвер', 'value': 'Премиум-сегмент +18%'},
                {'title': 'Рентабельность', 'value': '53% валовой маржи'},
                {'title': 'Налоговый резерв', 'value': '320 000 ₽'},
                {'title': 'Бюджет на март', 'value': '2,6 млн ₽'},
            ],
        },
    }
    data = sections.get(section)
    if not data:
        return redirect('dashboard')
    return render(request, 'core/placeholder_section.html', data)
