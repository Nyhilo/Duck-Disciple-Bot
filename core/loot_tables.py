import core.db.pools_db as db
import core.utils as utils


def list(serverId=0):
    pools = db.get_all_pools(serverId)
    return 'Pools available for this server:\n' + '\n'.join([f'\t{pool.name}' for pool in pools])


def info(pool):
    pool = db.get_pool(pool)
    return pool.__str__()


def roll(serverId, pool, extraEntry=None, extraAmount=None):
    pass


def add(serverId, poolName, entry, amount=1):
    pool = db.get_pool(poolName)
    db.add_entry(pool.id, entry, amount)


def remove(serverId, pool, entry, amount=-1):
    pass


def create(serverId, creatorId, pool, isGlobal=False):
    if isGlobal and utils.is_admin(creatorId):
        serverId = 0

    # TODO: Check if pool already exists
    db.add_pool(serverId, creatorId, pool)


def remove(serverId, creatorId, pool):
    pass
