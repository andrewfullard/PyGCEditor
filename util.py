def getObject(name: str, objectList: set):
    """Finds a named object in a list of objects and returns it"""
    for o in objectList:
        if o.name.lower() == name.lower():
            if o is not None:
                return o

    print("Object " + name + " not found!")
