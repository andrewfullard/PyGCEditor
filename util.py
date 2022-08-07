def getObject(name: str, objectList: set):
    """Finds a named object in a list of objects and returns it"""
    for o in objectList:
        if o.name.lower() == name.lower():
            if o is not None:
                return o

    print("Object " + name + " not found!")

def commaSepListParser(entry: str) -> list():
    """Parses a comma-separated string into a Python List"""
    entry = entry.replace(",", " ")
    return entry.split()

def commaReplaceInList(listToReplace: list) -> list():
    """Replaces spurious commas in a Python List"""
    outputList = []
    for text in listToReplace:
        newText = text.replace(",", "")
        outputList.append(newText)
    return outputList
