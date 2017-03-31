# PyroPLANE
The ~~PyRope Plotter, Analyser and Exporter~~ *well now PyRope is not being updated and Octane is used so now my nice name doesn't work anymore* -.-

~~PyRope~~ Octane dug up lots of usable data from the replay. PySickle gets things rolling by turning its output network stream into usable data. PyroPLANE is where things start taking off, creating a GUI which can extract data from Rocket League replay files parsed by ~~PyRope~~ Octane and PySickle. 

It can both plot and export generated stats.

## Usage
Put this stuff into a "pyroplane" folder. Move _pyr.py to the same directory as the folder (up one). Run _pyr.py.


## Functions

### Data gathering:
  Can gather data based on time, or goals.
  
##### By Goals:
  * Can either be a list of numbers separated by spaces (E.g. 1 2 3) or a range of x:y, where x and y are the 'number of goals that have been scored'.
  
  * The equivalent of '1 2 3' would be 0:2.
 
  * Negative values are accepted too, where -2:0 will give you the last two goals of a game.
  
    
##### By Time:
  * A start time and end time needs to be entered. 0 for both will result in the entire game being parsed.
  
  * It is a countdown, and so a start time of 60 and end time of 0 will parse the last 60s of normal time.
  

  
  
### Stats generation:
  Have a look at the sample output text file for the kind of stats it can generate.
  
  Hit detection, shot detection, and basically all positional categorisation use hardcoded numbers. These are liable to break, and may not apply for new maps.
  
  
### Plotting:
  Heatmaps and a simple line tracking position are available as choices.
  



## Known Issues:
  * Velocities are not imported into database. Not sure if PySickle problem or PyroPLANE problem. I think it's somewhere here.
  
  * Positions are screwed up. Actually think it's a PySickle issue. Oh well. I've committed that so...
  
  * Does not include anything beyond the last goal in normal time if goals = 0. I don't consider this expected behaviour, and will fix it. An input of 0 should ensure all the in-play time is parsed.
  
  * Basically nothing works for the new maps. All my numbers are hardcoded, and I'll have to fix that. Even something like 'on ground' is hard for Underpass.
  
  * Some cars don't have their own hitboxes. (I think.) It defaults to the Octane, which is good enough imo. Ping and the resultant inaccuracy of the network stream is a much greater hindrance.
  
  * Advanced data grouping is yet to be implemented. The section exists and can be shown, but won't do anything.
  
  * No way of inputting 'Starting *x* minutes'. Todo: Implement accept start time = 0.

  * Ball position addition is not included, and currently just does weird things. I'm not sure I'll ever get around to fixing this. A line following a ball for such a bad looking diagram seems rather pointless.
  
## Currently Working On:
  * FIXING EVERYTHING THANKS PYROPE GUY
  * Fixing adding data functionality.
  * Advanced data grouping.
  * Creating a config file so the numbers can be changed manually.
  * Finding a way to find out which damned stadium the thing is in. I can pickle the metadata from PyRope, but that'll mean changing my backend game folder stuff.
  
## Ideas for the future:
  * A 'Key Opportunities' stat where the ball fits the following criteria:
    * Ball is in attacking third.
    * No defender between ball to goal
    * For at least 2s
  * A stadiums.txt so that new stadiums can be added without fixing code.
  * A cars.txt so that new cars can be added without fixing code.
  * Accept mutator options and change things accordingly.
    * This is probably not gonna happen. It's hard, and there's simply too much that can be affected.
