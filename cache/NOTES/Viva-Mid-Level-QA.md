# DataVista Mid-Level Viva (Simple)

## 1) Full app flow (easy)
1. Upload CSV.
2. App reads file and checks data.
3. App shows row, column, missing, duplicate info.
4. App shows preview table.
5. App fills dropdown options.
6. App updates all charts.
7. User can open large scatter chart.

## 2) Important functions in easy words
- parse_uploaded_csv: Reads uploaded CSV.
- figure_to_base64: Converts chart to image text.
- find_chart_columns: Finds useful default columns.
- pick_line_columns: Picks default X and Y.
- apply_row_limit: Shows first 10/50/100/all rows.
- build_pie_chart: Pie chart.
- build_bar_chart: Bar chart.
- build_line_chart: Line chart.
- build_scatter_plot: Scatter chart.
- build_summary_list: Top 5 summary list.

## 3) Common mid-level viva questions
- Q: Why use StringIO?
- A: It lets Pandas read text as if it is a file.

- Q: Why convert values to numeric?
- A: Charts need numbers. Bad values are removed safely.

- Q: Why store data in dcc.Store?
- A: So callbacks can reuse same data without reading file again.

- Q: Why check if data is None?
- A: To handle case when user has not uploaded any file.

- Q: Why use use_reloader=False?
- A: To avoid app running twice during debug.

## 4) Seaborn and chart questions
- Q: Why rotate X labels?
- A: Long names overlap, rotation makes them readable.

- Q: Why close figure after saving?
- A: To save memory.

- Q: Why limit scatter rows?
- A: Large points make UI slow.

## 5) Easy code explanation examples
### Example 1
```python
y_numeric = pd.to_numeric(y_series, errors="coerce")
plot_df = pd.DataFrame({"x": x_values, "y": y_numeric}).dropna()
```
- Meaning: Make Y numeric and remove invalid rows.

### Example 2
```python
if row_limit_value in [None, "all", ""]:
    return df.copy()
return df.head(int(row_limit_value))
```
- Meaning: If no limit, use full data. Else use first N rows.

### Example 3
```python
if x_column not in [None, ""] and y_column not in [None, ""]:
    line_title = f"{y_column} by {x_column}"
```
- Meaning: Title changes based on selected columns.

## 6) Data-related viva questions
- Q: Which datasets are used?
- A: IPL, Iris, MSME, NIRF, and some sample synthetic CSV files.

- Q: What data quality info is shown?
- A: Row count, column count, missing cells, duplicate rows.

- Q: How are default chart columns selected?
- A: App picks first text-type column and first numeric column.

## 7) Problems and simple answers
- Problem: Y column is text.
- Answer: App converts values to numbers and shows message if invalid.

- Problem: CSV format is bad.
- Answer: App catches error and shows readable message.

- Problem: Selected data gives empty chart.
- Answer: App shows fallback chart with guidance message.
