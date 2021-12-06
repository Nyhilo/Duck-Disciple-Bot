from random import choices

from core.log import log
import core.db.pools_db as db
from core.db.models.pool_models import Entry
import core.utils as utils


def list(serverId=0):
    pools = db.get_all_pools(serverId)
    if pools is not None and len(pools) > 0:
        return 'Pools available for this server:\n' + '\n'.join([f'\t{pool.name}' for pool in pools])
    else:
        return 'There are no pools available on this server.'


def info(serverId, pool):
    pool = db.get_pool(serverId, pool)
    if pool is not None:
        return pool.__str__()
    else:
        return 'Could not find a pool with that name for this server.'


def roll(serverId, poolName, numRolls=1, extraEntry=None, extraAmount=1):
    pool = db.get_pool(serverId, poolName)
    if pool is None:
        return 'Could not find a pool with that name for this server.'

    if len(pool.entries) == 0 and extraEntry is None:
        return 'There are no results in this pool to roll on.'

    if len(pool.entries) == 0 and extraEntry is not None:
        return extraEntry

    if extraEntry is not None:
        pool.entries.append(Entry(0, 0, extraAmount, extraEntry))

    chosenEntries = choices(pool.entries, weights=[entry.amount for entry in pool.entries], k=numRolls)

    # This might go over the discord character limits, so we need to break the message up
    messageLimit = 2000

    # A list of all result strings, bullet pointed
    results = [f'* {entry.description}\n' for entry in chosenEntries]

    # Initialize the first message in the body
    body = [f'Result pulling from {pool.name}:\n```\n']

    index = 0
    for result in results:
        if len(body[index] + result) > messageLimit:
            # Close the current message
            body[index] += '```'
            # Add a new message to the list
            body.append('```\n')
            # Increment counter so we can add to the new message
            index += 1

        body[index] += result

    # Close the most recent message in the list
    body[index] += '```'

    return body


def add(serverId, poolName, entryDesc, amount=1):
    '''
    Adds a number of entries to a given pool
    '''
    pool = db.get_pool(serverId, poolName)
    if pool is None or (pool.server_id != serverId and pool.server_id != 0):
        return 'Could not find a pool with that name for this server.'

    matchingResults = [e for e in pool.entries if e.description == entryDesc]
    matchingResult = matchingResults[0] if len(matchingResults) else None

    # Add a new result to the table
    if matchingResult is None:
        if amount < 1:
            return f'Cannot remove from result "{entryDesc}" because it does not exist.'

        try:
            db.add_entry(pool.id, entryDesc, amount)
            return f'Successfully added result to {pool.name}'
        except Exception:
            log.info(f'Failed to add result `{entryDesc}` to pool {pool.name}')
            return 'Whoops, something went wrong trying to add this result.'

    # Updating an existing result.
    matchingResult.amount += amount
    if matchingResult.amount < 1:
        try:
            db.unset_entry(matchingResult.id)
            return 'Removed result.'
        except Exception:
            log.info(f'Failed to remove result {matchingResult.name} with id {matchingResult.id} from database')
            return 'Whoops, something went wrong trying to remove the result.'

    try:
        db.update_entry(matchingResult.id, matchingResult.amount)
        return 'Updated result with new amount.'
    except Exception:
        log.info(f'Failed to update result with id {matchingResult.id} in database')
        return 'Whoops, something went wrong trying to update the result.'


def create(serverId, creatorId, poolName, isGlobal=False):
    if isGlobal and utils.is_admin(creatorId):
        serverId = 0

    if isGlobal and not utils.is_admin(creatorId):
        return 'You do not have permission to create global pools.'

    existing = db.get_pool(serverId, poolName)

    if existing is not None:
        return 'Pool with that name already exists.'

    try:
        db.add_pool(serverId, creatorId, poolName)
        return f'Created new pool {poolName}'
    except Exception:
        log.info(f'Failed to creat pool {poolName}.')
        return 'Whoops, something went wrong trying to create that pool.'


def delete(poolName, serverId, userId):
    pool = db.get_pool(serverId, poolName)
    if not pool or (pool.server_id != serverId and pool.server_id != 0):
        return f'Pool named `{poolName}` not found in this server.'

    if pool.creator_id != userId and not utils.is_admin(userId):
        return 'You do not have permission to delete that pool.'

    try:
        db.unset_pool(pool.id)
        return f'{pool.name} pool removed.'
    except Exception:
        log.info(f'Failed to remove pool {pool.name} with id {pool.id} from database')
        return f'Whoops, something went wrong trying to remove the pool named {pool.name}.'
