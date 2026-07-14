# Bincom Basic Programming Test — Django Solution

Covers Q1, Q2, and Q3 from the test PDF, all backed by `bincom_test.sql`.

## 1. Set up

```bash
python -m venv venv
source venv/bin/activate          # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## 2. Load the real database

The dump's internal database name is `bincomphptest`:

```bash
mysql -u bincomuser -p -e "CREATE DATABASE bincomphptest CHARACTER SET utf8mb4;"
mysql -u bincomuser -p bincomphptest < bincom_test.sql
```

Set your DB credentials as environment variables (or edit `project/settings.py` directly):

```bash
export DB_NAME=freedb_b6t7oaFg
export DB_USER=u_gLWJr5
export DB_PASSWORD=cRcQcsi2ioYD
export DB_HOST=sql.freedb.tech
export DB_PORT=3306
```

## 3. Models are verified against the real dump

`results/models.py` uses `managed = False`, so Django never creates or
alters these tables — it just maps onto what's already in the dump. This
version was built and checked directly against the `bincom_test.sql` file,
not guessed. A few non-obvious things worth knowing if you extend this:

- `ward.lga_id` and `polling_unit.lga_id` reference `lga.lga_id` (a plain
  business id with gaps, e.g. 1,2,5,6,7...22,31..35) — **not**
  `lga.uniqueid` (the sequential 1–25 autoincrement PK). These are two
  different numbering schemes for the same LGA.
- `polling_unit` has **no state column** — state only lives on `lga`.
- `polling_unit.uniquewardid` is the clean join key back to `ward.uniqueid`;
  it's used in preference to matching `ward_id` values, which only repeat
  uniquely *within* a single LGA.
- `announced_pu_results.polling_unit_uniqueid` is stored as `VARCHAR`, so
  it's compared as a string against `polling_unit.uniqueid`.
- `announced_lga_results.lga_name` actually stores the LGA's numeric
  `lga_id` as text, not its name — moot here since Q2 doesn't use that
  table anyway, per the instructions.
- There's a real `party` lookup table (PDP, DPP, ACN, PPA, CDC, JP, ANPP,
  LABOUR, CPP) — Q3's form is generated from it directly.

## 4. Run it

```bash
python manage.py runserver
```

- `/` — **Q1**: chained State → LGA → Ward → Polling Unit select boxes, shows that PU's full result.
- `/lga-result/` — **Q2**: pick an LGA, see totals summed live from `announced_pu_results` (deliberately *not* reading `announced_lga_results`, per the instructions, so it can cross-check it).
- `/add-pu-result/` — **Q3**: create a brand-new polling unit and enter a score for every party in one form.

The test data only covers Delta State (state id 25), but the State dropdown
is generic so it'll work for any state present in the data.

## Notes for the reviewer

- Chained combo boxes (Q1 hint) implemented with plain `fetch()` calls to
  three small JSON endpoints — no framework needed.
- Q3's party list is pulled dynamically from whatever parties already exist
  in `announced_pu_results`, so the form always matches the live dataset
  instead of a hardcoded party list going stale.
- All writes to `PollingUnit` + `AnnouncedPuResult` in Q3 are wrapped in a
  single DB transaction so a half-saved polling unit can't happen.
