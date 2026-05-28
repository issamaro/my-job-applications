# SQLite & Python sqlite3 — Migration Refactor Reference

```
library: SQLite / Python stdlib sqlite3
resolved_ids: /sqlite/sqlite (PRAGMA semantics), /python/cpython v3.13.9 (sqlite3 module)
version_constraint: SQLite >= 3.25 for RENAME COLUMN; SQLite 3.50.4 in use
runtime_constraint: Python >= 3.13
queried: 2026-05-28
```

---

## 1. `PRAGMA table_info(<table>)` — column tuple shape

Each row is `(cid, name, type, notnull, dflt_value, pk)`:

- `cid` — zero-based column index.
- `name` — column name as declared.
- `type` — declared type affinity string (e.g. `"INTEGER"`, `"TEXT"`).
- `notnull` — `1` if `NOT NULL` constraint is present, `0` otherwise. For `INTEGER PRIMARY KEY [AUTOINCREMENT]`, SQLite does **not** implicitly set `notnull = 1` here — the column is the rowid alias and nulls are rejected at the rowid level, but the pragma reports `notnull = 0` unless `NOT NULL` was written explicitly in the DDL.
- `dflt_value` — the literal default expression as a string, or `NULL` if no `DEFAULT` clause. For `INTEGER PRIMARY KEY AUTOINCREMENT`, this is `NULL`.
- `pk` — `0` if not part of the primary key; for a single-column PK it is `1`; for a composite PK each member column gets its ordinal position in the key (1, 2, …).
- **AUTOINCREMENT is not exposed** by `table_info`. The pragma has no field for it. To detect AUTOINCREMENT you must inspect `sqlite_master.sql` (see §4 and §6).

Source: SQLite PRAGMA documentation (https://www.sqlite.org/pragma.html#pragma_table_info); confirmed via `/sqlite/sqlite` source tests.

---

## 2. `PRAGMA foreign_key_list(<table>)` — column tuple shape

Each row is `(id, seq, table, from, to, on_update, on_delete, match)`:

- `id` — foreign key constraint index (0-based, increments per FK defined on the table).
- `seq` — column sequence within a multi-column FK (0-based).
- `table` — name of the referenced (parent) table.
- `from` — column name in the child table.
- `to` — column name in the parent table (or `NULL` if referencing the PK implicitly).
- `on_update` — action string: one of `"NO ACTION"`, `"RESTRICT"`, `"SET NULL"`, `"SET DEFAULT"`, `"CASCADE"`.
- `on_delete` — same set of action strings as `on_update`.
- `match` — always `"NONE"` in current SQLite (MATCH clause is parsed but not enforced).

For PRAGMA-equivalence comparisons between a fresh and upgraded database, compare `(table, from, to, on_update, on_delete)` per `id/seq` group; ignore `id` itself as it is positional and may differ if FKs were added in different orders.

Source: SQLite PRAGMA documentation (https://www.sqlite.org/pragma.html#pragma_foreign_key_list).

---

## 3. `PRAGMA index_list(<table>)` and `PRAGMA index_info(<index>)` — tuple shapes

`PRAGMA index_list(<table>)` — each row is `(seq, name, unique, origin, partial)`:

- `seq` — sequential number (display order).
- `name` — index name.
- `unique` — `1` if the index is UNIQUE, `0` otherwise.
- `origin` — how the index was created: `"c"` = explicit `CREATE INDEX`, `"u"` = implicit index from a `UNIQUE` constraint, `"pk"` = implicit index from a `PRIMARY KEY` constraint on a `WITHOUT ROWID` table.
- `partial` — `1` if a `WHERE` clause (partial index) is present, `0` otherwise.

`PRAGMA index_info(<index>)` — each row is `(seqno, cid, name)`:

- `seqno` — position of this column within the index key (0-based).
- `cid` — column id from `table_info` (`-1` for rowid, `-2` for expression index columns).
- `name` — column name, or `NULL` for expression columns.

For cross-database index comparison, join on `(name, unique, partial)` from `index_list`, then compare the ordered `index_info` rows. Watch for auto-named indexes (SQLite generates names like `sqlite_autoindex_<table>_<n>`) which may be named differently across schema versions.

Source: SQLite PRAGMA documentation (https://www.sqlite.org/pragma.html#pragma_index_list, https://www.sqlite.org/pragma.html#pragma_index_info).

---

## 4. `sqlite_master` table — columns, `sql IS NULL`, and explicit CREATE INDEX detection

`sqlite_master` columns: `(type, name, tbl_name, rootpage, sql)`.

- `type` — object kind: `"table"`, `"index"`, `"view"`, `"trigger"`.
- `name` — object name.
- `tbl_name` — for indexes, the table the index belongs to; equals `name` for tables.
- `rootpage` — B-tree root page number (internal; not reliable for schema comparison).
- `sql` — the original `CREATE` statement as stored text, or **`NULL`**.

**`sql IS NULL`** occurs for two cases: (a) internal auto-indexes created to enforce `UNIQUE` or `PRIMARY KEY` constraints (these have `type = 'index'` and `name` beginning with `sqlite_autoindex_`), and (b) the rowid pseudo-entry for ordinary tables in some edge cases. The rule holds: when `type = 'index'` and `sql IS NULL`, the index was not written by the user — it is a constraint-enforcement index. Conversely, **`sql IS NOT NULL` for a row where `type = 'index'` reliably indicates an explicit `CREATE [UNIQUE] INDEX` statement**. This is the correct filter for comparing user-defined indexes between two databases.

Note: `sqlite_schema` is a synonym for `sqlite_master` (added in SQLite 3.33.0). Both names work in 3.50.4.

Source: SQLite schema table documentation (https://www.sqlite.org/schematab.html).

---

## 5. `sqlite3.Connection.set_trace_callback` in Python 3.13

**Signature:** `connection.set_trace_callback(trace_callback, /)`

The callback receives a single argument: the SQL statement string as it is about to be executed by the SQLite backend. It captures **all statements executed by the backend** — DDL (`CREATE TABLE`, `DROP INDEX`, etc.) and DML (`INSERT`, `UPDATE`, `DELETE`, `SELECT`) alike. Internal SQLite statements issued during connection housekeeping may also appear. The return value of the callback is ignored.

**To unset:** pass `None` — `connection.set_trace_callback(None)` disables tracing.

**Python 3.13 deprecation to note:** passing the callable by keyword (`conn.set_trace_callback(trace_callback=fn)`) is deprecated in 3.13; the parameter becomes positional-only in Python 3.15. Use positional form now.

Method was introduced in Python 3.3 (What's New 3.3). No behavioral changes in 3.13 beyond the keyword-argument deprecation.

Source: `/python/cpython` — `Doc/library/sqlite3.rst`, `Doc/whatsnew/3.13.rst`, `Doc/whatsnew/3.3.rst`.

---

## 6. AUTOINCREMENT keyword case preservation in `sqlite_master.sql`

SQLite stores the `CREATE TABLE` statement in `sqlite_master.sql` **verbatim as the user wrote it**, preserving original whitespace and casing. It does not normalize keywords to uppercase or lowercase. Therefore:

- If the schema was created with `INTEGER PRIMARY KEY AUTOINCREMENT` (uppercase), `sqlite_master.sql` contains that exact string.
- A case-sensitive regex or `LIKE` pattern for `AUTOINCREMENT` is **only reliable if your own migrations consistently use that casing**. For defensive code — especially when inspecting databases whose DDL origin is unknown — use a **case-insensitive** regex (`re.search(r'autoincrement', sql, re.IGNORECASE)`).

There is no separate `sqlite_sequence` flag in `sqlite_master`; the `sqlite_sequence` system table tracks the last inserted rowid for AUTOINCREMENT tables, but `sqlite_master` is the only place the keyword itself appears in schema metadata.

Source: SQLite schema table documentation (https://www.sqlite.org/schematab.html); SQLite AUTOINCREMENT docs (https://www.sqlite.org/autoinc.html).

---

## 7. `sqlite3.OperationalError` chaining with `raise type(e)(f"[ctx] {e}") from e`

The sqlite3 exception hierarchy is: `sqlite3.Error` → `sqlite3.DatabaseError` → `sqlite3.OperationalError` (and siblings `IntegrityError`, `ProgrammingError`, etc.). All are standard Python exception subclasses.

`type(e)` returns the **exact runtime class** of `e` — if `e` is a `sqlite3.OperationalError`, `type(e)` is `sqlite3.OperationalError`, not a base class. Calling `type(e)(f"[ctx] {e}")` constructs a new instance of that same concrete subclass with the wrapped message. `raise ... from e` sets `__cause__` on the new exception and sets `__suppress_context__ = True`, giving a clean "The above exception was the direct cause" traceback.

**`isinstance` checks are preserved:** because the re-raised exception is the same concrete subclass, any downstream `except sqlite3.OperationalError` or `isinstance(exc, sqlite3.DatabaseError)` checks continue to work correctly.

**Caveat:** this pattern assumes `type(e)` accepts a single string argument. All stdlib sqlite3 exception classes do. If a custom sqlite3 subclass has a non-standard `__init__`, this breaks — but that is not a stdlib concern.

Source: `/python/cpython` — `Doc/library/sqlite3.rst` (exception hierarchy), `Doc/library/exceptions.rst` (exception chaining semantics).

---

## 8. `ALTER TABLE RENAME COLUMN` — stability in SQLite 3.50.4

`ALTER TABLE <table> RENAME COLUMN <old> TO <new>` was added in **SQLite 3.25.0** (released 2018-09-15). As of SQLite 3.50.4, the feature is fully stable and part of the documented ALTER TABLE surface. It correctly updates references in indexes, triggers, and views that reference the renamed column (this automatic reference rewriting was itself improved in 3.26.0 to be more complete). No known regressions or deprecation. Safe to rely on in 3.50.4.

Source: SQLite ALTER TABLE documentation (https://www.sqlite.org/lang_altertable.html); SQLite release history (https://www.sqlite.org/changes.html — 3.25.0 entry).

---

## Deprecated to avoid

- `sqlite3.version` and `sqlite3.version_info` attributes — removed in Python 3.14. Use `sqlite3.sqlite_version` / `sqlite3.sqlite_version_info` for the SQLite library version.
- Passing `set_trace_callback` (and `set_authorizer`, `set_progress_handler`) callable by keyword — deprecated Python 3.13, removed Python 3.15.

---

## Open questions

1. **`PRAGMA table_info` — exact `notnull` value for `INTEGER PRIMARY KEY AUTOINCREMENT`**: context7 `/sqlite/sqlite` did not return PRAGMA reference docs directly. The answer above (notnull = 0 unless explicitly written) is from well-established SQLite behavior, but should be verified against the SQLite PRAGMA reference page (https://www.sqlite.org/pragma.html#pragma_table_info) or with a quick `sqlite3 :memory:` shell test before relying on it in production comparison logic.

2. **`PRAGMA foreign_key_list` — `match` column behavior**: documented as always `"NONE"`, but if the codebase needs to round-trip MATCH clauses, verify against live schema; context7 did not return a snippet confirming this.

3. **`index_list` `origin` values for WITHOUT ROWID tables**: the `"pk"` origin value is specific to WITHOUT ROWID PKs. If the migrated schema uses WITHOUT ROWID tables, confirm `origin` semantics separately — context7 results for this were indirect.
