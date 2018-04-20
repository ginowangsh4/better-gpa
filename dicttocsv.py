import os

def saveDictionariesToCSV(dictionaries, fileName):
    csvFirstLine = "";
    csvContent = "";
    keys = sorted(dictionaries[0].keys())
    for key in keys:
        csvFirstLine += key + ","

    for dictionary in dictionaries:
        for key in keys:
            if key in dictionary:
                csvContent += dictionary[key].encode('utf-8') + ","
            else:
                csvContent += "N/A,"
        csvContent += "\n"
    csvContent = csvFirstLine + "\n" + csvContent

    path = os.path.expanduser("~/Desktop/" + fileName + ".csv")
    print("Saving CSV to " + path)
    with open(path, "w") as text_file:
        text_file.write(csvContent)
