class Pool():
    def __init__(self, id, name, server_id, creator_id, entries):
        self.id = id
        self.name = name
        self.server_id = server_id
        self.creator_id = creator_id
        self.entries = entries

    def __str__(self):
        body = 'Entries | Description\n'
        for entry in self.entries:
            body += f'{entry.amount:>7} | {entry.description}\n'

        return body

    def __repr__(self):
        return self.__str__()


class Entry():
    def __init__(self, id, parent_pool, amount, description):
        self.id = id
        self.parent_pool = parent_pool
        self.amount = amount
        self.description = description
