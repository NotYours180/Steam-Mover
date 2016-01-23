## Steam Mover *v1.2*
*Steam library manager for Python 3*

Manage games from your Steam libraries – backup games, move them from your HDD to your SSD, visualise which game takes up the most space, clean up pesky DirectX redistributables, et cetera. Featuring:

- **Visualisation**: see how much of what drive is taken up by your games
- **Toolkit**: launch a game, browse its files, verify its cache, look at its store page and more
- **Library finder**: automagically detects your Steam libraries, finds a library given vague paths, or searches drives for libraries
- **Library Cleaner**: Finds and purges sneaky DirectX installers that every game seems to have an identical but useless copy of. *Saves gigabytes of storage!*

![](http://i.imgur.com/7bY2TNs.png)

Includes `Operation` class, for large-scale copy operations with status-keeping.

### Usage

To run, simply download both .py files into a folder and run `Steammover.py`. (The program is designed for Python 3.4 or newer, but may work on older versions.)

SM should automatically detect your library paths – type a path in the respective entry to change it. (You don't have to be ultra-precise in the path!) Double-click a game to select it, and click one of the fancy buttons to do an action. Simplicity itself! A few buttons at the top let you check for updates or start Library Cleaner, for example. For Library Cleaner, just enter a path and hit enter.

### Update log

- **1.2: Increase library-loading efficiency**
- 1.1.1:  Major upgrade to Library Cleaner's capacities.
- 1.1: Add Library Cleaner in basic form.
- 1.0: Release edition. Most features are still implemented.

### FAQ

**I cleaned my library, but a game won't run. What do I do now?**

Most likely you haven't installed the redistributables the game needs. Just click the game in SM, and do Tools -> Verify cache to reïnstall the missing installers. Run the game, and when your drivers or whatnot are installed, you can clean the library again. (If this occurs *after* you've played it, [send me an email](mailto:yunruse@gmail.com), because that's no good!)

**When I select a game, the bars at the top go slightly red and there's a question mark after the size. What do?**

Steam's estimates for sizes are quick to get but sometimes a tad imprecise, so while SM automagically figures the sizes out itself, it uses the estimate with this indication (that it may not be entirely precise or not.) If this lingers, it's most likely you have a game with a very large amount of files – everything will function fine.

**I can't seem to find the game I'm looking for.**

Steam Mover only does independently-launchable Steam games – no custom-linked ones, and no DLC (it's attached to its game). Other than that, try ensuring you're in the right drive and that the name isn't changed (Some names are neater for better organisation).

**The *Copy* and *Move* buttons are grey, even though I've selected a game.**

Check the filesize at the bottomright – you don't have enough storage space on the destination drive! (Try freeïng up some with Library Cleaner, or moving some other games over.)

##### License

Steam Mover is © Ami Ruse 2016. However, it operates on a lovely license. TL;DR? Copy, disassemble, reässemble, do whatever you want. And enjoy! Don't forget to do that, too. :)