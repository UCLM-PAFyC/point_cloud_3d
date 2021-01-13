from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import QSettings, QTranslator, QVersionNumber, QCoreApplication, Qt, QObject, pyqtSignal
from PyQt5.QtGui import QColor

class RectangleMapTool(QgsMapToolEmitPoint):
  endSelection = QtCore.pyqtSignal()
  def __init__(self, canvas,layerNames,selectPoints=True):
      self.canvas = canvas
      self.layerNames = layerNames
      self.selectPoints=selectPoints
      self.wktGeomery = None
      print("init")
      QgsMapToolEmitPoint.__init__(self, self.canvas)
      self.rubberBand = QgsRubberBand(self.canvas, True)
      rFillColor = QColor(254, 178, 76, 63)
      self.rubberBand.setColor(rFillColor)
      self.rubberBand.setWidth(1)
      self.reset()

  def getWktGeomeetry(self):
      return self.wktGeomery

  def reset(self):
      print("reset")
      self.startPoint = self.endPoint = None
      self.isEmittingPoint = False
      self.rubberBand.reset(True)


  def canvasPressEvent(self, e):
      print("press")
      self.startPoint = self.toMapCoordinates(e.pos())
      self.endPoint = self.startPoint
      self.isEmittingPoint = True
      self.showRect(self.startPoint, self.endPoint)

  def canvasReleaseEvent(self, e):
      print("release")
      self.isEmittingPoint = False
      r = self.rectangle()
      self.wktGeomery = None
      if r is not None:
          if not self.selectPoints:
              self.wktGeomery = r.asWktPolygon()
              self.endSelection.emit()
              return
          layers = self.canvas.layers()
          for layer in layers:
              layerName = layer.name()
              if not layerName in self.layerNames:
                  continue
              if layer.type() == QgsMapLayer.VectorLayer:
                  #Luego filtro x name
                  bbRect = self.canvas.mapSettings().mapToLayerCoordinates(layer, r)
                  layer.selectByRect(bbRect, True)
          self.rubberBand.hide()

  def canvasMoveEvent(self, e):
      if not self.isEmittingPoint:
        return
      self.endPoint = self.toMapCoordinates(e.pos())
      self.showRect(self.startPoint, self.endPoint)

  def showRect(self, startPoint, endPoint):
      self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
      if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
        return

      point1 = QgsPointXY(startPoint.x(), startPoint.y())
      point2 = QgsPointXY(startPoint.x(), endPoint.y())
      point3 = QgsPointXY(endPoint.x(), endPoint.y())
      point4 = QgsPointXY(endPoint.x(), startPoint.y())

      self.rubberBand.addPoint(point1, False)
      self.rubberBand.addPoint(point2, False)
      self.rubberBand.addPoint(point3, False)
      self.rubberBand.addPoint(point4, True)    # true to update canvas
      self.rubberBand.show()

  def rectangle(self):
      if self.startPoint is None or self.endPoint is None:
        return None
      elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
        return None

      return QgsRectangle(self.startPoint, self.endPoint)

  def deactivate(self):
      super(RectangleMapTool, self).deactivate()
#      self.emit(SIGNAL("deactivated()"))