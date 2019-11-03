import hashlib

import settings
from utils import logger
from models import Session, Admin, Perm, Role

rel_role_perm = {
    'role1': 'base',
    'role2': ['base', 'do_setting'],
    'role3': ['base', 'do_setting', 'do_auth'],
}


def init_system():
    session = Session()

    perms = [
        Perm(name='基础用户', slug='base'),
        Perm(name='配置系统', slug='do_setting'),
        Perm(name='权限分配', slug='do_auth'),
    ]

    roles = [
        Role(name='普通管理员', slug='role1'),
        Role(name='系统管理员', slug='role2'),
        Role(name='超级管理员', slug='role3'),
    ]

    session.add_all(perms)
    session.add_all(roles)
    session.commit()

    for role in roles:
        for perm in perms:
            if perm.slug in rel_role_perm[role.slug]:
                role.perms.append(perm)

    admin = Admin(
        username=settings.ADMIN_NAME,
        password=hashlib.md5((settings.ADMIN_PASSWORD + settings.SECRET_KEY).encode()).hexdigest(),
    )

    session.add(admin)
    session.commit()

    role3 = session.query(Role).filter(Role.slug == 'role3').one()
    admin.roles.append(role3)
    session.commit()

    session.close()


if __name__ == '__main__':
    init_system()
    logger.info('init system')
