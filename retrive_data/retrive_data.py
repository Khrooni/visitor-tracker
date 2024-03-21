import requests
import json


def get_json_info(json_data):
    """
    Extracts information from JSON data and returns a list containing dictionaries
    representing each entry along with the total entries.

    Parameters:
        json_data (str): A JSON formatted string containing the data to be processed.

    Returns:
        list: A list containing dictionaries representing each entry along with the total entries.
              Each dictionary contains the following keys:
              - 'location_id': The ID of the location.
              - 'location_name': The name of the location.
              - 'person_entries': The number of person entries for the location.
              The last dictionary in the list contains the total entries with the key 'entries_total'.

    Example:
        json_data = '''
        {
            "entriesByLocation": [
                {
                    "locationId": 1,
                    "locationName": "FUN Oulu Ritaharju",
                    "personEntries": 21
                }
            ],
            "entriesTotal": 21
        }
        '''
        information = get_json_info(json_data)
        print(information)

        Output:
        [{'location_id': 1, 'location_name': 'FUN Oulu Ritaharju', 'person_entries': 21}, {'entries_total': 21}]
    """
    parsed_data = json.loads(json_data)

    entries_by_location = parsed_data["entriesByLocation"]
    entries_total = parsed_data["entriesTotal"]

    info_list = []

    for entry in entries_by_location:
        location_id = entry["locationId"]
        location_name = entry["locationName"]
        person_entries = entry["personEntries"]

        entry_info = {
            "location_id": location_id,
            "location_name": location_name,
            "person_entries": person_entries,
        }
        info_list.append(entry_info)

    info_list.append({"entries_total": entries_total})

    return info_list


if __name__ == "__main__":

    url = "https://funouluritaharju.fi/?controller=ajax&getentriescount=1&locationId=1"

    page = requests.get(url)

    date = page.headers.get("date")

    data = json.loads(page.text)

    location_id = 0
    location_name = "No name"
    person_entries = 0
    entries_total = data["entriesTotal"]

    entries_by_location = data["entriesByLocation"]

    for entry in entries_by_location:
        location_id = entry["locationId"]
        location_name = entry["locationName"]
        person_entries = entry["personEntries"]
        print("Location ID:", location_id)
        print("Location Name:", location_name)
        print("Person Entries:", person_entries)

    print("Total Entries: ", entries_total)
    jep = get_json_info(page.text)

    jep.append({"date": date})

    int = 2
