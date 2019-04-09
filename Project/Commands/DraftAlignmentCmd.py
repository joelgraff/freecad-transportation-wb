# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************
'''
Command to draft a new alignment
'''

import os
import FreeCAD as App
import FreeCADGui as Gui

from Project.Tasks.alignment.DraftAlignmentTask import DraftAlignmentTask

import Resources
import Corridor
from Project.Commands.AlignmentTracker import AlignmentTracker

import Draft
import DraftTools
from DraftGui import translate

class DraftAlignmentCmd(DraftTools.Line):
    '''
    Initiates and manages drawing activities for alignment creation
    '''
    def __init__(self):

        Line.Activated(self, name=translate('Transportation', 'Alignment'))

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(Resources.__file__) + '/icons/new_alignment.svg'

        return {'Pixmap'  : icon_path,
                'Accel'   : 'Ctrl+Shift+D',
                'MenuText': 'Draft Alignment',
                'ToolTip' : 'Draft a horizontal alignment',
                'CmdType' : 'ForEdit'}

    def Activated(self):
        '''
        Command activation method
        '''

        DraftTools.Line.Activated(self, name=translate('Transportation', 'Alignment'))

        if self.doc:
            self.alignment_tracker = AlignmentTracker()

        #panel = DraftAlignmentTask()
        #Gui.Control.showDialog(panel)
        #panel.setup()

    def action(self, arg):
        '''
        Event handling for alignment drawing
        '''

        #trap the escape key to quit
        if arg['Type'] == 'SoKeyboardEvent':
            if arg['Key'] == 'ESCAPE':
                self.finish()
                return

        #trap mouse movement
        if arg['Type'] == 'SoLocation2Event':

            self.point, ctrl_point, info = DraftTools.getPoint(self, arg, noTracker=False)

            self.alignment_tracker.update(self.node + [self.point], degree=self.degree)

            redraw3DView()

            return

        #trap button clicks
        if arg['Type'] == 'SoMouseButtonEvent':

            if (arg['State'] == 'DOWN') and (arg['Button'] == 'BUTTON1'):

                if arg['Position'] == self.pos:
                    self.finish(False, cont=True)
                    return

                #first point
                if not (self.node or self.support):

                    getSupport(arg)
                    self.point, ctrl_point, info = DraftTools.getPoint(self, arg, noTracker=True)

                if self.point:

                    self.ui.redraw()
                    self.node.append(self.point)
                    self.draw_update(self.point)

                    if not self.isWire and len(self.node) == 2:
                        self.finish(False, cont = True)

    def undo_last(self):
        '''
        Undo the last segment
        '''

        if len(self.node) > 1:

            self.node.pop()
            self.alignment_tracker.update(self.node, degree = self.degree)
            self.obj.Shape = self.updateShape(self.node)
            print(translate('Transporation', 'Undo last point'))

    def draw_update(self, point):
        '''
        Update the geometry as it has been defined
        '''

        if len(self.node) == 1:

            self.alignment_tracker.on()

            if self.planetrack:
                self.planetrack.set(self.node[0])

            print(translate('Transportation', 'Pick next  point:\n'))
            
            return

        self.obj.Shape = self.update_shape(self.node)
        print(translate('Transportation', 'Pick next point, finish (Shift+f), or close (o):') + '\n')

    def update_shape(self, points):
        '''
        Generates the shape to be rendered during the creation process
        '''

        return Draft.makeWire(points)

    def finish(self, closed=False, cont=False):
        '''
        Finish drawing the alignment object
        '''

        pass

Gui.addCommand('DraftAlignmentCmd', DraftAlignmentCmd())
