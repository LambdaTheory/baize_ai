"""
Improved Fluent-style Loading Overlay component
==============================================

Revision history
----------------
* **2025‑06‑27 v3** – guard `.start()` call for older qfluentwidgets versions.
* **2025‑06‑27 v2** – removed invalid ctor args; switched to setters.
* **2025‑06‑27 v1** – initial redesign.
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor
from qfluentwidgets import ProgressRing  # 🔄 Built‑in Fluent spinner

# Centralised design tokens
from .fluent_styles import FluentColors, FluentSpacing


class LoadingOverlay(QWidget):
    """A polished, Fluent‑design loading overlay."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("LoadingOverlay")
        self.setAttribute(Qt.WA_StyledBackground)

        self._build_ui()
        self._setup_animation()
        self.hide()  # start hidden

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        """Build and style the overlay widgets."""

        # Semi‑transparent curtain ------------------------------------------------
        self.setStyleSheet(
            """
            QWidget#LoadingOverlay {
                background-color: rgba(255, 255, 255, 0.85);
            }
            """
        )

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setContentsMargins(0, 0, 0, 0)

        # Centre card -------------------------------------------------------------
        self.card = QWidget(self, objectName="Card")
        self.card.setFixedSize(380, 240)
        self.card.setStyleSheet(
            f"""
            QWidget#Card {{
                background: white;
                border-radius: 20px;
                border: 1px solid {FluentColors.get_color('border_primary')};
            }}
            """
        )

        # Soft drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(0, 0, 0, 64))  # ≈25 % opacity
        self.card.setGraphicsEffect(shadow)

        card_lo = QVBoxLayout(self.card)
        card_lo.setAlignment(Qt.AlignCenter)
        card_lo.setSpacing(FluentSpacing.LG)
        card_lo.setContentsMargins(40, 40, 40, 40)

        # Animated spinner --------------------------------------------------------
        self.spinner = ProgressRing(self.card)
        self.spinner.setFixedSize(64, 64)  # diameter ≈64 px
        if hasattr(self.spinner, "setStrokeWidth"):
            self.spinner.setStrokeWidth(5)
        if hasattr(self.spinner, "setCustomBarColor"):
            primary = FluentColors.get_color("primary")
            self.spinner.setCustomBarColor(primary, primary)
        if hasattr(self.spinner, "start"):
            self.spinner.start()
        card_lo.addWidget(self.spinner, 0, Qt.AlignHCenter)

        # Main label --------------------------------------------------------------
        self.titleLbl = QLabel("正在加载…", self.card)
        self.titleLbl.setAlignment(Qt.AlignCenter)
        self.titleLbl.setStyleSheet(
            f"""
            QLabel {{
                font-size: 20px;
                font-weight: 600;
                color: {FluentColors.get_color('text_primary')};
            }}
            """
        )
        card_lo.addWidget(self.titleLbl)

        # Subtitle ----------------------------------------------------------------
        self.subtitleLbl = QLabel("请稍候，我们正在为您优化体验", self.card)
        self.subtitleLbl.setAlignment(Qt.AlignCenter)
        self.subtitleLbl.setWordWrap(True)
        self.subtitleLbl.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                color: {FluentColors.get_color('text_secondary')};
            }}
            """
        )
        card_lo.addWidget(self.subtitleLbl)

        root.addWidget(self.card)

    # ------------------------------------------------------------------
    # Animations
    # ------------------------------------------------------------------
    def _setup_animation(self) -> None:
        self._fade = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade.setDuration(250)
        self._fade.setEasingCurve(QEasingCurve.OutCubic)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def show_loading(self, text: str = "正在加载…", sub_text: str = "") -> None:
        """Fade‑in the overlay with optional updated messages."""

        self.titleLbl.setText(self._elide(text, 24))
        self.subtitleLbl.setText(
            self._elide(
                sub_text or "请稍候，正在为您打造更好的体验…",
                60,
            )
        )

        if self.parent():
            self.setGeometry(self.parent().rect())
        self._fade.stop()
        self.setWindowOpacity(0)
        self.show()
        self.raise_()

        self._fade.setStartValue(0)
        self._fade.setEndValue(1)
        self._fade.start()

    def hide_loading(self) -> None:
        """Fade‑out the overlay."""

        self._fade.stop()
        self._fade.setStartValue(1)
        self._fade.setEndValue(0)
        self._fade.finished.connect(self.hide)
        self._fade.start()

    def set_loading_message(self, title: str, subtitle: str = "") -> None:
        """Update labels without re‑showing the overlay."""
        self.titleLbl.setText(self._elide(title, 24))
        if subtitle:
            self.subtitleLbl.setText(self._elide(subtitle, 60))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _elide(text: str, max_len: int) -> str:
        """Elide strings that exceed *max_len* characters."""
        return text if len(text) <= max_len else text[: max_len - 1] + "…"

    # Keep covering parent when resized --------------------------------
    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())
