# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_triangleplugin.ui'
#
# Created: Mon Aug 25 09:14:47 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TrianglePlugin(object):
    def setupUi(self, TrianglePlugin):
        TrianglePlugin.setObjectName(_fromUtf8("TrianglePlugin"))
        TrianglePlugin.resize(446, 309)
        self.buttonBox = QtGui.QDialogButtonBox(TrianglePlugin)
        self.buttonBox.setGeometry(QtCore.QRect(60, 260, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.layerLabel = QtGui.QLabel(TrianglePlugin)
        self.layerLabel.setGeometry(QtCore.QRect(0, 20, 210, 31))
        self.layerLabel.setFrameShadow(QtGui.QFrame.Plain)
        self.layerLabel.setScaledContents(False)
        self.layerLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.layerLabel.setWordWrap(False)
        self.layerLabel.setObjectName(_fromUtf8("layerLabel"))
        self.cbLayers = QtGui.QComboBox(TrianglePlugin)
        self.cbLayers.setGeometry(QtCore.QRect(240, 20, 150, 31))
        self.cbLayers.setObjectName(_fromUtf8("cbLayers"))
        self.nameLayer = QtGui.QLabel(TrianglePlugin)
        self.nameLayer.setGeometry(QtCore.QRect(70, 140, 140, 31))
        self.nameLayer.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.nameLayer.setObjectName(_fromUtf8("nameLayer"))
        self.angleLabel = QtGui.QLabel(TrianglePlugin)
        self.angleLabel.setGeometry(QtCore.QRect(70, 60, 140, 31))
        self.angleLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.angleLabel.setObjectName(_fromUtf8("angleLabel"))
        self.areaLabel = QtGui.QLabel(TrianglePlugin)
        self.areaLabel.setGeometry(QtCore.QRect(70, 100, 140, 31))
        self.areaLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.areaLabel.setObjectName(_fromUtf8("areaLabel"))
        self.textAngle = QtGui.QLineEdit(TrianglePlugin)
        self.textAngle.setGeometry(QtCore.QRect(240, 60, 113, 31))
        self.textAngle.setObjectName(_fromUtf8("textAngle"))
        self.textArea = QtGui.QLineEdit(TrianglePlugin)
        self.textArea.setGeometry(QtCore.QRect(240, 100, 113, 31))
        self.textArea.setObjectName(_fromUtf8("textArea"))
        self.textName = QtGui.QLineEdit(TrianglePlugin)
        self.textName.setGeometry(QtCore.QRect(240, 140, 113, 31))
        self.textName.setObjectName(_fromUtf8("textName"))
        self.descriptorLayer = QtGui.QLabel(TrianglePlugin)
        self.descriptorLayer.setGeometry(QtCore.QRect(70, 180, 140, 31))
        self.descriptorLayer.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.descriptorLayer.setObjectName(_fromUtf8("descriptorLayer"))
        self.textThresholdDescriptor = QtGui.QLineEdit(TrianglePlugin)
        self.textThresholdDescriptor.setGeometry(QtCore.QRect(240, 220, 113, 31))
        self.textThresholdDescriptor.setObjectName(_fromUtf8("textThresholdDescriptor"))
        self.cbShapeDescriptor = QtGui.QComboBox(TrianglePlugin)
        self.cbShapeDescriptor.setGeometry(QtCore.QRect(240, 180, 150, 31))
        self.cbShapeDescriptor.setObjectName(_fromUtf8("cbShapeDescriptor"))
        self.thresholdDescriptorLayer = QtGui.QLabel(TrianglePlugin)
        self.thresholdDescriptorLayer.setGeometry(QtCore.QRect(70, 220, 140, 31))
        self.thresholdDescriptorLayer.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.thresholdDescriptorLayer.setObjectName(_fromUtf8("thresholdDescriptorLayer"))

        self.retranslateUi(TrianglePlugin)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TrianglePlugin.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TrianglePlugin.reject)
        QtCore.QMetaObject.connectSlotsByName(TrianglePlugin)

    def retranslateUi(self, TrianglePlugin):
        TrianglePlugin.setWindowTitle(QtGui.QApplication.translate("TrianglePlugin", "TrianglePlugin", None, QtGui.QApplication.UnicodeUTF8))
        self.layerLabel.setText(QtGui.QApplication.translate("TrianglePlugin", "Select layer to triangle", None, QtGui.QApplication.UnicodeUTF8))
        self.nameLayer.setText(QtGui.QApplication.translate("TrianglePlugin", "Name of new Mesh", None, QtGui.QApplication.UnicodeUTF8))
        self.angleLabel.setText(QtGui.QApplication.translate("TrianglePlugin", "Minimum Angle", None, QtGui.QApplication.UnicodeUTF8))
        self.areaLabel.setText(QtGui.QApplication.translate("TrianglePlugin", "Maximum Area", None, QtGui.QApplication.UnicodeUTF8))
        self.descriptorLayer.setText(QtGui.QApplication.translate("TrianglePlugin", "Shape Descriptor", None, QtGui.QApplication.UnicodeUTF8))
        self.thresholdDescriptorLayer.setText(QtGui.QApplication.translate("TrianglePlugin", "Descriptor Threshold", None, QtGui.QApplication.UnicodeUTF8))

