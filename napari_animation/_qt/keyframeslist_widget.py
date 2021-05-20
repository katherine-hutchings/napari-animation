from napari._qt.containers import QtListModel, QtListView
from qtpy.QtCore import QModelIndex, QSize, Qt
from qtpy.QtGui import QImage


class KeyFrameModel(QtListModel):
    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.DecorationRole:  # thumbnail
            key_frame = index.data(Qt.UserRole)
            return QImage(
                key_frame.thumbnail,
                key_frame.thumbnail.shape[1],
                key_frame.thumbnail.shape[0],
                QImage.Format_RGBA8888,
            )
        if role == Qt.SizeHintRole:  # determines size of item
            return QSize(160, 34)
        return super().data(index, role)

    def setData(self, index, value, role) -> bool:
        if role == Qt.EditRole:
            # user has double-clicked on the keyframe name
            key_frame = index.data(Qt.UserRole)
            key_frame.name = value
        return super().setData(index, value, role=role)


class KeyFramesListWidget(QtListView):
    def __init__(self, root, parent=None):
        super().__init__(root, parent=parent)
        self.setModel(KeyFrameModel(root))
        self.setStyleSheet("KeyFramesListWidget::item { padding: 0px; }")


# class KeyFramesListWidget(QListWidget):
#     """List of key frames for an animation

#     Parameters
#     ----------
#     animation : napari_animation.Animation
#         napari-animation animation to be synced with the GUI.

#     Attributes
#     ----------
#     animation : napari_animation.Animation
#         napari-animation animation in sync with the GUI.
#     """

#     def __init__(self, animation, parent=None):
#         super().__init__(parent=parent)

#         self.animation = animation
#         self._frame_count = 0
#         self._item_id_to_key_frame = {}
#         self._key_frame_id_to_item = {}

#         self._connect_callbacks()
#         self.setDragDropMode(super().InternalMove)

#     def _connect_callbacks(self):
#         self._connect_key_frame_callbacks()
#         self.itemSelectionChanged.connect(self._selection_callback)

#     def _connect_key_frame_callbacks(self):
#         """Connect events on the key frame list to their callbacks"""
#         self.animation.key_frames.events.inserted.connect(self._add)
#         self.animation.key_frames.events.removed.connect(self._remove)
#         self.animation.key_frames.events.reordered.connect(
#             self._reorder_frontend
#         )
#         self.animation.key_frames.selection.events._current.connect(
#             self._update_selected_frame
#         )

#     def _selection_callback(self):
#         self._update_frame_number()
#         if self.animation.current_key_frame:
#             self.parentWidget()._update_frame_widget_from_animation()

#     def _add(self, event):
#         """Generate QListWidgetItem for current keyframe, store its unique id and add it to self"""
#         key_frame, idx = event.value, event.index
#         item = self._generate_list_item(key_frame)
#         self.insertItemBlockingSignals(idx, item)
#         self.insertItem(idx, item)
#         self._add_mappings(key_frame, item)
#         self._frame_count += 1

#     def _add_mappings(self, key_frame, item):
#         self._item_id_to_key_frame[id(item)] = key_frame
#         self._key_frame_id_to_item[id(key_frame)] = item

#     def _remove(self, event):
#         """Remove QListWidgetItem at event.index"""
#         self.takeItemBlockingSignals(event.index)
#         if len(self.animation.key_frames) > 0:
#             self._update_frame_number()

#     def _reorder_frontend(self, event=None):
#         """Reorder items in frontend based on current state in backend"""
#         for idx, key_frame in enumerate(self.animation.key_frames):
#             item = self._key_frame_id_to_item[id(key_frame)]
#             self.takeItem(idx)
#             self.insertItem(item, idx)

#     def _reorder_backend(self):
#         """reorder key frames in backend based on current state in frontend"""
#         for idx, key_frame in enumerate(self.frontend_key_frames):
#             self.animation.key_frames[idx] = key_frame

#     def _update_frame_number(self):
#         """update the frame number of self.animation based on selected item in frontend"""
#         self.animation.current_key_frame = self._get_selected_index()

#     def _update_selected_frame(self, event):
#         key_frame_idx = self.animation.current_key_frame
#         self.setCurrentRowBlockingSignals(key_frame_idx)

#     def _generate_list_item(self, key_frame):
#         """Generate a QListWidgetItem from a key-frame"""
#         item = QListWidgetItem(f"key-frame {self._frame_count}")
#         item.setIcon(self._icon_from_key_frame(key_frame))
#         return item

#     def _icon_from_key_frame(self, key_frame):
#         """Generate QIcon from a key frame"""
#         thumbnail = QImage(
#             key_frame.thumbnail,
#             key_frame.thumbnail.shape[1],
#             key_frame.thumbnail.shape[0],
#             QImage.Format_RGBA8888,
#         )
#         return QIcon(QPixmap.fromImage(thumbnail))

#     def _get_selected_index(self):
#         """Get index of currently selected row"""
#         idxs = self.selectedIndexes()
#         if len(idxs) == 0:
#             return -1
#         else:
#             return idxs[-1].row()

#     def _update_theme(self, theme_name):
#         """
#         Update styling based on the napari theme dictionary and any other attributes

#         Parameters
#         ----------
#         theme : str
#             name of napari theme
#         """
#         from napari.utils.theme import get_theme, template

#         qss_template = """
#         QListView::item:deselected {
#             background-color: {{ foreground }};
#         }
#         QListView::item:selected {
#             background-color: {{ current }};
#         }
#         QListView {
#             background: transparent;
#         }
#         QListView::item {
#             margin: 0px;
#             padding: 0px;
#             min-height:
#             32px;
#             max-height: 32px;
#         }
#         QImage {
#             margin: 0px;
#             padding: 0px;
#             qproperty-alignment: AlignLeft;
#         }
#         """

#         self.setStyleSheet(template(qss_template, **get_theme(theme_name)))
#         self.setIconSize(QSize(64, 64))
#         self.setSpacing(2)

#     @property
#     def frontend_items(self):
#         """Iterate over frontend_items in the keyframes list"""
#         for i in range(self.count()):
#             yield self.item(i)

#     @property
#     def frontend_key_frames(self):
#         for item in self.frontend_items:
#             yield self._item_id_to_key_frame[id(item)]

#     def dropEvent(self, event):
#         """update backend state on 'drop' of frame in key frames list"""
#         super().dropEvent(event)
#         self._reorder_backend()
#         self._update_frame_number()

#     def insertItem(self, row, item):
#         """overrides QListWidget.insertItem to also update index to newly inserted item"""
#         super().insertItem(row, item)
#         self.setCurrentIndex(self.indexFromItem(item))

#     def insertItemBlockingSignals(
#         self, row: int, item: QListWidgetItem
#     ) -> None:
#         return self.callMethodBlockingSignals(self.insertItem, row, item)

#     def setCurrentRowBlockingSignals(self, row: int) -> None:
#         return self.callMethodBlockingSignals(self.setCurrentRow, row)

#     def takeItemBlockingSignals(self, row: int) -> QListWidgetItem:
#         return self.callMethodBlockingSignals(self.takeItem, row)

#     def callMethodBlockingSignals(self, method, *args, **kwargs):
#         """Call 'method' without emitting events to avoid side effects"""
#         self.blockSignals(True)
#         output = method(*args, **kwargs)
#         self.blockSignals(False)
#         return output
