import math
import multiprocessing
import numpy
from numpy import array
from tkinter import filedialog, Button, Toplevel
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
    Label(frame_left, text="Оригинал").pack()

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
    Label(frame_right, text="Шаблон").pack()
    return image


def correlate(big_pic: Image, small_pic: Image) -> None:
    big = array(big_pic.convert("L"), dtype=float)
    small = array(small_pic.convert("L"), dtype=float)
    file = open("result.txt", 'w')
    np_small = numpy.shape(small)
    np_big = numpy.shape(big)
    if np_small[0] > np_big[0] or np_small[1] > np_big[1]:
        file.write(f"Шаблон больше чем главное изображение, "
                   f"проверьте изображения ( размеры шаблона - {np_small} , оригинал - {np_big})")
        return None
    else:

        small_x = numpy.shape(small)[1]  # размерность
        small_y = numpy.shape(small)[0]
        big_y = numpy.shape(big)[0]
        big_x = numpy.shape(big)[1]
        size_y = big_y - small_y + 1
        size_x = big_x - small_x + 1
        n_corr_2d = numpy.zeros((size_y, size_x))
        big_mean = numpy.zeros((small_y, small_x))
        small_mean = numpy.mean(small)  # среднее значение

        for x in range(size_x):
            for y in range(size_y):
                for u in range(small_x):
                    for v in range(small_y):
                        # считаем среднее значение под шаблоном
                        big_mean[v][u] = big[y + v][x + u]

                big_mean_total = numpy.mean(big_mean)  # среднее значение интенсивности изображения под шаблоном
                numer = 0
                for i in range(small_y):
                    for j in range(small_x):
                        numer += (big[y + i][x + j] - big_mean_total) * (small[i][j] - small_mean)

                den_big = 0
                den_small = 0
                for i in range(small_y):
                    for j in range(small_x):
                        den_big += pow((big[y + i][x + j] - big_mean_total), 2)
                for i in range(small_y):
                    for j in range(small_x):
                        den_small += pow((small[i][j] - small_mean), 2)
                den = math.sqrt(den_big * den_small)

                n_corr_2d[y][x] = numer / den
                if n_corr_2d[y][x] < -1 or n_corr_2d[y][x] > 1:
                    print("Выход за диапазон -1 и 1")
                    break
                file.write(f"{(n_corr_2d[y][x])} {x} , {y}\n")

        n_corr_2d = numpy.asarray(n_corr_2d)  # Convert the input to an array.
        max_value_corr = numpy.amax(n_corr_2d)
        index_y, index_x = (numpy.argwhere(n_corr_2d == max_value_corr)[0][0],
                            numpy.argwhere(n_corr_2d == max_value_corr)[0][1])
        file.write(f"\nX = {index_x} Y = {index_y}, корреляция = {max_value_corr}")
        file.close()
        if max_value_corr <= 0.9:
            print(f"Максимальное значение коэффициента корреляции недостаточно: {max_value_corr}. ")
            return None
        text = f"\nX = {index_x} Y = {index_y}, корреляция = {max_value_corr}"
        print(text)
        rect = ImageDraw.Draw(big_pic)
        rect.rectangle([(index_x, index_y), (index_x + small_x, index_y + small_y)], width=3, outline='black')
        big_pic.save('result.bmp')
        big_pic.show()
        return None


def delete_images() -> None:
    for widget_right in frame_right.winfo_children():
        widget_right.destroy()
        print("Картинка удалена")
    for widget_left in frame_left.winfo_children():
        widget_left.destroy()
        print("Картинка удалена")
    for widget_text in frame_text.winfo_children():
        widget_text.destroy()


def multi_corr():
    big_pic = load_pictures_big()
    small_pic = load_pictures_small()
    text = "Картинки загружены, идет корреляционный анализ, подождите"
    text_load_pic = Label(frame_text, text=text)
    text_load_pic.pack()
    process_corr = multiprocessing.Process(target=correlate, args=(big_pic, small_pic))
    process_corr.start()

    def destroy_process():
        for i in frame_text.winfo_children():
            if isinstance(i, Label):
                i.destroy()
        Label(frame_text, text="Расчет остановлен").pack()
        process_corr.kill()

    Button(frame_text, text='Остановить расчет', command=destroy_process).pack(padx=10, pady=2)


btn_select_images = Button(frame_top, text='Выберите изображения', command=multi_corr).pack(padx=10, pady=10)

btn_destroy_images = Button(frame_top, text='Очистить', command=delete_images).pack(padx=10, pady=10)

# Запускаем постоянный цикл
if __name__ == "__main__":
    root.mainloop()
