import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json,os
import datetime
URL = "https://www.ceec.edu.tw/xmfile?xsmsid=0J052424829869345634"
def get_years():
    try:
        with open("crawler/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            max_year = data["max_year"]
            cur_year = datetime.datetime.now().year-1911
            if max_year == cur_year:
                years = []
                for year in range(max_year,82,-1):
                    years.append(str(year))
                return years
    except:
        pass        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        years = []
        # 開啟網頁並忽略 SSL 驗證錯誤
        page.goto(URL, wait_until="networkidle")
        searcher  = BeautifulSoup(page.content(),"html.parser")
        li = searcher.find("select",id = "Annaul")
        for year in li.find_all("option"):
            if year.text != "全部":
                years.append(year.text)
        browser.close()
        if years:
            latest_year = int(years[0]) 
            
            save_data = {"max_year": latest_year}
            
            with open("crawler/data.json", "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
    return years

def get_link(subject,year):
    #若之前存取過，沒必要再爬
    try:
        with open("crawler/data.json", "r", encoding="utf-8") as f:
            load_data = json.load(f)
            if year in load_data and subject in load_data[year]:
                return load_data[year][subject]
    except:
        pass

    with sync_playwright() as p:
        # launch(headless=False) 讓你親眼看到瀏覽器開啟與點擊動作
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 開啟網頁並忽略 SSL 驗證錯誤
        page.goto(URL, wait_until="networkidle")
        
        # 這裡放你要模擬點擊的動作
        # 範例：點擊網頁上文字為 "2" 的分頁按鈕 (可依需求替換 Selector)
        page.select_option("select", label=str(year))
        page.locator("text='查詢'").click()
        page.get_by_text(subject,exact=True).click()
        time.sleep(0.5)
        searcher = BeautifulSoup(page.content(),"html.parser")
        
        
        table  = searcher.find("table",class_="rwdTable")
        data = []
        k=1
        for tr in table.find_all("tr"):
            for links in tr.find_all("a"):
                link = links.get('href')
                if ".pdf" in link:
                    text = f"{links.text}(PDF)"
                elif ".doc" in link:
                    text = f"{links.text}(Word)"
                else:
                    text = links.text
                if "https://www.ceec.edu.tw" in link:
                    data.append([text,link])
                else:
                    data.append([text,f"https://www.ceec.edu.tw{link}"])
                k=k+1



        if os.path.exists("crawler/data.json"):
            try:
                with open("crawler/data.json", "r", encoding="utf-8") as f:
                    wdata = json.load(f)
            except json.JSONDecodeError:
                wdata = {}  # 如果檔案空了或損壞，就初始化新字典
        else:
            wdata = {}

        if year not in wdata:
            wdata[year] = {}

        wdata[year][subject] = data
        with open("crawler/data.json","w",encoding="utf-8") as f:
            json.dump(wdata,f,ensure_ascii=False,indent=4)
        page.close()
        return data
