import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy as np
import time
import math
import Algorithms
import MathTools


# import sympy
# from sympy import Line3D
#
# Task1
#

class Task1(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Task1"  # TODO make this more human readable by adding spaces
        self.parent.categories = ["Examples"]
        self.parent.dependencies = []
        self.parent.contributors = ["Ioannis Souriadakis"]  # replace with "Firstname Lastname (Organization)"
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""  # replace with organization, grant and thanks.


#
# Task1Widget
#

class Task1Widget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # Instantiate and connect widgets ...

        #
        # Parameters Area
        #
        parametersCollapsibleButton = ctk.ctkCollapsibleButton()
        parametersCollapsibleButton.text = "Parameters"
        self.layout.addWidget(parametersCollapsibleButton)

        # Layout within the dummy collapsible button
        parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

        #
        # input volume selector
        #
        self.hippoSelector = slicer.qMRMLNodeComboBox()
        self.hippoSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
        self.hippoSelector.selectNodeUponCreation = True
        self.hippoSelector.addEnabled = False
        self.hippoSelector.removeEnabled = False
        self.hippoSelector.noneEnabled = False
        self.hippoSelector.showHidden = False
        self.hippoSelector.showChildNodeTypes = False
        self.hippoSelector.setMRMLScene(slicer.mrmlScene)
        self.hippoSelector.setToolTip("Pick the target object.")
        parametersFormLayout.addRow("Input Hippocampus Label Volume: ", self.hippoSelector)

        self.ventSelector = slicer.qMRMLNodeComboBox()
        self.ventSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
        self.ventSelector.selectNodeUponCreation = True
        self.ventSelector.addEnabled = False
        self.ventSelector.removeEnabled = False
        self.ventSelector.noneEnabled = False
        self.ventSelector.showHidden = False
        self.ventSelector.showChildNodeTypes = False
        self.ventSelector.setMRMLScene(slicer.mrmlScene)
        self.ventSelector.setToolTip("Pick the ventricles object.")
        parametersFormLayout.addRow("Input Ventricles Label Volume: ", self.ventSelector)

        self.vesselSelector = slicer.qMRMLNodeComboBox()
        self.vesselSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
        self.vesselSelector.selectNodeUponCreation = True
        self.vesselSelector.addEnabled = False
        self.vesselSelector.removeEnabled = False
        self.vesselSelector.noneEnabled = False
        self.vesselSelector.showHidden = False
        self.vesselSelector.showChildNodeTypes = False
        self.vesselSelector.setMRMLScene(slicer.mrmlScene)
        self.vesselSelector.setToolTip("Pick the blood vessel object.")
        parametersFormLayout.addRow("Input Blood Vessels Label Volume: ", self.vesselSelector)

        self.cortexSelector = slicer.qMRMLNodeComboBox()
        self.cortexSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
        self.cortexSelector.selectNodeUponCreation = True
        self.cortexSelector.addEnabled = False
        self.cortexSelector.removeEnabled = False
        self.cortexSelector.noneEnabled = False
        self.cortexSelector.showHidden = False
        self.cortexSelector.showChildNodeTypes = False
        self.cortexSelector.setMRMLScene(slicer.mrmlScene)
        self.cortexSelector.setToolTip("Pick the cortex object.")
        parametersFormLayout.addRow("Input cortex Label Volume: ", self.cortexSelector)

        # creating the ui dropdowns will let you generalize to other nodes
        self.inputTargetFiducialSelector = slicer.qMRMLNodeComboBox()
        self.inputTargetFiducialSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.inputTargetFiducialSelector.selectNodeUponCreation = True
        self.inputTargetFiducialSelector.addEnabled = False
        self.inputTargetFiducialSelector.removeEnabled = False
        self.inputTargetFiducialSelector.noneEnabled = False
        self.inputTargetFiducialSelector.showHidden = False
        self.inputTargetFiducialSelector.showChildNodeTypes = False
        self.inputTargetFiducialSelector.setMRMLScene(slicer.mrmlScene)
        self.inputTargetFiducialSelector.setToolTip("Pick the input fiducials to the algorithm.")
        parametersFormLayout.addRow("Input Target Fiducials: ", self.inputTargetFiducialSelector)

        self.inputEntryFiducialSelector = slicer.qMRMLNodeComboBox()
        self.inputEntryFiducialSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.inputEntryFiducialSelector.selectNodeUponCreation = True
        self.inputEntryFiducialSelector.addEnabled = False
        self.inputEntryFiducialSelector.removeEnabled = False
        self.inputEntryFiducialSelector.noneEnabled = False
        self.inputEntryFiducialSelector.showHidden = False
        self.inputEntryFiducialSelector.showChildNodeTypes = False
        self.inputEntryFiducialSelector.setMRMLScene(slicer.mrmlScene)
        self.inputEntryFiducialSelector.setToolTip("Pick the input fiducials to the algorithm.")
        parametersFormLayout.addRow("Input Entry Fiducials: ", self.inputEntryFiducialSelector)

        self.validAngleSlider = ctk.ctkSliderWidget()
        self.validAngleSlider.singleStep = 1
        self.validAngleSlider.minimum = 0
        self.validAngleSlider.maximum = 90
        self.validAngleSlider.value = 55
        self.validAngleSlider.setToolTip("Set angle value for valid incision")
        parametersFormLayout.addRow("Valid Incision Angle", self.validAngleSlider)

        self.precisionSlider = ctk.ctkSliderWidget()
        self.precisionSlider.singleStep = 0.001
        self.precisionSlider.minimum = 0.001
        self.precisionSlider.maximum = 0.1
        self.precisionSlider.value = 0.01
        self.precisionSlider.setToolTip("Set precision value for maximising distance to the critical structure")
        parametersFormLayout.addRow("Precision", self.precisionSlider)

        self.maximumIncisionLengthSlider = ctk.ctkSliderWidget()
        self.maximumIncisionLengthSlider.singleStep = 1
        self.maximumIncisionLengthSlider.minimum = 0.00
        self.maximumIncisionLengthSlider.maximum = 9999999999999
        self.maximumIncisionLengthSlider.value = 9999999999999
        self.maximumIncisionLengthSlider.setToolTip("Set maximum incision value")
        parametersFormLayout.addRow("Maximum Incision Length", self.maximumIncisionLengthSlider)
        #

        #
        # Apply Button
        #
        self.applyButton = qt.QPushButton("Apply")
        self.applyButton.toolTip = "Run the algorithm."
        self.applyButton.enabled = False
        parametersFormLayout.addRow(self.applyButton)

        # connections
        self.applyButton.connect('clicked(bool)', self.onApplyButton)
        self.inputEntryFiducialSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
        self.inputTargetFiducialSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

        # Add vertical spacer
        self.layout.addStretch(1)

        # Refresh Apply button state
        self.onSelect()

    def cleanup(self):
        pass

    def onSelect(self):
        self.applyButton.enabled = self.hippoSelector.currentNode() and self.ventSelector.currentNode() and self.vesselSelector.currentNode() and self.cortexSelector.currentNode() and self.inputTargetFiducialSelector.currentNode() and self.inputEntryFiducialSelector.currentNode()

    def onApplyButton(self):
        logic = Task1Logic()
        validAngleOfIntersection = self.validAngleSlider.value
        precisionValue = self.precisionSlider.value
        maximumIncisionValue = self.maximumIncisionLengthSlider.value
        logic.run(self.hippoSelector.currentNode(), self.ventSelector.currentNode(), self.vesselSelector.currentNode(),
                  self.cortexSelector.currentNode(),
                  self.inputTargetFiducialSelector.currentNode(),
                  self.inputEntryFiducialSelector.currentNode(),
                  validAngleOfIntersection, precisionValue, maximumIncisionValue)


#
# Task1Logic
#

class Task1Logic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def isValidInputOutputData(self, hippo, ventricles, vessels, cortex, targetsNode, entriesNode, validAngleOfIntersection, precisionValue, maximumIncisionValue):
        """Validates if the output is not the same as input
        """
        if not hippo:
            logging.debug('No hippo data selected')
            return False
        if not ventricles:
            logging.debug('No ventricle data selected')
            return False
        if not vessels:
            logging.debug('No blood vessel data selected')
            return False
        if not cortex:
            logging.debug('No cortex data selected')
            return False
        if not targetsNode:
            logging.debug('No etarget point data selected')
            return False
        if not entriesNode:
            logging.debug('No entry point data selected')
            return False
        if not validAngleOfIntersection:
            logging.debug('No valid angle selected')
            return False
        if not precisionValue:
            logging.debug('No precision value selected')
            return False
        if not maximumIncisionValue:
            logging.debug('No incision length value selected')
            return False
        return True

    def run(self, hippo, ventricles, vessels, cortex, targetsNode, entriesNode, validAngleOfIntersection, precisionValue, maximumIncisionValue):
        """
        Run the actual algorithm
        """
        if not self.isValidInputOutputData(hippo, ventricles, vessels, cortex, targetsNode, entriesNode, validAngleOfIntersection, precisionValue, maximumIncisionValue):
            slicer.util.errorDisplay('Invalid input.')
            return False

        logging.info('Processing started')

        entriesAndTargets = {}
        combinedEntriesAndTargets = {}
        newTargets = []
        bestTrajectories = {}

        startTime = time.time()
        newTargets = Algorithms.getValidTargets(targetsNode, hippo)
        endTime = time.time()
        print('Hippo targets: ', endTime - startTime, 'seconds')

        entriesAndTargets = Algorithms.entriesAndTargetsInDict(entriesNode, Algorithms.convertMarkupNodeToPoints(targetsNode))

        startTime = time.time()
        Algorithms.getIncisionsWithValidArea(entriesAndTargets, ventricles)
        endTime = time.time()
        print('Incisions - Ventricles: ', endTime - startTime, 'seconds')

        startTime = time.time()
        Algorithms.getIncisionsWithValidArea(entriesAndTargets, vessels)
        endTime = time.time()
        print('Incisions - Blood Vessels: ', endTime - startTime, 'seconds')

        startTime = time.time()
        Algorithms.getIncisionsWithValidAngle(entriesAndTargets, cortex, validAngleOfIntersection)
        endTime = time.time()
        print('Incisions - Valid Angle: ', endTime - startTime, 'seconds')

        startTime = time.time()
        newTargets = Algorithms.getValidTargets(targetsNode, hippo)
        combinedEntriesAndTargets = Algorithms.entriesAndTargetsInDict(entriesNode, newTargets)
        combinedEntriesAndTargets = Algorithms.combineConstraints(combinedEntriesAndTargets, ventricles, vessels, cortex, validAngleOfIntersection)
        endTime = time.time()
        print('Incisions - Combined: ', endTime - startTime, 'seconds')

        # good to have some way of seeing our results
        # allPaths = self.printEntryAndTargetsInDict(combinedEntriesAndTargets)
        # pathNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', 'GoodPaths')
        # pathNode.SetAndObserveMesh(allPaths)

        bestTrajectiries = Algorithms.printBestTrajectoryForEachEntry(precisionValue, maximumIncisionValue, combinedEntriesAndTargets, vessels, ventricles)
        # you can add something here to output the good entry target pairs
        logging.info('Processing completed')
        return True

    



    # Intersection Line first Try
    # def pointClashVentricles(self, entry, target, ventricles):
    #   xEntry, yEntry, zEntry = entry[0], entry[1], entry[2]
    #   xTarget, yTarget, zTarget = target[0], target[1], target[2]
    #   subSampling = 4
    #   step = 0.01
    #   for t in np.arange(0,1,step):
    #     x = xEntry + t*(xTarget - xEntry)
    #     y = yEntry + t*(yTarget - yEntry)
    #     z = zEntry + t*(zTarget - zEntry)
    #     #imageVoxelID = x*y*z
    #     imageVoxelID = ventricles.GetImageData().FindPoint(x/subSampling,y/subSampling,z/subSampling)
    #     xIndex = int(imageVoxelID%x)
    #     yIndex = int(imageVoxelID%(x*y)/x)
    #     zIndex = int((imageVoxelID/(x*y)))

    #     if ventricles.GetImageData().GetScalarComponentAsDouble(xIndex,yIndex,zIndex,0) == 1.0:
    #       return True
    #   return False

    # Intersection Line first Try
    # def pointsClassVessels(self,entry,target,vessels):
    #   xEntry, yEntry, zEntry = entry[0], entry[1], entry[2]
    #   xTarget, yTarget, zTarget = target[0], target[1], target[2]
    #   subSampling = 4
    #   step = 0.0001
    #   for t in np.arange(0,1,step):
    #     x = xEntry + t*(xTarget - xEntry)
    #     y = yEntry + t*(yTarget - yEntry)
    #     z = zEntry + t*(zTarget - zEntry)
    #     #imageVoxelID = x*y*z
    #     imageVoxelID = vessels.GetImageData().FindPoint(x/subSampling,y/subSampling,z/subSampling)
    #     xIndex = int(imageVoxelID%x)
    #     yIndex = int(imageVoxelID%(x*y)/x)
    #     zIndex = int((imageVoxelID/(x*y)))

    #     if vessels.GetImageData().GetScalarComponentAsDouble(xIndex,yIndex,zIndex,0) == 1.0:
    #       return True
    #   return False


class Task1Test(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_LoadData(
            "C:\Users\PWW\Documents\Assigment1")
        # # self.testGetHippoTargets()
        self.testAvoidVentriclesValidPath()
        self.testAvoidVentriclesInvalidPath()
        self.testAvoidBloodVesselsValidPath()
        self.testAvoidBloodVesselsInvalidPath()
        self.testAngleValidPath()
        self.testAngleInvalidPath()
        self.setUp()  # to reclear data

    def test_LoadData(self, path):
        self.delayDisplay("Starting load data test")
        isLoaded = slicer.util.loadLabelVolume(path + '/r_hippo.nii.gz')
        self.assertTrue(isLoaded)

        isLoaded = slicer.util.loadLabelVolume(path + '/ventricles.nii.gz')
        self.assertTrue(isLoaded)

        isLoaded = slicer.util.loadLabelVolume(path + '/vessels.nii.gz')
        self.assertTrue(isLoaded)

        isLoaded = slicer.util.loadLabelVolume(path + '/cortex.nii.gz')
        self.assertTrue(isLoaded)

        isLoaded = slicer.util.loadMarkupsFiducialList(path + '/targets.fcsv')
        self.assertTrue(isLoaded)

        isLoaded = slicer.util.loadMarkupsFiducialList(path + '/entries.fcsv')
        self.assertTrue(isLoaded)

        self.delayDisplay('Test passed! All data loaded correctly')

    


    def testGetHippoTargets(self):
        hippo = self.getNode("r_hippo")
        targets = self.getNode("targets")
        newTargets = Algorithms.getValidTargets(targets, hippo)
        self.assertTrue(targets.GetNumberOfMarkups() > len(newTargets))
        self.delayDisplay('testGetFilteredHippocampusTargets passed!')

    def testAvoidVentriclesValidPath(self):
        entriesID = [451,452,453,454,455,456,457,458]
        targetsID = [161,162,163,164,165,166,167,168]
        entriesAndTargets = Algorithms.addEntriesAndTargetsInDictFromID(entriesID,targetsID)
        ventricles = slicer.util.getNode("ventricles")
        result = Algorithms.getIncisionsWithValidArea(entriesAndTargets, ventricles)
        self.assertTrue(len(result) > 0)
        self.delayDisplay('testAvoidBloodVesselsValidPath passed!')

    def testAvoidVentriclesInvalidPath(self):
        entriesID = [4,5,7,11,12,16,17,33]
        targetsID = [3,4,5,6,7,10,11,12]
        entriesAndTargets = Algorithms.addEntriesAndTargetsInDictFromID(entriesID,targetsID)
        ventricles = slicer.util.getNode("ventricles")
        result = Algorithms.getIncisionsWithValidArea(entriesAndTargets, ventricles)
        self.assertTrue(len(result) > 0)
        self.delayDisplay('testAvoidBloodVesselsValidPath passed!')

    def testAvoidBloodVesselsValidPath(self):
        entriesID = [235,243,244,255,256,262,263,270]
        targetsID = [1,2,3,4,8,9,10,11]
        entriesAndTargets = Algorithms.addEntriesAndTargetsInDictFromID(entriesID,targetsID)
        vessels = slicer.util.getNode("vessels")
        result = Algorithms.getIncisionsWithValidArea(entriesAndTargets, vessels)
        self.assertTrue(len(result) > 0)
        self.delayDisplay('testAvoidBloodVesselsValidPath passed!')

    def testAvoidBloodVesselsInvalidPath(self):
        entriesID = [35,56,70,73,85,94,95,129]
        targetsID = [25,26,46,47,52,54,55,69]
        entriesAndTargets = Algorithms.addEntriesAndTargetsInDictFromID(entriesID,targetsID)
        vessels = slicer.util.getNode("vessels")
        result = Algorithms.getIncisionsWithValidArea(entriesAndTargets, vessels)
        self.assertTrue(len(result) > 0)
        self.delayDisplay('testAvoidBloodVesselsInvalidPath passed!')

    def testAngleValidPath(self):
        entriesAndTargets = {(212.09, 147.385, 76.878): [[162.0, 133.0, 90.0]]}
        cortex = slicer.util.getNode("cortex")
        result = Algorithms.getIncisionsWithValidAngle(entriesAndTargets, cortex,55)
        self.assertTrue(len(result) > 0)
        self.delayDisplay('testAngleValidPath passed!')

    def testAngleInvalidPath(self):
        entriesAndTargets = {(208.654, 134.777, 61.762): [[162.0, 128.0, 106.0]]}
        cortex = slicer.util.getNode("cortex")
        result = Algorithms.getIncisionsWithValidAngle(entriesAndTargets, cortex,55)
        self.assertTrue(len(result) == 0)
        self.delayDisplay('testAngleInvalidPath passed!')
