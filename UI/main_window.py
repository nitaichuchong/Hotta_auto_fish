# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLayout, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(350, 330)
        MainWindow.setMinimumSize(QSize(350, 330))
        MainWindow.setMaximumSize(QSize(350, 330))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 351, 381))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(-1, 10, -1, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(30, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.button = QPushButton(self.gridLayoutWidget)
        self.button.setObjectName(u"button")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.button.sizePolicy().hasHeightForWidth())
        self.button.setSizePolicy(sizePolicy1)
        self.button.setSizeIncrement(QSize(0, 0))
        self.button.setBaseSize(QSize(0, 0))

        self.horizontalLayout.addWidget(self.button)

        self.horizontalSpacer_2 = QSpacerItem(50, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.status_label = QLabel(self.gridLayoutWidget)
        self.status_label.setObjectName(u"status_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.status_label.sizePolicy().hasHeightForWidth())
        self.status_label.setSizePolicy(sizePolicy2)
        font = QFont()
        font.setPointSize(8)
        self.status_label.setFont(font)
        self.status_label.setFrameShape(QFrame.Shape.NoFrame)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.status_label)

        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(3, 3)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.fishing_label = QLabel(self.gridLayoutWidget)
        self.fishing_label.setObjectName(u"fishing_label")
        self.fishing_label.setTextFormat(Qt.TextFormat.AutoText)
        self.fishing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.fishing_label)

        self.endurance_label = QLabel(self.gridLayoutWidget)
        self.endurance_label.setObjectName(u"endurance_label")
        self.endurance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.endurance_label)

        self.tips_label = QLabel(self.gridLayoutWidget)
        self.tips_label.setObjectName(u"tips_label")
        self.tips_label.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)

        self.verticalLayout.addWidget(self.tips_label)

        self.verticalLayout.setStretch(0, 2)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)
        self.verticalLayout.setStretch(3, 8)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u81ea\u52a8\u9493\u9c7c", None))
        self.button.setText(QCoreApplication.translate("MainWindow", u"\u5148\u70b9\u6b64\u521d\u59cb\u5316", None))
        self.status_label.setText(QCoreApplication.translate("MainWindow", u"\u5c1a\u672a\u521d\u59cb\u5316", None))
        self.fishing_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:8pt; color:#ff0000;\">\u5c1a\u672a\u5f00\u59cb\u6267\u884c</span></p></body></html>", None))
        self.endurance_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:8pt; color:#55aaff;\">\u5c1a\u672a\u5f00\u59cb\u6267\u884c</span></p></body></html>", None))
        self.tips_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:8pt; font-weight:700; color:#00aa00;\">\u8bf7\u4e0d\u8981\u8ba9\u8be5\u7a0b\u5e8f\u7a97\u53e3\u906e\u6321\u4f4f\u9c7c\u7684\u8010\u529b\u503c\u548c\u4e2d\u95f4\u7684\u4f53\u529b\u6761</span></p><p align=\"center\"><span style=\" font-size:8pt; font-weight:700; color:#00aa00;\">\u4f7f\u7528\u65f6\u5148\u70b9\u51fb\u521d\u59cb\u5316\uff0c\u7136\u540e\u6bcf\u6b21\u5f00\u59cb\u6267\u884c\u7684\u7b2c\u4e00\u6b21\u6325\u6746\u9700\u8981\u81ea\u5df1\u64cd\u4f5c</span></p><p align=\"center\"><span style=\" font-size:8pt; font-weight:700; color:#00aa00;\">\u7b2c\u4e00\u6b21\u6325\u6746\u540e\u5f00\u59cb\u6267\u884c\uff0c\u540e\u9762\u5c31\u662f\u5168\u81ea\u52a8\u5faa\u73af\u9493\u9c7c\uff0c\u4f60\u4e5f\u53ef\u4ee5\u968f\u65f6\u505c\u6b62</span></p><p align=\"center\"><span style=\" font-size:8pt; font-weight:700; color:#00aa00;\">\u4f46\u6bcf\u6b21\u505c\u6b62\u540e\u7684\u7b2c\u4e00\u6b21\u6325\u6746\uff0c\u4f9d\u65e7\u9700\u8981\u81ea\u5df1\u64cd\u4f5c<"
                        "/span></p><p align=\"center\"><span style=\" font-size:8pt; font-weight:700; color:#00aa00;\">\u6267\u884c\u7684\u8fc7\u7a0b\u4e2d\u9f20\u6807\u548c\u952e\u76d8\u8bf7\u52ff\u64cd\u4f5c\uff0c\u9664\u975e\u4f60\u662f\u60f3\u505c\u6b62\u6216\u91cd\u65b0\u6267\u884c</span></p><p align=\"center\"><span style=\" font-size:8pt; font-weight:700; color:#00aa00;\">\u76ee\u524d\u662f\u8c03\u7528\u952e\u9f20\u8fdb\u884c\u64cd\u4f5c\uff0c\u6240\u4ee5\u4f60\u4f1a\u8ddf\u8be5\u7a0b\u5e8f\u64cd\u4f5c\u51b2\u7a81</span></p></body></html>", None))
    # retranslateUi

