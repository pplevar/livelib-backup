import re
from collections import defaultdict
from lxml import etree


def error_handler(where, raw):
    """
    Обработчик ошибки при парсинге html страницы
    :param where: string - что не распарсилось
    :param raw: html-узел
    :return: None
    """
    from export import logger
    logger.error(f'ERROR: Parsing error ({where} not parsed): {etree.tostring(raw)}')
    return None


def try_parse_month(raw_month):
    """
    Возвращает месяц в нужном виде
    :param raw_month: string - месяц в текстовом виде
    :return: string - месяц в цифровом виде
    """
    dict = defaultdict(lambda: '01', {
        'Январь': '01',
        'Февраль': '02',
        'Март': '03',
        'Апрель': '04',
        'Май': '05',
        'Июнь': '06',
        'Июль': '07',
        'Август': '08',
        'Сентябрь': '09',
        'Октябрь': '10',
        'Ноябрь': '11',
        'Декабрь': '12'
    })
    return dict[raw_month]


def is_last_page(page):
    """
    Проверяет, что на странице уже пустой список объектов (она последняя)
    :param page: страница
    :return: bool
    """
    return bool(len(page.xpath('//div[@class="with-pad"]')))


def is_redirecting_page(page):
    """
    Проверяет, что страница является перенаправляющей
    :param page: страница
    :return: bool
    """
    flag = bool(len(page.xpath('//div[@class="page-404"]')))
    if flag:
        print('ERROR: Oops! Livelib suspects that you are a bot! Reading stopped.')
        print()
    return flag


def href_i(href, i):
    """
    Возвращает ссылку на i-ую страницу данного типа
    :param href: string - ссылка на страницу
    :param i: int - номер страницы
    :return: string - нужная ссылка
    """
    return href + '/~' + str(i)


def date_parser(date):
    """
    Конвертирует дату в нужный формат
    :param date: string
    :return: string or None
    """
    m = re.search('\d{4} г.', date)
    if m is not None:
        year = m.group(0).split(' ')[0]
        raw_month = date.split(' ')[0]
        month = try_parse_month(raw_month)
        return '%s-%s-01' % (year, month)
    return None


def handle_xpath(html_node, request, i=0):
    """
    Обертка над xpath. Возвращает i-ый найденный узел. Если он не нашелся, то возвращается None
    :param html_node: html-узел
    :param request: string - xpath запрос
    :param i: int - индекс (по дефолту 0)
    :return: нужный html-узел или None
    """
    if html_node is None:
        return None
    tmp = html_node.xpath(request)
    return tmp[i] if i < len(tmp) else None


def slash_add(left, right):
    return left + '/' + right
