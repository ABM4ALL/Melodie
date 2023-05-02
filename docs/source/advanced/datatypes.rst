Data Types
==============

When your program is trying to write dataframe into database, the type might be uncertained if we use the default data types.
For example, there is a variable ``number_of_factories`` that is thought to be an ``integer``. But if this value is from
 arithmic operations or file parsing, this variable might become a ``float``, or a numpy datatype. If we store this into
 database by default method, the database may not regard it as integer.

 To solve this, we could define ``DataFrameInfo`` to assign datatypes as the following codeblocks shown:

 .. code-block:: python

    id_age_group = DataFrameInfo(
        df_name="table_name",
        file_name="SomeTable.xlsx",
        columns={
            "id": sqlalchemy.Integer(),
            "value": sqlalchemy.Float(),
            "name": sqlalchemy.Text(),
            },
    )

In the ``columns`` parameter, there are several common data types:

- ``sqlalchemy.Integer()``, stands for integer type in database;
- ``sqlalchemy.Float()``, stands for float in database;
- ``sqlalchemy.Text()``, stands for text in database.

Notice
~~~~~~
- Please use snake cased name as the table name like ``table_name``, not ``TableName``.
    + This is because some database, like ``MySQL``, could not name tables with Capital letters.
- Please always use ``sqlalchemy.Text()`` for length-undetermined string values.
    + For ``SQLite``, using ``sqlalchemy.String()`` is just okay;
    + But for ``MySQL``, ``sqlalchemy.String()`` will be interpreted as ``VARCHAR``, which must be initiated with length parameter.