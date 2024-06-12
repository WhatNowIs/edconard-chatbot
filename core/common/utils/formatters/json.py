def remove_nulls_and_empty_strings(json_tree):
    """
    Recursively removes null values and empty strings from a JSON tree.
    """
    if isinstance(json_tree, dict):
        return {key: remove_nulls_and_empty_strings(value) for key, value in json_tree.items() if value is not None and value != ''}
    elif isinstance(json_tree, list):
        return [remove_nulls_and_empty_strings(item) for item in json_tree if item is not None and item != '']
    else:
        return json_tree