import lxml.etree as et
#incomplete example of writing XML files to disk
class XMLWriter:

    def __init__(self):
        self.__inputTree
        self.__outputFileName


    def writer(self, self.__inputTree, self.__outputFileName):
        self.__inputTree.write(self.__outputFileName, xml_declaration="1.0")