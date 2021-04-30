import itertools

from PyQt5.QtCore import QSize, Qt, QMimeData
from PyQt5.QtGui import QDrag, QFont
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QApplication, QWidget, QSizePolicy, QLabel, QStackedLayout

import customlogger as logger
from gui.events.calculator_view_events import AddEmptyUnitEvent
from gui.viewmodels.mime_headers import CALCULATOR_GRANDUNIT
from gui.viewmodels.simulator.calculator import CalculatorView, DroppableCalculatorWidget
from gui.viewmodels.unit import UnitWidget, UnitCard
from gui.viewmodels.utils import UniversalUniqueIdentifiable
from settings import IMAGE_PATH32


class GrandCalculatorUnitWidget(UnitWidget, UniversalUniqueIdentifiable):
    def __init__(self, unit_view, parent=None, size=32, *args, **kwargs):
        super().__init__(unit_view, parent, size, *args, **kwargs)
        del self.unitName

        self.card_widget = QWidget(self)

        self.unit_view = unit_view
        self.cards_internal = [None] * 15
        self.cards = list()
        for idx in range(15):
            if idx % 5 == 0:
                color = 'red'
            else:
                color = 'black'
            card = UnitCard(unit_widget=self, card_idx=idx, size=size, color=color)
            self.cards.append(card)
        self.size = size
        self.path = IMAGE_PATH32

        self.verticalLayout = QVBoxLayout()
        self.cardLayouts = [QHBoxLayout(), QHBoxLayout(), QHBoxLayout()]

        for idx, card in enumerate(self.cards):
            card.setMinimumSize(QSize(self.size + 2, self.size + 2))
            self.cardLayouts[idx // 5].addWidget(card)
        for card_layout in self.cardLayouts:
            self.verticalLayout.addLayout(card_layout)

        self.card_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.card_widget.setLayout(self.verticalLayout)

        # Setup overlay
        self.label = QLabel(self.card_widget)
        self.label.setText("Running...")
        font = QFont()
        font.setPixelSize(20)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: rgba(255, 255, 255, 100);")
        self.label.setAutoFillBackground(True)

        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.card_widget)
        self.stacked_layout.addWidget(self.label)
        self.stacked_layout.setContentsMargins(0, 0, 0, 0)
        self.stacked_layout.setStackingMode(QStackedLayout.StackAll)

        self.setLayout(self.stacked_layout)
        self.toggle_running_simulation(False)
        self.running_simulation = False

    def toggle_running_simulation(self, running=False):
        self.label.setVisible(running)
        self.running_simulation = running

    def permute_units(self):
        self.unit_view.permute_units()

    def handle_lost_mime(self, mime_text):
        pass


class GrandCalculatorTableWidget(DroppableCalculatorWidget):
    def __init__(self, calculator_view, *args, **kwargs):
        super(GrandCalculatorTableWidget, self).__init__(calculator_view, *args, **kwargs)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        if self.selectedItems():
            self.selected = self.selectedIndexes()
        if not self.selected:
            return
        drag = QDrag(self)
        mimedata = QMimeData()
        mimedata.setText(CALCULATOR_GRANDUNIT + str(self.cellWidget(self.selected[0].row(), 0).card_ids))
        drag.setMimeData(mimedata)
        drag.exec_(Qt.CopyAction | Qt.MoveAction)


class GrandCalculatorView(CalculatorView):
    def __init__(self, main, main_view):
        super().__init__(main, main_view)
        self.widget.verticalHeader().setDefaultSectionSize(120)

    def initialize_widget(self, main):
        self.widget = GrandCalculatorTableWidget(self, main)

    def set_unit(self, cards, unit, row=None):
        if row is None:
            row = self.widget.rowCount() - 1
        for idx, card in enumerate(cards):
            if card is None:
                continue
            self.widget.cellWidget(row, 0).set_card(idx=unit * 5 + idx, card=card)
        logger.info("Unit insert: {} - {} row {}".format(self.widget.cellWidget(row, 0).get_uuid(), cards, row))

    def insert_unit(self):
        self.widget.insertRow(self.widget.rowCount())
        simulator_unit_widget = GrandCalculatorUnitWidget(self, None, size=32)
        self.widget.setCellWidget(self.widget.rowCount() - 1, 0, simulator_unit_widget)
        logger.debug("Inserted empty unit at {}".format(self.widget.rowCount()))
        self.widget.setColumnWidth(0, 40 * 6)

    def add_unit(self, cards):
        if len(cards) == 6:
            cards = cards[:5]
        if len(cards) == 15:
            # Duplicate unit
            for r in range(self.widget.rowCount()):
                if self.widget.cellWidget(r, 0).card_ids == [None] * 15:
                    logger.debug("Empty calculator unit at row {}".format(r))
                    self.set_unit(row=r, unit=0, cards=cards)
                    return
            self.model.add_empty_unit(AddEmptyUnitEvent(self.model))
            self.set_unit(row=self.widget.rowCount() - 1, unit=0, cards=cards)
            return
        for r in range(self.widget.rowCount()):
            card_ids = self.widget.cellWidget(r, 0).card_ids
            for u_id in range(3):
                if card_ids[u_id * 5: (u_id + 1) * 5] == [None] * 5:
                    logger.debug("Empty calculator unit at row {}.{}".format(r, u_id))
                    self.set_unit(row=r, unit=u_id, cards=cards)
                    return
        self.model.add_empty_unit(AddEmptyUnitEvent(self.model))
        self.set_unit(row=self.widget.rowCount() - 1, unit=0, cards=cards)

    def permute_units(self):
        n = self.widget.rowCount()
        all_units = list()
        for r in range(n):
            card_ids = self.widget.cellWidget(r, 0).card_ids
            if None in card_ids:
                continue
            units = [card_ids[0:5], card_ids[5:10], card_ids[10:15]]
            all_units.append(units)
        for grand_unit in all_units:
            for permutation in itertools.permutations(grand_unit, 3):
                permutation = list(permutation)
                if permutation in all_units:
                    continue
                self.model.add_empty_unit(AddEmptyUnitEvent(self.model))
                for unit_idx, unit in enumerate(permutation):
                    self.set_unit(row=self.widget.rowCount() - 1, unit=unit_idx, cards=unit)
