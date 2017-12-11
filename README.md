# Freecad Transportation Workbench
Python transportation engineeering workbench for FreeCAD

This workbench is being developed to provide functionality specific to transportation engineering (road and rail).

## Usage 


## Installation
Clone the project into the `~/.FreeCAD/Mod/Transportation` folder to use.

**Note:**  This project has a dependency in another FreeCAD workbench, [@microelly2's](https://github.com/microelly2) [Nurbs Workbench](https://github.com/microelly2/freecad-nurbs).  A symlink exists which points to it in the Transportation source.  

You can satisfy this dependency one of two ways:

1. Clone the Nurbs workbench into the `~/.FreeCAD/Mod/nurbs` folder
2. Delete the symlink and copy the `freecad-nurbs/sketcher/feedbacksketch.py` file to the `~/.FreeCAD/Mod/Transportation` folder.

## Feedback 
Discuss this Workbench on the FreeCAD forum thread dedicated to this topic: [Civil engineering feature implementation (Transportation Engineering)](https://forum.freecadweb.org/viewtopic.php?f=8&t=22277). FYI, this thread was born of a parent thread: [Civil Engineering Design functions](https://forum.freecadweb.org/viewtopic.php?f=8&t=6973)

## Developer 
Joel Graff (@graffy76) with inspiration and help from the FreeCAD community