import pymysql


class ConnMysql(object):

    def __init__(self, db, host="localhost", port=33061, user="root", pwd="root", charset="utf8") -> None:
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = db
        self.charset = charset

    def init(self):
        self.conn_mysql = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.pwd,
            db=self.db,
            charset=self.charset
        )
        self.cursor = self.conn_mysql.cursor()

    def query(self, sql, params):
        self.init()
        res = self.cursor.execute(sql, params)
        # record = self.cursor.fetchone()
        records = self.cursor.fetchall()
        self.close()
        return res, records  # 此时以元组的形式返回

    def insert(self, sql, params):
        self.init()
        try:
            res = self.cursor.execute(sql, params)
            self.conn_mysql.commit()
            return res
        except Exception as e:
            print("插入失败, 错误信息：{}".format(e))
            self.conn_mysql.rollback()
        finally:
            self.close()

    def delete(self, sql, params):
        self.init()
        try:
            res = self.cursor.execute(sql, params)
            self.conn_mysql.commit()
            return res
        except Exception as e:
            print("删除失败, 错误信息：{}".format(e))
            self.conn_mysql.rollback()
        finally:
            self.close()

    def update(self, sql, params):
        self.init()
        try:
            res = self.cursor.execute(sql, params)
            self.conn_mysql.commit()
            return res
        except Exception as e:
            print("修改失败, 错误信息：{}".format(e))
            self.conn_mysql.rollback()
        finally:
            self.close()

    def close(self):
        self.init()
        if self.cursor:
            self.cursor.close()
        if self.conn_mysql:
            self.conn_mysql.close()
