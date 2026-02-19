import pathway as pw

class S(pw.Schema):
    a: int

t = pw.debug.table_from_rows(S, [(10,), (20,)])
res = pw.debug.table_to_dicts(t)
print(f"Results type: {type(res)}")
if res:
    print(f"First element type: {type(res[0])}")
    print(f"First element: {res[0]}")
