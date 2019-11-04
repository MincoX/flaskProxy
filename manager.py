from flask_script import Manager

from App import create_app


class FlaskServer:
    def __init__(self):
        self.app = create_app('develop')
        self.manager = Manager(self.app)

    def run(self):
        self.manager.run()

    @classmethod
    def start(cls):
        fs = cls()
        fs.run()


app = create_app('develop')
# manager = Manager(app)

if __name__ == '__main__':
    # FlaskServer.start()
    # manager.run()
    app.run()
