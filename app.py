import base64
import io

import dash
from dash import dcc, html, Input, Output, State
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


sns.set_theme(style="whitegrid")


app = dash.Dash(__name__)
app.title = "DataVista Dashboard"


def parse_uploaded_csv(contents):
    
    if contents is None:
        return None, "No file uploaded yet."

    _, content_string = contents.split(",")

    try:
        decoded_bytes = base64.b64decode(content_string)
        text_data = decoded_bytes.decode("utf-8")
        data_frame = pd.read_csv(io.StringIO(text_data))
        return data_frame, None
    except Exception as error:
        return None, f"Could not read CSV file: {error}"


def figure_to_base64(fig):
    
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close(fig)
    return f"data:image/png;base64,{image_base64}"


def build_message_chart(message):
    
    fig, ax = plt.subplots(figsize=(5.0, 3.6))
    ax.axis("off")
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12)
    return figure_to_base64(fig)


def get_column_as_series(df, column_name):
    
    if column_name is None:
        return None, "Column name is empty"

    if column_name not in df.columns:
        return None, f"Column '{column_name}' not found"

    selected_data = df.loc[:, column_name]

    if isinstance(selected_data, pd.DataFrame):
        if selected_data.shape[1] == 0:
            return None, f"Column '{column_name}' has no values"
        selected_data = selected_data.iloc[:, 0]

    if isinstance(selected_data, pd.Series):
        return selected_data.copy(), None

    try:
        forced_series = pd.Series(selected_data)
        return forced_series, None
    except Exception as error:
        return None, f"Could not convert '{column_name}' to 1D series: {error}"


def create_preview_table(df, max_rows=5):
    
    shown_df = df.head(max_rows)

    header_row = html.Tr([html.Th(column_name) for column_name in shown_df.columns])
    body_rows = []

    for _, row in shown_df.iterrows():
        one_row = html.Tr([html.Td(str(cell_value)) for cell_value in row])
        body_rows.append(one_row)

    return html.Table([html.Thead(header_row), html.Tbody(body_rows)])


def find_chart_columns(df):
    
    categorical_columns = []
    numeric_columns = []

    for column_name in df.columns:
        column_data = df[column_name]

        if (
            pd.api.types.is_object_dtype(column_data)
            or pd.api.types.is_string_dtype(column_data)
            or pd.api.types.is_categorical_dtype(column_data)
        ):
            categorical_columns.append(column_name)

        if pd.api.types.is_numeric_dtype(column_data):
            numeric_columns.append(column_name)

    chosen_category = None
    chosen_numeric = None

    if len(categorical_columns) > 0:
        chosen_category = categorical_columns[0]

    if len(numeric_columns) > 0:
        chosen_numeric = numeric_columns[0]

    return chosen_category, chosen_numeric


def pick_line_columns(df):
    
    x_column = None
    y_column = None

    if len(df.columns) > 0:
        x_column = df.columns[0]

    for column_name in df.columns:
        if pd.api.types.is_numeric_dtype(df[column_name]):
            y_column = column_name
            break

    return x_column, y_column


def apply_row_limit(df, row_limit_value):
    
    if row_limit_value in [None, "all", ""]:
        return df.copy()

    try:
        row_limit_int = int(row_limit_value)
        if row_limit_int > 0:
            return df.head(row_limit_int)
        return df.copy()
    except Exception:
        return df.copy()


def build_pie_chart(df, category_column, chart_title="Distribution"):
    
    if category_column is None:
        return build_message_chart("Pick a category column for Pie chart")

    category_series, series_error = get_column_as_series(df, category_column)
    if series_error is not None:
        return build_message_chart(series_error)

    counts = category_series.astype(str).value_counts().head(6)

    if counts.empty:
        return build_message_chart("No values available for Pie chart")

    fig, ax = plt.subplots(figsize=(4.5, 4))
    pie_colors = ["#9b7edb", "#a091de", "#c8b9ec", "#e2d9f5", "#f0ebf9", "#f4d663"]
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90, colors=pie_colors)
    ax.set_title(chart_title)

    return figure_to_base64(fig)


def build_bar_chart(df, category_column, chart_title="Performance"):
    
    if category_column is None:
        return build_message_chart("Pick a category column for Bar chart")

    category_series, series_error = get_column_as_series(df, category_column)
    if series_error is not None:
        return build_message_chart(series_error)

    counts = category_series.astype(str).value_counts().head(10)

    if counts.empty:
        return build_message_chart("No values available for Bar chart")

    chart_df = pd.DataFrame({"category": counts.index, "count": counts.values})

    fig, ax = plt.subplots(figsize=(5.0, 4))
    sns.barplot(data=chart_df, x="category", y="count", ax=ax, color="#9b7edb")
    ax.set_title(chart_title)
    ax.set_xlabel(category_column)
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=35)

    return figure_to_base64(fig)


def build_scatter_plot(df, x_column, y_column, chart_title="Scatter plot"):
    
    if x_column is None or y_column is None:
        return build_message_chart("Select both X and Y for scatter plot")

    x_series, x_error = get_column_as_series(df, x_column)
    if x_error is not None:
        return build_message_chart(x_error)

    y_series, y_error = get_column_as_series(df, y_column)
    if y_error is not None:
        return build_message_chart(y_error)

    y_numeric = pd.to_numeric(y_series, errors="coerce")

    if pd.api.types.is_numeric_dtype(x_series):
        x_values = pd.to_numeric(x_series, errors="coerce")
    else:
        x_values = x_series.astype(str)

    plot_df = pd.DataFrame({"x": x_values, "y": y_numeric}).dropna()
    if plot_df.empty:
        return build_message_chart("Scatter plot needs valid X values and numeric Y values")

    plot_df = plot_df.head(2000)

    fig, ax = plt.subplots(figsize=(5.0, 3.8))
    sns.scatterplot(data=plot_df, x="x", y="y", s=26, alpha=0.75, color="#9b7edb", ax=ax)
    ax.set_title(chart_title)
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)

    if not pd.api.types.is_numeric_dtype(x_series):
        ax.tick_params(axis="x", rotation=35)

    return figure_to_base64(fig)


def build_line_chart(df, x_column, y_column, chart_title="Trend"):
    
    if x_column is None or y_column is None:
        return build_message_chart("Pick both X and Y columns for Line chart")

    x_series, x_error = get_column_as_series(df, x_column)
    if x_error is not None:
        return build_message_chart(x_error)

    y_series, y_error = get_column_as_series(df, y_column)
    if y_error is not None:
        return build_message_chart(y_error)

    working_df = pd.DataFrame({x_column: x_series, y_column: y_series})
    working_df = working_df.dropna(subset=[x_column, y_column])

    if working_df.empty:
        return build_message_chart("No values available for Line chart")

    working_df[y_column] = pd.to_numeric(working_df[y_column], errors="coerce")
    working_df = working_df.dropna(subset=[y_column])

    if working_df.empty:
        return build_message_chart("Y column is not numeric for Line chart")

    fig, ax = plt.subplots(figsize=(5.0, 4))

    if pd.api.types.is_numeric_dtype(x_series):
        working_df = working_df.sort_values(by=x_column)
        sns.lineplot(data=working_df, x=x_column, y=y_column, marker="o", ax=ax, color="#c96ba0")
    else:
        grouped_df = (
            working_df.groupby(x_column, as_index=False)[y_column]
            .mean()
            .sort_values(by=y_column, ascending=False)
            .head(25)
        )
        sns.lineplot(data=grouped_df, x=x_column, y=y_column, marker="o", ax=ax, color="#c96ba0")
        ax.tick_params(axis="x", rotation=35)

    ax.set_title(chart_title)
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)

    return figure_to_base64(fig)


def build_summary_list(df, category_column, numeric_column):
    
    if category_column is None:
        return [html.Li("Upload data to see summary", className="summary-item")]

    category_series, category_error = get_column_as_series(df, category_column)
    if category_error is not None:
        return [html.Li(category_error, className="summary-item")]

    top_values = category_series.astype(str).value_counts().head(5)

    if top_values.empty:
        return [html.Li("No values available for summary", className="summary-item")]

    numeric_series = None
    if numeric_column is not None:
        numeric_series, _ = get_column_as_series(df, numeric_column)
        if numeric_series is not None:
            numeric_series = pd.to_numeric(numeric_series, errors="coerce")

    color_classes = ["purple", "pink", "yellow", "green", "blue"]
    item_components = []

    for index, category_name in enumerate(top_values.index):
        value_text = str(top_values.loc[category_name])

        if numeric_series is not None:
            filtered_values = numeric_series[category_series.astype(str) == category_name].dropna()
            if not filtered_values.empty:
                value_text = f"{filtered_values.sum():,.2f}"

        item_components.append(
            html.Li(
                [
                    html.Div(
                        [
                            html.Div(className=f"item-icon {color_classes[index % len(color_classes)]}"),
                            html.Span(str(category_name), className="item-name"),
                        ],
                        className="item-left",
                    ),
                    html.Span(value_text, className="item-value"),
                ],
                className="summary-item",
            )
        )

    return item_components


def build_summary_title(category_column, numeric_column):
    
    if category_column in [None, ""] or numeric_column in [None, ""]:
        return "Top 5 summary"

    return f"Top 5 by {category_column} (sum of {numeric_column})"


def build_chart_titles(category_column, x_column, y_column):
    
    pie_title = "Distribution"
    line_title = "Trend"
    bar_title = "Performance"
    hist_title = "Scatter plot"

    if category_column not in [None, ""]:
        pie_title = f"Distribution by {category_column}"
        bar_title = f"Top counts by {category_column}"

    if x_column not in [None, ""] and y_column not in [None, ""]:
        line_title = f"{y_column} by {x_column}"

    if x_column not in [None, ""] and y_column not in [None, ""]:
        hist_title = f"Scatter plot of {y_column} vs {x_column}"

    return pie_title, line_title, bar_title, hist_title


app.layout = html.Div(
    [
        dcc.Store(id="stored-data"),
        dcc.Loading(
            id="global-loading",
            type="circle",
            fullscreen=False,
            color="#9b7edb",
            parent_style={"position": "relative", "zIndex": 9999},
            overlay_style={"visibility": "visible"},
            children=html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                "DV",
                                className="logo",
                            ),
                            html.Div("DataVista", className="brand-name"),
                        ],
                        className="header",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div(
                                                        "Distribution",
                                                        id="pie-title",
                                                        className="card-header",
                                                    ),
                                                    html.Div(
                                                        [html.Img(id="pie-chart", className="dash-chart-img")],
                                                        className="chart-container",
                                                    ),
                                                ],
                                                className="card",
                                            ),
                                            html.Div(
                                                [
                                                    html.Div("Top 5 summary", id="summary-title", className="card-header"),
                                                    html.Ul(id="summary-list", className="summary-list"),
                                                ],
                                                className="card",
                                            ),
                                        ],
                                        className="dashboard-row row-2-cols",
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div("Trend", id="line-title", className="card-header"),
                                                    html.Div(
                                                        [html.Img(id="line-chart", className="dash-chart-img")],
                                                        className="chart-container",
                                                    ),
                                                ],
                                                className="card",
                                            ),
                                            html.Div(
                                                [
                                                    html.Div("Performance", id="bar-title", className="card-header"),
                                                    html.Div(
                                                        [html.Img(id="bar-chart", className="dash-chart-img")],
                                                        className="chart-container",
                                                    ),
                                                ],
                                                className="card",
                                            ),
                                        ],
                                        className="dashboard-row row-2-cols",
                                    ),
                                ],
                                className="dashboard",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            dcc.Upload(
                                                id="upload-csv",
                                                children=html.Button("Import CSV", className="import-btn"),
                                                multiple=False,
                                            ),
                                            html.Div(id="file-status", className="status-text"),
                                            html.Div(id="dataset-summary", className="status-text"),
                                        ],
                                        className="config-section",
                                    ),
                                    html.Div(
                                        [
                                            html.Div("Data selection (NEW)", className="section-title"),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Div("Rows", className="select-label"),
                                                            html.Div("Row1", className="select-demo-text"),
                                                            dcc.Dropdown(
                                                                id="row-limit-select",
                                                                options=[
                                                                    {"label": "Select rows", "value": ""},
                                                                    {"label": "First 10 rows", "value": "10"},
                                                                    {"label": "First 50 rows", "value": "50"},
                                                                    {"label": "First 100 rows", "value": "100"},
                                                                    {"label": "All rows", "value": "all"},
                                                                ],
                                                                value="",
                                                                clearable=False,
                                                            ),
                                                        ],
                                                        className="select-field",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Div("Group By (X-axis)", className="select-label"),
                                                            dcc.Dropdown(id="line-x-column", options=[], value="", clearable=False),
                                                        ],
                                                        className="select-field",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Div("Value (Y-axis)", className="select-label"),
                                                            dcc.Dropdown(id="line-y-column", options=[], value="", clearable=False),
                                                        ],
                                                        className="select-field",
                                                    ),
                                                ],
                                                className="select-group",
                                            ),
                                        ],
                                        className="config-section",
                                    ),
                                    html.Div(
                                        [
                                            html.Div("Data preview", className="section-title"),
                                            html.Div(id="data-preview", className="data-table"),
                                        ],
                                        className="config-section",
                                    ),
                                    html.Div(
                                        [
                                            html.Div("Scatter plot", id="hist-title", className="section-title"),
                                            html.Button("Open Large View", id="hist-open-btn", className="expand-btn"),
                                            html.Div(
                                                [html.Img(id="hist-chart", className="dash-chart-img")],
                                                className="hist-container",
                                            ),
                                        ],
                                        className="config-section",
                                    ),
                                ],
                                className="side-config",
                            ),
                        ],
                        className="container",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div("Scatter Plot - Large View", className="modal-title"),
                                    html.Button("Close", id="hist-modal-close", className="expand-btn"),
                                ],
                                className="modal-header",
                            ),
                            html.Div(
                                [html.Img(id="hist-modal-img", className="modal-chart-img")],
                                className="modal-body",
                            ),
                        ],
                        id="hist-modal",
                        className="modal-overlay",
                        style={"display": "none"},
                    ),
                ],
                className="app-shell",
            ),
        ),
    ]
)


@app.callback(
    Output("file-status", "children"),
    Output("dataset-summary", "children"),
    Output("data-preview", "children"),
    Output("stored-data", "data"),
    Output("line-x-column", "options"),
    Output("line-x-column", "value"),
    Output("line-y-column", "options"),
    Output("line-y-column", "value"),
    Input("upload-csv", "contents"),
    State("upload-csv", "filename"),
)
def update_data_state(uploaded_contents, uploaded_filename):
    if uploaded_contents is None:
        return (
            "No file uploaded yet.",
            "Rows: -, Columns: -, Missing cells: -, Duplicate rows: -",
            "Upload a CSV file to see a preview.",
            None,
            [{"label": "Select line X", "value": ""}],
            "",
            [{"label": "Select line Y", "value": ""}],
            "",
        )

    df, read_error = parse_uploaded_csv(uploaded_contents)

    if read_error is not None:
        return (
            read_error,
            "Rows: -, Columns: -, Missing cells: -, Duplicate rows: -",
            "Could not build preview.",
            None,
            [{"label": "Select line X", "value": ""}],
            "",
            [{"label": "Select line Y", "value": ""}],
            "",
        )

    row_count = len(df)
    column_count = len(df.columns)
    missing_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    summary_text = (
        f"Rows: {row_count} | "
        f"Columns: {column_count} | "
        f"Missing cells: {missing_cells} | "
        f"Duplicate rows: {duplicate_rows}"
    )

    preview_table = create_preview_table(df, max_rows=5)

    category_column, numeric_column = find_chart_columns(df)
    line_x_column, line_y_column = pick_line_columns(df)

    line_x_options = [{"label": "Select line X", "value": ""}]
    line_y_options = [{"label": "Select line Y", "value": ""}]

    for column_name in df.columns:
        line_x_options.append({"label": str(column_name), "value": str(column_name)})
        if pd.api.types.is_numeric_dtype(df[column_name]):
            line_y_options.append({"label": str(column_name), "value": str(column_name)})

    if uploaded_filename is None:
        uploaded_filename = "Unknown file"

    status_text = f"Loaded file: {uploaded_filename}"
    stored_data_json = df.to_json(date_format="iso", orient="split")

    return (
        status_text,
        summary_text,
        preview_table,
        stored_data_json,
        line_x_options,
        "" if line_x_column is None else str(line_x_column),
        line_y_options,
        "" if line_y_column is None else str(line_y_column if numeric_column is None else numeric_column),
    )


@app.callback(
    Output("pie-title", "children"),
    Output("line-title", "children"),
    Output("bar-title", "children"),
    Output("hist-title", "children"),
    Output("pie-chart", "src"),
    Output("line-chart", "src"),
    Output("bar-chart", "src"),
    Output("hist-chart", "src"),
    Output("hist-modal-img", "src"),
    Output("summary-title", "children"),
    Output("summary-list", "children"),
    Input("stored-data", "data"),
    Input("row-limit-select", "value"),
    Input("line-x-column", "value"),
    Input("line-y-column", "value"),
)
def update_charts(stored_data, row_limit_select, line_x_column, line_y_column):
    if stored_data is None:
        empty_message = build_message_chart("Upload a CSV to generate charts")
        return (
            "Distribution",
            "Trend",
            "Performance",
            "Scatter plot",
            empty_message,
            empty_message,
            empty_message,
            empty_message,
            empty_message,
            "Top 5 summary",
            [html.Li("Upload data to see summary", className="summary-item")],
        )

    try:
        df = pd.read_json(io.StringIO(stored_data), orient="split")
        used_df = apply_row_limit(df, row_limit_select)

        auto_category, auto_numeric = find_chart_columns(used_df)
        auto_line_x, auto_line_y = pick_line_columns(used_df)

        if line_x_column in [None, ""]:
            line_x_column = auto_line_x

        if line_y_column in [None, ""]:
            line_y_column = auto_numeric if auto_numeric is not None else auto_line_y

        if line_y_column not in used_df.columns:
            error_chart = build_message_chart("Select a numeric Y column for charts")
            return (
                "Distribution",
                "Trend",
                "Performance",
                "Scatter plot",
                error_chart,
                error_chart,
                error_chart,
                error_chart,
                error_chart,
                "Top 5 summary",
                [html.Li("Select a numeric Y column for summary", className="summary-item")],
            )

        y_check_series = pd.to_numeric(used_df[line_y_column], errors="coerce").dropna()
        if y_check_series.empty:
            error_chart = build_message_chart("Selected Y column is not numeric")
            return (
                "Distribution",
                "Trend",
                "Performance",
                "Scatter plot",
                error_chart,
                error_chart,
                error_chart,
                error_chart,
                error_chart,
                "Top 5 summary",
                [html.Li("Selected Y column is not numeric", className="summary-item")],
            )

        category_column = line_x_column if line_x_column not in [None, ""] else auto_category
        pie_title, line_title, bar_title, hist_title = build_chart_titles(
            category_column,
            line_x_column,
            line_y_column,
        )

        pie_src = build_pie_chart(used_df, category_column, chart_title=pie_title)
        line_src = build_line_chart(used_df, line_x_column, line_y_column, chart_title=line_title)
        bar_src = build_bar_chart(used_df, category_column, chart_title=bar_title)
        hist_src = build_scatter_plot(used_df, line_x_column, line_y_column, chart_title=hist_title)
        summary_title = build_summary_title(category_column, line_y_column)
        summary_items = build_summary_list(used_df, category_column, line_y_column)

        return (
            pie_title,
            line_title,
            bar_title,
            hist_title,
            pie_src,
            line_src,
            bar_src,
            hist_src,
            hist_src,
            summary_title,
            summary_items,
        )
    except Exception as error:
        error_chart = build_message_chart(f"Chart callback error: {error}")
        return (
            "Distribution",
            "Trend",
            "Performance",
            "Scatter plot",
            error_chart,
            error_chart,
            error_chart,
            error_chart,
            error_chart,
            "Top 5 summary",
            [html.Li(f"Summary error: {error}", className="summary-item")],
        )


@app.callback(
    Output("hist-modal", "style"),
    Input("hist-open-btn", "n_clicks"),
    Input("hist-modal-close", "n_clicks"),
)
def toggle_hist_modal(open_clicks, close_clicks):
    open_count = 0 if open_clicks is None else open_clicks
    close_count = 0 if close_clicks is None else close_clicks

    if open_count > close_count:
        return {"display": "flex"}

    return {"display": "none"}


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
