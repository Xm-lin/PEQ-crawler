import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import crawler
import webbrowser
import tkmacosx
#色彩定義 
COLOR_BG = "#F8F9FA"         
COLOR_TEXT = "#495057"       
COLOR_BTN = "#1D3557"        
COLOR_BTN_TXT = "#FFFFFF"   
COLOR_LINK = "#457B9D"       
COLOR_LINK_HOVER = "#128D2D"


datas = []


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
        screen, text=f"{year}年{subject}科內容:", 
        fg=COLOR_TEXT, bg=COLOR_BG, font=("Helvetica", 10, "bold")
    )
    data_frame.grid(row=1, column=0, sticky='NSEW', padx=15, pady=10)
    
    # 紀錄這個 frame，方便下次查詢時可以刪除舊的
    update_ui.data_frame = data_frame
    
    # 將資料動態生成 Label 顯示出來
    r = 4
    for data in datas:
        name = tk.Label(
            data_frame, text=data[0], fg=COLOR_LINK, bg=COLOR_BG, 
            cursor="hand2", font=("Helvetica", 10)
        )
        name.grid(column=0, row=r, sticky="W", padx=10, pady=6)
        r = r + 1
        
        # 綁定點擊事件
        name.bind("<Button-1>", lambda e, url=data[1]: webbrowser.open(url))
        
        # 互動反饋：滑鼠移入（Hover）變深色並加底線
        name.bind("<Enter>", lambda e, lbl=name: lbl.config(fg=COLOR_LINK_HOVER, font=("Helvetica", 10, "underline")))
        # 互動反饋：滑鼠移出（Leave）恢復原狀
        name.bind("<Leave>", lambda e, lbl=name: lbl.config(fg=COLOR_LINK, font=("Helvetica", 10)))

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
            datas = crawler.get_link(subject, year)
            success = True
        except Exception as e:
            messagebox.showerror("錯誤", f"爬取失敗: {str(e)}")
        finally:
            # 恢復按鈕狀態
            btn.config(state="normal", text="確認")
            # 如果成功抓到資料，通知主視窗更新 UI
            if success:
                # 使用 screen.after 確保 UI 更新在主執行緒中執行，安全且不崩潰
                screen.after(0, lambda: update_ui(screen, subject, year))

    threading.Thread(target=run_crawler, daemon=True).start()


def main(years):
    screen = tk.Tk()

    window_width = 240
    window_height = 520
    screen_width = screen.winfo_screenwidth()
    screen_height = screen.winfo_screenheight()
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)


    screen.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")  # 稍微加寬加高，讓整體視覺更舒適不擁擠
    screen.title("歷屆試題查詢")
    #screen.resizable(False, False)
    screen.config(bg=COLOR_BG)   # 設定主視窗背景色

    # 設定 Grid 的 權重，讓元件可以跟著視窗縮放
    screen.grid_rowconfigure(1, weight=1)
    screen.grid_columnconfigure(0, weight=1)

    # 自訂 Combobox 的樣式，使其融入現代風背景
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TCombobox", fieldbackground="#FFFFFF", background=COLOR_BG)

    # 項目選擇區塊
    select = tk.LabelFrame(
        screen, text="項目選擇", fg=COLOR_TEXT, bg=COLOR_BG, 
        font=("Helvetica", 10, "bold")
    )
    select.grid(row=0, column=0, sticky='NSEW', padx=15, pady=15)
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
        select, text="確認",width= 100,
        bg=COLOR_BTN, fg=COLOR_BTN_TXT,
        activebackground=COLOR_LINK, activeforeground=COLOR_BTN_TXT,
        bd=0,relief="flat", font=("Helvetica", 10, "bold"),
        cursor="hand2",
        command=lambda: get_data(sub_box.get(), year_box.get(), confirm_btn, screen)
    )
    confirm_btn.grid(column=0, row=4, padx=10, pady=(0, 12), ipadx=5, ipady=3)

    data_frame = tk.LabelFrame(
        screen, text=f"考題", 
        fg=COLOR_TEXT, bg=COLOR_BG, font=("Helvetica", 10, "bold")
    )
    data_frame.grid(row=1, column=0, sticky='NSEW', padx=15, pady=10)
    

    screen.mainloop()

if __name__ == "__main__":
    print("正在取得年份列表，請稍候...")
    try:
        years = crawler.get_years()
        print("載入成功")
        main(years)
    except Exception as e:
        print(f"初始化失敗，無法取得年份: {e}")