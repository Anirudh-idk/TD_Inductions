import pandas as pd
import pdfplumber
import json

# Strings for specific field
roomStr = "ROOM NO "
lecCapStr = "LECTURE CAPACITY"
examCapStr = "EXAM CAPACITY"
typeStr = "TYPE "


def CreateJson(pages: list[pdfplumber.page.Page]) -> dict:
    """
    Function to get details about a room from a room map.

    Args:
        pages: list[pdfplumber.page.Page] - list of page objects to extract room information.

    Return:
        dict - Final dictionary with details for each room.

    """

    finalJson: dict = {}
    df: pd.DataFrame() = pd.DataFrame()
    for page in pages:
        table = page.extract_table()

        # To check if the page contains a new room or continuation of previous room
        if roomStr not in table[0][0]:
            df = pd.concat(
                [df, pd.DataFrame(table)]
            )  # add data to previous room dataframe
            df = df.reset_index()
            df.pop("index")
        else:
            df.drop(df.index, inplace=True)  # clear DataFrame if new room
            df = pd.DataFrame(table)

        obj: dict = {}

        if len(df.index) == 9:  # create json if full DataFrame
            df.drop(2)  # dropping the row with hour header
            for index, row in df.iterrows():
                if index == 0:
                    lecCapIndex = list(row).index(lecCapStr)
                    lecCap = df.iloc[index + 1, lecCapIndex]

                    examCapIndex = list(row).index(examCapStr)
                    examCap = df.iloc[index + 1, examCapIndex]

                    for c in list(row):
                        if roomStr in c:
                            Room = c.replace(roomStr, "")
                            break
                    obj[lecCapStr] = lecCap
                    obj[examCapStr] = examCap
                    obj[roomStr] = Room

                elif index == 1:
                    for c in list(row):
                        if typeStr in c:
                            Type = c.replace(typeStr, "")
                            break

                    obj[typeStr] = Type

                else:
                    if obj.get("FixedClasses"):
                        obj["FixedClasses"].append(list(row)[1:])

                    else:
                        obj["FixedClasses"] = []  # initialize FixedClasses field
                        obj["FixedClasses"].append(list(row)[1:])

        finalJson[Room] = obj

    return finalJson


if __name__ == "__main__":
    pageRange: list[int] = [2, 170]  # Start and end page
    roomMap: str = "Room map-jan-31-2023.pdf"

    pdf: pdfplumber.pdf.PDF = pdfplumber.open(roomMap)
    pages: list[pdfplumber.page.Page] = pdf.pages[pageRange[0] - 1 : pageRange[1]]

    json.dump(CreateJson(pages), open("final.json", "w"), indent=2)
