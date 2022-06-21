from tkinter import Tk, Label, Frame

# Создаем главный объект (по сути окно приложения)
root = Tk()
# Указываем фоновый цвет
root['bg'] = '#1a1b1f'
# Указываем название окна
root.title('Корреляция изображения')
# Указываем размеры окна
root.geometry('1000x600')
label = Label(text="Корреляция изображения", fg="black")
label.pack()
# Создаем фрейм (область для размещения других объектов)
# Указываем к какому окну он принадлежит, какой у него фон и какая обводка
frame_top = Frame(root, bg="#1a1b1f", bd=10)
frame_top.place(relx=0, rely=0, relwidth=1, relheight=0.49)

frame_left = Frame(root, bg="#1a1b1f", bd=10)
frame_left.place(relx=0, rely=0.5, relwidth=0.5, relheight=0.5)

frame_right = Frame(root, bg="#1a1b1f", bd=10)
frame_right.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5)
