import sys
import requests
import pygame
import os

# Этот класс поможет нам сделать картинку из потока байт
from api_utils import get_degree_size, get_toponim, get_coords, show_map_pygame, show_map
from PyQt5 import QtWidgets
from PyQt5 import uic

Form, Window = uic.loadUiType("MapsApi1.ui")


class Ui(QtWidgets.QDialog, Form):
    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.clickedbutton)
        self.setWindowTitle('Параметры для отображения карты')
                            
    def clickedbutton(self):
        self.params = all((self.lineEdit.text(), self.lineEdit_2.text()))
        
        running = True
        
        if self.params:
            pygame.init()
            screen = pygame.display.set_mode((600, 450))
            
            k = int(self.lineEdit_2.text())
            
            func = True
            
            m_y = 0
            m_x = 0
            
            type_map = 0
            types_map = ['map', 'sat', 'sat,skl']
            
            while running:
                move = 100 / 2 ** k
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_PAGEUP:
                            if k < 16.5:
                                k += 1
                                func = True
                                
                        if event.key == pygame.K_UP:
                            if m_y < 30:
                                m_y += move
                                func = True
                                
                        if event.key == pygame.K_DOWN:
                            if m_y > -120:
                                m_y -= move
                                func = True

                        if event.key == pygame.K_LEFT:
                            if m_x > -180:
                                m_x -= move
                                func = True

                        if event.key == pygame.K_RIGHT:
                            if m_x < 120:
                                m_x += move
                                func = True
                        
                        if event.key == pygame.K_PAGEDOWN:
                            if k > 0.5:
                                k -= 1
                                func = True
                                
                        if event.key == pygame.K_LSHIFT:
                            type_map += 1
                            if type_map == 3:
                                type_map = 0
                            func = True
                # Пусть наше приложение предполагает запуск:
                # python search.py Москва, ул. Ак. Королева, 12
                # Тогда запрос к геокодеру формируется следующим образом:
                if func:
                    toponym_to_find = self.lineEdit.text()
                    
                    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
                    
                    geocoder_params = {
                        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                        "geocode": toponym_to_find,
                        "format": "json"}
                    
                    response = requests.get(geocoder_api_server, params=geocoder_params)
                    
                    if not response:
                        # обработка ошибочной ситуации
                        pass
                    # Координаты центра топонима:
                    toponym_coodrinates = get_coords(toponym_to_find)
                    # Долгота и широта:
                    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
                    
                    # Собираем параметры для запроса к StaticMapsAPI:
                    map_params = {
                        "ll": ",".join([str(float(toponym_longitude) + m_x), str(float(toponym_lattitude) + m_y)]),
                        'z': k,
                        "l": types_map[type_map]
                    }
                    api_server = "http://static-maps.yandex.ru/1.x/"
                    response = requests.get(api_server, params=map_params)
                
                    if not response:
                        print("Ошибка выполнения запроса:")
                        sys.exit(1)
                
                    # Запишем полученное изображение в файл.
                    map_file = "map.png"
                    with open(map_file, "wb") as file:
                        file.write(response.content)
                    
                    screen.blit(pygame.image.load(map_file), (0, 0))
                    pygame.display.flip()
                    func = False
            pygame.quit()
            os.remove('map.png')
            self.lineEdit.clear()
            self.lineEdit_2.clear()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Ui()
    ex.show()
    sys.exit(app.exec())