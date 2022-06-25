import math
import multiprocessing
import numpy
from numpy import array
from tkinter import filedialog, Button
from PIL import Image, ImageTk, ImageDraw
import os
from settings import *
import time


def load_pictures_big() -> Image:
    """ Загружает оригинал """
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
    """ Загружает шаблон"""
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
    min_allowable_value = 0.9   # очень высокая корреляция
    timer_start = time.time()
    big_image = array(big_pic.convert("L"), dtype=numpy.float64)  # Конвертит в 8 пиксельное изображение
    small_image = array(small_pic.convert("L"), dtype=numpy.float64)
    file = open("result.txt", 'w')
    np_small = numpy.shape(small_image)   # размер картинки
    np_big = numpy.shape(big_image)
    if np_small[0] > np_big[0] or np_small[1] > np_big[1]:
        file.write(f"Шаблон больше чем главное изображение, "
                   f"проверьте изображения ( размеры шаблона - {np_small} , оригинал - {np_big})")
        return None
    small_image_x = numpy.shape(small_image)[1]  # размерность
    small_image_y = numpy.shape(small_image)[0]
    big_image_y = numpy.shape(big_image)[0]     # по y
    big_image_x = numpy.shape(big_image)[1]     # по x
    size_y = big_image_y - small_image_y + 1
    size_x = big_image_x - small_image_x + 1
    n_correlate_2d = numpy.zeros((size_y, size_x))
    big_middle = numpy.zeros((small_image_y, small_image_x))
    small_middle = numpy.mean(small_image)  # среднее значение
    for x in range(size_x):
        for y in range(size_y):
            for u in range(small_image_x):
                for v in range(small_image_y):
                    # считаем среднее значение под шаблоном
                    big_middle[v][u] = big_image[y + v][x + u]

            total_big_intensive_mean = numpy.mean(big_middle)  # среднее значение интенсивности изображения под шаблоном
            numer = 0
            for i in range(small_image_y):
                for j in range(small_image_x):
                    numer += (big_image[y + i][x + j] - total_big_intensive_mean) * (small_image[i][j] - small_middle)

            den_big = 0
            den_small = 0
            for i in range(small_image_y):
                for j in range(small_image_x):
                    den_big += pow((big_image[y + i][x + j] - total_big_intensive_mean), 2)
            for i in range(small_image_y):
                for j in range(small_image_x):
                    den_small += pow((small_image[i][j] - small_middle), 2)
            den = math.sqrt(den_big * den_small)

            n_correlate_2d[y][x] = numer / den
            if -1 > n_correlate_2d[y][x] or n_correlate_2d[y][x] > 1:
                print("Выход за диапазон -1 и 1")
                break
            file.write(f"{(n_correlate_2d[y][x])} {x} {y}\n")

    n_correlate_2d = numpy.asarray(n_correlate_2d)
    MAX_VALUE_CORRELATE = numpy.amax(n_correlate_2d)    # Convert the input to an array.
    index_Y, index_X = (numpy.transpose(numpy.nonzero(n_correlate_2d == MAX_VALUE_CORRELATE))[0][0],
                        numpy.transpose(numpy.nonzero((n_correlate_2d == MAX_VALUE_CORRELATE)))[0][1])
    file.write(f"\nX = {index_X} Y = {index_Y}, корреляция = {MAX_VALUE_CORRELATE}")
    timer_stop = time.time() - timer_start
    file.write(f"\nВремя: {timer_stop} sec")
    if MAX_VALUE_CORRELATE <= min_allowable_value:
        file.write(f"Максимальное значение коэффициента корреляции недостаточно: {MAX_VALUE_CORRELATE}. ")
        return None
    file.close()
    rect = ImageDraw.Draw(big_pic)
    rect.rectangle([(index_X, index_Y), (index_X + small_image_x, index_Y + small_image_y)], width=3, outline='black')
    big_pic.save('picture.bmp')
    big_pic.show()
    return None


def delete_images() -> None:
    """ Удаляет фотографии с приложения """
    for widget_right in frame_right.winfo_children():
        widget_right.destroy()
        print("Картинка удалена")
    for widget_left in frame_left.winfo_children():
        widget_left.destroy()
        print("Картинка удалена")
    for widget_text in frame_text.winfo_children():
        widget_text.destroy()


def multi_correlate() -> None:
    """Загружает фотографии и создает новый процесс"""
    big_pic = load_pictures_big()
    small_pic = load_pictures_small()
    text = "Картинки загружены, идет корреляционный анализ, подождите"
    text_load_pic = Label(frame_text, text=text)
    text_load_pic.pack()
    new_process_correlate = multiprocessing.Process(target=correlate, args=(big_pic, small_pic))
    new_process_correlate.start()

    def destroy_process() -> None:
        """Останавливает расчеты (убивает процесс)"""

        for widget in frame_text.winfo_children():
            widget.destroy()
        Label(frame_text, text="Расчет остановлен").pack()
        new_process_correlate.kill()

    Button(frame_text, text='Остановить расчет', command=destroy_process).pack(padx=10, pady=2)


btn_select_images = Button(frame_top, text='Выберите изображения', command=multi_correlate).pack(padx=10, pady=10)

btn_destroy_images = Button(frame_top, text='Очистить', command=delete_images).pack(padx=10, pady=10)

# Запускаем постоянный цикл
if __name__ == "__main__":
    root.mainloop()
