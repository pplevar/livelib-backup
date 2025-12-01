def handle_none(none):
    """
    Возвращает пустую строку, если объект является None, сам объект иначе
    :param none: any class - какой-то объект
    :return: param class or string
    """
    return '' if none is None else none


def add_livelib(link):
    """
    Добавляет доменное имя к ссылке, взятой из внутренностей HTML-кода, где доменное имя опускается
    :param link: string - ссылка, начинается с '/'
    :return: string - полноценная ссылка, к которой можно обращаться
    """
    ll = 'https://www.livelib.ru'
    return link if ll in link else ll + link
