from random import choices
from typing import List

from core.log import log
from core.db import pools_db as db
from core.db.models.pool_models import Entry
from core import utils, language

locale = language.Locale("core.loot_tables")


def list(serverId: int = 0) -> str:
    pools = db.get_all_pools(serverId)
    if pools is not None and len(pools) > 0:

        body = '\n'.join(
            [f'\t{pool.name}\t{"(global)" if pool.server_id == 0 else ""}' for pool in pools])
        return locale.get_string('poolsAvailable', body=body)
    else:
        return locale.get_string('noPoolsAvailable')


def info(serverId: int, poolName: str) -> str:
    pool = db.get_pool(serverId, poolName)
    if pool is not None:
        return pool.__str__()
    else:
        return locale.get_string('poolNotFound', pool=poolName)


def roll(serverId: int, poolName: str, numRolls: int = 1, extraEntries: List[Entry] = None) -> str:
    chosenEntries, error = _get_roll_entries(serverId, poolName, numRolls, extraEntries)

    if error is not None:
        return error

    # A list of all result strings, bullet pointed
    results = '\n'.join(f'→ {entry.description}' for entry in chosenEntries)

    # Initialize the first message in the body
    header = locale.get_string('rollHeader', poolName=poolName)

    msg = (f'{header}'
           f'{results}\n'
           )

    return msg


def _get_roll_entries(serverId: int,
                      poolName: str,
                      numRolls: int = 1,
                      extraEntries: List[Entry] = None
                      ) -> tuple[List[Entry], str]:
    pool = db.get_pool(serverId, poolName)
    if pool is None:
        return (None, locale.get_string('poolNotFound', pool=poolName))

    if len(pool.entries) == 0 and extraEntries is None:
        return (None, locale.get_string('poolEmpty'))

    if extraEntries is not None:
        for entry in extraEntries:
            pool.entries.append(entry)

    chosenEntries = choices(pool.entries, weights=[
                            entry.amount for entry in pool.entries], k=numRolls)

    return (chosenEntries, None)


def combo(serverId: int, numRolls: int = 1, *poolNames) -> str:
    entriesWithErrors = [_get_roll_entries(serverId, poolName, numRolls) for poolName in poolNames]

    manyChosenEntries = []
    for (entry, error) in entriesWithErrors:
        if error is not None:
            return error

        manyChosenEntries.append(entry)

    results = []
    for i in range(len(manyChosenEntries[0])):
        results.append('→ ' + ' | '.join(entries[i].description for entries in manyChosenEntries))

    result = '\n'.join(results)

    header = locale.get_string('rollHeader', poolName='several pools')

    return (f'{header}'
            f'{result}')


def add(serverId: int, poolName: str, entries: List[Entry], deleteMode: bool = False) -> str:
    '''
    Adds a number of entries to a given pool
    '''
    pool = db.get_pool(serverId, poolName)
    if pool is None or (pool.server_id != serverId and pool.server_id != 0):
        return locale.get_string('poolNotFound', pool=poolName)

    # Additions
    if not deleteMode:
        for entry in entries:
            matchingResults = [
                e for e in pool.entries if e.description == entry.description]
            matchingResult = matchingResults[0] if len(
                matchingResults) else None

            # Add a new result to the pool
            if matchingResult is None:
                try:
                    db.add_entry(pool.id, entry.description, entry.amount)
                except Exception:
                    log.info(
                        f'Failed to add result `{entry.description}` to pool {pool.name}')
                    return locale.get_string('resultAddFail', entryDescription=entry.description)
            else:
                try:
                    matchingResult.amount += entry.amount
                    db.update_entry(matchingResult.id, matchingResult.amount)
                except Exception:
                    return locale.get_string('resultAddFail', entryDescription=entry.description)

        return locale.get_string('resultAddSuccess', plural="s" if len(entries) > 1 else "", poolName=pool.name)

    # Deletions
    else:
        deletionResponse = ""
        for entry in entries:
            matchingResults = [
                e for e in pool.entries if e.description == entry.description]
            matchingResult = matchingResults[0] if len(
                matchingResults) else None

            if matchingResult is not None:
                matchingResult.amount -= entry.amount
                if matchingResult.amount < 1:
                    try:
                        db.unset_entry(matchingResult.id)
                    except Exception:
                        log.info(f'Failed to remove result {matchingResult.name} '
                                 f'with id {matchingResult.id} from database')
                        return locale.get_string('resultRemoveFail', entryDescription=entry.description)

                try:
                    db.update_entry(matchingResult.id, matchingResult.amount)
                except Exception:
                    log.info(
                        f'Failed to update result with id {matchingResult.id} in database')
                    return locale.get_string('resultRemoveFail', entryDescription=entry.description)
            else:
                if len(entries) == 1:
                    return locale.get_string('resultRemoveDoesNotExist')

                deletionResponse += f'"{entry.description}" does not exist in pool. Skipping...\n'

        deletionResponse += locale.get_string('resultRemovedSuccess')
        return deletionResponse


def create(serverId: int, creatorId: int, poolName: str, isGlobal: bool = False) -> str:
    if isGlobal and utils.is_admin(creatorId, serverId):
        serverId = 0

    if isGlobal and not utils.is_admin(creatorId, serverId):
        return locale.get_string('createGlobalAccessDenied')

    existing = db.get_pool(serverId, poolName)

    if existing is not None:
        return locale.get_string('poolAlreadyExists')

    try:
        db.add_pool(serverId, creatorId, poolName)
        return locale.get_string('poolCreatedSuccess', poolName=poolName)

    except Exception:
        log.info(f'Failed to create pool {poolName}.')
        return locale.get_string('poolCreatedFail')


def delete(poolName: str, serverId: int, userId: int) -> str:
    pool = db.get_pool(serverId, poolName)
    if not pool or (pool.server_id != serverId and pool.server_id != 0):
        return locale.get_string('poolDeleteNotFound', poolName=poolName)

    if pool.creator_id != userId and not utils.is_admin(userId):
        return locale.get_string('deleteAccessDenied')

    try:
        db.unset_pool(pool.id)
        return locale.get_string('poolDeleteSuccess', poolName=poolName)
    except Exception:
        log.info(
            f'Failed to remove pool {pool.name} with id {pool.id} from database')
        return locale.get_string('poolDeleteFail')
