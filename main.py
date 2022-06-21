# Импортируем все из библиотеки TKinter
import math
import multiprocessing
import numpy as np
from numpy import array
from tkinter import filedialog, Button
from PIL import Image, ImageTk, ImageDraw
import os
from settings import *


def load_pictures_big() -> Image:
    f = filedialog.askopenfilename(
        parent=root, initialdir=os.environ,
        title='Choose file',
        filetypes=[('jpg images', '.jpg'),
                   ('png images', '.png'),
                   ('bmp images', '.bmp')
                   ]
    )
    print(f)
    image = Image.open(f)
    image_black = ImageTk.PhotoImage(image)
    l1 = Label(frame_left, image=image_black)
    l1.image_black = image_black
    l1.pack()
    print("Картинка загружена")
    return image


def load_pictures_small() -> Image:
    f = filedialog.askopenfilename(
        parent=root, initialdir=os.environ,
        title='Choose file',
        filetypes=[('jpg images', '.jpg'),
                   ('png images', '.png'),
                   ('bmp images', '.bmp')
                   ]
    )
    print(f)
    image = Image.open(f)
    image_black = ImageTk.PhotoImage(image)
    l1 = Label(frame_right, image=image_black)
    l1.image_black = image_black
    l1.pack()
    print("Картинка загружена")
    return image


def correlate(big_pic, small_pic) -> None:
    big = array(big_pic.convert("L"), dtype=float)
    small = array(small_pic.convert("L"), dtype=float)

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
        rectangle = ImageDraw.Draw(big_pic)
        rectangle.rectangle([(index_x, index_y), (index_x + tmp_x, index_y + tmp_y)], width=2, outline='red')
        big_pic.save('result.bmp')
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


def corr():
    big_pic = load_pictures_big()
    small_pic = load_pictures_small()
    process_corr = multiprocessing.Process(target=correlate, args=(big_pic, small_pic))
    process_corr.start()


btn_select_images = Button(frame_top, text='Выберите изображения', command=corr).pack(padx=10, pady=10)
btn_destroy_images = Button(frame_top, text='Очистить', command=delete_images).pack(padx=10, pady=10)

# Запускаем постоянный цикл
if __name__ == "__main__":
    root.mainloop()
