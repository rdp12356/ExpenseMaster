import os
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from utils.i18n import t
from utils.format import money
from services.api import AuthService, DbService, supabase
from services.fx import convert
from services.charts import plot_spend_by_category, plot_time_series
from services.oauth import start_google_oauth
from utils.currency_names import localized_currency_list
from dotenv import load_dotenv

load_dotenv()
Builder.load_file("expense.kv")

class ExpenseMaster(App):
    locale = "en"
    base_currency = "USD"
    user_id = None

    def build(self):
        Window.minimum_width, Window.minimum_height = 390, 720
        self.title = "ExpenseMaster"
        return self.root

    def on_start(self):
        try:
            user = AuthService.user()
            if user and getattr(user, 'user', None):
                self.user_id = user.user.id
                self.post_login_setup()
            else:
                self.root.current = "login"
        except Exception:
            self.root.current = "login"

    def tr(self, key, **kw):
        return t(self.locale, key, **kw)

    def currency_items(self):
        items = localized_currency_list(self.locale)
        return [f"{name} ({code})" for code, name in items]

    def sign_in(self, email, password):
        try:
            res = AuthService.sign_in(email, password)
            if not getattr(res.user, 'email_confirmed_at', True):
                self.popup(self.tr('verify_notice'))
                return
            self.user_id = res.user.id
            self.post_login_setup()
        except Exception as e:
            self.popup(f"{self.tr('invalid')}: {e}")

    def google_sign_in(self):
        try:
            tokens = start_google_oauth()
            # Note: supabase client in services.api must persist session appropriately
            self.popup('Signed in with Google (check Supabase session)')
            self.post_login_setup()
        except Exception as e:
            self.popup(str(e))

    def goto_signup(self):
        self.root.current = 'signup'

    def sign_up(self, full_name, email, password):
        try:
            AuthService.sign_up(email, password, full_name)
            self.popup(self.tr('verify_notice'))
        except Exception as e:
            self.popup(str(e))

    def post_login_setup(self):
        DbService.ensure_profile(self.user_id, self.locale, self.base_currency)
        prof = supabase.table('profiles').select('*').eq('id', self.user_id).execute().data
        if prof:
            self.locale = prof[0].get('locale','en')
            self.base_currency = prof[0].get('base_currency','USD')
        self.root.current = 'home'
        Clock.schedule_once(lambda *_: self.refresh_expenses(), 0.2)

    def logout(self):
        AuthService.sign_out()
        self.user_id = None
        self.root.current = 'login'

    def add_expense(self, amount_txt, currency_txt, note_txt):
        try:
            amt = float(amount_txt)
            # currency_txt from Spinner like "Indian Rupee (INR)"
            if '(' in currency_txt and ')' in currency_txt:
                cur = currency_txt.split('(')[-1].split(')')[0]
            else:
                cur = currency_txt.strip().upper()
            rec = DbService.add_expense(self.user_id, amt, cur, None, note_txt.strip())
            self.refresh_expenses()
        except Exception as e:
            self.popup(f"{self.tr('invalid')}: {e}")

    def refresh_expenses(self):
        gl = self.root.get_screen('home').ids.expense_list
        gl.clear_widgets()
        expenses = DbService.list_expenses(self.user_id, 200) or []
        total_base = 0.0
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.animation import Animation

        for row in expenses:
            try:
                converted = convert(row['amount'], row['currency'], self.base_currency)
                total_base += converted['amount']
                card = BoxLayout(orientation='horizontal', size_hint_y=None, height='56dp', padding=('12dp'), spacing='8dp')
                left = Label(text=f"{row.get('note','')}", halign='left')
                center = Label(text=f"{row['currency']} {row['amount']}", halign='center')
                right = Label(text=f"{self.base_currency} {converted['amount']:.2f}", halign='right')
                card.add_widget(left); card.add_widget(center); card.add_widget(right)
                gl.add_widget(card)
                Animation(opacity=0, d=0).start(card)
                Animation(opacity=1, d=.25).start(card)
            except Exception:
                pass

        self.root.get_screen('home').ids.total_label.text = f"{self.tr('total_this_month')}: {money(total_base, self.base_currency, self.locale)}"

    def update_base_currency(self, cur):
        self.base_currency = (cur or 'USD').strip().upper()
        DbService.set_profile(self.user_id, base_currency=self.base_currency)
        self.refresh_expenses()

    def update_locale(self, loc):
        self.locale = (loc or 'en').split('-')[0]
        DbService.set_profile(self.user_id, locale=self.locale)
        self.refresh_expenses()

    def show_charts(self):
        try:
            expenses = DbService.list_expenses(self.user_id, limit=200) or []
        except Exception:
            expenses = []
        pie_path = plot_spend_by_category(expenses, outname='spend_by_category.png')
        monthly = {}
        for e in expenses:
            dt = e.get('spent_at') or e.get('created_at') or ''
            key = str(dt)[:7]
            monthly[key] = monthly.get(key, 0) + float(e.get('amount') or 0)
        months = sorted(monthly.keys())[:12]
        amounts = [monthly[m] for m in months]
        ts_path = plot_time_series(months, amounts, outname='time_series.png')
        try:
            screen = self.root.get_screen('charts')
        except Exception:
            from kivy.uix.screenmanager import Screen
            from kivy.uix.image import Image
            from kivy.uix.boxlayout import BoxLayout
            cs = Screen(name='charts')
            bl = BoxLayout(orientation='vertical')
            bl.add_widget(Image(source=pie_path))
            bl.add_widget(Image(source=ts_path))
            cs.add_widget(bl)
            self.root.add_widget(cs)
            self.root.current = 'charts'
            return
        screen.clear_widgets()
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.image import Image
        bl = BoxLayout(orientation='vertical')
        bl.add_widget(Image(source=pie_path))
        bl.add_widget(Image(source=ts_path))
        screen.add_widget(bl)
        self.root.current = 'charts'

    def popup(self, msg):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        Popup(title='Info', content=Label(text=str(msg)), size_hint=(.7,.3)).open()

if __name__ == '__main__':
    ExpenseMaster().run()
