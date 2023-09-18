import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Scrapper kompenero')
        self.setGeometry(100, 100, 400, 200)

        # Create widgets
        self.input_text = QLineEdit(self)
        self.process_button = QPushButton('start', self)
        self.result_label = QLabel('', self)

        # Create a layout
        layout = QVBoxLayout()
        layout.addWidget(self.input_text)
        layout.addWidget(self.process_button)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

        # Connect the button click event to the process_text function
        self.process_button.clicked.connect(self.process_url)

    def get_page_source(self,url):
        driver = webdriver.Chrome()
        driver.get(url)
        def has_new_content(current_source, new_source):
            return current_source != new_source

        current_page_source = driver.page_source
        new_page_source = ""


        # the next try,except are used if there is any modal present ypiu ned to write xpath and change it accordingly.
        try:
                time.sleep(10)
                modal_locator = (By.CLASS_NAME,"popup__dismiss-icon")
                wait = WebDriverWait(driver, 10) 
                modal = wait.until(EC.presence_of_element_located(modal_locator))
                xpath='//button[@class="popup__dismiss-icon"]'
                close_button=modal.find_element(By.XPATH,xpath)
                close_button.click()
        except:
            pass

        while has_new_content(current_page_source, new_page_source):
            current_page_source = driver.page_source

        # Scroll down to load more content


            #body_tag=driver.find_element(by="class", value="popup__dismiss-icon")


            scroll_down=modal.find_element(By.XPATH,'//body')
            scroll_down.send_keys(Keys.END)
        # Wait for a brief moment to allow content to load
            time.sleep(4)  # Adjust the sleep time as needed

        # Update the new page source
            new_page_source = driver.page_source

        driver.quit()
        return current_page_source        

    def data_ex(self,product):
     
        name = product.find('div',class_='spf-product__info').find('a').text
        image = str(product.find('img')['srcset'].split(",")[-1]).strip().split(" ")[0]
        try:
            price = product.find('span',class_='spf-product-card__price money').text
        except:
            price = product.find('span',class_='spf-product-card__saleprice money').text 
        product_link=f"https://kompanero.in{str(product.find('div',class_='spf-product__info').find('a')['href'])}"

        return([name,image,price,product_link])
    

    def image_list(self,img_list_html):
        image_list=[f"https:{i['src']}" for i in img_list_html.find('ul', class_='product-thumbnails__items').find_all('img')]
        return(image_list)
    

    def process_url(self):

        all_thumbs=[]
        all_sku=[]
        # Get the text from the input field
        url = self.input_text.text()
        data=pd.DataFrame(columns=['Name','Image_link','Price','Product_link'])
        soup = BeautifulSoup(self.get_page_source(url),'html.parser')
        product_container = soup.find('div', id='gf-products')
        for i in product_container.find_all('div','spf-product-card spf-product-card__center spf-product-card__template-2'):
            df_length=len(data)
            data.loc[df_length]=self.data_ex(i)

        # Display the result in the label
        self.result_label.setText(f'status {"processing"}')
        
        data.to_csv("data.csv",index=False)
        
        for i in data['Product_link']:
            try:    
                url = i
                driver = webdriver.Chrome()
                driver.get(url)
                time.sleep(5)
                page_source=driver.page_source

                driver.quit()

                soup = BeautifulSoup(str(page_source),'html.parser')

                main_div=soup.find('main',id='main')
                #print(main_div.find('ul', class_='product-thumbnails__items'))

                images = self.image_list(main_div)

                sku = main_div.find('div',class_='product__sku fs-body-25 t-opacity-60').text

                all_thumbs.append(images)
                all_sku.append(sku)

            except:
                all_thumbs.append("nodata")
                all_sku.append("nodata")
        data['Thumb_images']=all_thumbs
        data['SKU']=all_sku

        data.to_csv('data_final.csv')



        self.result_label.setText(f'status {"completed"}')




def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()



