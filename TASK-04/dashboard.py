from import_csv import get_connection
from PySide6.QtWidgets import QTableWidgetItem


import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QGridLayout, 
    QTextEdit, QSizePolicy, QLineEdit
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CineScope – Dashboard")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("background-color: #121212; color: white; padding: 20px;")
        self.search_mode = None        #------     
        self.selected_columns = []           #------
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Header
        header = QLabel("🎬 CineScope Dashboard")
        header.setFont(QFont("Arial", 24, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(80)
        main_layout.addWidget(header)
        split_layout = QHBoxLayout()

        # Left Panel
        left_container = QVBoxLayout()
        left_container.setSpacing(10)
        left_container.setAlignment(Qt.AlignTop)

        # Search buttons
        search_heading = QLabel("Search By")
        search_heading.setFont(QFont("Arial", 18, QFont.Bold))
        left_container.addWidget(search_heading)

        search_buttons = [                                                             #-------
            ("Genre", "Genre"),                                                      #------
            ("Year", "Released_Year"),                                                 #------
            ("Rating", "IMDB_Rating"),                                               #------
            ("Director", "Director"),                                                  #------
            ("Actor", "Star1"),  # facing bug if i am trying to search star2 and star3        #------
         ]


        search_grid = QGridLayout()
        for index, (label, mode) in enumerate(search_buttons):
            btn = QPushButton(label)
            btn.setStyleSheet(self.get_button_style(False))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _, m=mode: self.set_search_mode(m))
            row, col = divmod(index, 2)
            search_grid.addWidget(btn, row, col)
        left_container.addLayout(search_grid)

        # Column selection
        column_heading = QLabel("Select Columns")
        column_heading.setFont(QFont("Arial", 18, QFont.Bold))
        left_container.addWidget(column_heading)

       # ✅ Use actual DB column names
        column_buttons = [                        #---------------
            ("Title", "Series_Title"),            #------------
            ("Year", "Released_Year"),
            ("Genre", "Genre"),
            ("Rating", "IMDB_Rating"),
            ("Director", "Director"),
            ("Star1", "Star1"),
            ("Star2", "Star2"),
            ("Star3", "Star3"),                   #------------
         ]


        column_grid = QGridLayout()
        for index, (label, col) in enumerate(column_buttons):
            btn = QPushButton(label)
            btn.setStyleSheet(self.get_button_style(False))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _, c=col: self.toggle_column(c))
            row, col = divmod(index, 2)
            column_grid.addWidget(btn, row, col)
        left_container.addLayout(column_grid)

        # Search input
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Enter search term")
        self.query_input.setStyleSheet("background-color: #1e1e1e; color: white; padding: 5px; border: 1px solid #444;")
        left_container.addWidget(self.query_input)

        # Action buttons
        action_layout = QHBoxLayout()
        search_btn = QPushButton("Search")
        search_btn.setStyleSheet("background-color: #e50914; color: white; padding: 6px; border-radius: 5px;")
        search_btn.clicked.connect(self.execute_search)
        action_layout.addWidget(search_btn)

        export_btn = QPushButton("Export CSV")
        export_btn.setStyleSheet("background-color: #1f1f1f; color: white; padding: 6px; border-radius: 5px;")
        export_btn.clicked.connect(self.export_csv)
        action_layout.addWidget(export_btn)
        left_container.addLayout(action_layout)

        # Right Panel
        right_side_layout = QVBoxLayout()
        right_side_layout.setSpacing(10)

        # Table
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                color: white;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                padding: 4px;
            }
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Output console
        self.output_console = QTextEdit()
        self.output_console.setPlaceholderText("Results will appear here...")
        self.output_console.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #444;
                padding: 5px;
            }
        """)
        self.output_console.setFixedHeight(100)

        right_side_layout.addWidget(self.table)
        right_side_layout.addWidget(self.output_console)

        split_layout.addLayout(left_container, 2)
        split_layout.addLayout(right_side_layout, 8)
        main_layout.addLayout(split_layout)
        self.setLayout(main_layout)

    def get_button_style(self, is_selected):
        if is_selected:
            return """
                QPushButton {
                    background-color: #ffcc00;
                    border: 1px solid #ff9900;
                    border-radius: 3px;
                    padding: 6px;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #1f1f1f;
                    border: 1px solid #333;
                    border-radius: 3px;
                    padding: 6px;
                }
                QPushButton:hover {
                    background-color: #333;
                }
            """

    def set_search_mode(self, mode):
        self.search_mode = mode
        self.output_console.append(f"Search mode set to: {mode}")

    def toggle_column(self, column):
        if column in self.selected_columns:
            self.selected_columns.remove(column)
            self.output_console.append(f"Column removed: {column}")
        else:
            self.selected_columns.append(column)
            self.output_console.append(f"Added the Column: {column}")


    def execute_search(self):
        try:
            from import_csv import get_connection
            connection = get_connection()
            cursor = connection.cursor()
            
            
             # ✅ Build dynamic query using selected columns + search mode
           
            if self.selected_columns:
                 columns = ", ".join(self.selected_columns)  
            else:
                 columns = "*"  

            query = f"SELECT {columns} FROM movies"
            my_custom_list = []


        # Apply filter only if mode + term provided
            if self.search_mode and self.query_input.text().strip() != "":
                term = self.query_input.text().strip()

                if self.search_mode == "Released_Year" or self.search_mode == "IMDB_Rating":
                    query = query + " WHERE " + self.search_mode + " = %s"
                    my_custom_list.append(term)
                else:
                    query = query + " WHERE " + self.search_mode + " LIKE %s"
                    my_custom_list.append("%" + term + "%")

                
            cursor.execute(query, my_custom_list)
            rows = cursor.fetchall()

        # Clear table before showing results
            self.table.clear()
            number_of_rows = len(rows)
            self.table.setRowCount(number_of_rows)

            if number_of_rows > 0:
                number_of_columns = len(rows[0])
            else:
                number_of_columns = 0

            self.table.setColumnCount(number_of_columns)    
        
        
        
        # Set table headers
            headers = []
            for column_info in cursor.description:
                 column_name = column_info[0]
                 headers.append(column_name)

            self.table.setHorizontalHeaderLabels(headers)


        # Fill table with query results
            row_number = 0
            for row in rows:
                column_number = 0
                for item in row:
                    item_widget = QTableWidgetItem(str(item))
                    self.table.setItem(row_number, column_number, item_widget)
                    column_number += 1
                row_number += 1

                    
                    
            self.output_console.append("Executing search...")
                    
            cursor.close()
            connection.close()
                    
                    
        except Exception as e:
            self.output_console.append(f"Error: {e}")



    def export_csv(self):
        self.output_console.append("Exporting to CSV...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec())
