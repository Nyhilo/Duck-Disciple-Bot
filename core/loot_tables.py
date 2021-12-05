from core.log import log
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
    '''
    Adds a number of entries to a given pool
    '''
    pool = db.get_pool(poolName)
    db.add_entry(pool.id, entry, amount)



def create(serverId, creatorId, poolName, isGlobal=False):
    if isGlobal and utils.is_admin(creatorId):
        serverId = 0

    existing = db.get_pool(poolName)

    if not existing:
        db.add_pool(serverId, creatorId, poolName)


def remove(poolName, userId):
    pool = db.get_pool(poolName)
    if not pool:
        return f'Pool named `{poolName}` not found.'

    if pool.creator_id != userId and not utils.is_admin(userId):
        return 'You do not have permission to delete that pool.'

    if db.unset_pool(pool.id):
        return f'{pool.name} pool removed.'
    else:
        log.info(f'Failed to remove pool {pool.name} with id {pool.id} from database')
        return f'Whoops, something went wrong trying to remove the pool named {pool.name}.'
