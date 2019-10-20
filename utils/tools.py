from datetime import datetime

from sqlalchemy.orm import class_mapper


def object_to_dict(obj):
    def parse(o, c):
        r = getattr(o, c)

        if isinstance(r, datetime):
            return r.strftime('%Y-%m-%d %H:%M:%S')

        return r

    columns = [c.key for c in class_mapper(obj.__class__).columns]
    data = {c: parse(obj, c) for c in columns}

    return data


def object_to_list(obj):
    def parse(o, c):
        r = getattr(o, c)

        if isinstance(r, datetime):
            return r.strftime('%Y-%m-%d %H:%M:%S')

        return r

    columns = [c.key for c in class_mapper(obj.__class__).columns]
    data = [parse(obj, c) for c in columns]

    return data
