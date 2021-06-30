from flask import current_app
from .db import get_db, normalizeDBcol


def getCSVCols():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM datacols")
    return [(row['colname'], row['name']) for row in cur]


def processDataExtensionBatch(batch):
    ids, props = tuple(batch[x] for x in ('ids', 'properties'))
    cols = {normalizeDBcol(p['id']): p['id'] for p in props}
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT colname FROM datacols WHERE isid == 1")
    res = cur.fetchall()
    if len(res) != 1:
        raise RuntimeError("database not properly initialized")
    idcol = res[0]['colname']

    # Could use some defensiveness in generating this SQL
    cur.execute(
        "SELECT %s,%s FROM data WHERE %s in (%s)" %
        (idcol, ','.join(cols.keys()), idcol, ','.join('?' * len(ids))), ids)

    rows = dict()
    for row in cur:
        rows[row[idcol]] = {cols[col]: [{'str': row[col]}] for col in cols}

    meta = [dict(id=p['id'], name=p['id']) for p in props]

    return dict(meta=meta, rows=rows)
