from additional_task import table, websocket_response, base_ws
import json
import re


def transform_table_to_json(table, websocket_response, base_ws):
    """
    Преобразует таблицу в JSON-запрос.
    """
    result = {
        "columns": [],
        "order_by": {},
        "conditions_data": {},
        "page_size": "",
        "row_height": "",
        "color_conditions": {},
        "module": "SO"
    }

    for index, row in enumerate(table):
        for key, value in row.items():
            if key in base_ws:
                field_name = base_ws[key]

                if key == "Columns View" and value in websocket_response:
                    column_info = websocket_response[value]
                    result["columns"].append({
                        "index": column_info["index"],
                        "sort": index
                    })

                elif key == "Sort By" and value:

                    result["order_by"] = {"direction": value, "index": websocket_response[row["Columns View"]]["index"]}

                elif key == "Condition" and value:
                    conditions = [
                        {"type": cond.split("=")[0], "value": cond.split("=")[1]}
                        for cond in value.split(",") if "=" in cond
                    ]
                    result["conditions_data"][websocket_response[row["Columns View"]]["filter"]] = conditions

                elif key == "Lines per page" and value:
                    result["page_size"] = value

                elif key == "Row Height" and value:
                    result["row_height"] = value

                elif key == "Highlight By" and value:
                    highlights = []
                    for highlight in re.findall(r"([a-zA-Z]+)=([^=]+)(?:=(rgba\([^\)]+\)|[^,]+))?", value):
                        highlight_type = highlight[0]
                        highlight_value = highlight[1]
                        highlight_color = highlight[2] if highlight[2] else ""
                        highlights.append({"type": highlight_type, "value": highlight_value, "color": highlight_color})
                    result["color_conditions"].setdefault(websocket_response[row["Columns View"]]["filter"], []).extend(highlights)

    return result


if __name__ == "__main__":
    json_output = transform_table_to_json(table, websocket_response, base_ws)
    print(json.dumps(json_output, indent=2))
