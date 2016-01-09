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

SM should automatically detect your library paths – type a path in the respective entry to change it. (You don't have to be ultra-precise in the path!) Double-click a game to select it, and click one of the fancy buttons to do an action. Simplicity itself!

A few buttons at the top let you check for updates or start Library Cleaner, for example. For Library Cleaner, just enter a path and hit enter. *Use Library Cleaner and find you can't play a game because you deleted an installer? Just go to tools > Verify cache to reïnstall them.*

### Update log

- **1.2 Major upgrade to Library Cleaner's capacities.**
- 1.1: Add Library Cleaner in basic form.
- 1.0: Release edition. Most features are still implemented.

##### License

Steam Mover is © Ami Ruse 2016. However, it operates on a lovely license. TL;DR: Copy, disassemble, <span title="Yes, that's a diaresis. I have weird standards, but goshdarnit I stick to 'em.">reässemble</span>, do whatever you want, as long as the license stays and that you don't try to sneakily sell it for monies. And enjoy! Don't forget to do that, too. :)