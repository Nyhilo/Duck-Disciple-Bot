from time import sleep
from asyncio import TimeoutError
from random import choice, randint, shuffle

# Global context for simplicity? Set in run_game
# TODO: Refactor this whole thing as a class so this isn't dumb
global_context = None

class Gem():
    def __init__(self, id, size, worth):
        self.id = id
        # Sizes come in 1, 4, and 9
        self.size = size
        self.name = 'Small' if size == 1 else 'Medium' if size == 4 else 'Large' if size == 9 else 'Weird'
        self.type = self.name.lower()
        self.worth = worth


class Wall():
    def __init__(self):
        self.gems = [
            Gem('A', 4, 300_000),
            Gem('B', 9, 600_000),
            Gem('C', 1, 20_000),
            Gem('D', 1, 35_000),
            Gem('E', 9, 1_500_000),
            Gem('F', 1, 10_000),
            Gem('G', 4, 400_000),
            Gem('H', 1, 80_000)
        ]
        self.fully_prospected_gems = []
        self.gem_map = [
            [' ',' ',' ','B','B','B',' ',' '],
            ['A','A','C','B','B','B',' ',' '],
            ['A','A',' ','B','B','B',' ','H'],
            ['D','E','E','E',' ','G','G',' '],
            [' ','E','E','E',' ','G','G',' '],
            [' ','E','E','E','F',' ',' ',' ']
        ]
        self.covereage_map = [
            [ 0 , 0 , 0 , 0 , 1 , 1 , 2 , 2 ],
            [ 1 , 0 , 1 , 0 , 1 , 2 , 2 , 2 ],
            [ 2 , 1 , 1 , 1 , 1 , 2 , 2 , 1 ],
            [ 2 , 2 , 2 , 2 , 2 , 1 , 2 , 1 ],
            [ 1 , 2 , 2 , 2 , 2 , 2 , 2 , 0 ],
            [ 1 , 1 , 2 , 2 , 2 , 1 , 1 , 0 ]
        ]
        self.height, self.width = len(self.gem_map), len(self.gem_map[0])
        self.health = 20
        self.recent_damage = 0
        self.max_health = self.health

        # debug
        self.last_target_coord = [-1, -1]
        self.last_gems_uncovered = []

    def get_healthbar(self):
        if self.health == 0:
            return ('*' * self.recent_damage) + ('.' * (self.max_health - self.recent_damage))
        
        # /\/\/\/\/\/\/ <- number of zigs equal to health
        # /\/\*****.... <- number of asterisks is recently dealt damage
        # /\/\......... <- number of dots equal to previous health lost
        return (
            '\/' * (self.health // 2)                   # Even leading slashes
            + ('\\' * (self.health % 2))                # Trailing odd slash
            + ('*' * self.recent_damage)
            + ('.' * (self.max_health - self.health - self.recent_damage))   # Missing health dots
        )

    def get_map_info_block(self):
        # inverted for reading simplicity. x is vertical, y is horizontal
        x,y = self.height, self.width

        id_count = {}

        # Count unmasked squares
        for i in range(x):
            for j in range(y):
                if self.covereage_map[i][j] == 0:
                    letter = self.gem_map[i][j]
                    if letter not in id_count:
                        id_count[letter] = 0
                    
                    id_count[letter] += 1

        # Build info block
        output = ''
        for gem in self.gems:
            if gem.id in id_count:
                # The gem is partially uncovered
                if id_count[gem.id] < gem.size:
                    percent = f'{int(id_count[gem.id] / gem.size * 100)}%'
                    output += f'{gem.id} - See {percent} of {gem.type} gem\n'
                
                # The gem has been fully unearthed
                else:
                    output += f'{gem.id} - Found {gem.type} gem! - ${gem.worth:,}\n'

                    # Ensure it's in the fully prospected list
                    if gem not in self.fully_prospected_gems:
                        self.fully_prospected_gems.append(gem)

        return (
            '```\n'
            'PROSPECTING\n'
            f'Wall Health: {self.get_healthbar()}\n'
            '\n'
            'Gems Visible:\n'
            f'{output}\n'
            '```'
        )

    def get_mineable_spaces(self, id=None):
        '''Return a list of square coordinates that are valid to mine'''
        coordinates = []
        x,y = self.height, self.width
        
        # If we are searching the whole board
        if id is None:
            for i in range(x):
                for j in range(y):
                    if self.covereage_map[i][j] > 0:
                        coordinates.append([i, j])

        # If we are only looking at one gem
        else:
            for i in range(x):
                for j in range(y):
                    if self.gem_map[i][j] == id and self.covereage_map[i][j] > 0:
                        coordinates.append([i, j])

        return coordinates

    def get_visible_gems(self):
        visible_gems = []
        x,y = self.height, self.width

        # Count visible gems
        for i in range(x):
            for j in range(y):
                if self.covereage_map[i][j] == 0:
                    id = self.gem_map[i][j]
                    if id not in visible_gems:
                        visible_gems.append(id)

        return visible_gems
    
    def gem_ids(self):
        return [gem.id for gem in self.gems]

    def prospect(self, type, spaces):
        '''Returns a tuple
            The first values is list of gem ids with squares that were uncovered during the process.
            The second value is an optional message to display as a result of the attempt'''
        x,y = choice(spaces)
        self.last_target_coord = [x, y]
        
        if type == 'PICK':
            self.covereage_map[x][y] -= 1
            square_contents = self.gem_map[x][y]

            # Some of the wall was dug away, but we don't know what's beneath
            if self.covereage_map[x][y] == 1:
                self.damage_wall()
                return ([], 'Some of the stone was chipped away. The wall recieved a little damage.')

            # The square was completely mined away, and some of a gem was found under
            if self.covereage_map[x][y] == 0 and square_contents != ' ':
                self.damage_wall()
                self.last_gems_uncovered = [square_contents]         
                return ([square_contents],
                       'A bit of a gem has been uncovered! The wall recieved a little damage.')

            # The square was completely mined away, but you didn't uncover any more of a gem             
            if self.covereage_map[x][y] == 0 and square_contents == ' ':
                self.damage_wall(bonus_damage=1)
                self.last_gems_uncovered = [square_contents]
                return ([square_contents],
                       'Some stone was dug away, but nothing new was found. The wall recieved some more damage')

        if type == 'HAMMER':
            # Hammer mines in a cross shape. The adjacent sides don't need to be on top of the target square
            # Using a hammer causes some extra damage inherently
            bonus_damage = 2
            square_contents = self.gem_map[x][y]
            all_uncovered_gems = []

            # Start wtih the center square
            self.covereage_map[x][y] -= 2

            # Extra damage for hitting a square that was only 1 thick
            if self.covereage_map[x][y] < 0:
                self.covereage_map[x][y] = 0
                bonus_damage += 1

            # Extra damage for hitting a square that didn't have a gem under
            if square_contents == ' ':
                bonus_damage += 1
            else:
                all_uncovered_gems.append(square_contents)
            
            # Now for all the adjacent squares
            adjacent_coords = self.get_adjacent_coordinates(x,y)
            for xa,ya in adjacent_coords:
                adj_contents = self.gem_map[xa][ya]

                # If it's already dug up, we may deal some damage but no more
                if self.covereage_map[xa][ya] == 0:
                    if adj_contents == ' ':
                        bonus_damage += 1
                else:
                    # Otherwise, the value must be greater than 0                
                    self.covereage_map[xa][ya] -= 1

                    # Did we uncover any gems near the square we targeted?
                    if (self.covereage_map[xa][ya] == 0
                            and adj_contents != ' '
                            and adj_contents not in all_uncovered_gems):
                        all_uncovered_gems.append(adj_contents)

            self.last_gems_uncovered = all_uncovered_gems

            # Damage the wall with bonus damage
            self.damage_wall(bonus_damage=bonus_damage)

            gems_found = len(all_uncovered_gems)
            # We did a big, clean hit and uncovered multiple gems
            if bonus_damage == 1 and gems_found > 1:
                return (all_uncovered_gems,
                        'You uncovered multiple gems! And the wall was only damaged a little bit!')
            
            
            if bonus_damage <= 3 and gems_found > 1:
                return (all_uncovered_gems,
                        'You uncovered multiple gems! The wall recieved a some damage.')
            
            if bonus_damage <= 5 and gems_found > 1:
                return (all_uncovered_gems,
                        'You uncovered multiple gems! But the wall took quite a bit of damage.')
            
            # Near the maximum amount of damage was dealt.
            # I'm actually not sure this is possible while revealing multiple gems, but including it just in case
            if bonus_damage >= 6 and gems_found > 1:
                return (all_uncovered_gems,
                        'You uncovered a couple gems! But the wall took major damage from that hit.')
            
            # Now for single gem reveals
            if bonus_damage == 1 and gems_found == 1:
                return (all_uncovered_gems,
                        'You uncovered some of a gem. The wall took a little damage.')
            
            if bonus_damage <= 3 and gems_found == 1:
                return (all_uncovered_gems,
                        'You uncovered some of a gem. The wall took some damage in the process.')
            
            if bonus_damage <= 5 and gems_found == 1:
                return (all_uncovered_gems,
                        'You uncovered some of a gem. The wall took quite a bit of damage')
            
            if bonus_damage >= 6 and gems_found == 1:
                return (all_uncovered_gems,
                        'You uncovered some of a gem. But the wall took some major damage.')
            
            # And finally, if no gems were uncovered (such as with an ANY hit)
            if bonus_damage == 1:
                return (all_uncovered_gems,
                        ('You knocked away a bunch of stone, but didn\'t uncover any gems. '
                         'The wall took a little bit of damage.'))
            
            if bonus_damage <= 3:
                return (all_uncovered_gems,
                        ('You knocked away a good amount of stone, but didn\'t uncover any gems. '
                         'The wall took a good amount of damage.'))
            
            if bonus_damage <= 5:
                return (all_uncovered_gems,
                        ('You knocked away some stone, hitting a lot of bare bedrock. '
                         'The wall took a quite a bit of damage.'))
            
            if bonus_damage >= 6:
                return (all_uncovered_gems,
                        ('You hit the bedrock really hard, only knocking away a bit of surface stone '
                         'and the wall took some major damage!'))

    def get_adjacent_coordinates(self, x, y):
        coords = []
        # North
        if x > 0:
            coords.append([x-1, y])
        
        # West
        if y > 0:
            coords.append([x, y-1])
        
        # East
        if y+1 < self.width:
            coords.append([x, y+1])
        
        # South
        if x+1 < self.height:
            coords.append([x+1, y])
        
        return coords

    def damage_wall(self, bonus_damage=0):
        damage = randint(1,2) + bonus_damage
        
        if self.health < damage:
            damage = self.health

        self.health -= damage
        self.recent_damage = damage

    def debug(self):
        # convert arrays to simple grids
        gem_rows = [''.join(row) for row in self.gem_map]
        covereage_rows = [''.join([str(i) for i in row]) for row in self.covereage_map]

        map_rows = []
        for i in range(len(gem_rows)):
            map_rows.append(covereage_rows[i] + ' | ' + gem_rows[i].replace(' ', '.'))

        gem_map = '\n'.join(map_rows)

        x, y = self.last_target_coord
        x += 1
        y += 1

        return (
            '```\n'
            f'Last target coordinate: [{y}, {x}]\n'
            f'Last gems uncovered: {self.last_gems_uncovered}\n\n'
            'Covereage map:\n'
            f'{gem_map}\n'
            '```'
        )


async def run_game(context, bot):
    global ctx
    ctx = context

    await send_intro()

    wall = Wall()

    await send(
        f'{len(wall.gems)} gems detected!',
        'Type HAMMER or PICK along with a letter choice or "ANY" to begin prospecting.',
        wall.get_map_info_block()
    )

    def check_msg(m):
        content = m.content.upper()
        return (
            (m.channel == ctx or m.channel == ctx.channel) and
            (content.startswith('HAMMER') or
             content.startswith('PICK') or
             content.startswith('H ') or
             content.startswith('P ') or
             content.startswith('STOP') or
             content.startswith('EXIT') or
             content.startswith('QUIT') or
             content.startswith('DEBUG'))
        )

    running = True
    stopped = False
    collapsed = False
    quickexit = False
    retries = 0

    general_help_msg = ('Type HAMMER for a big hit or PICK for a small hit followed by the letter of a gem you can see'
                        ' to prospect a specific gem or ANY to prospect a random space.\nFor example: "HAMMER B"')

    # LET'S RUN THE GAME #
    while running:
        try:
            response = (await bot.wait_for('message', timeout=600, check=check_msg)).content.upper()
        except TimeoutError:
            if retries == 0:
                await send(f'{ctx.author.mention}, are you still there? One minute left!')
                retries += 1
                continue
            else:
                await send('Cancelling miningame...')
                running = False
                quickexit = True
                break

        # I didn't want to play this game anyway
        if response == 'EXIT' or response == 'QUIT':
            await ctx.send('Ending minigame.')
            running = False
            quickexit = True
            break

        ## UH-OH DEV TERRITORY!! ##
        if response.startswith('DEBUG'):
            await ctx.send(wall.debug())
            continue
        ##                       ##

        if response.startswith('STOP'):
            running = False
            stopped = True
            break

        args = response.split(' ')
        
        # Gotta do the whole thing man
        if len(args) < 2:
            await send(
                general_help_msg,
                wall.get_map_info_block()
            )
            continue
        
        tool, target = args[0], args[1]

        if tool == 'P':
            tool = 'PICK'

        if tool == 'H':
            tool = 'HAMMER'

        # We're done here
            
        # You can't even see that gem
        if target != 'ANY' and target not in wall.get_visible_gems():
            await send(
                general_help_msg.replace('gem you can see', '*gem you can see*'),
                wall.get_map_info_block()
            )
            continue

        mineable_spaces = wall.get_mineable_spaces(None if target == 'ANY' else target)

        # The player accidentally picks a gem that's already been fully uncovered
        if mineable_spaces == 0 and target != 'ANY':
            await send(
                'That gem has already been mined! Pick somewhere else to dig.',
                wall.get_map_info_block()
            )
            continue

        # Do some prospecting, will damage the wall a bit
        uncovered_gem_ids, message = wall.prospect(tool, mineable_spaces)
        await send(message)

        # We do nothing with this string because we're cheating to make it repopulate the prospected gems list
        wall.get_map_info_block()

        # Report our findings
        for gem in wall.fully_prospected_gems:
            if gem.id in uncovered_gem_ids:
                await send(f'Unearthed a {gem.type} gem, worth ${gem.worth:,}!')

        # Check if we're dead :(
        if wall.health <= 0:
            collapsed = True
            running = False
            await send(wall.get_map_info_block())
            break

        await send(
            'Type HAMMER or PICK along with a letter choice or "ANY" to continue prospecting. Or type STOP to stop.',
            wall.get_map_info_block()
        )

    # Begone!
    if quickexit:
        return
    
    # Otherwise, conclude the game
    gems = wall.fully_prospected_gems
    money = 0
    if stopped:
        if len(gems) == 0:
            await send('Sorry. You didn\'t manage to dig up any gems.')
        
        else:
            await send(f'Congratulations, you unearthed {len(gems)} gems!')
            for gem in gems:
                await send(f'{gem.name} gem worth ${gem.worth:,}')
                money += gem.worth
    
    elif collapsed:
        await send('Ah! The wall collapsed!')
        
        if len(gems) == 0:
            await send('Oh well. You didn\'t manage to dig up any gems anyway.')

        elif len(gems) == 1:
            await send('You managed to save the one gem you dug up, though.')
            gem = gems[0]
            await send(f'{gem.name} gem worth ${gem.worth:,}')
            money += gem.worth

        else:
            # lose a random number of gems, keeping at least one
            print(f'gems: {[gem.id for gem in gems]}')
            found_gems = randint(1, len(gems)-1)
            print(f'num: {found_gems}')
            shuffle(gems)
            print(f'shuffled: {[gem.id for gem in gems]}')
            gems = gems[:found_gems]
            print(f'found: {[gem.id for gem in gems]}')
            
            await send('Some of your gems were lost in the collapse, these are the ones you managed to keep:')
            for gem in gems:
                await send(f'{gem.name} gem worth ${gem.worth:,}')
                money += gem.worth
        
    await send(f'Game Over. You won **${money:,}** from Prospector.')



async def send_intro():
    await send(
        'You have started a demo of the PROSPECTOR minigame. Type EXIT to quit the game early.',

        ('In Prospector, you are attempting to mine gems out of a wall without causing it to collapse.\n'
        'There are 3 sizes of gems (small, medium, and large) buried in a stone wall.\n'
        'Each size of gem is worth a different amount of money.\n'
        'Your job is to use your HAMMER and PICK and dig away at the wall and unearth the gems.\n'
        'But be careful! The wall will lose integrity as you mine it, and it may collapse if it gets too damaged.\n'
        'Using a HAMMER on the wall reveals more of a gem, but does more damage. Using a PICK on the wall does less '
        'damage, but will take longer to unearth a deeply buried stone.\n'
        'You are free to stop at any time, and will keep the gems that you mined up to that point.\n')
    )


# *args so the input is a tuple
async def send(*messages):
    for msg in messages:
        await ctx.send(msg)
        sleep(1)
