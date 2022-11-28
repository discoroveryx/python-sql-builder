from django.db import connection

from constants import errors, sql_ops


class SqlBuilder(object):
    table_name = None
    dict_arr = None

    def __init__(self, table_name, *args, **kwargs):
        self.table_name = table_name
        self.dict_arr = {
            'SELECT': [],
            'JOIN': [],
            'WHERE': [],
            'LIKE': [],
            'SEARCH': [],
            'DISTINCT': False,
            'ORDER_BY': None,
            'LIMIT': None,
        }

    def build_sql(self):
        sql_collector = ''
        if len(self.table_name) <= 0:
            return errors.ERROR_TABLE_NAME

        if len(self.dict_arr['SELECT']) <= 0:
            return errors.ERROR_EXPRESSION

        # SELECT
        for x, y in enumerate(self.dict_arr['SELECT']):
            self.dict_arr['SELECT'][x] = self.dict_arr['SELECT'][x].rstrip()
            self.dict_arr['SELECT'][x] = self.dict_arr['SELECT'][x].lstrip()
            self.dict_arr['SELECT'][x] = '\t%s' % (self.dict_arr['SELECT'][x])

        fields_str = ', \n'.join(str(x) for x in self.dict_arr['SELECT'])

        if self.dict_arr['DISTINCT'] is True:
            sql_collector = f'''{sql_ops.S_DISTINCT} \n{fields_str} \n\nFROM "{self.table_name}"'''
        else:
            sql_collector = '''SELECT \n%s \n\nFROM "%s"''' % (fields_str, self.table_name)

        # JOIN
        if len(self.dict_arr['JOIN']) > 0:
            for i in self.dict_arr['JOIN']:
                sql_collector = '%s \n\n%s' % (sql_collector, i)

        # WHERE
        if len(self.dict_arr['WHERE']) > 0:
            where_str = '\n\tAND '.join(self.dict_arr['WHERE'])
            sql_collector = '%s \n\nWHERE %s' % (sql_collector, where_str)

        # LIKE & SEARCH
        like_search_arr = []

        # LIKE
        if len(self.dict_arr['LIKE']) > 0:
            for i in self.dict_arr['LIKE']:
                like_str = '''UPPER("''' + self.table_name + '''"."''' + i['field'] + '''"::text) LIKE UPPER(\'%''' + i['text'] + '''%\')'''
                like_search_arr.append(like_str)

        # SEARCH
        if len(self.dict_arr['SEARCH']) > 0:
            for i in self.dict_arr['SEARCH']:
                search_str = '''to_tsvector("''' + self.table_name + '''"."''' + i['field'] + '''") @@ plainto_tsquery(\'''' + i['text'] + '''\') = true'''
                like_search_arr.append(search_str)

        if len(like_search_arr) > 0:
            like_search_arr = ' OR '.join(like_search_arr)
            if len(self.dict_arr['WHERE']) > 0:
                sql_collector = '%s \n\tAND (%s)' % (sql_collector, like_search_arr)
            else:
                sql_collector = '%s \n\t (%s)' % (sql_collector, like_search_arr)

        # ORDER_BY
        if self.dict_arr['ORDER_BY'] is not None:
            sql_collector = '%s \n\nORDER BY %s' % (sql_collector, self.dict_arr['ORDER_BY'])

        # LIMIT
        if self.dict_arr['LIMIT'] is not None:
            sql_collector = '%s \n\nLIMIT %s' % (sql_collector, self.dict_arr['LIMIT'])

        # Replace ";" to ""
        sql_collector = sql_collector.replace(';', '')

        return sql_collector

    def SELECT(self, fields):
        for i in fields:
            self.dict_arr['SELECT'].append(i)
        return self

    def DISTINCT(self):
        self.dict_arr['DISTINCT'] = True
        return self

    def JOIN(self, expression):
        if len(self.dict_arr['SELECT']) > 0:
            if len(expression) > 0:
                self.dict_arr['JOIN'].append(expression)
        return self

    def WHERE(self, expression):
        if len(self.dict_arr['SELECT']) > 0:
            if len(expression) > 0:
                self.dict_arr['WHERE'].append(expression)
        return self

    def LIKE(self, field, text):
        if len(self.dict_arr['SELECT']) > 0:
            if len(field) > 0 and len(text) > 0:
                self.dict_arr['LIKE'].append({'field': field, 'text': text})
        return self

    def SEARCH(self, field, text):
        if len(self.dict_arr['SELECT']) > 0:
            if len(field) > 0 and len(text) > 0:
                self.dict_arr['SEARCH'].append({'field': field, 'text': text})
        return self

    def ORDER_BY(self, field, sort):
        if len(self.dict_arr['SELECT']) > 0:
            if len(field) > 0:
                if sort == 'ASC' or sort == 'DESC':
                    self.dict_arr['ORDER_BY'] = '%s %s' % (field, sort)
        return self

    def LIMIT(self, limit):
        if len(self.dict_arr['SELECT']) > 0:
            try:
                limit = int(limit)
            except ValueError:
                pass
            else:
                self.dict_arr['LIMIT'] = limit
        return self

    def get(self):
        r_sql = self.build_sql()

        data = None
        count = 0

        conn_cursor = connection.cursor()
        conn_cursor.execute(r_sql)

        data_fetchall = conn_cursor.fetchall()

        columns = [col[0] for col in conn_cursor.description]
        data = [
            dict(zip(columns, row))
            for row in data_fetchall
        ]

        count = len(data_fetchall)

        try:
            conn_cursor.close()
        except Exception:
            pass
        return {'data': data, 'count': count}

    @property
    def sql(self):
        r_sql = self.build_sql()
        return '\n%s\n' % (r_sql)

    @property
    def arr(self):
        return '\n%s\n' % (self.dict_arr)

    def __str__(self):
        pass
