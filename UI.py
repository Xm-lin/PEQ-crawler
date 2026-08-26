import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import MYcrawler
import webbrowser

# 初始化 CustomTkinter 設定
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

datas = []


class App(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("歷屆試題查詢")
    self.resizable(False, False)

    # 視窗置中設定
    window_width = 340
    window_height = 560
    screen_width = self.winfo_screenwidth()
    screen_height = self.winfo_screenheight()
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)
    self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

    # 建立頂端選單
    self.setup_menu()

    # 顯示載入畫面
    self.show_loading_frame()

    # 非同步在背景載入年份
    self.after(100, self.async_load_years)

  def setup_menu(self):
    menu = tk.Menu(self)
    setting_menu = tk.Menu(menu, tearoff=False)
    setting_menu.add_command(
        label="修改檔案儲存路徑", command=MYcrawler.choose_path
    )
    menu.add_cascade(label="設定", menu=setting_menu)
    self.configure(menu=menu)

  def show_loading_frame(self):
    """顯示初始化載入畫面"""
    self.loading_frame = ctk.CTkFrame(self, fg_color="transparent")
    self.loading_frame.pack(fill="both", expand=True)

    self.loading_label = ctk.CTkLabel(
        self.loading_frame, text="載入年份列表中....", font=ctk.CTkFont(size=14)
    )
    self.loading_label.pack(expand=True)

  def async_load_years(self):
    """在背景執行緒抓取年份，避免主執行緒凍結"""

    def task():
      try:
        years = MYcrawler.get_years()
        # 切回主執行緒更新 UI
        self.after(0, lambda: self.show_main_frame(years))
      except Exception as e:
        self.after(
            0,
            lambda: [
                messagebox.showerror("錯誤", f"初始化失敗:\n{e}"),
                self.destroy(),
                sys.exit(),
            ],
        )

    threading.Thread(target=task, daemon=True).start()

  def show_main_frame(self, years):
    """移除載入畫面，建立主功能介面"""
    self.loading_frame.destroy()

    # 項目選擇區塊
    select = ctk.CTkFrame(self)
    select.pack(fill="x", padx=15, pady=15)

    sub_lab = ctk.CTkLabel(
        select, text="選擇科目:", font=ctk.CTkFont(size=12, weight="bold")
    )
    sub_lab.pack(anchor="w", padx=10, pady=(10, 2))
    subjects = ["國文", "國寫", "英文", "數學", "社會", "自然"]
    sub_box = ctk.CTkComboBox(select, values=subjects, width=280, state="readonly")
    sub_box.set(subjects[0])
    sub_box.pack(padx=10, pady=(0, 10))

    year_lab = ctk.CTkLabel(
        select, text="選擇年份:", font=ctk.CTkFont(size=12, weight="bold")
    )
    year_lab.pack(anchor="w", padx=10, pady=(5, 2))
    year_box = ctk.CTkComboBox(select, values=years, width=280, state="readonly")
    if years:
      year_box.set(years[0])
    year_box.pack(padx=10, pady=(0, 15))

    # 查詢按鈕
    confirm_btn = ctk.CTkButton(
        select,
        text="查詢",
        width=280,
        font=ctk.CTkFont(size=12, weight="bold"),
        command=lambda: self.get_data(
            sub_box.get(), year_box.get(), confirm_btn, data_frame
        ),
    )
    confirm_btn.pack(padx=10, pady=(0, 15))

    # 結果顯示捲動區塊
    data_frame = ctk.CTkScrollableFrame(
        self,
        label_text="查詢結果",
        label_font=ctk.CTkFont(size=12, weight="bold"),
    )
    data_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    self.data_frame = data_frame

  def get_data(self, subject, year, btn, scrollable_frame):
    if not subject or not year:
      messagebox.showwarning("提示", "請務必選擇科目與年份！")
      return

    btn.configure(state="disabled", text="查詢中...")

    def run_crawler():
      global datas
      success = False
      try:
        datas = MYcrawler.get_link(subject, year)
        success = True
      except Exception as e:
        messagebox.showerror("錯誤", f"爬取失敗: {str(e)}")
      finally:
        btn.configure(state="normal", text="查詢")
        if success:
          self.after(
              0, lambda: self.update_ui_results(scrollable_frame, subject, year)
          )

    threading.Thread(target=run_crawler, daemon=True).start()

  def update_ui_results(self, scrollable_frame, subject, year):
    global datas

    # 清除舊結果
    for widget in scrollable_frame.winfo_children():
      widget.destroy()

    if not datas:
      messagebox.showinfo("提示", "查無資料！")
      return

    header_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    header_frame.pack(fill="x", padx=5, pady=5)

    result_text = ctk.CTkLabel(
        header_frame, text="查詢結果", font=ctk.CTkFont(size=12, weight="bold")
    )
    result_text.pack(side="left", padx=5)

    dl_text = ctk.CTkLabel(
        header_frame, text="下載", font=ctk.CTkFont(size=12, weight="bold")
    )
    dl_text.pack(side="right", padx=15)

    for data in datas:
      row_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
      row_frame.pack(fill="x", padx=5, pady=3)

      name_btn = ctk.CTkButton(
          row_frame,
          text=data[0],
          anchor="w",
          fg_color="transparent",
          text_color=("#1f6aa5", "#3786d1"),
          hover_color=("gray85", "gray25"),
          font=ctk.CTkFont(size=11),
          command=lambda url=data[1]: webbrowser.open(url),
      )
      name_btn.pack(side="left", fill="x", expand=True)

      download_btn = ctk.CTkButton(
          row_frame,
          text="下載",
          width=50,
          height=24,
          font=ctk.CTkFont(size=11),
          command=lambda url=data[1], title=f"{year}年{subject}{data[0]}": (
              threading.Thread(
                  target=MYcrawler.download_pdf, args=(url, title), daemon=True
              ).start()
          ),
      )
      download_btn.pack(side="right", padx=5)


if __name__ == "__main__":
  app = App()
  app.mainloop()