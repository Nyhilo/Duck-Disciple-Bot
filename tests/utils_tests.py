import core.utils
from importlib import reload


def run_tests():
    reload(core.utils)
    # test_long_string_with_codeblock()
    # test_wide_string()
    test_no_spaces()


def test_long_string_with_codeblock():
    long_message = """
Test Pool:
```
Entries | Description
      5 | rusty old bolts
      3 | broken glass bottles
      4 | worn-out rubber tires
      2 | smashed plastic containers
      6 | twisted metal scraps
      3 | discarded soda cans
      5 | frayed electrical wires
      2 | cracked ceramic plates
      7 | empty cardboard boxes
      4 | shattered wooden planks
      5 | bent aluminum pipes
      3 | mangled bicycle parts
      6 | faded newspaper clippings
      4 | crushed tin cans
      2 | decomposing food wrappers
      5 | soiled rags
      3 | torn plastic bags
      4 | splintered wooden crates
      6 | used batteries
      3 | burnt-out light bulbs
      5 | scratched DVDs
      2 | warped vinyl records
      4 | tangled fishing lines
      3 | rusted screws
      5 | moldy books
      2 | broken picture frames
      6 | leaking paint cans
      4 | melted plastic toys
      3 | stained mattress springs
      5 | ripped upholstery
      2 | chipped pottery shards
      4 | old shoe soles
      6 | damaged car parts
      3 | stuck zippers
      5 | twisted wire hangers
      2 | crumpled tin foil
      4 | frayed rope ends
      3 | used tissue papers
      5 | bent nails
      2 | rusty hinges
      4 | peeling wallpaper
      6 | snapped guitar strings
      3 | busted keyboards
      5 | leaking ink pens
      2 | cracked mirrors
      4 | crumpled paper bags
      3 | shredded plastic sheets
      5 | rusty chain links
      2 | worn-out shoes
      4 | old garden hoses
      6 | mismatched socks
      3 | chipped paint flakes
      5 | broken door handles
      2 | bent coat hangers
      4 | used bandages
      3 | deflated basketballs
      5 | frayed seat belts
      2 | old shoe laces
      4 | rusted car rims
      6 | cracked tiles
      3 | moldy bread
      5 | worn-out gloves
      2 | torn curtains
      4 | split rubber bands
      3 | crumpled receipts
      5 | burnt toast crumbs
      2 | broken staplers
      4 | dented helmets
      6 | discarded phone cases
      3 | chipped bricks
      5 | worn-out belts
      2 | cracked clay pots
      4 | rusty faucets
      3 | shattered window panes
      5 | old blankets
      2 | torn denim jeans
      4 | split wooden chopsticks
      6 | flattened cans
      3 | frayed shoelaces
      5 | burnt matchsticks
      2 | twisted paper clips
      4 | leaking glue sticks
      3 | dented metal buckets
      5 | crushed soda cans
      2 | old mobile phones
      4 | burnt-out candles
      3 | snapped pencils
      5 | dull razor blades
      2 | rusty saw blades
      4 | broken clock hands
      6 | stained napkins
      3 | torn maps
      5 | bent paper clips
      2 | melted crayons
      4 | broken remote controls
      3 | worn-out tires
      5 | cracked phone screens
      2 | smashed flower pots
      4 | rusty spanners
      3 | old batteries
```
    """

    pages = core.utils.page_message(long_message)

    for page in pages:
        print(page)
        print('----------')


def test_wide_string():
    wide_message = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam mollis ex ut enim porta, ac accumsan tortor vehicula. Integer ut libero malesuada justo mattis pretium. Fusce vitae tellus pellentesque felis viverra eleifend. Curabitur iaculis sem a turpis aliquam, vel dapibus tellus tincidunt. Donec ullamcorper vel urna in fringilla. Nunc quis pulvinar diam, et bibendum lorem. Suspendisse commodo placerat ipsum, ut aliquam metus sagittis a. Vivamus consequat vehicula elementum.

Nulla sed orci non neque feugiat posuere sed at mi. Sed rutrum odio eu ultricies hendrerit. Sed mollis, turpis quis lobortis tincidunt, enim magna fringilla turpis, ut congue nibh ex vitae nisi. Fusce nec lorem quis massa aliquet tempor quis non risus. Maecenas nec cursus nulla. Proin eleifend a purus a semper. Aliquam dictum augue mauris, non condimentum libero iaculis eget. Praesent tincidunt enim ante, id viverra tortor venenatis vel.

Curabitur ullamcorper, sem at suscipit lacinia, tellus metus porta mauris, vel dapibus mauris justo nec felis. Etiam porta est a neque egestas, a molestie mauris aliquam. Mauris vulputate non orci eu cursus. Aliquam pharetra mauris tellus, id auctor diam auctor sed. In sed libero laoreet, efficitur est sit amet, commodo tellus. Curabitur id risus eget neque rhoncus dignissim. Curabitur lacinia imperdiet purus, at tempor felis bibendum in. Sed pharetra, diam non faucibus blandit, orci nisl venenatis nulla, et dictum eros massa ut ante. Proin consequat, massa a posuere finibus, velit metus consectetur magna, gravida pulvinar est nunc vitae arcu. Nunc vitae velit vitae mauris commodo cursus ornare et purus.

```
Mauris sagittis, dui non vulputate laoreet, felis tellus pretium orci, et vulputate velit ex vitae mi. Etiam vel nunc enim. Ut nunc est, fringilla eget consequat ut, scelerisque quis odio. Donec condimentum ac mi at iaculis. Curabitur fringilla nulla arcu, sed eleifend sapien aliquam at. Sed vitae nunc posuere, lobortis velit sed, euismod mauris. Ut eu placerat nibh. Etiam ullamcorper mauris ac justo eleifend, sed tincidunt nisi euismod. Aliquam erat volutpat. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nam et justo gravida, iaculis tellus et, tempor sapien.
```

Proin bibendum cursus dapibus. Donec nec rhoncus ex. Aliquam semper nunc non tempor lacinia. Phasellus diam mi, maximus id consequat sit amet, sollicitudin quis nisi. Duis placerat risus in orci tempor, sit amet pharetra nisl viverra. Sed vitae porta quam. Nulla auctor pulvinar consectetur. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Nam enim ex, rutrum et leo sit amet, posuere volutpat felis. Donec eu ex id mauris sollicitudin sollicitudin id in elit. Quisque rhoncus nibh sit amet est suscipit lacinia at vitae quam. Proin in luctus odio, vel faucibus est. Sed eget vestibulum augue, vel accumsan augue.'''

    pages = core.utils.page_message(wide_message)

    for page in pages:
        print(page)
        print('----------')


def test_no_spaces():
    wide_message = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam mollis ex ut enim porta, ac accumsan tortor vehicula. Integer ut libero malesuada justo mattis pretium. Fusce vitae tellus pellentesque felis viverra eleifend. Curabitur iaculis sem a turpis aliquam, vel dapibus tellus tincidunt. Donec ullamcorper vel urna in fringilla. Nunc quis pulvinar diam, et bibendum lorem. Suspendisse commodo placerat ipsum, ut aliquam metus sagittis a. Vivamus consequat vehicula elementum.

Nulla sed orci non neque feugiat posuere sed at mi. Sed rutrum odio eu ultricies hendrerit. Sed mollis, turpis quis lobortis tincidunt, enim magna fringilla turpis, ut congue nibh ex vitae nisi. Fusce nec lorem quis massa aliquet tempor quis non risus. Maecenas nec cursus nulla. Proin eleifend a purus a semper. Aliquam dictum augue mauris, non condimentum libero iaculis eget. Praesent tincidunt enim ante, id viverra tortor venenatis vel.

Curabitur ullamcorper, sem at suscipit lacinia, tellus metus porta mauris, vel dapibus mauris justo nec felis. Etiam porta est a neque egestas, a molestie mauris aliquam. Mauris vulputate non orci eu cursus. Aliquam pharetra mauris tellus, id auctor diam auctor sed. In sed libero laoreet, efficitur est sit amet, commodo tellus. Curabitur id risus eget neque rhoncus dignissim. Curabitur lacinia imperdiet purus, at tempor felis bibendum in. Sed pharetra, diam non faucibus blandit, orci nisl venenatis nulla, et dictum eros massa ut ante. Proin consequat, massa a posuere finibus, velit metus consectetur magna, gravida pulvinar est nunc vitae arcu. Nunc vitae velit vitae mauris commodo cursus ornare et purus.

```
Maurissagittis,duinonvulputatelaoreet,felistelluspretiumorci,etvulputatevelitexvitaemi.Etiamvelnuncenim.Utnuncest,fringillaegetconsequatut,scelerisquequisodio.Doneccondimentumacmiatiaculis.Curabiturfringillanullaarcu,sedeleifendsapienaliquamat.Sedvitaenuncposuere,lobortisvelitsed,euismodmauris.Uteuplaceratnibh.Etiamullamcorpermaurisacjustoeleifend,sedtinciduntnisieuismod.Aliquameratvolutpat.Classaptenttacitisociosquadlitoratorquentperconubianostra,perinceptoshimenaeos.Nametjustogravida,iaculistelluset,temporsapien.
```

Proinbibendumcursusdapibus.Donecnecrhoncus ex. Aliquam semper nunc non tempor lacinia. Phasellus diam mi, maximus id consequat sit amet, sollicitudin quis nisi. Duis placerat risus in orci tempor, sit amet pharetra nisl viverra. Sed vitae porta quam. Nulla auctor pulvinar consectetur. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Nam enim ex, rutrum et leo sit amet, posuere volutpat felis. Donec eu ex id mauris sollicitudin sollicitudin id in elit. Quisque rhoncus nibh sit amet est suscipit lacinia at vitae quam. Proin in luctus odio, vel faucibus est. Sed eget vestibulum augue, vel accumsan augue.'''

    pages = core.utils.page_message(wide_message)

    for page in pages:
        print(page)
        print('----------')