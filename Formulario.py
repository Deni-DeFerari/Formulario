# -*- coding: utf-8 -*-
"""Untitled4.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LARN3URFg3zdUZmxYDZtqiRIS9W3n_7i
"""

!pip install ipywidgets openpyxl
from google.colab import output
output.enable_custom_widget_manager()

import os
import ipywidgets as widgets
from IPython.display import display
import pandas as pd

# ------------------------------------------------------
# 1. LECTURA DE DATOS
# ------------------------------------------------------
df_ocos = pd.read_excel(
    '/content/drive/MyDrive/Matriz 2025/Matriz CAPEX Regular 2025.xlsx',
    sheet_name='Matriz 2025',
    header=5  # Salta las 5 primeras filas (cabecera en la fila 6)
)

# Eliminamos filas totalmente vacías, por si acaso
df_ocos.dropna(how='all', inplace=True)
# Eliminamos columnas "Unnamed:" si existen
df_ocos = df_ocos.loc[:, ~df_ocos.columns.str.contains('^Unnamed')]

# Crea la columna 'EsAhorroSede' basándote en "Nombre solicitud"
df_ocos['EsAhorroSede'] = (
    df_ocos['Nombre solicitud'] == 'Gestión sede por ahorros de presupuesto'
)

# ------------------------------------------------------
# 2. OPCIONES PRINCIPALES (Sede, Tipo de solicitud)
# ------------------------------------------------------
sede_options = [
    "Alameda", "Alonso Ovalle", "Antonio Varas", "Arauco", "Concepción",
    "Liceo Renca", "Maipú", "Melipilla", "Nacimiento", "Plaza Norte",
    "Plaza Oeste", "Plaza Vespucio", "Puente Alto", "Puerto Montt",
    "San Bernardo", "San Carlos", "San Joaquín", "Valparaíso",
    "Villarrica", "Viña del Mar", "Educación Continua",
    "Puente Alto ", "Campus Online"
]

tipo_solicitud_options = [
    "Disminución presupuesto (Destino ahorro SEDE)",
    "Aumento presupuesto (Origen ahorro SEDE)",
    "Traslado presupuesto (entre OCOS vigentes)"
]

# ------------------------------------------------------
# 3. WIDGETS BÁSICOS (Sede, Tipo, Monto, Mes, Adjuntos)
# ------------------------------------------------------
sede_dropdown = widgets.Dropdown(
    options=sede_options,
    description='Sede:',
    style={'description_width': 'initial'},
    layout=widgets.Layout(width='50%')
)

tipo_solicitud_dropdown = widgets.Dropdown(
    options=tipo_solicitud_options,
    description='Tipo de Solicitud:',
    style={'description_width': 'initial'},
    layout=widgets.Layout(width='70%')
)

monto_text = widgets.FloatText(
    value=0,
    description='Monto:',
    style={'description_width': 'initial'},
    layout=widgets.Layout(width='50%')
)

mes_text = widgets.Text(
    value='',
    description='Mes de planificación:',
    style={'description_width': 'initial'},
    layout=widgets.Layout(width='50%')
)

adjuntos_upload = widgets.FileUpload(
    description="Subir documentos",
    accept="",  # Aceptar cualquier tipo de archivo
    multiple=True
)

# ------------------------------------------------------
# 4. MOSTRAR INFORMACIÓN COMPLETA EN LOS DROPDOWNS
#    (OCO, ID Solicitud, Nombre, Item)
# ------------------------------------------------------
oco_origen_dropdown = widgets.Dropdown(
    options=[],
    description='OCO Origen:',
    style={'description_width': 'initial'},
    layout=widgets.Layout(width='70%')
)
oco_destino_dropdown = widgets.Dropdown(
    options=[],
    description='OCO Destino:',
    style={'description_width': 'initial'},
    layout=widgets.Layout(width='70%')
)

def crear_opciones_oco(df):
    """
    Devuelve una lista de tuplas (label, value) para que el Dropdown
    muestre, por ejemplo:
      "OCO123 | ID: 45 | Nombre: Sala de Computación | Item: 567"
    pero el "value" real sea sólo el OCO (o si gustas, todo el row).
    """
    opciones = []
    for _, row in df.iterrows():
        label = f"{row['OCO']} | ID: {row['ID Solicitud']} | Nom: {row['Nombre solicitud']} | Item: {row['Item']}"
        value = row['OCO']  # El valor interno que se guardará
        opciones.append((label, value))
    return opciones

# ------------------------------------------------------
# 5. LÓGICA DE ACTUALIZACIÓN DE DROPDOWNS
# ------------------------------------------------------
def actualizar_oco_options(*args):
    """
    Callback que se dispara cuando cambia la sede o el tipo de solicitud.
    """
    sede_selected = sede_dropdown.value
    tipo_selected = tipo_solicitud_dropdown.value

    # Filtramos las OCO de la sede elegida
    # Suponiendo que en la columna 'División' (o 'Sede'?) figure la sede
    df_filtrado = df_ocos[df_ocos['División'] == sede_selected]

    # --- ORIGEN ---
    if "Aumento presupuesto" in tipo_selected:
        # Por defecto, la OCO de ahorro de la sede
        df_origen = df_filtrado[df_filtrado['EsAhorroSede'] == True]

        if len(df_origen) == 0:
            # No hay "EsAhorroSede" en esa sede, de modo que no tenemos OCO de ahorro
            oco_origen_dropdown.options = []
        else:
            oco_origen_dropdown.options = crear_opciones_oco(df_origen)
            # Selecciona el primero si existe
            oco_origen_dropdown.value = oco_origen_dropdown.options[0][1]

    else:
        # Muestra todas las OCO de la sede
        if len(df_filtrado) == 0:
            oco_origen_dropdown.options = []
        else:
            oco_origen_dropdown.options = crear_opciones_oco(df_filtrado)
            oco_origen_dropdown.value = oco_origen_dropdown.options[0][1]

    # --- DESTINO ---
    if "Disminución presupuesto" in tipo_selected:
        # Por defecto, la OCO de ahorro de la sede
        df_destino = df_filtrado[df_filtrado['EsAhorroSede'] == True]

        if len(df_destino) == 0:
            oco_destino_dropdown.options = []
        else:
            oco_destino_dropdown.options = crear_opciones_oco(df_destino)
            oco_destino_dropdown.value = oco_destino_dropdown.options[0][1]
    else:
        # Muestra todas las OCO de la sede
        if len(df_filtrado) == 0:
            oco_destino_dropdown.options = []
        else:
            oco_destino_dropdown.options = crear_opciones_oco(df_filtrado)
            oco_destino_dropdown.value = oco_destino_dropdown.options[0][1]

sede_dropdown.observe(actualizar_oco_options, 'value')
tipo_solicitud_dropdown.observe(actualizar_oco_options, 'value')

# ------------------------------------------------------
# 6. BOTÓN DE ENVÍO Y ALMACENAMIENTO DE SOLICITUDES
# ------------------------------------------------------
submit_button = widgets.Button(
    description='Enviar formulario',
    button_style='success',  # 'success', 'info', 'warning', 'danger' o ''
    layout=widgets.Layout(width='30%')
)

output = widgets.Output()

def on_submit_clicked(b):
    with output:
        output.clear_output()
        print("=== Resumen de la Solicitud ===")
        print(f"Sede: {sede_dropdown.value}")
        print(f"Tipo de Solicitud: {tipo_solicitud_dropdown.value}")
        print(f"OCO Origen: {oco_origen_dropdown.value}")
        print(f"OCO Destino: {oco_destino_dropdown.value}")
        print(f"Monto: {monto_text.value}")
        print(f"Mes de planificación: {mes_text.value}")

        # Mostrar archivos subidos, si los hay
        attached_files = []
        if adjuntos_upload.value:
            print("\nDocumentos adjuntos:")
            for fname, fdata in adjuntos_upload.value.items():
                print(f"- {fname}, {len(fdata['content'])} bytes")
                attached_files.append(fname)
        else:
            print("\nNo se adjuntaron documentos.")

        # Guardar en el "repositorio" (un Excel) con ticket consecutivo
        guardar_en_repo(
            sede=sede_dropdown.value,
            tipo_solicitud=tipo_solicitud_dropdown.value,
            oco_origen=oco_origen_dropdown.value,
            oco_destino=oco_destino_dropdown.value,
            monto=monto_text.value,
            mes=mes_text.value,
            archivos=attached_files
        )

        print("\n¡Formulario enviado correctamente (ejemplo)!")

submit_button.on_click(on_submit_clicked)

# ------------------------------------------------------
# 7. FUNCIÓN PARA GUARDAR EN EXCEL LAS RESPUESTAS
# ------------------------------------------------------
def guardar_en_repo(sede, tipo_solicitud, oco_origen, oco_destino, monto, mes, archivos):
    """
    Guarda en un Excel 'history.xlsx' la nueva fila, autogenerando
    un número de ticket consecutivo.
    """
    history_file = 'history.xlsx'

    # Si no existe el archivo, creamos un DF vacío con columnas definidas.
    if not os.path.exists(history_file):
        df_history = pd.DataFrame(columns=[
            'TicketID', 'Sede', 'TipoSolicitud', 'OCO_Origen', 'OCO_Destino',
            'Monto', 'Mes', 'Archivos'
        ])
        next_ticket = 1
    else:
        df_history = pd.read_excel(history_file)
        if df_history.empty:
            next_ticket = 1
        else:
            next_ticket = df_history['TicketID'].max() + 1

    # Crear la nueva fila
    new_row = {
        'TicketID': next_ticket,
        'Sede': sede,
        'TipoSolicitud': tipo_solicitud,
        'OCO_Origen': oco_origen,
        'OCO_Destino': oco_destino,
        'Monto': monto,
        'Mes': mes,
        'Archivos': '; '.join(archivos)  # Guárdalos como texto
    }

    # Agregar la nueva fila al DF
    df_history = pd.concat([df_history, pd.DataFrame([new_row])], ignore_index=True)
    # Guardar en Excel
    df_history.to_excel(history_file, index=False)
    print(f"--> Solicitud guardada con TicketID={next_ticket} en {history_file}")

# ------------------------------------------------------
# 8. MOSTRAR EL FORMULARIO FINAL
# ------------------------------------------------------
formulario = widgets.VBox([
    widgets.HTML("<h2>Formulario para solicitudes de traslado de presupuesto entre proyectos aprobados</h2>"),
    sede_dropdown,
    tipo_solicitud_dropdown,
    oco_origen_dropdown,
    oco_destino_dropdown,
    monto_text,
    mes_text,
    widgets.HTML("<b>Adjunte documentos de respaldo (cotizaciones, etc):</b>"),
    adjuntos_upload,
    submit_button,
    output
])

display(formulario)

# Dispara una primera actualización para poblar los dropdowns
actualizar_oco_options()