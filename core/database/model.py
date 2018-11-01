import json

import aiosqlite

TEST_DB = "./craftbeerpi.db"



class DBModel(object):

    __priamry_key__ = "id"
    __as_array__ = False
    __order_by__ = None
    __json_fields__ = []

    def __init__(self, args):

        self.__setattr__(self.__priamry_key__, args[self.__priamry_key__])
        for f in self.__fields__:
            if f in self.__json_fields__:
                if args[f] is not None:

                    if isinstance(args[f], dict) or isinstance(args[f], list):
                        self.__setattr__(f, args[f])
                    else:
                        self.__setattr__(f, json.loads(args[f]))
                else:
                    self.__setattr__(f, None)
            else:
                print(f,args[f])
                self.__setattr__(f, args[f])

    @classmethod
    async def test_connection(self):

        print("CREATE DATABSE")
        async with aiosqlite.connect(TEST_DB) as db:
            print("DB OK")
            assert isinstance(db, aiosqlite.Connection)
            qry = open('./core/sql/create_table_user.sql', 'r').read()
            cursor = await db.executescript(qry)





    @classmethod
    async def get_all(cls):
        print("GET ALL")
        if cls.__as_array__ is True:
            result = []
        else:
            result = {}
        async with aiosqlite.connect(TEST_DB) as db:

            if cls.__order_by__ is not None:
                sql = "SELECT * FROM %s ORDER BY %s.'%s'" % (cls.__table_name__,cls.__table_name__,cls.__order_by__)
            else:
                sql = "SELECT * FROM %s" % cls.__table_name__

            db.row_factory = aiosqlite.Row
            async with db.execute(sql) as cursor:
                    async for row in cursor:
                        if cls.__as_array__ is True:
                            result.append(cls(row))
                        else:
                            result[row[0]] = cls(row)
                    await cursor.close()

        return result

    @classmethod
    async def get_one(cls, id):
        async with aiosqlite.connect(TEST_DB) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM %s WHERE %s = ?" % (cls.__table_name__, cls.__priamry_key__), (id,)) as cursor:
                row = await cursor.fetchone()
                if row is not None:
                    return cls(row)
                else:
                    return None

    @classmethod
    async def delete(cls, id):
        async with aiosqlite.connect(TEST_DB) as db:
            await db.execute("DELETE FROM %s WHERE %s = ? " % (cls.__table_name__, cls.__priamry_key__), (id,))
            await db.commit()

    @classmethod
    async def insert(cls, **kwargs):

        async with aiosqlite.connect(TEST_DB) as db:
            if cls.__priamry_key__ is not None and cls.__priamry_key__ in kwargs:
                query = "INSERT INTO %s (%s, %s) VALUES (?, %s)" % (
                    cls.__table_name__,
                    cls.__priamry_key__,
                    ', '.join("'%s'" % str(x) for x in cls.__fields__),
                    ', '.join(['?'] * len(cls.__fields__)))
                data = ()
                data = data + (kwargs.get(cls.__priamry_key__),)
                for f in cls.__fields__:
                    if f in cls.__json_fields__:
                        data = data + (json.dumps(kwargs.get(f)),)
                    else:
                        data = data + (kwargs.get(f),)
            else:

                query = 'INSERT INTO %s (%s) VALUES (%s)' % (
                    cls.__table_name__,
                    ', '.join("'%s'" % str(x) for x in cls.__fields__),
                    ', '.join(['?'] * len(cls.__fields__)))

                data = ()
                for f in cls.__fields__:
                    if f in cls.__json_fields__:
                        data = data + (json.dumps(kwargs.get(f)),)
                    else:
                        data = data + (kwargs.get(f),)

            print(query, data)
            cursor = await db.execute(query, data)
            await db.commit()

            i = cursor.lastrowid
            kwargs["id"] = i

            return cls(kwargs)

    @classmethod
    async def update(cls, **kwargs):
        async with aiosqlite.connect(TEST_DB) as db:
            query = 'UPDATE %s SET %s WHERE %s = ?' % (cls.__table_name__, ', '.join("'%s' = ?" % str(x) for x in cls.__fields__), cls.__priamry_key__)

            data = ()
            for f in cls.__fields__:
                if f in cls.__json_fields__:
                    data = data + (json.dumps(kwargs.get(f)),)
                else:
                    data = data + (kwargs.get(f),)

            data = data + (kwargs.get(cls.__priamry_key__),)
            cursor = await db.execute(query, data)
            await db.commit()
            return cls(kwargs)


class ActorModel(DBModel):
    __fields__ = ["name","type","config"]
    __table_name__ = "actor"
    __json_fields__ = ["config"]


class SensorModel(DBModel):
    __fields__ = ["name","type", "config"]
    __table_name__ = "sensor"
    __json_fields__ = ["config"]