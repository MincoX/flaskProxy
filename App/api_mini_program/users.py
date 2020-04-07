from App.api_mini_program import api


@api.route('/mp/getSession')
def get_session():
    return 'hello world'
