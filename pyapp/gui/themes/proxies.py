from collections.abc import Callable
from pathlib import Path

from PySide2.QtWidgets import QProxyStyle, QStyle
from PySide2.QtGui import QIcon

from ...utils.json import load_jsonc


class IconThemedProxyStyle(QProxyStyle):
    """
    QProxyStyle subclass for runtime icon theming in PySide2.
    Do NOT add any new instance attributes after __init__.
    Use class-level dicts for per-instance data.
    """
    _icon_theme_data = {}

    def __init__(self, base_style=None):
        super().__init__(base_style)
        # Do not assign to self.<anything> except what QProxyStyle expects

    @classmethod
    def set_icon_theme_data(cls, style, *, icon_generator, mapping_file):
        """Attach icon theming data to a style instance (by id)."""
        data = {
            'icon_generator': icon_generator,
            'standard_pixmaps': {},
            'primitive_elements': {},
            'complex_controls': {},
        }
        # Load mapping
        mapping_path = Path(mapping_file)
        if not mapping_path.exists():
            print(f"Warning: Icon mapping file not found: {mapping_file}")
        else:
            mapping = load_jsonc(mapping_path)
            if not isinstance(mapping, dict):
                print(f"Error: Invalid mapping format in {mapping_file}")
            else:
                cls._load_standard_pixmaps(data,
                                           mapping.get('standard_pixmaps', {}))
                cls._load_primitive_elements(data,
                                             mapping.get('primitive_elements',
                                                         {}))
                cls._load_complex_controls(data,
                                           mapping.get('complex_controls', {}))
                print(f"Loaded icon mapping: {len(data['standard_pixmaps'])} "
                      "standard pixmaps, "
                      f"{len(data['primitive_elements'])} primitive elements, "
                      f"{len(data['complex_controls'])} complex controls")
        cls._icon_theme_data[id(style)] = data

    @staticmethod
    def _load_standard_pixmaps(data, pixmaps):
        for pixmap_name, icon_info in pixmaps.items():
            try:
                pixmap_enum = getattr(QStyle, pixmap_name)
                data['standard_pixmaps'][pixmap_enum] = icon_info
            except AttributeError:
                print(f"Warning: Unknown standard pixmap: {pixmap_name}")

    @staticmethod
    def _load_primitive_elements(data, elements):
        for element_name, states in elements.items():
            try:
                element_enum = getattr(QStyle, element_name)
                data['primitive_elements'][element_enum] = states
            except AttributeError:
                print(f"Warning: Unknown primitive element: {element_name}")

    @staticmethod
    def _load_complex_controls(data, controls):
        for control_name, sub_controls in controls.items():
            try:
                control_enum = getattr(QStyle, control_name)
                data['complex_controls'][control_enum] = sub_controls
            except AttributeError:
                print(f"Warning: Unknown complex control: {control_name}")

    def standardIcon(self, standardPixmap, option=None, widget=None):
        data = self._icon_theme_data.get(id(self), None)
        if (data and standardPixmap in data['standard_pixmaps']
                and data['icon_generator']):
            icon_info = data['standard_pixmaps'][standardPixmap]
            print("[IconThemedProxyStyle] Generating custom icon: "
                  f"{icon_info}")
            return data['icon_generator'](
                icon_info["fontspec_name"],
                icon_info["icon_name"]
            )
        return super().standardIcon(standardPixmap, option, widget)

    def drawPrimitive(self, element, option, painter, widget=None):
        data = self._icon_theme_data.get(id(self), None)
        if (data and element in data['primitive_elements']
                and data['icon_generator']):
            state_key = self._get_primitive_state(element, option)
            element_states = data['primitive_elements'][element]
            if state_key in element_states:
                icon_info = element_states[state_key]
                icon = data['icon_generator'](
                    icon_info["fontspec_name"],
                    icon_info["icon_name"]
                )
                self._draw_icon_for_primitive(icon, option, painter)
                return
        return super().drawPrimitive(element, option, painter, widget)

    def drawComplexControl(self, control, option, painter, widget=None):
        data = self._icon_theme_data.get(id(self), None)
        if (data and control in data['complex_controls']
                and data['icon_generator']):
            # Handle complex controls like combo boxes and spin boxes
            if control == QStyle.CC_ComboBox:
                self._draw_combo_box(data, option, painter, widget)
                return
            elif control == QStyle.CC_SpinBox:
                self._draw_spin_box(data, option, painter, widget)
                return
        return super().drawComplexControl(control, option, painter, widget)

    def _draw_combo_box(self, data, option, painter, widget):
        # Draw the base combo box without the arrow
        super().drawComplexControl(QStyle.CC_ComboBox, option, painter, widget)
        # Draw custom arrow
        arrow_rect = self.subControlRect(QStyle.CC_ComboBox, option,
                                         QStyle.SC_ComboBoxArrow, widget)
        if not arrow_rect.isValid():
            return
        control_info = data['complex_controls'][QStyle.CC_ComboBox]
        if "SC_ComboBoxArrow" in control_info:
            icon_info = control_info["SC_ComboBoxArrow"]
            icon = data['icon_generator'](
                icon_info["fontspec_name"],
                icon_info["icon_name"]
            )
            self._draw_icon_in_rect(icon, arrow_rect, painter)

    def _draw_spin_box(self, data, option, painter, widget):
        super().drawComplexControl(QStyle.CC_SpinBox, option, painter, widget)
        up_rect = self.subControlRect(QStyle.CC_SpinBox, option,
                                      QStyle.SC_SpinBoxUp, widget)
        if up_rect.isValid():
            control_info = data['complex_controls'][QStyle.CC_SpinBox]
            if "SC_SpinBoxUp" in control_info:
                icon_info = control_info["SC_SpinBoxUp"]
                icon = data['icon_generator'](
                    icon_info["fontspec_name"],
                    icon_info["icon_name"]
                )
                self._draw_icon_in_rect(icon, up_rect, painter)
        down_rect = self.subControlRect(QStyle.CC_SpinBox, option,
                                        QStyle.SC_SpinBoxDown, widget)
        if down_rect.isValid():
            control_info = data['complex_controls'][QStyle.CC_SpinBox]
            if "SC_SpinBoxDown" in control_info:
                icon_info = control_info["SC_SpinBoxDown"]
                icon = data['icon_generator'](
                    icon_info["fontspec_name"],
                    icon_info["icon_name"]
                )
                self._draw_icon_in_rect(icon, down_rect, painter)

    @staticmethod
    def _get_primitive_state(element, option) -> str:
        if element == QStyle.PE_IndicatorCheckBox:
            if hasattr(option, 'state'):
                if option.state & QStyle.State_On:
                    return "checked"
                elif option.state & QStyle.State_NoChange:
                    return "indeterminate"
                else:
                    return "unchecked"
        elif element == QStyle.PE_IndicatorRadioButton:
            if hasattr(option, 'state'):
                if option.state & QStyle.State_On:
                    return "checked"
                else:
                    return "unchecked"
        elif element == QStyle.PE_IndicatorBranch:
            if hasattr(option, 'state'):
                if option.state & QStyle.State_Open:
                    return "open"
                else:
                    return "closed"
        return "default"

    @staticmethod
    def _draw_icon_for_primitive(icon: QIcon, option, painter):
        if not hasattr(option, 'rect'):
            return
        rect = option.rect
        IconThemedProxyStyle._draw_icon_in_rect(icon, rect, painter)

    @staticmethod
    def _draw_icon_in_rect(icon: QIcon, rect, painter):
        size = min(rect.width(), rect.height(), 16)
        pixmap = icon.pixmap(size, size)
        x = rect.x() + (rect.width() - size) // 2
        y = rect.y() + (rect.height() - size) // 2
        painter.drawPixmap(x, y, pixmap)


def create_themed_proxy_style(icon_generator: Callable[[str, str], QIcon],
                              mapping_file: str, base_style=None):
    """
    Create and configure an IconThemedProxyStyle instance.
    Args:
        icon_generator: Function (fontspec_name, icon_name) -> QIcon
        mapping_file: Path to JSON file with icon mappings
        base_style: Optional base style (QStyle)
    Returns:
        Configured IconThemedProxyStyle instance
    """
    style = IconThemedProxyStyle(base_style)
    IconThemedProxyStyle.set_icon_theme_data(style,
                                             icon_generator=icon_generator,
                                             mapping_file=mapping_file)
    print("Themed proxy style created successfully")
    return style
