# DataVista Quick Revision (Very Simple)

## 1) Project in simple words
- This project is a dashboard made in Python.
- User uploads a CSV file.
- App shows table preview and charts.
- Goal: Understand data quickly without writing many scripts.

## 2) Tools used (easy meaning)
- Python: Main language.
- Dash: Makes the web page and updates it live.
- Pandas: Reads CSV and handles rows and columns.
- Matplotlib + Seaborn: Draw charts.
- CSS: Makes UI look clean.

## 3) How CSV upload works
1. User uploads CSV in browser.
2. File comes as encoded text.
3. Code decodes that text.
4. Pandas reads it and makes a table (DataFrame).
5. App uses this table to build charts.

One line for viva:
- "CSV upload is decoded, read by Pandas, then used for charts and summary."

## 4) How chart image is shown
1. Seaborn/Matplotlib creates chart.
2. Chart is saved in memory as PNG.
3. PNG is converted to base64 text.
4. That text is placed in image source.
5. Dash shows it on screen.

One line for viva:
- "Chart is created in Python and shown in browser as a base64 image."

## 5) Run commands
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

- Open: http://127.0.0.1:8050
- Stop app: Ctrl + C

## 6) What user can do
- Upload CSV
- See row/column info
- See missing and duplicate count
- Pick X and Y columns
- Change row limit
- View Pie, Line, Bar, Scatter charts
- Open large scatter view

## 7) Important terms (beginner)
- Callback: Function runs when user changes input.
- DataFrame: Data table in Pandas.
- Missing value: Empty cell.
- Duplicate row: Same row repeated.
- Numeric column: Number column.
- Categorical column: Text label column.

## 8) Basic viva Q and A (easy)
- Q: Why Dash?
- A: To make interactive dashboard in Python.

- Q: Why Pandas?
- A: To read and process CSV data.

- Q: Why Seaborn and Matplotlib?
- A: To draw clear charts.

- Q: Why fallback message chart?
- A: If data is not valid, app shows message instead of crash.

## 9) Similar easy project ideas
- Student marks dashboard
- Sales dashboard
- Hospital records dashboard
- HR employee dashboard
- E-commerce orders dashboard
