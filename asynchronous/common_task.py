import time

from flask_mail import Mail, Message

from celery_app import celery_app as c_app


@c_app.task(bind=True)
def mail_send(self, subject, sender, recipients, body):
    """
    发送邮件任务
    :param self:
    :param subject: 邮件主题
    :param sender:  邮件发送者
    :param recipients:  邮件接收者邮箱（type：list）
    :param body: 邮件内容
    :return:
    """
    # 循环导入 bug
    from manager import app

    mail = Mail(app)
    msg = Message(
        subject=subject,
        sender=(sender, "903444601@qq.com"),
        recipients=recipients  # 接收方邮箱（列表类型）
    )
    msg.body = body
    with app.app_context():
        mail.send(msg)
