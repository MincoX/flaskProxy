print('start')


class ApiService:
    def __init__(self, func=None):
        self.func = func

    def func_wrapper(self, *args, **kwargs):
        try:
            c = 3
            ret = self.func(c, *args, **kwargs)
        except:
            pass
        finally:
            pass

    def __call__(self, *args, **kwargs):
        return self.func_wrapper(*args, **kwargs)


@ApiService
def test(ser, a, b):
    print(ser, a, b)


def dec1(func):
    def wrapper():
        print('dec1 start')
        func()
        print('dec1 end')

    return wrapper


def dec2(func):
    def wrapper():
        print('dec2 start')
        func()
        print('dec2 end')

    return wrapper


@dec2
@dec1
def dec():
    print('dec start')
    print('dec end')


if __name__ == '__main__':
    print('debug')
    # test(1, 2)
    dec()
