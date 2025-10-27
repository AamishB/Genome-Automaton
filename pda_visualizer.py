"""
PDA Visualizer
Renders a visual stack representation for PDA engines with improved 3D appearance.
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient


class PDAVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stack = []
        self.control_state = "push"
        self.automaton = None
        self.setMinimumHeight(300)
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        self.setFocusPolicy(Qt.StrongFocus)

    def set_automaton(self, automaton):
        self.automaton = automaton
        self.update_stack(getattr(automaton, 'stack', []), getattr(automaton, 'mode', 'push'))

    def update_stack(self, stack, control_state):
        self.stack = list(stack)
        self.control_state = control_state
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Background
        bg_gradient = QLinearGradient(0, 0, 0, self.height())
        bg_gradient.setColorAt(0, QColor(25, 30, 40))
        bg_gradient.setColorAt(1, QColor(20, 25, 35))
        p.fillRect(self.rect(), bg_gradient)

        # Control state badge
        badge_text = f"State: {self.control_state.upper()}"
        p.setFont(QFont('Segoe UI', 12, QFont.Bold))
        p.setPen(QColor(100, 200, 255))
        p.drawText(QRectF(15, 10, self.width()-30, 30), Qt.AlignLeft | Qt.AlignVCenter, badge_text)

        # Draw stack label
        stack_label = f"Stack ({len(self.stack)} items):"
        p.setFont(QFont('Segoe UI', 10, QFont.Bold))
        p.setPen(QColor(180, 200, 220))
        p.drawText(QRectF(15, 45, self.width()-30, 20), Qt.AlignLeft | Qt.AlignVCenter, stack_label)

        # Draw stack visualizer
        self._draw_stack(p)

    def wheelEvent(self, event):
        """Handle mouse wheel for zoom in/out."""
        if event.angleDelta().y() > 0:
            # Scroll up - zoom in
            self.zoom = min(self.max_zoom, self.zoom + 0.1)
        else:
            # Scroll down - zoom out
            self.zoom = max(self.min_zoom, self.zoom - 0.1)
        self.update()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for zoom."""
        if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.zoom = min(self.max_zoom, self.zoom + 0.1)
            self.update()
        elif event.key() == Qt.Key_Minus:
            self.zoom = max(self.min_zoom, self.zoom - 0.1)
            self.update()
        elif event.key() == Qt.Key_0:
            # Reset zoom
            self.zoom = 1.0
            self.update()
        else:
            super().keyPressEvent(event)

    def _draw_stack(self, p):
        """Draw a vertical stack representation with zoom support."""
        if not self.stack:
            # Empty stack message
            p.setFont(QFont('Segoe UI', 11))
            p.setPen(QColor(120, 140, 160))
            p.drawText(QRectF(20, 100, self.width()-40, 100), 
                      Qt.AlignCenter, "Stack is empty\n(waiting for input)")
            return

        # Stack parameters with zoom applied
        stack_width = int(150 * self.zoom)
        cell_height = int(40 * self.zoom)
        cell_margin = int(8 * self.zoom)
        arrow_offset = int(30 * self.zoom)
        arrow_length = int(15 * self.zoom)
        stack_x = (self.width() - stack_width) // 2
        stack_y = int(85 * self.zoom)
        
        # Draw base (floor) of stack
        floor_y = stack_y + (len(self.stack) + 1) * cell_height + cell_margin * 2
        p.setPen(QPen(QColor(100, 120, 140), max(2, int(3 * self.zoom))))
        p.setBrush(QBrush(QColor(40, 50, 65)))
        floor_rect = QRectF(stack_x - 10 * self.zoom, floor_y, stack_width + 20 * self.zoom, 8 * self.zoom)
        p.drawRoundedRect(floor_rect, int(4 * self.zoom), int(4 * self.zoom))
        
        # Draw each stack element from bottom to top
        for i, sym in enumerate(self.stack):
            # Position: bottom to top
            y = floor_y - (i + 1) * (cell_height + cell_margin)
            x = stack_x
            
            rect = QRectF(x, y, stack_width, cell_height)
            
            # Highlight top of stack (most recently added)
            is_top = (i == len(self.stack) - 1)
            if is_top:
                # Top element - bright cyan/blue with glow
                gradient = QLinearGradient(x, y, x, y + cell_height)
                gradient.setColorAt(0, QColor(0, 200, 255, 200))
                gradient.setColorAt(1, QColor(0, 150, 220, 200))
                p.setBrush(QBrush(gradient))
                p.setPen(QPen(QColor(100, 255, 255), max(2, int(3 * self.zoom))))
                
                # Draw arrow pointing to top
                arrow_x = x - arrow_offset
                arrow_y = y + cell_height // 2
                arrow_points = [
                    QPointF(arrow_x, arrow_y - 8 * self.zoom),
                    QPointF(arrow_x - arrow_length, arrow_y),
                    QPointF(arrow_x, arrow_y + 8 * self.zoom)
                ]
                p.setBrush(QBrush(QColor(100, 255, 255)))
                p.setPen(QPen(QColor(100, 255, 255), 1))
                p.drawPolygon(arrow_points)
                
                # Draw "TOP" label
                top_font = QFont('Segoe UI', max(6, int(8 * self.zoom)), QFont.Bold)
                p.setFont(top_font)
                p.setPen(QColor(100, 255, 255))
                p.drawText(QRectF(arrow_x - 35 * self.zoom, arrow_y - 10 * self.zoom, 30 * self.zoom, 20 * self.zoom), 
                          Qt.AlignCenter, "TOP")
            else:
                # Regular stack elements with gradient
                gradient = QLinearGradient(x, y, x, y + cell_height)
                gradient.setColorAt(0, QColor(70, 100, 140, 150))
                gradient.setColorAt(1, QColor(50, 80, 120, 150))
                p.setBrush(QBrush(gradient))
                p.setPen(QPen(QColor(100, 140, 180), max(1, int(2 * self.zoom))))
            
            # Draw cell
            p.drawRoundedRect(rect, int(8 * self.zoom), int(8 * self.zoom))
            
            # Draw symbol
            symbol_font = QFont('Consolas', max(10, int(14 * self.zoom)), QFont.Bold)
            p.setFont(symbol_font)
            p.setPen(QColor(255, 255, 255) if is_top else QColor(200, 220, 240))
            p.drawText(rect, Qt.AlignCenter, sym)
            
            # Draw position indicator
            if not is_top:
                pos_font = QFont('Segoe UI', max(6, int(8 * self.zoom)))
                p.setFont(pos_font)
                p.setPen(QColor(140, 160, 180))
                pos_text = f"[{len(self.stack) - i - 1}]"
                p.drawText(QRectF(x + stack_width + 10 * self.zoom, y, 30 * self.zoom, cell_height), 
                          Qt.AlignVCenter, pos_text)
        
        # Draw mode indicator
        mode_text = "PUSH MODE" if self.control_state == "push" else "POP MODE"
        mode_color = QColor(0, 200, 100) if self.control_state == "push" else QColor(255, 150, 0)
        
        mode_font = QFont('Segoe UI', max(8, int(10 * self.zoom)), QFont.Bold)
        p.setFont(mode_font)
        p.setPen(mode_color)
        indicator_rect = QRectF(self.width() - 200, self.height() - 35, 190, 30)
        p.drawText(indicator_rect, Qt.AlignRight | Qt.AlignVCenter, mode_text)
        
        # Draw mode indicator box
        p.setBrush(QBrush(mode_color.lighter(150)))
        p.setPen(QPen(mode_color, max(1, int(2 * self.zoom))))
        box_rect = QRectF(self.width() - 215, self.height() - 40, 30, 30)
        p.drawRoundedRect(box_rect, 5, 5)
        mode_symbol = "⬇" if self.control_state == "push" else "⬆"
        symbol_font = QFont('Segoe UI', max(10, int(14 * self.zoom)), QFont.Bold)
        p.setFont(symbol_font)
        p.setPen(mode_color)
        p.drawText(box_rect, Qt.AlignCenter, mode_symbol)
        
        # Draw zoom level indicator
        zoom_text = f"Zoom: {self.zoom:.1f}x"
        zoom_font = QFont('Segoe UI', 8)
        p.setFont(zoom_font)
        p.setPen(QColor(150, 170, 190))
        p.drawText(QRectF(15, self.height() - 30, 120, 25), Qt.AlignLeft | Qt.AlignVCenter, zoom_text)
