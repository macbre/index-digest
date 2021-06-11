from indexdigest.schema import Column


def test_column_int_column_normalization():
    col = Column(name='foo', column_type='int')
    assert col.type == 'int'

    # normalize int(N) from MySQL 8.0.16 and older to int
    col = Column(name='foo', column_type='int(11)')
    assert col.type == 'int'
