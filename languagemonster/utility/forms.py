
black_list_items = (
    'csrfmiddlewaretoken',
)


def _populate(d, model, obj):

    # for k, v in d.items():
    #     if k in obj:
    #         obj[k] = d[k]
    #     elif k in model._fields:
    #         obj[k] = d[k]

    for k, v in d.items():
        if k not in black_list_items:
            # obj[k] = v
            setattr(obj, k, v)


def populate_from_dict(d, model, obj):
    _populate(d, model, obj)


def populate(request, model, obj):
    d = request.POST.dict()
    _populate(d, model, obj)


def dict_contains_keys(d, keys):
    '''Checks if all keys are present in d'''

    if not isinstance(d, dict):
        return False

    for k in keys:
        if k not in d:
            return False

    return True
