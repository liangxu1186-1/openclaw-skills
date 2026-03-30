TOP_LIMIT = 10


def default_normalize_api_path(api_path):
    if not api_path:
        raise ValueError("path 不能为空")
    return api_path if api_path.startswith("/") else "/" + api_path


def to_number(value):
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            if "." in raw:
                return float(raw)
            return int(raw)
        except ValueError:
            return None
    return None


def sort_desc(items, key):
    return sorted(items, key=lambda item: to_number(item.get(key)) or 0, reverse=True)


def pick_fields(payload, fields):
    return {field: payload[field] for field in fields if field in payload and payload[field] is not None}


def limit_items(items, limit=TOP_LIMIT):
    if not isinstance(items, list):
        return []
    return items[:limit]


def build_named_rows(rows, fields, sort_key=None):
    if not isinstance(rows, list):
        return []
    normalized_rows = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        normalized = {
            "name": row.get("orgName")
            or row.get("shopName")
            or row.get("timeName")
            or row.get("periodName")
            or row.get("periodDate")
            or row.get("cityName")
            or row.get("provinceName")
            or row.get("groupByName")
            or row.get("paySubjectGroupName")
            or "未命名项"
        }
        normalized.update(pick_fields(row, fields))
        normalized_rows.append(normalized)
    if sort_key:
        normalized_rows = sort_desc(normalized_rows, sort_key)
    return limit_items(normalized_rows)


def compact_rank_summary(result, payload, request_fields, item_fields, sort_key):
    if not isinstance(result, dict):
        return result

    return {
        "request": pick_fields(payload or {}, request_fields),
        "size": result.get("size"),
        "topStores": limit_items(
            sort_desc(
                [pick_fields(item, item_fields) for item in result.get("list") or [] if isinstance(item, dict)],
                sort_key,
            )
        ),
    }
