import re

import unidecode


def string_cleaner(input_string):
    if isinstance(input_string, str):
        raw_string = re.sub(r'[\/:*?"<>|]', " ", input_string)
        temp_string = re.sub(r"\s+", " ", raw_string)
        stripped_string = temp_string.strip()
        normalised_string = unidecode.unidecode(stripped_string)
        return normalised_string

    elif isinstance(input_string, list):
        cleaned_strings = []
        for string in input_string:
            raw_string = re.sub(r'[\/:*?"<>|]', " ", string)
            temp_string = re.sub(r"\s+", " ", raw_string)
            stripped_string = temp_string.strip()
            normalised_string = unidecode.unidecode(stripped_string)
            cleaned_strings.append(normalised_string)
        return cleaned_strings
