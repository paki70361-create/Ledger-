import sqlite3
from datetime import datetime
from pathlib import Path

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup

Window.clearcolor = (0.95, 0.96, 0.98, 1)

class LedgerApp(App):
    def build(self):
        self.title = "My Personal Ledger"
        db_file = Path(self.user_data_dir) / "ledger.db"
        self.db = sqlite3.connect(str(db_file))
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person TEXT NOT NULL,
                amount REAL NOT NULL,
                kind TEXT NOT NULL,
                reason TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)
        self.db.commit()

        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))

        header = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(72),
                           padding=[dp(14), dp(9)])
        header.canvas.before.clear()
        from kivy.graphics import Color, RoundedRectangle
        with header.canvas.before:
            Color(0.09, 0.14, 0.23, 1)
            self.header_bg = RoundedRectangle(pos=header.pos, size=header.size, radius=[dp(12)])
        header.bind(pos=lambda w, p: setattr(self.header_bg, "pos", p),
                    size=lambda w, s: setattr(self.header_bg, "size", s))
        header.add_widget(Label(text="[b]MY PERSONAL LEDGER[/b]\\n[ size=12 ] Track money given and received",
                                markup=True, color=(1,1,1,1), halign="left", valign="middle"))
        root.add_widget(header)

        summary = GridLayout(cols=3, size_hint_y=None, height=dp(82), spacing=dp(6))
        self.given_label = self.summary_card(summary, "GIVEN")
        self.received_label = self.summary_card(summary, "RECEIVED")
        self.balance_label = self.summary_card(summary, "NET")
        root.add_widget(summary)

        form = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(245),
                         padding=dp(10), spacing=dp(7))
        form.add_widget(self.section_label("NEW TRANSACTION"))
        self.name_input = TextInput(hint_text="Person's name", multiline=False, size_hint_y=None, height=dp(43))
        self.amount_input = TextInput(hint_text="Amount (e.g. 1500)", multiline=False,
                                      input_filter="float", size_hint_y=None, height=dp(43))
        self.kind_spinner = Spinner(text="Given", values=("Given", "Received"),
                                    size_hint_y=None, height=dp(43))
        self.reason_input = TextInput(hint_text="Reason / transaction details", multiline=False,
                                      size_hint_y=None, height=dp(43))
        for widget in (self.name_input, self.amount_input, self.kind_spinner, self.reason_input):
            form.add_widget(widget)
        save = Button(text="SAVE TRANSACTION", size_hint_y=None, height=dp(44),
                      background_normal="", background_color=(0.13, 0.36, 0.85, 1))
        save.bind(on_release=self.add_transaction)
        form.add_widget(save)
        root.add_widget(form)

        tools = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        self.search_input = TextInput(hint_text="Search name or reason", multiline=False)
        self.search_input.bind(text=lambda *_: self.refresh_history())
        tools.add_widget(self.search_input)
        root.add_widget(tools)

        root.add_widget(self.section_label("TRANSACTION HISTORY"))
        self.history = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.history.bind(minimum_height=self.history.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.history)
        root.add_widget(scroll)

        self.refresh_history()
        return root

    def section_label(self, text):
        return Label(text=f"[b]{text}[/b]", markup=True, color=(0.10,0.15,0.24,1),
                     size_hint_y=None, height=dp(25), halign="left", valign="middle")

    def summary_card(self, parent, title):
        box = BoxLayout(orientation="vertical", padding=dp(5), spacing=dp(3))
        label = Label(text=f"[size=11]{title}[/size]\\n[b]0.00[/b]", markup=True,
                      color=(0.10,0.15,0.24,1), halign="center", valign="middle")
        box.add_widget(label)
        parent.add_widget(box)
        return label

    def notify(self, title, message):
        Popup(title=title, content=Label(text=message), size_hint=(0.85, 0.28)).open()

    def add_transaction(self, *_):
        person = self.name_input.text.strip()
        amount_text = self.amount_input.text.strip().replace(",", "")
        reason = self.reason_input.text.strip()
        kind = self.kind_spinner.text
        if not person or not amount_text or not reason:
            self.notify("Missing information", "Enter the person's name, amount and reason.")
            return
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            self.notify("Invalid amount", "Please enter an amount greater than zero.")
            return

        self.db.execute(
            "INSERT INTO transactions (person, amount, kind, reason, date) VALUES (?, ?, ?, ?, ?)",
            (person, amount, kind, reason, datetime.now().strftime("%d %b %Y, %I:%M %p"))
        )
        self.db.commit()
        self.name_input.text = ""
        self.amount_input.text = ""
        self.reason_input.text = ""
        self.kind_spinner.text = "Given"
        self.refresh_history()
        self.notify("Saved", "Your transaction has been saved on this phone.")

    def refresh_history(self):
        if not hasattr(self, "history"):
            return
        self.history.clear_widgets()
        rows = self.db.execute(
            "SELECT id, person, amount, kind, reason, date FROM transactions ORDER BY id DESC"
        ).fetchall()
        total_given = sum(r[2] for r in rows if r[3] == "Given")
        total_received = sum(r[2] for r in rows if r[3] == "Received")
        self.given_label.text = f"[size=10]GIVEN[/size]\\n[b]{total_given:,.2f}[/b]"
        self.received_label.text = f"[size=10]RECEIVED[/size]\\n[b]{total_received:,.2f}[/b]"
        self.balance_label.text = f"[size=10]NET[/size]\\n[b]{total_received-total_given:,.2f}[/b]"

        term = self.search_input.text.strip().lower()
        for row in rows:
            rid, person, amount, kind, reason, date = row
            if term and term not in person.lower() and term not in reason.lower():
                continue
            item = BoxLayout(size_hint_y=None, height=dp(92), padding=dp(8), spacing=dp(6))
            details = Label(
                text=f"[b]{person}[/b]  •  {kind}\\n{amount:,.2f}  |  {reason}\\n[size=10]{date}[/size]",
                markup=True, color=(0.12,0.16,0.23,1), halign="left", valign="middle"
            )
            details.bind(size=lambda w, s: setattr(w, "text_size", s))
            item.add_widget(details)
            delete = Button(text="DELETE", size_hint_x=None, width=dp(76),
                            background_normal="", background_color=(0.75,0.18,0.18,1))
            delete.bind(on_release=lambda btn, transaction_id=rid: self.delete_transaction(transaction_id))
            item.add_widget(delete)
            self.history.add_widget(item)

        if not rows:
            self.history.add_widget(Label(text="No transactions yet. Add your first record above.",
                                          color=(0.35,0.40,0.48,1), size_hint_y=None, height=dp(55)))

    def delete_transaction(self, transaction_id):
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text="Delete this transaction?"))
        buttons = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        popup = Popup(title="Confirm delete", content=content, size_hint=(0.8, 0.28))
        yes = Button(text="Delete", background_normal="", background_color=(0.75,0.18,0.18,1))
        no = Button(text="Cancel")
        buttons.add_widget(yes); buttons.add_widget(no)
        content.add_widget(buttons)
        yes.bind(on_release=lambda *_: (self.db.execute("DELETE FROM transactions WHERE id=?", (transaction_id,)),
                                        self.db.commit(), popup.dismiss(), self.refresh_history()))
        no.bind(on_release=popup.dismiss)
        popup.open()

    def on_stop(self):
        if hasattr(self, "db"):
            self.db.close()

if __name__ == "__main__":
    LedgerApp().run()
