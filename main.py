# Импортируем все из библиотеки TKinter
import math
from time import sleep
from tkinter import *

import numpy as np
from numpy import array, ndarray
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import threading

# Создаем главный объект (по сути окно приложения)
root = Tk()
# Указываем фоновый цвет
root['bg'] = '#ffffff'
# Указываем название окна
root.title('Корреляция изображения')
# Указываем размеры окна
root.geometry('1000x600')
label = Label(text="Корреляция изображения", fg="black")
label.pack()
# Создаем фрейм (область для размещения других объектов)
# Указываем к какому окну он принадлежит, какой у него фон и какая обводка
frame_top = Frame(root, bg="#ffffff", bd=10)
frame_top.place(relx=0, rely=0, relwidth=1, relheight=0.49)

frame_left = Frame(root, bg="#ffffff", bd=10)
frame_left.place(relx=0, rely=0.5, relwidth=0.5, relheight=0.5)

frame_right = Frame(root, bg="#ffffff", bd=10)
frame_right.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5)
# Создаем фрейм (область для размещения других объектов)
# Указываем к какому окну он принадлежит, какой у него фон и какая обводка
frame_top = Frame(root, bg="#ffffff", bd=10)
frame_top.place(relx=0, rely=0, relwidth=1, relheight=0.49)
frame_left = Frame(root, bg="#ffffff", bd=10)
frame_left.place(relx=0, rely=0.5, relwidth=0.5, relheight=0.5)

frame_right = Frame(root, bg="#ffffff", bd=10)
frame_right.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5)


def load_pictures() -> Image:
    f = filedialog.askopenfilename(
        parent=root, initialdir='/Users/batalabdulaev/Desktop',
        title='Choose file',
        filetypes=[('jpg images', '.jpg'),
                   ('png images', '.png'),
                   ('bmp images', '.bmp')
                   ]
    )
    print(f)
    image = Image.open(f).convert('L')
    image_black = ImageTk.PhotoImage(image)
    # imagine_array_big = array(image, dtype=float)
    # print(imagine_array_big)
    l1 = Label(frame_left, image=image_black)
    l1.image_black = image_black
    l1.pack()
    print("Картинка загружена")
    return image


def load_pictures_two() -> Image:
    f = filedialog.askopenfilename(
        parent=root, initialdir='/Users/batalabdulaev/Desktop',
        title='Choose file',
        filetypes=[('jpg images', '.jpg'),
                   ('png images', '.png'),
                   ('bmp images', '.bmp')
                   ]
    )
    image_2 = Image.open(f).convert('L')

    image_black_two = ImageTk.PhotoImage(image_2)

    label_right = Label(frame_right, image=image_black_two)

    label_right.image_black = image_black_two
    label_right.pack()
    print("Картинка загружена")
    return image_2


def correlate() -> None:
    big_pic = load_pictures()
    small_pic = load_pictures_two()
    big = array(big_pic, dtype=float)
    small = array(small_pic, dtype=float)

    if np.shape(small)[1] <= np.shape(big)[1] and np.shape(small)[0] <= np.shape(big)[0]:
        tmp_x = np.shape(small)[1]
        tmp_y = np.shape(small)[0]

        big_x = np.shape(big)[1]
        big_y = np.shape(big)[0]

        ncorr2d = np.zeros((big_y - tmp_y + 1, big_x - tmp_x + 1))
        big_mean = np.zeros((tmp_y, tmp_x))
        tmp_mean = np.mean(small)

        for x in range(big_x - tmp_x + 1):
            for y in range(big_y - tmp_y + 1):
                for m in range(tmp_x):
                    for n in range(tmp_y):
                        # считаем среднее значение под шаблоном
                        big_mean[n][m] = big[y + n][x + m]
                big_mean_total = np.mean(big_mean)

                numerator = sum(
                    ((big[y + i][x + j] - big_mean_total) * (small[i][j] - tmp_mean)) for i in range(tmp_y) for j in
                    range(tmp_x))

                denominator = (math.sqrt(
                    sum(((big[y + p][x + k] - big_mean_total) ** 2) for p in range(tmp_y) for k in range(tmp_x))
                    * sum(((small[t][r] - tmp_mean) ** 2) for t in range(tmp_y) for r in range(tmp_x))))

                ncorr2d[y][x] = numerator / denominator
                if ncorr2d[y][x] > 1 or ncorr2d[y][x] < -1:
                    print("Error ncorr2d value out of expected range -1<>1")
                    break
                print(ncorr2d[y][x], x, y)

        np_ncorr2d = np.asarray(ncorr2d)
        max_value = np.amax(np_ncorr2d)
        index_y, index_x = (np.argwhere(np_ncorr2d == max_value)[0][0], np.argwhere(np_ncorr2d == max_value)[0][1])
        if max_value < 0.7:
            print("Наибольшее значение коэффициента корреляции мало: " + str(max_value) +
                  ". \n Возможно, искомого шаблона нет в изображении. \n Проверьте входные "
                  "изображения и повторите попытку")
            return
        # newWindow = Toplevel(root)
        # frame_result = Frame(newWindow, bg="#ffffff", bd=10)
        rectangle = ImageDraw.Draw(big_pic)
        rectangle.rectangle([(index_x, index_y), (index_x + tmp_x, index_y + tmp_y)], width=2, outline='red')
        big_pic.save('result.bmp')
        # image_result = ImageTk.PhotoImage(big_pic)
        # label_result = Label(frame_result, image=image_result)
        # label_result.pack()
        big_pic.show()
        print(f"Координаты фрагмента по X:{index_x} Y: {index_y}, корреляция равна:{max_value}")
    else:
        return


def delete_images() -> None:
    for widget_right in frame_right.winfo_children():
        widget_right.destroy()
        print("Картинка удалена")
    for widget_left in frame_left.winfo_children():
        widget_left.destroy()
        print("Картинка удалена")


btn_images = Button(frame_top, text='Выберите изображения', command=correlate).pack(padx=10, pady=10)

btn = Button(frame_top, text='Очистить', command=delete_images).pack(padx=10, pady=10)


# Запускаем постоянный цикл, чтобы программа работала
if __name__ == "__main__":
    root.mainloop()
