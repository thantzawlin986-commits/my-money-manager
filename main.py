import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

Window.clearcolor = (0.055, 0.09, 0.11, 1)

BG = (0.055, 0.09, 0.11, 1)
PANEL = (0.10, 0.16, 0.18, 1)
GREEN = (0.16, 0.55, 0.36, 1)
RED = (0.65, 0.24, 0.25, 1)
BLUE = (0.16, 0.36, 0.43, 1)
WHITE = (0.95, 0.97, 0.97, 1)
MUTED = (0.68, 0.76, 0.77, 1)

class MoneyApp(App):
    def build(self):
        self.title = "My Money Manager"
        self.data_file = Path(self.user_data_dir) / "transactions.json"
        self.transactions = self.load_data()

        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        header = BoxLayout(size_hint_y=None, height=dp(48))
        header.add_widget(Label(text="[b]MY MONEY MANAGER[/b]", markup=True,
                                color=WHITE, font_size="21sp", halign="left"))
        header.add_widget(Label(text="MMK  •  THB", color=MUTED, font_size="12sp",
                                size_hint_x=None, width=dp(100)))
        root.add_widget(header)

        cards = GridLayout(cols=2, spacing=dp(9), size_hint_y=None, height=dp(100))
        self.mmk_label = self.make_card(cards, "မြန်မာကျပ် (MMK)")
        self.thb_label = self.make_card(cards, "ထိုင်းဘတ် (THB)")
        root.add_widget(cards)

        root.add_widget(Label(text="ငွေစာရင်းအသစ်ထည့်ရန်", color=WHITE,
                              bold=True, size_hint_y=None, height=dp(28),
                              halign="left", text_size=(Window.width, None)))

        form = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(100))
        self.kind = Spinner(text="ဝင်ငွေ", values=("ဝင်ငွေ", "ထွက်ငွေ"),
                            background_color=BLUE, color=WHITE)
        self.currency = Spinner(text="MMK", values=("MMK", "THB"),
                                background_color=BLUE, color=WHITE)
        self.amount = TextInput(hint_text="ငွေပမာဏ", multiline=False,
                                input_filter="float", background_color=PANEL,
                                foreground_color=WHITE, hint_text_color=MUTED)
        self.note = TextInput(hint_text="မှတ်ချက် (ဥပမာ - လစာ၊ စားစရိတ်)",
                              multiline=False, background_color=PANEL,
                              foreground_color=WHITE, hint_text_color=MUTED)
        for w in (self.kind, self.currency, self.amount, self.note):
            form.add_widget(w)
        root.add_widget(form)

        actions = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(46))
        add_in = Button(text="+ ဝင်ငွေသိမ်းမယ်", background_color=GREEN, color=WHITE)
        add_out = Button(text="− ထွက်ငွေသိမ်းမယ်", background_color=RED, color=WHITE)
        add_in.bind(on_release=lambda *_: self.save_transaction("ဝင်ငွေ"))
        add_out.bind(on_release=lambda *_: self.save_transaction("ထွက်ငွေ"))
        actions.add_widget(add_in)
        actions.add_widget(add_out)
        root.add_widget(actions)

        self.summary = Label(text="", color=WHITE, size_hint_y=None, height=dp(55),
                             halign="left", valign="middle")
        self.summary.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        root.add_widget(self.summary)

        root.add_widget(Label(text="နောက်ဆုံးစာရင်းများ", color=WHITE, bold=True,
                              size_hint_y=None, height=dp(25), halign="left"))
        scroll = ScrollView()
        self.history_box = BoxLayout(orientation="vertical", spacing=dp(5),
                                     size_hint_y=None)
        self.history_box.bind(minimum_height=self.history_box.setter("height"))
        scroll.add_widget(self.history_box)
        root.add_widget(scroll)

        footer = Label(text="စာရင်းများကို ဒီဖုန်းထဲတွင် သိမ်းဆည်းထားသည်",
                       color=MUTED, font_size="11sp",
                       size_hint_y=None, height=dp(22))
        root.add_widget(footer)

        self.refresh()
        return root

    def make_card(self, parent, title):
        card = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(3))
        card.canvas.before.clear()
        from kivy.graphics import Color, RoundedRectangle
        with card.canvas.before:
            Color(*PANEL)
            card.bg_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
        card.bind(pos=lambda inst, val: setattr(inst.bg_rect, "pos", val),
                  size=lambda inst, val: setattr(inst.bg_rect, "size", val))
        card.add_widget(Label(text=title, color=MUTED, font_size="12sp"))
        value = Label(text="0", color=WHITE, bold=True, font_size="19sp")
        card.add_widget(value)
        parent.add_widget(card)
        return value

    def load_data(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return []

    def persist(self):
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.transactions, f, ensure_ascii=False, indent=2)

    def save_transaction(self, kind):
        raw = self.amount.text.strip()
        try:
            value = Decimal(raw)
            if not value.is_finite() or value <= 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            self.message("ငွေပမာဏ မှန်ကန်စွာ ထည့်ပေးပါ။")
            return

        self.transactions.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "kind": kind,
            "currency": self.currency.text,
            "amount": str(value),
            "note": self.note.text.strip() or "မှတ်ချက်မရှိ"
        })
        self.persist()
        self.amount.text = ""
        self.note.text = ""
        self.kind.text = kind
        self.refresh()
        self.message("စာရင်းသိမ်းပြီးပါပြီ။")

    def totals(self, currency):
        income = Decimal("0")
        expense = Decimal("0")
        for item in self.transactions:
            if item.get("currency") != currency:
                continue
            amount = Decimal(str(item.get("amount", "0")))
            if item.get("kind") == "ဝင်ငွေ":
                income += amount
            else:
                expense += amount
        return income, expense, income - expense

    def refresh(self):
        mi, me, mb = self.totals("MMK")
        ti, te, tb = self.totals("THB")
        self.mmk_label.text = f"{mb:,.2f} Ks"
        self.thb_label.text = f"{tb:,.2f} ฿"
        self.summary.text = (
            f"MMK  ဝင်ငွေ {mi:,.2f}  |  ထွက်ငွေ {me:,.2f}\n"
            f"THB  ဝင်ငွေ {ti:,.2f}  |  ထွက်ငွေ {te:,.2f}"
        )
        self.history_box.clear_widgets()
        for item in reversed(self.transactions[-100:]):
            sign = "+" if item.get("kind") == "ဝင်ငွေ" else "−"
            color = GREEN if sign == "+" else RED
            line = BoxLayout(size_hint_y=None, height=dp(55), padding=dp(7), spacing=dp(5))
            from kivy.graphics import Color, RoundedRectangle
            with line.canvas.before:
                Color(*PANEL)
                rect = RoundedRectangle(pos=line.pos, size=line.size, radius=[8])
            line.bind(pos=lambda inst, val, r=rect: setattr(r, "pos", val),
                      size=lambda inst, val, r=rect: setattr(r, "size", val))
            details = BoxLayout(orientation="vertical")
            details.add_widget(Label(text=f"{item.get('note','')}  •  {item.get('currency','')}",
                                     color=WHITE, halign="left", valign="middle",
                                     text_size=(Window.width * .55, None)))
            details.add_widget(Label(text=item.get("date", ""), color=MUTED,
                                     font_size="10sp", halign="left"))
            line.add_widget(details)
            line.add_widget(Label(text=f"{sign}{Decimal(str(item.get('amount','0'))):,.2f}",
                                  color=color, bold=True, size_hint_x=.42,
                                  font_size="14sp"))
            self.history_box.add_widget(line)

    def message(self, text):
        popup = Popup(title="My Money Manager",
                      content=Label(text=text, color=WHITE),
                      size_hint=(.8, .25), auto_dismiss=True)
        popup.open()


if __name__ == "__main__":
    MoneyApp().run()
