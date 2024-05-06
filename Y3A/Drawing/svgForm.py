import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QWidget, QVBoxLayout
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtCore import Qt, QDomDocument
from PyQt5.QtGui import QWheelEvent

class ZoomableSvgView(QGraphicsView):
    def __init__(self, parent=None):
        super(ZoomableSvgView, self).__init__(parent)

        # create a QGraphicsScene
        scene = QGraphicsScene(self)

        # create a QGraphicsSvgItem and add it to the scene
        self.svg_item = QGraphicsSvgItem("Drawing.svg")
        scene.addItem(self.svg_item)

        # Set the scene for the view
        self.setScene(scene)

        # Enable support for dragging and scaling
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set up the layout
        layout = QVBoxLayout(self)

        # Store the last mouse position for dragging
        self.last_mouse_pos = None

    def wheelEvent(self, event: QWheelEvent):
        # Zoom in or out based on the direction of the wheel
        factor = 1.2  # You can adjust the zoom factor
        if event.angleDelta().y() > 0:
            self.scale(factor, factor)
        else:
            self.scale(1.0 / factor, 1.0 / factor)

    def mousePressEvent(self, event):
        # Store the current mouse position for dragging
        self.last_mouse_pos = self.mapToScene(event.pos())

        # Identify the clicked item
        item = self.itemAt(event.pos())
        if item and isinstance(item, QGraphicsSvgItem):
            print(f"{event.pos()} = {item}")
            # Display information about the clicked node
#            title = self.get_title_from_svg(item)
#            print(f"Clicked Node Title: {title}")

    def get_title_from_svg(self, svg_item):
        # Extract the title from the SVG content
        raw_svg_data = svg_item.renderer().data()
        doc = QDomDocument()
        doc.setContent(raw_svg_data)
        title_elements = doc.elementsByTagName("title")
        if title_elements.size() > 0:
            return title_elements.item(0).toElement().text()
        else:
            return "No Title"
        
    def mouseMoveEvent(self, event):
        # Check if the left mouse button is pressed and there's a stored position
        if event.buttons() == Qt.LeftButton and self.last_mouse_pos:
            # Calculate the distance moved
            delta = self.mapToScene(event.pos()) - self.last_mouse_pos
            # Move the QGraphicsSvgItem
            self.svg_item.setPos(self.svg_item.pos() + delta)
            # Update the stored position for the next move
            self.last_mouse_pos = self.mapToScene(event.pos())

    def mouseReleaseEvent(self, event):
        # Reset the stored position when the mouse is released
        self.last_mouse_pos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Use ZoomableSvgView for a QGraphicsView with zoom control using the mouse wheel
    # and mouse dragging, and display information about the clicked node
    widget = ZoomableSvgView()
    
    widget.show()
    sys.exit(app.exec_())
