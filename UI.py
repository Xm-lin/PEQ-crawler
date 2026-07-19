import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import MYcrawler 
import webbrowser
import tkmacosx,os,sys
#色彩定義 
COLOR_BG = "#F8F9FA"         
COLOR_TEXT = "#495057"       
COLOR_BTN = "#1D3557"        
COLOR_BTN_TXT = "#FFFFFF"   
COLOR_LINK = "#457B9D"       
COLOR_LINK_HOVER = "#128D2D"
os.system("pip install requests beautifulsoup4 playwright tkmacosx ")

datas = []
class LoadingWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("系統初始化")

        # 1. 定義你想要的視窗寬度與高度
        window_width = 300
        window_height = 150

        # 2. 取得使用者螢幕的解析度（寬與高）
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 3. 計算讓視窗置中的左上角 (x, y) 座標
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)

        # 4. 設定視窗大小與置中位置，格式為: 寬x高+X座標+Y座標
        self.root.geometry(
            f"{window_width}x{window_height}+{center_x}+{center_y}"
        )

        # 固定視窗大小，禁止使用者縮放
        self.root.resizable(False, False)

        # 攔截關閉按鈕
        self.root.protocol("WM_DELETE_WINDOW", self.on_cancel)

        # 狀態文字標籤
        self.label = tk.Label(
            self.root, text="準備中...", font=("Arial", 12), pady=20
        )
        self.label.pack()

        # 取消按鈕
        self.cancel_btn = tk.Button(
            self.root, text="Cancel", command=self.on_cancel, width=10
        )
        self.cancel_btn.pack(pady=10)

        self.years = None
        self.is_cancelled = False

        # 視窗載入完成後，立刻依序執行
        self.root.after(100, self.run_steps)

    def on_cancel(self):
        """按下 Cancel 時跳出確認畫面"""
        # showwarning 或 askokcancel 都可以，這裡用 askokcancel 最符合「是否離開 + 確認按鈕」
        confirm = messagebox.askokcancel("提示", "是否離開？")
        if confirm:
            self.is_cancelled = True
            self.root.destroy()
            sys.exit()  # 完全結束整個 Python 程式

    def update_status(self, text):
        """更新文字並強制刷新畫面，避免視窗凍結"""
        if self.is_cancelled:
            return
        self.label.config(text=text)
        self.root.update()

    def run_steps(self):
        try:
            # ---------------------------------------------
            # 1. 載入年份列表中....
            # ---------------------------------------------
            self.update_status("載入年份列表中....")
            self.root.after(500)  # 微調延遲，讓使用者看得到字眼切換

            # 實際呼叫你的爬蟲功能取得年份
            self.years = MYcrawler.get_years()

            if self.is_cancelled:
                return

            # ---------------------------------------------
            # 2. 載入成功
            # ---------------------------------------------
            self.update_status("載入成功！")
            self.root.after(1000)  # 讓「載入成功」在畫面上停個 1 秒鐘

            if self.is_cancelled:
                return

            # ---------------------------------------------
            # 3. 正在開啟 crawler...
            # ---------------------------------------------
            self.update_status("正在開啟 crawler...")
            self.root.after(1000)  # 停頓一下，隨後進入主程式

            if self.is_cancelled:
                return

            # 關閉讀取視窗
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("錯誤", f"初始化失敗:\n{e}")
            self.root.destroy()
            sys.exit()

def update_ui(screen, subject, year):
    global datas
    
    # 檢查是否已經存在舊的資料容器，有的話先刪除，避免重複疊加
    if hasattr(update_ui, "data_frame"):
        update_ui.data_frame.destroy()
        
    if not datas:
        messagebox.showinfo("提示", "查無資料！")
        return

    # 建立一個新的 LabelFrame 來放結果，套用深碳灰文字與淺灰白背景
    data_frame = tk.LabelFrame(
        screen, text=f"{year}年{subject}科歷屆", 
        fg=COLOR_TEXT, bg=COLOR_BG, font=("Helvetica", 10, "bold")
    )
    data_frame.grid(row=1, column=0, sticky='NSEW', padx=15, pady=10)
    
    # 紀錄這個 frame，方便下次查詢時可以刪除舊的
    update_ui.data_frame = data_frame
    result_text = tk.Label(data_frame,text="查詢結果",font=("Helvetica", 10, "bold"))
    result_text.grid(column=0, row=0, sticky="W", padx=10, pady=6)
    dl_text = tk.Label(data_frame,text="下載",font=("Helvetica", 10, "bold"))
    dl_text.grid(column=1, row=0, sticky="W", padx=10, pady=6)
    # 將資料動態生成 Label 顯示出來
    r = 1
    for data in datas:
        name = tk.Label(
            data_frame, text=data[0], fg=COLOR_LINK, bg=COLOR_BG, 
            cursor="hand2", font=("Helvetica", 10)
        )
        name.grid(column=0, row=r, sticky="W", padx=10, pady=6)
        
        # 綁定點擊事件
        name.bind("<Button-1>", lambda e, url=data[1]: webbrowser.open(url))
        # 互動反饋：滑鼠移入（Hover）變深色並加底線
        name.bind("<Enter>", lambda e, lbl=name: lbl.config(fg=COLOR_LINK_HOVER, font=("Helvetica", 10, "underline")))
        # 互動反饋：滑鼠移出（Leave）恢復原狀
        name.bind("<Leave>", lambda e, lbl=name: lbl.config(fg=COLOR_LINK, font=("Helvetica", 10)))

        Download = tk.Label(
            data_frame, text="下載", fg=COLOR_LINK, bg=COLOR_BG, 
            cursor="hand2", font=("Helvetica", 10)
        )
        Download.grid(column=1, row=r, sticky="W", padx=10, pady=6)

        # 綁定點擊事件
        # 當點擊 [ 下載 ] 時，觸發我們剛剛寫好的背景下載函式
        Download.bind("<Button-1>", lambda e, url=data[1], title=f"{year}年{subject}{data[0]}": 
            threading.Thread(
                target=MYcrawler.download_pdf, 
                args=(url, title), 
                daemon=True
            ).start()
        )
        # 互動反饋：滑鼠移入（Hover）變深色並加底線
        Download.bind("<Enter>", lambda e, lbl=Download: lbl.config(fg=COLOR_LINK_HOVER, font=("Helvetica", 10, "underline")))
        # 互動反饋：滑鼠移出（Leave）恢復原狀
        Download.bind("<Leave>", lambda e, lbl=Download: lbl.config(fg=COLOR_LINK, font=("Helvetica", 10)))
        r = r + 1


def get_data(subject, year, btn, screen):
    if not subject or not year:
        messagebox.showwarning("提示", "請務必選擇科目與年份！")
        return
    
    # 查詢中狀態維持優雅的深色調
    btn.config(state="disabled", text="查詢中...")
    
    def run_crawler():
        global datas
        success = False
        try:
            datas = MYcrawler.get_link(subject, year)
            success = True
        except Exception as e:
            messagebox.showerror("錯誤", f"爬取失敗: {str(e)}")
        finally:
            # 恢復按鈕狀態
            btn.config(state="normal", text="查詢")
            # 如果成功抓到資料，通知主視窗更新 UI
            if success:
                # 使用 screen.after 確保 UI 更新在主執行緒中執行，安全且不崩潰
                screen.after(0, lambda: update_ui(screen, subject, year))

    threading.Thread(target=run_crawler, daemon=True).start()

def main(years):
    screen = tk.Tk()

    window_width = 270
    window_height = 520
    screen_width = screen.winfo_screenwidth()
    screen_height = screen.winfo_screenheight()
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)


    screen.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")  # 稍微加寬加高，讓整體視覺更舒適不擁擠
    screen.title("歷屆試題查詢")
    screen.resizable(False, False)
    screen.config(bg=COLOR_BG)  

    
    screen.grid_rowconfigure(1, weight=1)
    screen.grid_columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TCombobox", 
                fieldbackground="#DD0000",  
                background=COLOR_BG,       
                foreground="#000000",       
                arrowcolor="#333333",        
                arrowsize=12,              
                bordercolor=COLOR_BTN,
                relief="raised",       
                padding=5                    
    )
    
    menu = tk.Menu(screen)
    setting_menu = tk.Menu(menu,tearoff=False)
    setting_menu.add_command(label="修改檔案儲存路徑",command=MYcrawler.choose_path)
    menu.add_cascade(label="setting",menu=setting_menu)

    screen.config(menu=menu)



    select = tk.LabelFrame(
        screen, text="項目選擇", fg=COLOR_TEXT, bg=COLOR_BG, 
        font=("Helvetica", 10, "bold")
    )
    select.grid(row=0, column=0, sticky='NSEW', padx=15, pady=(10,0))
    select.grid_columnconfigure(0, weight=1)


    # 科目選擇
    sub_lab = tk.Label(select, text="選擇科目:",fg=COLOR_TEXT, bg=COLOR_BG,font=("Helvetica", 10))
    sub_lab.grid(column=0, row=0, sticky="W", padx=10, pady=(8, 2))
    subjects = ["國文", "國寫", "英文", "數學", "社會", "自然"]
    sub_box = ttk.Combobox(select, values=subjects,width=30, state="readonly")
    sub_box.current(0)
    sub_box.grid(column=0, row=1, padx=10, pady=(0, 12))

    # 年份選擇
    year_lab = tk.Label(select, text="選擇年份:", fg=COLOR_TEXT,bg=COLOR_BG, font=("Helvetica", 10))
    year_lab.grid(column=0, row=2, sticky="W", padx=10, pady=(5, 2)) 
    year_box = ttk.Combobox(select, values=years, width=30,state="readonly")
    year_box.current(0)
    year_box.grid(column=0, row=3, padx=10, pady=(0, 20))

    #確認按鈕
    confirm_btn = tkmacosx.Button(
        select, text="查詢",width= 100,
        bg=COLOR_BTN, fg=COLOR_BTN_TXT,
        activebackground=COLOR_LINK, activeforeground=COLOR_BTN_TXT,
        bd=0,relief="flat", font=("Helvetica", 10, "bold"),
        cursor="hand2",
        command=lambda: get_data(sub_box.get(), year_box.get(), confirm_btn, screen)
    )
    confirm_btn.grid(column=0, row=4, padx=10, pady=(0, 12))

    data_frame = tk.LabelFrame(
        screen, text=f"查詢結果", 
        fg=COLOR_TEXT, bg=COLOR_BG, font=("Helvetica", 10, "bold")
    )
    data_frame.grid(row=1, column=0, sticky='NSEW', padx=15, pady=10)
    
    screen.mainloop()

if __name__ == "__main__":
    # 啟動進度視窗
    loading = LoadingWindow()
    loading.root.mainloop()

    # 當讀取視窗順利結束後，把取得的年份傳入你的主程式
    if loading.years is not None:
        main(loading.years)