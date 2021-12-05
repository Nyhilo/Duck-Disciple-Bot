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


def add(serverId, poolName, entryDesc, amount=1):
    '''
    Adds a number of entries to a given pool
    '''
    pool = db.get_pool(poolName)
    if pool is None or (pool.server_id != serverId and pool.server_id != 0):
        return 'Could not find a pool with that name for this server.'

    matchingResults = [e for e in pool.entries if e.description == entryDesc]
    matchingResult = matchingResults[0] if len(matchingResults) else None

    # Add a new result to the table
    if matchingResult is None:
        if db.add_entry(pool.id, entryDesc, amount):
            return f'Successfullly added result to {pool.name}'
        else:
            log.info(f'Failed to add result {matchingResult.name} with id {matchingResult.id} to pool {pool.name}')
            return 'Whoops, something went wrong trying to add this result.'

    # Updating an existing result.
    matchingResult.amount += amount
    if matchingResult.amount < 0:
        if db.unset_entry(matchingResult.id):
            return 'Removed result.'
        else:
            log.info(f'Failed to remove result {matchingResult.name} with id {matchingResult.id} from database')
            return 'Whoops, something went wrong trying to remove the result.'

    if db.update_entry(matchingResult.id, matchingResult.amount):
        return 'Updated result with new amount.'
    else:
        log.info(f'Failed to update result {matchingResult.name} with id {matchingResult.id} from database')
        return 'Whoops, something went wrong trying to update the result.'


def create(serverId, creatorId, poolName, isGlobal=False):
    if isGlobal and utils.is_admin(creatorId):
        serverId = 0

    existing = db.get_pool(poolName)

    if existing is not None:
        return 'Pool with that name already existss.'

    if db.add_pool(serverId, creatorId, poolName):
        return f'Created new pool {poolName}'
    else:
        log.info(f'Failed to creat pool {poolName}.')
        return 'Whoops, something went wrong trying to create that pool.'


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
