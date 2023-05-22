import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
from tkinter import filedialog
import pytesseract
import mysql.connector
import numpy as np
import tkinter.font as tkFont


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def popupmsg():
    title = "Tutorial"
    mensaje = "Seleccione el titulo y oprima Enter para confirmar la seleccion"
    messagebox.showinfo(title, mensaje)
def popupmsg2():
    title = "Tutorial"
    mensaje = "Seleccione el autor y oprima Enter para confirmar la seleccion"
    messagebox.showinfo(title, mensaje)
def popuperror():
    title = "Error"
    mensaje = "No se pudo cargar la imagen"
    messagebox.showerror(title, mensaje, icon="error")
def popuperrordifimg():
    title = "Warning"
    mensaje = "Las portadas no coinciden, mostrando coincidencias."
    messagebox.showerror(title, mensaje, icon="warning")


def guardar():
    texto = variable_label.get()
    autor = variable_autor.get()
    print("El titulo es:", texto)
    print("El autor es:", autor)
    conectar(texto,autor)

def conectar(title,auth):
    # Configuración de la conexión a la base de datos
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="libros"
    )

    cursor = conexion.cursor()

    if title:
        title = f"%{title}%"
    if auth:
        auth = f"%{auth}%"

    # Ejecutar una consulta preparada con LIKE si se ingresaron datos
    if title or auth:
        consulta = "SELECT ruta, titulo, autor, edicion, editorial, estante, codigo_libro FROM portadas WHERE "
        if title and auth:
            consulta += "titulo LIKE %s OR autor LIKE %s"
            datos = (title, auth)
        elif title:
            consulta += "titulo LIKE %s OR autor LIKE %s"
            datos = (title, title)
        else:
            consulta += "autor LIKE %s OR titulo LIKE %s"
            datos = (auth, auth)
        cursor.execute(consulta, datos)

        resultados = cursor.fetchall()
    else:
        resultados = []

    if len(resultados) > 0:
        ruta_imagen = resultados[0][0]
        imgbd = cv2.imread(ruta_imagen)
    else:
         ruta_imagen = None

    umbral_similitud = 10
    if get_color_similarity(img, imgbd) < umbral_similitud:
        print("Los colores predominantes son similares.")
    else:
        print("Los colores predominantes son diferentes.")
        popuperrordifimg()
    mostrar_resultados(resultados)

    cursor.close()
    conexion.close()

def mostrar_resultados(resultados):
    if len(resultados) > 0:
        global res
        res = tk.Toplevel()
        
        res.geometry("{}x{}+{}+{}".format(withv, heighv, int(top.winfo_screenwidth()/2 - withv/2), int(top.winfo_screenheight()/2 - heighv/2)))
        res.resizable(True, False)
        res.title("Resultados")
        frame = ttk.Frame(res, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        titulo = 'Se encontraron ' + str(len(resultados)) + ' posibles resultados'
        titulo_lbl = ttk.Label(frame, text=titulo)
        titulo_lbl.pack(side=tk.TOP, pady=10)

        # Creación del botón para cerrar la ventana
        close_button = ttk.Button(frame, text="X", command=close_all_windows, style='danger.TButton')
        close_button.pack(side=tk.TOP, anchor=tk.E, pady=10)

        # Creación del canvas y el widget del scrollbar para la tabla
        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        tabla_frame = ttk.Frame(canvas)
        tabla_frame.pack(fill=tk.BOTH, expand=True)
        canvas.create_window((0, 0), window=tabla_frame, anchor='nw', width=950)

        headers = ['Título', 'Autor', 'Edición', 'Editorial', 'Estante', 'Código del libro']
        tabla_treeview = ttk.Treeview(tabla_frame, columns=headers, show='headings')
        tabla_treeview.pack(fill=tk.BOTH, expand=True)

        for i, header in enumerate(headers):
            tabla_treeview.heading(i, text=header, anchor=tk.W)
            # Set the column width to fit the content
            tabla_treeview.column(i, width=tkFont.Font().measure(header))

        for i, resultado in enumerate(resultados):
            resultado = resultado[1:]
            tabla_treeview.insert('', 'end', values=resultado)

        # Call update_idletasks and configure tabla_treeview columns to right size
        tabla_treeview.update_idletasks()
        for i, header in enumerate(headers):
            width = max(tabla_treeview.column(i, width=None), tkFont.Font().measure(header) + 20)
            tabla_treeview.column(i, width=width)

        # Call update_idletasks on the canvas before updating the scrollregion
        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))


        if len(resultados) > 0:
            ruta_imagen = resultados[0][0]
        else:
            ruta_imagen = None

        if os.path.exists(ruta_imagen):
            # Open the image and resize it to 100 x 200
            original_image = Image.open(ruta_imagen)
            resized_image = original_image.resize((150, 200), Image.ANTIALIAS)

            # Create the PhotoImage object from the resized image
            imagen = ImageTk.PhotoImage(resized_image)

            # Create the label and display the image
            imagen_frame = ttk.LabelFrame(frame, text='Imagen BD')
            imagen_frame.pack(pady=10)
            imagen_label = ttk.Label(imagen_frame, image=imagen)
            imagen_label.pack(padx=5, pady=5)
        else:
            print("No existe el path")
            popuperror()
            res.deiconify()


        # Creación del botón para nueva busqueda
        cancelarbtn = ttk.Button(frame, command=regresar, text='Nueva Busqueda', style='success.TButton')
        cancelarbtn.pack(side=tk.BOTTOM, pady=10)

        res.mainloop()
    else:
        title = "Resultado"
        mensaje = "No se encontraron posibles resultados"
        messagebox.showerror(title, mensaje)
        top.deiconify()

def get_color_similarity(img1, img2):
    predominant_color1 = get_predominant_color(img1)
    print(predominant_color1)
    predominant_color2 = get_predominant_color(img2)
    print(predominant_color2)

    # Calcula la distancia euclidiana entre ambos colores
    similarity = np.sqrt(np.sum((np.array(predominant_color1) - np.array(predominant_color2))**2))
    return similarity

def cancelar():
    top.destroy()
    ventana.deiconify()
def regresar():
    res.destroy()
    top.destroy()
    ventana.deiconify()

def mostrar_nueva_ventana(title,auth,imagen):
    titulo = title
    autor = auth
    global top
    top = ttk.Toplevel()
    top.geometry("{}x{}+{}+{}".format(700, 800, int(top.winfo_screenwidth()/2 - withv/2), int(top.winfo_screenheight()/2 - heighv/2)))
    top.resizable(False, False)
    top.title(titulov)
    margin = 10
    padd = 5

    global variable_label
    global variable_autor
    # crear la etiqueta de título de la ventana
    labeltituloventana = ttk.Label(top, text="Confirma los datos obtenidos:", padding=padd, font=(10))
    labeltituloventana.grid(column=0, row=0, padx=margin, pady=margin, columnspan=3)

    # crear las etiquetas de título y autor
    labeltitulo = ttk.Label(top, text="Titulo:", padding=padd)
    labeltitulo.grid(column=0, row=1, padx=margin, pady=margin, sticky="w")
    variable_label = ttk.StringVar()
    variable_label.set(titulo)
    label_editable = ttk.Entry(top, textvariable=variable_label)
    label_editable.grid(column=1, row=1, padx=margin, pady=margin, sticky="ew")

    labelautor = ttk.Label(top, text="Autor:", padding=padd)
    labelautor.grid(column=0, row=2, padx=margin, pady=margin, sticky="w")
    variable_autor = ttk.StringVar()
    variable_autor.set(autor)
    label_autor = ttk.Entry(top, textvariable=variable_autor)
    label_autor.grid(column=1, row=2, padx=margin, pady=margin, sticky="ew")

    # crear la etiqueta de imagen y la imagen
    imagenlabel = ttk.Label(top, text="Imagen ingresada:", padding=padd)
    imagenlabel.grid(column=2, row=1, padx=margin, pady=margin, sticky="w")
    color_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(color_image)
    image_tk = ImageTk.PhotoImage(image_pil)
    label_imagen = ttk.Label(top, image=image_tk, padding=padd, borderwidth=2, relief="groove")
    label_imagen.image = image_tk
    label_imagen.grid(column=2, row=2, padx=margin, pady=margin, rowspan=3, sticky="nsew")

    # crear el botón para cerrar la ventana
    close_button = ttk.Button(top, text="X", command=close_all_windows, style='danger.TButton')
    close_button.grid(column=2, row=0, padx=margin, pady=margin, sticky='ne')

    # crear los botones para cancelar y guardar
    cancelarbtn = ttk.Button(top, command=cancelar, text= 'Cancelar', bootstyle= 'danger', padding=padd)
    cancelarbtn.grid(column=0, row=3, padx=margin, pady=margin)

    guardarbtn = ttk.Button(top, command=guardar, text= 'Confirmar', padding=padd)
    guardarbtn.grid(column=1, row=3, padx=margin, pady=margin)

def get_predominant_color(image):
    # Get image shape
    shape = image.shape[:2]

    # Reshape image to a list of pixels
    pixels = image.reshape(-1, 3)

    # Calculate histogram using 32 bins for each color channel
    histogram = np.histogramdd(pixels, bins=32, range=[(0, 255), (0, 255), (0, 255)])[0]

    # Calculate dominant color using the highest bin from the histogram
    color = np.unravel_index(histogram.argmax(), histogram.shape)

    # Normalize color values to the range [0, 1] and return as a tuple
    rgb_tuple = (int(color[0] * 8.225), int(color[1] * 8.225), int(color[2] * 8.225))
    return rgb_tuple
    # return (color[0] / 31.0, color[1] / 31.0, color[2] / 31.0)

def abrir_imagen():
    global img
    global cv_img
    titulo = ""
    autor = ""
    # Crea una ventana emergente para que el usuario seleccione la imagen
    filename = filedialog.askopenfilename()
    # codifica la ruta del archivo utilizando utf-8
    filename_encoded = filename.encode('utf-8')

    # Carga la imagen seleccionada
    img = cv2.imread(filename_encoded.decode())
    if img is None:
        print("Error: failed to load the image.")
        popuperror()
        return
    else:
        global resized_image
        resized_image = cv2.resize(img, (400, 500))

    popupmsg()
    try:
        puntos = cv2.selectROI('selecciona el titulo', resized_image, fromCenter=False, showCrosshair=True)
    except cv2.error:
        return

    # Recorta la región seleccionada de la imagen original
    (x, y, ancho, alto) = puntos
    roi = resized_image[y:y+alto, x:x+ancho]

    # Convierte la imagen a escala de grises
    if roi.size > 0:
        gris = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # cv2.imshow('Imagen en escala de grises', gris)
        # Aplica un filtro de mediana para reducir el ruido
        mediana = cv2.medianBlur(gris, 1)
        # cv2.imshow('Imagen con filtro de mediana', mediana)

        # Binariza la imagen para obtener el texto en blanco y el fondo en negro
        binaria = cv2.threshold(mediana, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # cv2.imshow('Imagen binarizada', binaria)

        # Aplica un filtro de apertura para eliminar pequeños objetos y áreas ruidosas
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        apertura = cv2.morphologyEx(binaria, cv2.MORPH_OPEN, kernel)
        # cv2.imshow('Imagen con filtro de apertura', apertura)

        cv2.destroyAllWindows()

        # Configura las opciones de Tesseract OCR
        config = '--psm 11 -l eng+spa -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


        # Realiza la OCR en la imagen y extrae el texto
        titulo = pytesseract.image_to_string(gris, config=config)
        titulo = titulo.replace('\n', ' ').rstrip()

        # extraer el autor
        popupmsg2()
        puntos = cv2.selectROI('selecciona el autor', resized_image, fromCenter=False, showCrosshair=True)

        # Recorta la región seleccionada de la imagen original
        (x, y, ancho, alto) = puntos
        roi = resized_image[y:y+alto, x:x+ancho]

        # Convierte la imagen a escala de grises
        gris = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # cv2.imshow('Imagen en escala de grises', gris)

        # Aplica un filtro de mediana para reducir el ruido
        mediana = cv2.medianBlur(gris, 1)
        # cv2.imshow('Imagen con filtro de mediana', mediana)

        # Binariza la imagen para obtener el texto en blanco y el fondo en negro
        binaria = cv2.threshold(mediana, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # cv2.imshow('Imagen binarizada', binaria)

        # Aplica un filtro de apertura para eliminar pequeños objetos y áreas ruidosas
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        apertura = cv2.morphologyEx(binaria, cv2.MORPH_OPEN, kernel)

        cv2.destroyAllWindows()

        # Realiza la OCR en la imagen y extrae el texto
        autor = pytesseract.image_to_string(gris, config=config)
        autor = autor.replace('\n', ' ').rstrip()

        # predominant_color = get_predominant_color(resized_image)
        # print(predominant_color)
        print(titulo)
        print(autor)
        mostrar_nueva_ventana(titulo,autor,img)

def close_all_windows():
    ventana.destroy()

# ventana principal
ventana = ttk.Window(themename = 'superhero')
withv = 1200
heighv = 800
titulov = "Search My Book"
padd = (10, 10, 10, 10)
margin = 10
resized_image = None
ventana.geometry("{}x{}+{}+{}".format(withv, heighv, int(ventana.winfo_screenwidth()/2 - withv/2), int(ventana.winfo_screenheight()/2 - heighv/2)))
ventana.resizable(False, False)
ventana.title(titulov)

frame = ttk.Frame(ventana)
frame.pack(fill='both', expand=True)
close_button = ttk.Button(frame, text="X", command=close_all_windows, style='danger.TButton')
close_button.pack(side='top', padx=(0, margin), pady=margin, anchor='ne')



ttk.Label(frame, text="Ingresa la imagen del libro a buscar: ", padding=50, font=(15)).pack()
ttk.Label(frame, text='', padding=padd).pack(side='top', fill='y', expand=True)

boton = ttk.Button(frame, command=abrir_imagen, text='Subir imagen', bootstyle='secondary', padding=padd)
boton.pack(padx=margin, pady=0, side='top')

ttk.Label(frame, text='', padding=padd).pack(side='top', fill='y', expand=True)
ventana.mainloop()