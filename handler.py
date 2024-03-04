class Handler:
    def __init__(self):
        self.dbPathOrUrl = ""

    def getDbPathOrUrl(self):
        return self.dbPathOrUrl

    def setDbPathOrUrl(self, new_path_or_url):
        if type(new_path_or_url) == str:
            self.dbPathOrUrl = new_path_or_url
            return self.dbPathOrUrl == new_path_or_url
        else:
            return False
