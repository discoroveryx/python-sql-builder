## Sql Builder

#### INIT TABLE
The first argument is the name of the table ```node_goods``` from the database:
```python
data = SqlBuilder('node_goods')
```

#### SELECT
```python

data = data.SELECT(['"node_goods"."id"', '"node_goods"."name"'])

data = data.SELECT([
    '''
    COALESCE((select sum(value) from node_goodsinstock where node_goodsinstock.goods_id = node_goods.id), 0) AS "quantinstock"
    '''
])

arg_data = '(1,2,3)'
data = data.SELECT([
    '''
    COALESCE((select sum(value) from node_goodsinstock where node_goodsinstock.goods_id = node_goods.id and node_goodsinstock.stock_id in (%s)),0) AS "quantinstock_incity"
    ''' % (arg_data)
])

data = data.SELECT(['(select typeof from node_tax where node_tax.id = node_goods_tax.tax_id order by node_tax.id asc limit 1) as "typeof"'])
```

#### DISTINCT
```python
data = data.DISTINCT()
```

#### JOIN
```python
data = data.JOIN('''INNER JOIN "node_goods_tax" ON ("node_goods_tax"."goods_id" = "node_goods"."id")''')
```

#### WHERE
```python
data = data.WHERE('''"node_goods"."status" = True''')

data = data.WHERE('''"node_goods_tax"."tax_id" IS NOT NULL''')

arg_data = '(1,2,3)'
data = data.WHERE('''COALESCE((select sum(value) from node_goodsinstock where node_goodsinstock.goods_id = node_goods.id and node_goodsinstock.stock_id in (%s)),0) >= 1''' % (arg_data))
```

#### LIKE
```python
data = data.LIKE('name', 'Loren Ipsum')
data = data.LIKE('bname', 'Loren Ipsum')
```

```sql
WHERE (UPPER("node_goods"."name"::text) LIKE UPPER('%Loren Ipsum%') OR UPPER("node_goods"."bname"::text) LIKE UPPER('%Loren Ipsum%'))

```

#### SEARCH
```python
data = data.SEARCH('name', 'Loren Ipsum')
data = data.SEARCH('bname', 'Loren Ipsum')
```

```sql
WHERE (to_tsvector("node_goods"."name") @@ plainto_tsquery('Loren Ipsum') = true OR to_tsvector("node_goods"."bname") @@ plainto_tsquery('Loren Ipsum') = true)
```

#### ORDER_BY
```python

data = data.ORDER_BY('"node_goods"."name"', 'ASC')

data = data.ORDER_BY('"node_goods"."name"', 'DESC')
```

#### LIMIT
```python
data = data.LIMIT(10)
```
