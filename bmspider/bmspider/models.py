"""
Modelos para armazenar dados extraídos no banco de dados.
"""

import inspect

from peewee import CharField, ForeignKeyField, Model, SqliteDatabase, TextField

db = SqliteDatabase("bmspider.db")


class BaseModel(Model):
    class Meta:
        database = db


class Author(BaseModel):
    name = CharField(max_length=100, index=True, unique=True)

    class Meta:
        db_table = "author"

    def __str__(self):
        return self.name


class Quote(BaseModel):
    text = TextField(index=True)
    author = ForeignKeyField(model=Author, backref="authors")

    class Meta:
        db_table = "quote"
        indexes = [(("text", "author"), True)]

    def __str__(self):
        return self.text


class Tag(BaseModel):
    name = CharField(max_length=100, index=True, unique=True)

    class Meta:
        db_table = "tag"

    def __str__(self):
        return self.name


class QuoteTag(BaseModel):
    quote = ForeignKeyField(model=Quote, backref="tags")
    tag = ForeignKeyField(model=Tag)


# Criar tabelas automaticamente.
def create_tables():
    models = []
    for name, cls in globals().items():
        if inspect.isclass(cls) and issubclass(cls, BaseModel):
            if name == "BaseModel":
                continue
            models.append(cls)
    db.create_tables(models, safe=True)


if __name__ == "__main__":
    create_tables()
