class Pool():
    def __init__(self, id=None, name=None, server_id=None, creator_id=None, entries=[]):
        self.id = id
        self.name = name
        self.server_id = server_id
        self.creator_id = creator_id
        self.entries = entries

    def __str__(self):
        if len(self.entries) == 0:
            return '```This pool is empty.```'

        body = 'Entries | Description\n'
        for entry in self.entries:
            body += f'{entry.amount:>7} | {entry.description}\n'

        body = f'{self.name.title()} Pool:\n```\n{body}\n```'

        return body


class Entry():
    def __init__(self, id=None, parent_pool=None, amount=None, description=None):
        self.id = id
        self.parent_pool = parent_pool
        self.amount = amount
        self.description = description
