import tkinter
from datetime import datetime
from  tkinter import *
import sqlite3
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

window = Tk()
window.title(" باشگاه ورزشی سوگند")
window.geometry("400x400")
window.resizable(False, False)
window.config(bg="white")

conn = sqlite3.connect("bashgah.db")
cursor = conn.cursor()

#پنل کابری
def user_panel():

    def show_info():
        phone = entry_phone.get().strip()
        if phone == "":
            messagebox.showwarning(
                "خطا",
                "شماره موبایل را وارد کنید"
            )
            return

        # اطلاعات کاربر
        cursor.execute(
            "SELECT name, phone FROM user WHERE phone=?", (phone,))
        user = cursor.fetchone()
        if not user:
            messagebox.showerror(
                "خطا",
                "کابر گرامی ، سلام  برای شروع ابتدا باید به عنوان ورزشکار نام کاربری خود را ایجاد کنید. پس از ثبت نام، میتوانید وارد پنل کاربری خود شده و ز امکانات آن استفاده کنید  " )
            return
        name = user[0]

        # ورزش های کاربر
        cursor.execute("SELECT name, ghimat FROM varzeshs WHERE user_name=?",(name,))
        sports = cursor.fetchall()
        total_price = 0
        sport_names = []

        for sport_name, price in sports:
            sport_names.append(sport_name)
            try:
                total_price += int(
                    str(price).replace(",", "").strip()
                )
            except:
                pass
        if sport_names:
            sport_text = " ، ".join(sport_names)
        else:
            sport_text = "ورزشی ثبت نشده"

        # اشتراک کاربر
        cursor.execute("""
            SELECT type, end_date
            FROM eshterak
            WHERE user_id=?
            AND status='active'
        """, (phone,))
        sub = cursor.fetchone()

        if sub:
            sub_type = sub[0]
            end_date = sub[1]
        else:
            sub_type = "ندارد"
            end_date = "-"

        tedad_varzesh = len(sports)

        # اطلاعات خروجی
        info = [
            ("نام کاربر", name),
            ("شماره موبایل", phone),
            ("تعداد ورزش ها", tedad_varzesh),
            ("ورزش های انتخابی", sport_text),
            ("مجموع هزینه ورزش ها",
             f"{total_price:,} تومان"),
            ("نوع اشتراک", sub_type),
            ("تاریخ پایان اشتراک", end_date)

        ]
        result_text.config(
            state="normal"
        )
        result_text.delete(
            "1.0",
            END
        )
   # علامت راست به چپ فارسی
        RTL = "\u200F"
        for title, value in info:
            text_line = (
                RTL +
                title +
                " : " +
                str(value) +
                RTL +
                "\n\n"
            )
            result_text.insert(
                END,
                text_line,
                "info"
            )
        result_text.tag_configure(
            "info",
            justify="right",
            font=("B Nazanin", 13, "bold")
        )
        result_text.config(
            state="disabled"
        )
    # پنجره پنل کاربری
    panel_window = Toplevel(window)
    panel_window.title(
        "پنل کاربری"
    )
    panel_window.geometry(
        "650x500"
    )
    Label(panel_window, text="پنل کاربری اعضا",font=("B Titr",16)).pack(pady=10)
    Label(panel_window, text="شماره موبایل",font=("B Nazanin",12)).pack(pady=5)

    entry_phone = Entry(panel_window,font=("B Nazanin",12),justify="center")
    entry_phone.pack(pady=5,ipadx=30)

    Button(panel_window, text="نمایش اطلاعات",command=show_info,font=("B Nazanin",12)).pack(pady=10)

    result_text = ScrolledText( panel_window,font=("B Nazanin",13),wrap="word")
    result_text.pack(padx=10,pady=10,fill="both",expand=True)
    result_text.config(state="disabled")

#ایجاد کاربر
def create_user():

    def save_user():
        nameN = entry_name.get()
        phoneN = entry_phone.get()

        if nameN and phoneN:
            cursor.execute(
                "INSERT INTO user (name, phone) VALUES (?, ?)",
                (nameN, phoneN)
            )
            conn.commit()
            messagebox.showinfo("موفق", "کاربر با موفقیت اضافه شد!")
            user_window.destroy()
        else:
            messagebox.showwarning("خطا", "لطفاً تمام فیلدها را پر کنید.")
    # پنجره افزودن کاربر
    user_window = Toplevel(window)
    user_window.title("افزودن کاربر")
    user_window.geometry("300x180")
    user_window.resizable(False, False)

    Label(user_window, text="نام و نام خانوگی کاربر").pack(pady=5)
    entry_name = Entry(user_window, width=30)
    entry_name.pack(pady=5)

    Label(user_window, text="شماره تلفن").pack(pady=5)
    entry_phone = Entry(user_window, width=30)
    entry_phone.pack(pady=5)

    Button(user_window,text="ذخیره", command=save_user, width=15).pack(pady=10)


#حذف کاربر
def delete_user():

    def remove_user():
        phoneN = entry_uesr_phone.get().strip()
        if phoneN == "":
            messagebox.showwarning(
                "خطا",
                "شماره تلفن را وارد کنید"
            )
            return
        try:
            # پیدا کردن نام کاربر قبل از حذف
            cursor.execute(
                "SELECT name FROM user WHERE phone=?",
                (phoneN,)
            )
            user = cursor.fetchone()
            if user is None:
                messagebox.showwarning(
                    "خطا",
                    "کاربری با این شماره پیدا نشد!"
                )
                return
            user_name = user[0]

            # تایید حذف
            answer = messagebox.askyesno(
                "تایید حذف",
                f"آیا مطمئن هستید کاربر {user_name} حذف شود؟\nتمام اطلاعات او پاک خواهد شد."
            )

            if answer:

                # حذف ورزش های کاربر
                cursor.execute( """DELETE FROM varzeshs WHERE user_name=?""",(user_name,))

                # حذف اشتراک کاربر
                cursor.execute("""DELETE FROM eshterak WHERE user_id=?""", (phoneN,))

                # حذف فاکتورهای کاربر
                cursor.execute( """ DELETE FROM faktor WHERE user_name=?   """, (user_name,))

                # حذف خود کاربر
                cursor.execute(""" DELETE FROM user WHERE phone=? """, (phoneN,))

                conn.commit()

                messagebox.showinfo( "موفق", "کاربر و تمام اطلاعات مربوط به او حذف شد.")

                delete_user_window.destroy()

        except Exception as e:

            conn.rollback()

            messagebox.showerror( "خطای دیتابیس",str(e))
    delete_user_window = Toplevel(window)
    delete_user_window.title(  "حذف کاربر" )
    delete_user_window.geometry("300x150")

    Label(delete_user_window,text="شماره تلفن کاربر").pack(pady=5)

    entry_uesr_phone = Entry(delete_user_window)

    entry_uesr_phone.pack(pady=5)

    Button(delete_user_window,text="حذف کامل کاربر", command=remove_user ).pack(pady=10)


# ویرایش کاربر
def edit_user():

    def update_user():

        phone_id = edit_phone_id.get().strip()
        name = edit_name.get().strip()
        phone = edit_phone.get().strip()

        if not phone_id or not name or not phone:
            messagebox.showwarning("خطا","لطفاً همه فیلدها را پر کنید!")
            return
        try:
            # گرفتن نام قبلی کاربر
            cursor.execute( "SELECT name FROM user WHERE phone=?",(phone_id,))

            old_user = cursor.fetchone()

            if old_user is None:
                messagebox.showwarning( "خطا", "این شماره تلفن یافت نشد!")
                return

            old_name = old_user[0]

            # ویرایش کاربر
            cursor.execute( """UPDATE user SET name=?, phone=?  WHERE phone=?""",(name, phone, phone_id))

            # اگر نام تغییر کرده بود، ورزش‌ها هم تغییر کنند
            cursor.execute( """  UPDATE varzeshs SET user_name=? WHERE user_name=?""",(name, old_name) )

            conn.commit()

            messagebox.showinfo("موفق", "کاربر با موفقیت ویرایش شد!")

            edit_user_window.destroy()

        except Exception as e:
            messagebox.showerror( "خطای دیتابیس", str(e))

    edit_user_window = Toplevel(window)
    edit_user_window.title("ویرایش کاربر")
    edit_user_window.geometry("300x300")

    Label( edit_user_window, text="شماره تلفن قبلی").pack(pady=5)

    edit_phone_id = Entry(edit_user_window)
    edit_phone_id.pack(pady=5)

    Label(edit_user_window,text="نام جدید"  ).pack(pady=5)

    edit_name = Entry(edit_user_window)
    edit_name.pack(pady=5)


    Label(edit_user_window,text="شماره تماس جدید").pack(pady=5)

    edit_phone = Entry(edit_user_window)
    edit_phone.pack(pady=5)

    Button(edit_user_window, text="ویرایش",command=update_user).pack(pady=10)

#اضافه کردن ورزش
data_varzesh = {
    "فیتنس": {"روز": "شنبه و دوشنبه", "هزینه": "500,000"},
    "ایروبیک": {"روز": "یکشنبه و سه‌شنبه", "هزینه": "450,000"},
    "یوگا": {"روز": "چهارشنبه", "هزینه": "600,000"},
    "زومبا": {"روز": "پنجشنبه", "هزینه": "400,000"},
    "پیلاتس": {"روز": "شنبه و چهارشنبه", "هزینه": "550,000"},
    "بدنسازی": {"روز": "هر روز", "هزینه": "800,000"}
}

def add_varzesh():

    def update_fields(event):

        selected = enter_name.get()

        if selected in data_varzesh:
            enter_day.delete(0, END)
            enter_day.insert(
                0,
                data_varzesh[selected]["روز"]
            )

            enter_ghimat.delete(0, END)
            enter_ghimat.insert(
                0,
                data_varzesh[selected]["هزینه"]
            )
    def save_data():
        name = enter_name.get().strip()
        day = enter_day.get().strip()
        ghimatt = enter_ghimat.get().strip()
        user_name = enter_user_name.get().strip()

        if (
            name == "" or
            day == "" or
            ghimatt == "" or
            user_name == ""
        ):

            messagebox.showwarning("خطا",  "لطفاً همه فیلدها را پر کنید!" )
            return
        try:
            # بررسی وجود کاربر
            cursor.execute(
                "SELECT * FROM user WHERE name=?", (user_name,))
            user = cursor.fetchone()

            if user is None:
                messagebox.showwarning( "خطا", "این کاربر وجود ندارد.")

                return
            # جلوگیری از ثبت ورزش تکراری
            cursor.execute(  """ SELECT * FROM varzeshs  WHERE user_name=? AND name=? """, (user_name,name))

            if cursor.fetchone():
                messagebox.showwarning(  "خطا", "این کاربر قبلاً این ورزش را انتخاب کرده است.")
                return

            # ثبت ورزش
            cursor.execute( """ INSERT INTO varzeshs(name,day,ghimat, user_name)
                VALUES (?, ?, ?, ?)""",(name, day,ghimatt,user_name))
            conn.commit()
            messagebox.showinfo( "موفق", f"ورزش '{name}' برای '{user_name}' ثبت شد.")
            add_varzesh_window.destroy()

        except Exception as e:
            messagebox.showerror(  "خطای دیتابیس", str(e))
    # ---------------- UI ----------------

    add_varzesh_window = Toplevel(window)
    add_varzesh_window.title( "افزودن ورزش")
    add_varzesh_window.geometry( "300x420")

    Label(add_varzesh_window,text="نوع ورزش را انتخاب کنید").pack(pady=5)

    enter_name = ttk.Combobox( add_varzesh_window, values=list(data_varzesh.keys()),state="readonly")
    enter_name.pack(pady=5)

    enter_name.bind( "<<ComboboxSelected>>",update_fields)

    Label(add_varzesh_window,text="روز کلاس").pack(pady=5)

    enter_day = Entry(add_varzesh_window)
    enter_day.pack(pady=5)

    Label(add_varzesh_window,text="هزینه کلاس" ).pack(pady=5)

    enter_ghimat = Entry(add_varzesh_window)
    enter_ghimat.pack(pady=5)

    Label( add_varzesh_window,text="نام کاربر").pack(pady=5)

    enter_user_name = Entry(add_varzesh_window)
    enter_user_name.pack(pady=5)

    Button(add_varzesh_window,text="ثبت نهایی",command=save_data).pack(pady=15)
#___________________________________________________________________


# حذف کردن ورزش
def delete_varzesh():

    def load_varzesh():

        user_name = enter_user_name.get().strip()
        if user_name == "":
            messagebox.showwarning( "خطا", "نام کاربر را وارد کنید.")
            return

        cursor.execute(
            """ SELECT name FROM varzeshs WHERE user_name=? """, (user_name,))
        rows = cursor.fetchall()
        if not rows:
            messagebox.showwarning("خطا","برای این کاربر ورزشی ثبت نشده است." )
            return
        sports = [row[0] for row in rows]
        combo_varzesh["values"] = sports
        combo_varzesh.current(0)
    def remove_varzesh():
        user_name = enter_user_name.get().strip()
        sport_name = combo_varzesh.get().strip()
        if user_name == "" or sport_name == "":
            messagebox.showwarning( "خطا", "نام کاربر و ورزش را انتخاب کنید." )
            return
        answer = messagebox.askyesno(  "تایید حذف",f"آیا ورزش '{sport_name}' برای کاربر '{user_name}' حذف شود؟" )

        if answer:
            cursor.execute( """ DELETE FROM varzeshs WHERE user_name=? AND name=?""", ( user_name, sport_name) )

            conn.commit()

            if cursor.rowcount > 0:
                messagebox.showinfo( "موفق","ورزش با موفقیت حذف شد.")
                delete_varzesh_window.destroy()
            else:
                messagebox.showwarning("خطا","اطلاعاتی برای حذف پیدا نشد.")
    # پنجره
    delete_varzesh_window = Toplevel(window)
    delete_varzesh_window.title( "حذف ورزش" )
    delete_varzesh_window.geometry( "350x250")

    Label(delete_varzesh_window,text="نام کاربر").pack(pady=5)
    enter_user_name = Entry( delete_varzesh_window)
    enter_user_name.pack(pady=5)

    Button( delete_varzesh_window,text="نمایش ورزش‌ها",command=load_varzesh).pack(pady=5)

    Label( delete_varzesh_window,text="انتخاب ورزش").pack(pady=5)

    combo_varzesh = ttk.Combobox(delete_varzesh_window, state="readonly")

    combo_varzesh.pack(pady=5)

    Button(delete_varzesh_window,text="حذف ورزش",command=remove_varzesh ).pack(pady=15)

# ویرایش ورزش
def edit_verzesh():

    data_varzesh = {
        "فیتنس": 500000,
        "ایروبیک": 40000,
        "یوگا": 600000,
        "زومبا": 400000,
        "پیلاتس": 550000,
        "بدنسازی": 800000
    }

    def load_user_varzesh():
        user_name = user_entry.get()

        if user_name == "":
            messagebox.showwarning("خطا", "نام کاربر را وارد کنید")
            return

        cursor.execute("SELECT name FROM varzeshs WHERE user_name=?", (user_name,))

        result = cursor.fetchall()

        if not result:
            messagebox.showwarning("خطا","برای این کاربر ورزشی ثبت نشده است")
            return

        user_varzesh = [row[0] for row in result]
        old_varzesh["values"] = user_varzesh
        old_varzesh.config(state="readonly")
        messagebox.showinfo( "موفق", "ورزش‌های کاربر نمایش داده شد")

    def update_price(event):
        selected = new_varzesh.get()
        if selected in data_varzesh:
            price_entry.delete(0, END)
            price_entry.insert(0, str(data_varzesh[selected]))

    def update_verzesh():
        user_name = user_entry.get()
        old_name = old_varzesh.get()
        new_name = new_varzesh.get()
        price = price_entry.get()

        if user_name and old_name and new_name and price:
            cursor.execute( """ UPDATE varzeshs SET name=?, ghimat=? WHERE user_name=? AND name=?""", (new_name, price, user_name, old_name))

            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showwarning("خطا","ورزش پیدا نشد")
            else:
                messagebox.showinfo( "موفق","ورزش با موفقیت ویرایش شد")
                edit_varzesh_window.destroy()
        else:
            messagebox.showwarning("خطا","همه فیلدها را پر کنید" )

    # پنجره
    edit_varzesh_window = Toplevel(window)
    edit_varzesh_window.title("ویرایش ورزش")
    edit_varzesh_window.geometry("320x450")

    # نام کاربر
    Label(edit_varzesh_window,text="نام کاربر").pack(pady=5)

    user_entry = Entry(edit_varzesh_window)
    user_entry.pack(pady=5)

    Button(edit_varzesh_window, text="نمایش ورزش‌های کاربر", command=load_user_varzesh).pack(pady=10)
    # ورزش فعلی
    Label(edit_varzesh_window,text="ورزش فعلی").pack(pady=5)

    old_varzesh = ttk.Combobox( edit_varzesh_window, state="disabled")
    old_varzesh.pack(pady=5)

    # ورزش جدید
    Label(edit_varzesh_window,text="ورزش جدید" ).pack(pady=5)

    new_varzesh = ttk.Combobox(
        edit_varzesh_window,
        values=list(data_varzesh.keys()),
        state="readonly")
    new_varzesh.pack(pady=5)

    # قیمت
    Label(edit_varzesh_window,text="قیمت").pack(pady=5)

    price_entry = Entry(edit_varzesh_window)
    price_entry.pack(pady=5)

    new_varzesh.bind("<<ComboboxSelected>>",  update_price)

    Button(edit_varzesh_window,text="ویرایش",command=update_verzesh).pack(pady=15)

# برنامه غذایی
def nutrition_plan():

    def generate_plan():
        try:
            age = int(entry_age.get())
            ghad = int(entry_height.get())
            vazn = int(entry_weight.get())

        except ValueError:
            messagebox.showwarning( "خطا","لطفاً سن، قد و وزن را فقط عدد وارد کنید.")
            return
        user_id = entry_user.get().strip()

        if user_id == "":
            messagebox.showwarning( "خطا","لطفاً شماره کاربر را وارد کنید.")
            return

        # بررسی اشتراک فعال
        cursor.execute("""SELECT * FROM eshterak WHERE user_id = ? AND status = 'active' """, (user_id,))
        sub = cursor.fetchone()

        if sub is None:
            result_label.config(text="🔒 برنامه غذایی قفل است\n\nبرای مشاهده برنامه غذایی لطفاً اشتراک تهیه کنید.")

            messagebox.showwarning("نیاز به اشتراک","اشتراک فعالی برای این کاربر یافت نشد.")
            return

        goal = goal_var.get()
        plans = {
            "افزایش وزن":
            """
برنامه افزایش وزن

:صبحانه
تخم مرغ + نان + شیر

:میان وعده
مغزها و میوه

:ناهار
برنج + گوشت + سالاد

:شام
پروتئین + سبزیجات
""",

 "کاهش وزن":
            """
برنامه کاهش وزن

:صبحانه
تخم مرغ + سبزیجات

:میان وعده
میوه

:ناهار
غذای کم چرب

:شام
سالاد و پروتئین
""",

  "حفظ وزن":
            """
برنامه حفظ وزن

رژیم متعادل شامل
پروتئین، کربوهیدرات و سبزیجات
"""
        }
        plan = plans.get(goal, "برنامه‌ای وجود ندارد")

        result_label.config(text=plan)

        try:

            cursor.execute("""CREATE TABLE IF NOT EXISTS taghzeh(id INTEGER PRIMARY KEY AUTOINCREMENT,age INTEGER,ghad INTEGER, vazn INTEGER, plan TEXT) """)

            cursor.execute("""INSERT INTO taghzeh (age, ghad, vazn, plan)VALUES (?, ?, ?, ?) """, ( age,ghad,vazn,plan ))

            conn.commit()

        except Exception as e:
            messagebox.showerror( "خطای دیتابیس",str(e))

    # پنجره
    nut_window = Toplevel(window)
    nut_window.title("برنامه غذایی")
    nut_window.geometry("420x600")

    Label(nut_window,text="شماره کاربر").pack(pady=5)

    entry_user = Entry(nut_window)
    entry_user.pack()

    Label(nut_window,text="سن" ).pack(pady=5)

    entry_age = Entry(nut_window)
    entry_age.pack()

    Label(nut_window,text="قد").pack(pady=5)

    entry_height = Entry(nut_window)
    entry_height.pack()

    Label(nut_window,text="وزن" ).pack(pady=5)

    entry_weight = Entry(nut_window)
    entry_weight.pack()

    Label(nut_window,text="هدف").pack(pady=5)

    goal_var = ttk.Combobox(
        nut_window,
        values=[
            "افزایش وزن",
            "کاهش وزن",
            "حفظ وزن"
        ],
        state="readonly"
    )

    goal_var.current(0)
    goal_var.pack()

    Button(nut_window,text="ساخت برنامه", command=generate_plan ).pack(pady=15)

    result_label = Label(nut_window,text="", wraplength=350, justify="right")
    result_label.pack(pady=10)

# خرید اشتراک
def buy_subscription():

    def save_subscription():

        from datetime import date, timedelta

        phone = entry_phone.get().strip()

        if phone == "":
            messagebox.showwarning( "خطا","شماره کاربر را وارد کنید" )
            return

        # بررسی وجود کاربر
        cursor.execute(  "SELECT * FROM user WHERE phone=?", (phone,))
        user = cursor.fetchone()

        if user is None:
            messagebox.showerror("خطا", "این شماره در جدول کاربران وجود ندارد")
            return

        sub_type = combo_type.get()
        modat = combo_modat.get()

        # قیمت پایه
        if sub_type == "رایگان":
            price_base = 0
        elif sub_type == "حرفه ای":
            price_base = 200000
        elif sub_type == "CRP":
            price_base = 400000
        elif sub_type == "VIP":
            price_base = 600000
        else:
            price_base = 0

        # مدت اشتراک
        if modat == "1 ماه":
            days = 30
            multiplier = 1
        elif modat == "3 ماه":
            days = 90
            multiplier = 2.8
        elif modat == "6 ماه":
            days = 180
            multiplier = 5
        elif modat == "12 ماه":
            days = 365
            multiplier = 9
        else:
            days = 30
            multiplier = 1
        price = int(price_base * multiplier)
        start_date = date.today()
        end_date = start_date + timedelta(days=days)

        try:
            # حذف اشتراک قبلی کاربر
            cursor.execute( "DELETE FROM eshterak WHERE user_id=?", (phone,))

            # ثبت اشتراک جدید
            cursor.execute("""INSERT INTO eshterak( user_id,type,modat,ghimat,start_date,end_date,status)
                VALUES (?, ?, ?, ?, ?, ?, ?) """,( phone, sub_type,modat,price,str(start_date),str(end_date),"active"))

            conn.commit()
            messagebox.showinfo( "موفق",f"""اشتراک با موفقیت ثبت شد
نوع: {sub_type}
مدت: {modat}
مبلغ: {price:,} تومان
                """)
            sub_window.destroy()
        except Exception as e:
            messagebox.showerror("خطای دیتابیس",str(e))
    # پنجره خرید اشتراک
    sub_window = Toplevel(window)
    sub_window.title("خرید اشتراک")
    sub_window.geometry("350x320")

    Label(sub_window,text="شماره تلفن کاربر").pack(pady=5)

    entry_phone = Entry(sub_window)
    entry_phone.pack()

    Label( sub_window,text="نوع اشتراک").pack(pady=5)

    combo_type = ttk.Combobox(
        sub_window,
        values=[
            "رایگان",
            "حرفه ای",
            "CRP",
            "VIP"
        ],
        state="readonly")

    combo_type.current(0)
    combo_type.pack()

    Label(sub_window,text="مدت اشتراک" ).pack(pady=5)

    combo_modat = ttk.Combobox(
        sub_window,
        values=[
            "1 ماه",
            "3 ماه",
            "6 ماه",
            "12 ماه"
        ],
        state="readonly"
    )
    combo_modat.current(0)
    combo_modat.pack()

    Button( sub_window,text="خرید اشتراک",command=save_subscription).pack(pady=20)

#فاکتور
def add_faktor():

    def load_user_info():

        phone = entry_phone.get().strip()

        if not phone:
            messagebox.showwarning("خطا", "شماره را وارد کنید")
            return

        cursor.execute("""  SELECT id, name FROM user WHERE phone=? """, (phone,))

        user = cursor.fetchone()

        if not user:
            label_info.config(text="فاکتوری برای این کاربر پیدا نشد")
            return

        user_id = user[0]
        name = user[1]

        # گرفتن ورزش های کاربر
        cursor.execute(""" SELECT name, ghimat  FROM varzeshs  WHERE user_name=? """, (name,))

        sports = cursor.fetchall()
        if not sports:
            sport_text = "هیچ ورزشی انتخاب نشده"
        else:
            sport_text = ""
            for sport in sports:
                sport_text += f"{sport[0]} - {sport[1]} تومان\n"

        label_info.config( text=f"""
نام: {name}
شماره: {phone}
ورزش‌ها:
{sport_text}
""")

        entry_phone.user_data = {
            "id": user_id,
            "name": name,
            "phone": phone
        }

    def save_faktor():

        if not hasattr(entry_phone, "user_data"):
            messagebox.showerror( "خطا",  "ابتدا اطلاعات کاربر را نمایش دهید")
            return

        user_data = entry_phone.user_data
        name = user_data["name"]
        cursor.execute("""  SELECT name, ghimat FROM varzeshs WHERE user_name = ?""", (name,))
        rows = cursor.fetchall()

        if not rows:
            messagebox.showwarning( "خطا", "این کاربر هیچ ورزشی انتخاب نکرده است")
            return

        total = 0
        ghimat_list = []
        for sport_name, price in rows:
            try:
                price = int(
                    str(price)
                    .replace(",", "")
                    .strip())
            except:
                price = 0
            total += price
            ghimat_list.append(str(price))
        tedad_varzesh = len(rows)
        ghimat_text = " , ".join(ghimat_list)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""INSERT INTO faktor(user_name,content,date,ghimat,meghdar,total)
                               VALUES (?, ?, ?, ?, ?, ?)  """, (name, "فاکتور ورزشگاه سوگند", now,ghimat_text,tedad_varzesh, total))

        conn.commit()
        faktor_id = cursor.lastrowid
        messagebox.showinfo( "موفق",f""" فاکتور ثبت شد
    شماره فاکتور: {faktor_id}
    نام کاربر: {name}
    تعداد ورزش: {tedad_varzesh}
    جمع کل: {total:,} تومان
    """)
        faktor_window.destroy()

    # ---------- UI ----------
    global faktor_window
    faktor_window = Toplevel(window)
    faktor_window.title("فاکتور اتوماتیک")
    faktor_window.geometry("400x500")

    Label(faktor_window,text="شماره کاربر" ).pack(pady=5)
    entry_phone = Entry(faktor_window)
    entry_phone.pack()

    Button(faktor_window,text="نمایش اطلاعات",command=load_user_info).pack(pady=10)

    label_info = Label(faktor_window,text="",justify="right", fg="blue")
    label_info.pack(pady=15)

    Button(faktor_window,text="ثبت فاکتور", command=save_faktor  ).pack(pady=15)
#________________________________________________

#راهنما
from tkinter import *
from tkinter.scrolledtext import ScrolledText

def rahnama():

    help_window = Toplevel(window)
    help_window.title("راهنمای برنامه")
    help_window.geometry("650x500")
    help_window.resizable(False, False)

    Label(
        help_window,
        text="راهنمای مدیریت باشگاه ورزشی سوگند",
        font=("B Titr", 16)
    ).pack(pady=10)

    result_text = ScrolledText(
        help_window,
        font=("B Nazanin", 14),
        wrap="word"
    )
    result_text.pack(
        padx=10,
        pady=10,
        fill="both",
        expand=True
    )

    help_text = """
راهنمای استفاده از برنامه مدیریت باشگاه ورزشی سوگند                       

به برنامه مدیریت باشگاه ورزشی سوگند خوش آمدید.  این برنامه به منظور مدیریت اطلاعات ورزشکاران، اشتراک‌ها، ورزش‌های انتخابی و برنامه‌های غذایی طراحی شده است.

 ثبت نام ورزشکار
برای استفاده از امکانات برنامه، ابتدا از بخش «کاربری» اطلاعات ورزشکار شامل نام، نام خانوادگی، شماره موبایل و سایر اطلاعات مورد نیاز را ثبت نمایید.


 انتخاب ورزش
پس از ثبت نام، می‌توانید یک یا چند ورزش را برای ورزشکار انتخاب و ثبت کنید. هزینه هر ورزش به صورت خودکار در سیستم محاسبه و ذخیره می‌شود.


 مدیریت اشتراک
برای استفاده از خدمات باشگاه، لازم است برای ورزشکار اشتراک ثبت شود. امکان ثبت و مشاهده نوع اشتراک و تاریخ پایان آن در سامانه وجود دارد.

 برنامه غذایی
پس از ثبت اشتراک، می‌توانید با وارد کردن اطلاعاتی مانند سن، قد و وزن، برنامه غذایی مناسب را دریافت کنید.
نکته: شما با نداشتن اشتراک نمیتوانید از این برنامه غذایی استفاده مکنید.

 پنل کاربری
ورزشکاران می‌توانند با وارد کردن شماره موبایل خود وارد پنل کاربری شوند و اطلاعاتی مانند ورزش‌های انتخابی، تعداد ورزش‌ها، هزینه‌ها، نوع اشتراک و تاریخ پایان اشتراک را مشاهده کنند.

 ویرایش اطلاعات
در صورت نیاز می‌توانید اطلاعات ثبت‌شده ورزشکاران را ویرایش و به‌روزرسانی کنید.

 حذف ورزشکار
در صورت حذف یک ورزشکار، تمامی اطلاعات وابسته به وی از جمله ورزش‌های انتخابی، اشتراک‌ها و سایر اطلاعات ثبت‌ شده نیز از سامانه حذف خواهد شد.

نکات مهم:
• شماره موبایل هر ورزشکار باید به درستی وارد شود.
• فیلدهای عددی مانند سن، قد و وزن باید فقط شامل عدد باشند.
• قبل از ثبت اطلاعات، از صحت داده‌های واردشده اطمینان حاصل کنید.
• برای دریافت برنامه غذایی، ثبت اشتراک الزامی است.

با تشکر از مدیریت باشگاه ورزشی سوگند

طراح برنامه: نرجس رحیمی جزئی
"""

    result_text.insert("1.0", "\u200F" + help_text)

    result_text.tag_add("right", "1.0", "end")
    result_text.tag_configure(
        "right",
        justify="right",
        font=("B Nazanin", 14)
    )

    result_text.config(state="disabled")

    Button(
        help_window,
        text="بستن",
        command=help_window.destroy,
        font=("B Nazanin", 12, "bold"),
        bg="red",
        fg="white"
    ).pack(pady=10)


#منو های و ایجاد کلید
# عکس بگراند
bg_image = PhotoImage(file="400.png")
bg_label = Label(window, image=bg_image,width=400, height=400)
bg_label.pack(fill=BOTH,expand=True,side=TOP)

#منو کاربر جدید
menubar = Menu(window)
window.configure(menu=menubar)
user_menu = Menu(menubar,tearoff=0)
menubar.add_command(label="پنل کاربری",command=user_panel)
user_menu.add_command(label="افزودن کاربرجدید",command=create_user)
user_menu.add_command(label="ویرایش کاربر",command=edit_user)
user_menu.add_command(label="حذف کاربر",command=delete_user)
menubar.add_cascade(label= "کاربر" , menu=user_menu)

#برای ورزش
var_menu = Menu(menubar,tearoff=0)
var_menu.add_command(label="افزودن ورزش جدید", command=add_varzesh)
var_menu.add_command(label="ویرایش ورزش ", command=edit_verzesh)
var_menu.add_command(label="حذف ورزش", command=delete_varzesh)
menubar.add_cascade(label= "ورزش " , menu=var_menu)

#برنامه غذایی
nutrition_menu = Menu(menubar, tearoff=0)
nutrition_menu.add_command(label="برنامه غذایی", command=nutrition_plan)
menubar.add_cascade(label="برنامه غذایی",menu=nutrition_menu)

#خرید اشتراک
subscription_menu = Menu(menubar, tearoff=0)
subscription_menu.add_command(label="خرید اشتراک",command=buy_subscription)
menubar.add_cascade(label="اشتراک",menu=subscription_menu)

#برای فاکتور
faktor_menu = Menu(menubar,tearoff=0)
faktor_menu.add_command(label="ایجاد فاکتور",command=add_faktor)
menubar.add_cascade(label="فاکتور",menu=faktor_menu)


#راهنما
help_menu = Menu(menubar, tearoff=0)
help_menu.add_command(label="راهنمای استفاده",command=rahnama)
menubar.add_cascade(label="راهنما",menu=help_menu)


window.mainloop()