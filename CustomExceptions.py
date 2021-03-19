class DuplicateEntryError(Exception):
    pass


class Set_duplicate_detector(set):
    count = 0

    def add(self, value):
        if value in self:
            self.count += 1
            raise DuplicateEntryError()
        super().add(value)


class NoElementFound(Exception):

    def __init__(self, changed_attribute):
        self.message = "\nWARNING: WEBPAGE HTML NAME MAY HAVE CHANGED, TRY UPDATING ELEMENT IDENTIFIER\n" \
                       "CHANGED ELEMENT ATTRIBUTE: {}".format(changed_attribute)
        super().__init__(self.message)
