# Mini CSV Dashboard (Beginner Friendly)

This project is a very small "Power BI-like" dashboard built with:
- Dash (web app UI)
- Pandas (read and inspect CSV)
- Matplotlib + Seaborn (charts)

The code is intentionally written in a simple and explicit way.

## 1. Create/activate environment

This workspace already has `.venv`.

If needed, run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 2. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Run app

```powershell
.\.venv\Scripts\python.exe app.py
```

Open this URL in your browser:
- http://127.0.0.1:8050

## 4. What the app does

1. Upload a CSV file.
2. Detect dataset info:
   - row count
   - column count
   - missing cells
   - duplicate rows
3. Show first 10 rows.
4. Draw charts:
   - Pie chart from first categorical column
   - Bar chart from first categorical column
   - Histogram from first numeric column

## 5. Beginner notes

- Functions are small and named clearly.
- No advanced one-liners.
- The callback (`update_dashboard`) reads top to bottom in a simple flow.
- You can explain the app by following function order in `app.py`.
