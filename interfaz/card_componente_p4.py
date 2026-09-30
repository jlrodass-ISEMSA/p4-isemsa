import tkinter as tk
from tkinter import ttk
from .ui_medidas_p4 import render_medidas_grid

# === Helper para imágenes de perfil ===
from .perfil_imagenes_p4 import safe_open_perfil_image

# ANCLA_INICIO: ORING_EXTERNO_CONSTANTES_P4
_PERFIL_ORING = "O-RING"
_FAB_EXTERNO = "EXTERNO"
_TIPO_COMP_SELLO = "SELLO"
_MATS_ORING_EXTERNO = ["NBR 70 Shore A", "FKM 75 Shore A", "EPDM 70 Shore A"]
# ANCLA_FINAL: ORING_EXTERNO_CONSTANTES_P4

# ANCLA_INICIO: DOCSTRING_CARD_COMPONENTE_P4
class CardComponente(ttk.LabelFrame):
    """
    Tarjeta genérica para un componente del kit.
    VERSIÓN P4:
    - Selector de perfil activo (readonly + selector)
    - Lógica desacoplada (sin LogicController)
    - Validaciones geométricas externas
    - Imágenes de perfil con zoom a demanda (doble click)
    """
# ANCLA_FINAL: DOCSTRING_CARD_COMPONENTE_P4

    def __init__(self, parent, titulo: str, tipo: str, on_delete=None):
        super().__init__(parent, text=titulo, padding=(8, 8))
        self.tipo = (tipo or "").upper().strip()
        self._on_delete = on_delete

        # ANCLA_INICIO: GRID_EMPujar_MEDIDAS_A_DERECHA_P4 (FIX)
        # Panel izquierdo (0-1): Material/Cantidad/Buscar
        # Columna 2: SEPARADOR expansible para empujar medidas+imagen a la derecha
        # Columna 3: Medidas (frame fijo)
        # Columna 4: Imagen (fija)
        try:
            self.columnconfigure(0, weight=0)
            self.columnconfigure(1, weight=0)
            self.columnconfigure(2, weight=1)   # <-- clave: empuja a la derecha
            self.columnconfigure(3, weight=0)
            self.columnconfigure(4, weight=0)
        except Exception:
            pass

        # Contenedor dedicado para medidas, anclado a la derecha
        self.frm_medidas = ttk.Frame(self)
        self.frm_medidas.grid(row=3, column=3, sticky="ne", padx=(10, 0), pady=(6, 0))
        # ANCLA_FINAL: GRID_EMPujar_MEDIDAS_A_DERECHA_P4 (FIX)

        # --- Declaración preventiva para Pylance (los builders asignan estos widgets) ---
        self.ent_perfil = None
        self.ent_material = None

        # ANCLA_INICIO: ORING_EXTERNO_ESTADO_INICIAL_P4
        self._oring_externo_activo = False
        # ANCLA_FINAL: ORING_EXTERNO_ESTADO_INICIAL_P4

        # ANCLA_INICIO: HEADER_TARJETA_P4 (PARCHE_G)
        from .ui_card_header_p4 import construir_header_perfil
        self.btn_buscar_perfil, _btn_del_header = construir_header_perfil(self, self._abrir_selector_perfil, self._pedir_eliminar)
        # ANCLA_FINAL: HEADER_TARJETA_P4 (PARCHE_G)

        # ANCLA_INICIO: RESTAURAR_BOTON_BUSCAR_PERFIL_P4_FINAL
        # Reubicar y DAR ANCHO REAL al botón "Buscar..."
        try:
            btn_buscar = None

            for w in self.winfo_children():
                try:
                    if isinstance(w, (ttk.Button, tk.Button)) and (w.cget("text") or "").strip().startswith("Buscar"):
                        btn_buscar = w
                        break
                except Exception:
                    continue

            if btn_buscar is not None:
                # Quitar del grid roto
                try:
                    btn_buscar.grid_forget()
                except Exception:
                    pass

                # Volver a colocar con ancho visible
                btn_buscar.grid(
                    row=0,
                    column=2,
                    sticky="w",
                    padx=(6, 0),
                    pady=2,
                    ipadx=10      # <<< ESTO ES LA CLAVE (ancho interno)
                )

                # Asegurar que la columna no lo aplaste
                try:
                    self.columnconfigure(2, minsize=120)
                except Exception:
                    pass
        except Exception:
            pass
        # ANCLA_FINAL: RESTAURAR_BOTON_BUSCAR_PERFIL_P4_FINAL

        # ANCLA_INICIO: PERFIL_ENTRY_READONLY_Y_BINDS_P4 (RESTORE_SELECTOR)
        # Restaurar comportamiento previo:
        # - El perfil NO se escribe a mano (evita basura).
        # - El selector siempre debe poder abrirse (doble click / Enter).
        try:
            if getattr(self, "ent_perfil", None):
                # 1) Bloquear edición manual
                try:
                    self.ent_perfil.configure(state="readonly")
                except Exception:
                    pass

                # 2) Atajos para abrir selector (si el botón Buscar queda incómodo)
                def _abrir_selector_evt(_evt=None):
                    try:
                        self._abrir_selector_perfil()
                    except Exception:
                        pass
                    return "break"

                self.ent_perfil.bind("<Double-Button-1>", _abrir_selector_evt)
                self.ent_perfil.bind("<Return>", _abrir_selector_evt)
        except Exception:
            pass
        # ANCLA_FINAL: PERFIL_ENTRY_READONLY_Y_BINDS_P4 (RESTORE_SELECTOR)

        # ---------- Imagen de perfil a la derecha ----------
        self._img_perfil = None
        self.lbl_img = ttk.Label(self, text="")
        # columna 3 reservada visualmente para la imagen
        # ANCLA_INICIO: IMG_FIJA_DERECHA_P4 (FIX)
        self.lbl_img.grid(row=1, column=4, rowspan=20, sticky="ne", padx=(20, 0), pady=(10, 0))
        # ANCLA_FINAL: IMG_FIJA_DERECHA_P4 (FIX)

        # ANCLA_INICIO: ZOOM_IMG_BIND_P4 (FIX)
        # Doble click sobre la imagen -> abrir zoom (no cambia tamaño estándar)
        try:
            self._perfil_img_actual = ""
            self.lbl_img.bind("<Double-Button-1>", lambda _e: self._abrir_zoom_imagen_perfil())
        except Exception:
            pass
        # ANCLA_FINAL: ZOOM_IMG_BIND_P4 (FIX)

        # ---------- FILA 1: MATERIAL (EXTRAÍDO A ui_materiales_p4.py) ----------
        from .ui_materiales_p4 import build_material_dmh
        build_material_dmh(self, fila=1, col_label=0, col_widget=1)

        # ---------- FILA 2: CANTIDAD ----------
        ttk.Label(self, text="Cantidad:").grid(row=2, column=0, sticky="e", padx=(0, 6), pady=2)
        self.var_cantidad = tk.IntVar(value=1)
        self.spn_cantidad = ttk.Spinbox(
            self, from_=1, to=999, width=5,
            textvariable=self.var_cantidad, justify="center"
        )
        self.spn_cantidad.grid(row=2, column=1, sticky="w", pady=2)

        # ---------- MEDIDAS DINÁMICAS POR PERFIL (INICIALIZACIÓN) ----------
        # No hay medidas genéricas. Este diccionario se llenará
        # únicamente cuando el técnico elija un perfil (A, A1, B, C, etc.).
        self.medidas_entries = {}
       
        # ANCLA_INICIO: CACHE_DIMENSIONAL_P4
        self._ultimo_resultado_dimensional = None
        # ANCLA_FINAL: CACHE_DIMENSIONAL_P4

        if self.tipo in ("VASTAGO", "PISTON"):
            frm_gap = ttk.Frame(self)
            frm_gap.grid(row=4, column=0, columnspan=2, sticky="w", pady=(4, 2))

            # Regla UI:
            # - VÁSTAGO: capturar SOLO D1
            # - PISTÓN:  capturar SOLO D2
            if self.tipo == "VASTAGO":
                ttk.Label(frm_gap, text="D1 (vástago):").grid(row=0, column=0, sticky="e", padx=(0, 4))
                self.ent_D1 = ttk.Entry(frm_gap, width=10)
                self.ent_D1.grid(row=0, column=1, sticky="w")

                # Solo D1 en esta tarjeta
                self.ent_D2 = None
                self.gap_entries = {"D1": self.ent_D1}

            else:  # PISTON
                ttk.Label(frm_gap, text="D2 (pistón):").grid(row=0, column=0, sticky="e", padx=(0, 4))
                self.ent_D2 = ttk.Entry(frm_gap, width=10)
                self.ent_D2.grid(row=0, column=1, sticky="w")

                # Solo D2 en esta tarjeta
                self.ent_D1 = None
                self.gap_entries = {"D2": self.ent_D2}

            # ANCLA_INICIO: BOTON_EVALUAR_GAP_P4 (REEMPLAZO)
            def _solicitar_gap_ahora():
                """
                P4:
                El botón NO calcula GAP dentro de la tarjeta.
                Solo solicita evaluación técnica al orquestador principal.

                Flujo esperado:
                CardComponente -> evento <<SolicitarEvaluacionGap>>
                App/orquestador -> preparación entrada -> GUIADO -> EXTRUSIÓN -> respuesta a la UI
                """
                try:
                    self._solicitar_gap_once = True
                    self.event_generate("<<SolicitarEvaluacionGap>>", when="tail")
                except Exception:
                    pass

            self.btn_gap = ttk.Button(frm_gap, text="Evaluar GAP", command=_solicitar_gap_ahora)
            self.btn_gap.grid(row=1, column=0, columnspan=2, sticky="w", pady=(3, 0))
            # ANCLA_FINAL: BOTON_EVALUAR_GAP_P4 (REEMPLAZO)

        else:
            self.gap_entries = {}

        # ANCLA_INICIO: BIND_CAMBIO_MEDIDAS (F1.1_REEMPLAZO)
        # Nota:
        # - Las medidas dinámicas (A/B/C/...) se bindean al crearse en ui_medidas_p4.py.
        # - Aquí solo se bindea GAP D1/D2, porque existe desde __init__ (VASTAGO/PISTON).
        try:
            for _entry in (self.gap_entries or {}).values():
                # GAP desactivado: D1/D2 no disparan validación automática
                pass
        except Exception:
            pass

        # ANCLA_FINAL: BIND_CAMBIO_MEDIDAS (F1.1_REEMPLAZO)

        # ANCLA_INICIO: ETIQUETA_GAP_P4_UI
        # tk.Message: wrap automático + auto-altura.
        # CLAVE: sincronizar el "width" (wraplength) con el ancho REAL del widget, para que NO se corte.

        self.lbl_gap = tk.Message(
            self,
            text="",
            width=1,          # <-- wrap dinámico (se ajusta en runtime)
            anchor="nw",
            justify="left",
            fg="black",
        )

        # IMPORTANTE:
        # - columnspan=5 para cubrir también la columna donde está la imagen (col 4)
        # - sticky="nwe" para que crezca horizontalmente
        self.lbl_gap.grid(
            row=999,
            column=0,
            columnspan=5,
            sticky="nwe",
            pady=(6, 0),
        )

        # Permitir que esta fila pueda crecer en altura si hay muchas líneas
        try:
            self.grid_rowconfigure(999, weight=1)
        except Exception:
            pass

        # Sincronizar el wraplength con el ancho real visible del Message
        def _sync_wrap(_evt=None):
            try:
                w = self.lbl_gap.winfo_width()
                if w and w > 20:
                    # margen para evitar corte por padding interno/bordes
                    self.lbl_gap.configure(width=max(w - 10, 20))
            except Exception:
                pass

        # Cada vez que cambie el tamaño del widget, recalcula el wrap
        self.lbl_gap.bind("<Configure>", _sync_wrap)

        # ANCLA_FINAL: ETIQUETA_GAP_P4_UI

        # ---------- FILA 5: NOTAS ----------
        ttk.Label(self, text="Notas:").grid(row=5, column=0, sticky="ne", padx=(0, 6), pady=(6, 2))
        self.txt_notas = tk.Text(self, width=40, height=3)
        self.txt_notas.grid(row=5, column=1, sticky="we", pady=(6, 2))

        # ANCLA_INICIO: PLANO_REFERENCIA_P4
        # Universal (todas las tarjetas, no solo ESPECIAL). NEXO no almacena
        # ni incrusta el archivo — solo referencia la ruta al servidor de
        # dibujos de ISEMSA (hoy Z:\DIBUJOS ISEMSA\..., puede moverse por IT
        # en cualquier momento; NEXO no asume ninguna ruta base fija).
        ttk.Label(self, text="Plano de referencia:").grid(
            row=90, column=0, sticky="e", padx=(0, 6), pady=(6, 2))
        self.ent_plano_referencia = ttk.Entry(self, width=45)
        self.ent_plano_referencia.grid(row=90, column=1, sticky="w", pady=(6, 2))

        def _abrir_plano_referencia():
            ruta = (self.ent_plano_referencia.get() or "").strip()
            if not ruta:
                return
            try:
                import os
                os.startfile(ruta)
            except Exception:
                pass

        ttk.Button(self, text="Abrir", width=8, command=_abrir_plano_referencia).grid(
            row=90, column=2, sticky="w", padx=(6, 0), pady=(6, 2))
        # ANCLA_FINAL: PLANO_REFERENCIA_P4

        # ANCLA_INICIO: PIEZA_ESPECIAL_TIPO_COMPONENTE_P4
        # Exclusivo para tarjetas "ESPECIAL" (Pieza Especial). Arquitectura
        # libre: no restringido a los 105 perfiles de catálogo. El tipo de
        # componente determina qué validaciones posteriores aplican
        # (motor de material, fabricabilidad interna de torno).
        if self.tipo == "ESPECIAL":
            ttk.Label(self, text="Tipo de pieza:").grid(row=6, column=0, sticky="e", padx=(0, 6), pady=(6, 2))
            self.var_tipo_componente = tk.StringVar(value="SELLO")
            self.cbo_tipo_componente = ttk.Combobox(
                self,
                textvariable=self.var_tipo_componente,
                state="readonly",
                width=22,
                values=["SELLO", "ESTRUCTURAL", "EXTRUIDO_COMERCIAL", "OTRO"],
            )
            self.cbo_tipo_componente.grid(row=6, column=1, sticky="w", pady=(6, 2))

            ttk.Label(self, text="Quién fabrica:").grid(row=7, column=0, sticky="e", padx=(0, 6), pady=(6, 2))
            self.var_quien_fabrica = tk.StringVar(value="ISEMSA")
            self.cbo_quien_fabrica = ttk.Combobox(
                self,
                textvariable=self.var_quien_fabrica,
                state="readonly",
                width=22,
                values=["ISEMSA", "EXTERNO"],
            )
            self.cbo_quien_fabrica.grid(row=7, column=1, sticky="w", pady=(6, 2))

            # ANCLA_INICIO: ORING_EXTERNO_WIDGETS_P4
            # Solo visibles con SELLO + perfil O-RING + EXTERNO (ver
            # _actualizar_widgets_oring_externo). Se construyen con grid() y se
            # ocultan con grid_remove() para que al re-mostrarlos con grid()
            # conserven fila/columna.
            self.lbl_oring_externo = ttk.Label(self, text="O-RING (AS 568 / ISO 3601):")
            self.lbl_oring_externo.grid(row=10, column=0, sticky="e", padx=(0, 6), pady=(6, 2))
            self.var_codigo_oring_externo = tk.StringVar(value="")
            self.ent_codigo_oring_externo = ttk.Entry(
                self, textvariable=self.var_codigo_oring_externo, state="readonly", width=25,
            )
            self.ent_codigo_oring_externo.grid(row=10, column=1, sticky="w", pady=(6, 2))
            self.btn_buscar_oring = ttk.Button(
                self, text="Buscar O-RING", command=self._abrir_selector_oring_externo,
            )
            self.btn_buscar_oring.grid(row=10, column=2, sticky="w", padx=(6, 0), pady=(6, 2))
            self.var_back_up_as574 = tk.BooleanVar(value=False)
            self.chk_back_up = ttk.Checkbutton(
                self, text="Lleva back-up AS 574", variable=self.var_back_up_as574,
            )
            self.chk_back_up.grid(row=11, column=1, columnspan=2, sticky="w", pady=(2, 2))
            for _w in (self.lbl_oring_externo, self.ent_codigo_oring_externo,
                       self.btn_buscar_oring, self.chk_back_up):
                _w.grid_remove()
            # ANCLA_FINAL: ORING_EXTERNO_WIDGETS_P4

            # ANCLA_INICIO: VALIDACION_MANUAL_ESTRUCTURAL_P4 (Capa 2, HALLAZGO CRÍTICO DE SEGURIDAD)
            # Solo visible para ESTRUCTURAL — trazabilidad de quién revisó el
            # riesgo de corrosión antes de aprobar. NO bloquea (decisión del
            # usuario, 16/09/2026): mismo patrón que "+ Elemento adicional",
            # solo alerta si queda vacío al generar el reporte.
            ttk.Label(self, text="Validado por:").grid(row=8, column=0, sticky="e", padx=(0, 6), pady=(6, 2))
            self.ent_validado_por = ttk.Entry(self, width=25)
            self.ent_validado_por.grid(row=8, column=1, sticky="w", pady=(6, 2))

            ttk.Label(self, text="Fecha de validación:").grid(row=8, column=2, sticky="e", padx=(15, 6), pady=(6, 2))
            self.ent_fecha_validacion = ttk.Entry(self, width=14)
            self.ent_fecha_validacion.grid(row=8, column=3, sticky="w", pady=(6, 2))

            ttk.Label(self, text="Nota de validación:").grid(row=9, column=0, sticky="ne", padx=(0, 6), pady=(6, 2))
            self.txt_nota_validacion = tk.Text(self, width=40, height=2)
            self.txt_nota_validacion.grid(row=9, column=1, columnspan=3, sticky="we", pady=(6, 2))

            def _mostrar_ocultar_validacion_manual(*_):
                tipo_actual = (self.var_tipo_componente.get() or "").strip()
                # ANCLA_INICIO: REGLA_TIPO_PIEZA_ESPECIAL_P4_CONSOLIDADA
                # Decisión consolidada (17/09/2026, caso "PERFIL ESP. LINEA
                # 56" + amortiguador OTRO): solo SELLO tiene perfil de
                # catálogo (105) y evaluación real de material. Los otros
                # tres (EXTRUIDO_COMERCIAL/ESTRUCTURAL/OTRO) siempre
                # requieren validación manual del material, capturan Perfil
                # como nombre/identificador libre, y muestran los campos de
                # trazabilidad (Validado por/Fecha/Nota) — sin excepción,
                # aunque STAMP corra distinto para cada uno (normal/con
                # reservas/nunca, eso se resuelve en preparacion_entrada_p4.py,
                # no aquí).
                requiere_validacion = tipo_actual != "SELLO"
                widgets_validacion = [
                    self.ent_validado_por, self.ent_fecha_validacion, self.txt_nota_validacion,
                ]
                for w in widgets_validacion:
                    try:
                        if requiere_validacion:
                            w.grid()
                        else:
                            w.grid_remove()
                    except Exception:
                        pass

                try:
                    if tipo_actual == "SELLO":
                        self.ent_perfil.configure(state="readonly")
                        self.lbl_perfil.configure(text="Perfil:")
                        if getattr(self, "btn_buscar_perfil", None):
                            self.btn_buscar_perfil.grid()
                    else:
                        self.ent_perfil.configure(state="normal")
                        self.lbl_perfil.configure(text="Nombre/Identificador:")
                        if getattr(self, "btn_buscar_perfil", None):
                            self.btn_buscar_perfil.grid_remove()
                except Exception:
                    pass

                # Material: solo SELLO ofrece dropdown de catálogo DMH.
                # Los otros 3 tipos son texto libre sin sugerencias, porque
                # su material real (ej. "Neopreno 50 Shore A") vive fuera
                # del universo DMH por completo — no es que falte el dato,
                # es que el catálogo nunca fue construido para ese dominio.
                try:
                    if hasattr(self, "cbo_material") and self.cbo_material:
                        if tipo_actual == "SELLO":
                            self.cbo_material["values"] = self._materiales_catalogo or []
                        else:
                            self.cbo_material["values"] = []
                except Exception:
                    pass

                # ANCLA_INICIO: AYUDA_TIPO_PIEZA_ESPECIAL_P4
                textos_ayuda = {
                    "SELLO": "Sello que puede ser parte de un cilindro hidráulico/neumático o de una "
                             "válvula. Se elige perfil por similitud con los 105 catalogados.",
                    "EXTRUIDO_COMERCIAL": "Perfil extruido lineal para sellar compuertas u otras "
                             "aplicaciones — no es uno de los 105 perfiles de cilindro. "
                             "Ej: empaque de compuerta de autoclave.",
                    "ESTRUCTURAL": "Pieza de metal o plástico de ingeniería que va dentro de un "
                             "cilindro (no es sello). Ej: pistón de aluminio.",
                    "OTRO": "Pieza que no va dentro de ningún cilindro. "
                             "Ej: amortiguador de vibrador, tope de hule.",
                }
                # ANCLA_INICIO: AYUDA_NOMBRE_MATERIAL_CONECTADA_TIPO_PIEZA_P4
                # Conectada al mismo tipo_actual que "Tipo de pieza" arriba,
                # con los mismos ejemplos, para que ambos textos se lean como
                # continuidad, no como ayudas desconectadas (decisión del
                # usuario, 17/09/2026).
                textos_ayuda_nombre_material = {
                    "EXTRUIDO_COMERCIAL": "Nombre/Identificador: cómo llamas a este perfil "
                             "(ej. 'Empaque extruido para compuerta'). Material: el material real "
                             "del perfil, tal como te lo indicó el proveedor "
                             "(ej. 'Silicón gris 45 Shore A').",
                    "ESTRUCTURAL": "Nombre/Identificador: qué pieza es dentro del cilindro "
                             "(ej. 'Pistón interno', 'Camisa guía'). Material: el metal o plástico, "
                             "tal como te lo indicó el proveedor (ej. 'Aluminio', 'SAE 1045').",
                    "OTRO": "Nombre/Identificador: qué es la pieza "
                             "(ej. 'Amortiguador de vibrador', 'Tope de hule'). "
                             "Material: de qué está hecha (ej. 'Hule 70 Shore A').",
                }
                if not hasattr(self, "lbl_ayuda_nombre_material"):
                    self.lbl_ayuda_nombre_material = ttk.Label(
                        self, text="", foreground="#555555",
                        wraplength=480, justify="left", font=("Segoe UI", 8, "italic"),
                    )
                    self.lbl_ayuda_nombre_material.grid(
                        row=0, column=2, columnspan=3, sticky="nw", padx=(15, 0), pady=(2, 2)
                    )
                self.lbl_ayuda_nombre_material.configure(
                    text=textos_ayuda_nombre_material.get(tipo_actual, "")
                )
                # ANCLA_FINAL: AYUDA_NOMBRE_MATERIAL_CONECTADA_TIPO_PIEZA_P4
                if not hasattr(self, "lbl_ayuda_tipo_pieza"):
                    self.lbl_ayuda_tipo_pieza = ttk.Label(
                        self, text="", foreground="#555555",
                        wraplength=520, justify="left", font=("Segoe UI", 8, "italic"),
                    )
                    self.lbl_ayuda_tipo_pieza.grid(
                        row=6, column=2, columnspan=3, sticky="w", padx=(15, 0), pady=(6, 2)
                    )
                self.lbl_ayuda_tipo_pieza.configure(text=textos_ayuda.get(tipo_actual, ""))
                # ANCLA_FINAL: AYUDA_TIPO_PIEZA_ESPECIAL_P4

                # ANCLA_INICIO: FLUIDO_TEMP_CAPTURA_SIN_MOTOR_P4
                # Solo EXTRUIDO_COMERCIAL/ESTRUCTURAL — captura simple de
                # Fluido/Temperatura para revisión experta humana, SIN motor
                # de evaluación (ver STAMP_PIEZA_ESPECIAL_P4.docx §3: sin
                # laboratorio, ISEMSA no puede verificar identidad exacta de
                # material declarado por el cliente; cualquier motor
                # automático sería apariencia de cálculo sin base real).
                # SELLO usa el panel STAMP compartido de kit (motor completo,
                # sin cambios). OTRO no captura estos campos en absoluto.
                if not hasattr(self, "lbl_fluido_especial"):
                    self.lbl_fluido_especial = ttk.Label(self, text="Fluido (referencia):")
                    self.lbl_fluido_especial.grid(row=95, column=0, sticky="e", padx=(0, 6), pady=(6, 2))
                                        # ANCLA_INICIO: FLUIDO_ESPECIAL_AUTOCOMPLETADO_CAPA3_P4
                    # Antes: Entry de texto libre -- riesgo real de error de
                    # tipeo que Capa 3 (COMPATIBILIDAD_METAL_FLUIDO_P4) nunca
                    # podria encontrar, sin que el tecnico se entere. Ahora:
                    # Combobox con lista real combinada de Flowserve+Bal Seal,
                    # filtrado al escribir -- mismo patron que el Fluido de
                    # STAMP normal (ui_condiciones_p4.py). NUNCA bloquea
                    # (state="normal"): el tecnico puede seguir escribiendo
                    # algo fuera de catalogo si es necesario, pero ve las
                    # opciones reales mientras tipea.
                    try:
                        from datos.catalogo_metal_fluido_p4 import NOMBRES_FLUIDOS_CAPA3
                        _opciones_fluido_especial = NOMBRES_FLUIDOS_CAPA3
                    except Exception:
                        _opciones_fluido_especial = []

                    self.ent_fluido_especial = ttk.Combobox(
                        self, width=25, state="normal", values=_opciones_fluido_especial,
                    )
                    self.ent_fluido_especial.grid(row=95, column=1, sticky="w", pady=(6, 2))

                    def _filtrar_fluido_especial(_ev=None):
                        try:
                            texto = (self.ent_fluido_especial.get() or "").lower()
                            if not texto:
                                self.ent_fluido_especial["values"] = _opciones_fluido_especial
                            else:
                                self.ent_fluido_especial["values"] = (
                                    [f for f in _opciones_fluido_especial if texto in f.lower()]
                                    or _opciones_fluido_especial
                                )
                        except Exception:
                            pass

                    self.ent_fluido_especial.bind("<KeyRelease>", _filtrar_fluido_especial, add="+")
                    # ANCLA_FINAL: FLUIDO_ESPECIAL_AUTOCOMPLETADO_CAPA3_P4

                    self.lbl_temp_especial = ttk.Label(self, text="Temperatura (°C, referencia):")
                    self.lbl_temp_especial.grid(row=95, column=2, sticky="e", padx=(15, 6), pady=(6, 2))
                    self.ent_temp_especial = ttk.Entry(self, width=14)
                    self.ent_temp_especial.grid(row=95, column=3, sticky="w", pady=(6, 2))

                requiere_fluido_temp = tipo_actual in ("EXTRUIDO_COMERCIAL", "ESTRUCTURAL")
                for w in (self.lbl_fluido_especial, self.ent_fluido_especial,
                          self.lbl_temp_especial, self.ent_temp_especial):
                    try:
                        if requiere_fluido_temp:
                            w.grid()
                        else:
                            w.grid_remove()
                    except Exception:
                        pass

                # ANCLA_INICIO: METAL_CAPA3_ESTRUCTURAL_P4
                # Solo ESTRUCTURAL -- dropdown SEPARADO del campo "Material"
                # (texto libre, ver arriba). "Material" es la nota real del
                # proveedor; este dropdown clasifica en una de las 6 claves
                # exactas del catálogo Capa 3 (COMPATIBILIDAD_METAL_FLUIDO_P4),
                # nunca por coincidencia aproximada de texto.
                if not hasattr(self, "lbl_metal_capa3"):
                    self.lbl_metal_capa3 = ttk.Label(self, text="Metal (catálogo Capa 3):")
                    self.lbl_metal_capa3.grid(row=96, column=0, sticky="e", padx=(0, 6), pady=(6, 2))
                    self.var_metal_capa3 = tk.StringVar(value="")
                    self.cbo_metal_capa3 = ttk.Combobox(
                        self, textvariable=self.var_metal_capa3, state="readonly", width=30,
                        values=[
                            "", "302", "304", "316",
                            "AceroCarbono_12614Leadloy", "Aluminio", "Bronce_Aluminio",
                        ],
                    )
                    self.cbo_metal_capa3.grid(row=96, column=1, columnspan=2, sticky="w", pady=(6, 2))

                requiere_metal_capa3 = tipo_actual == "ESTRUCTURAL"
                for w in (self.lbl_metal_capa3, self.cbo_metal_capa3):
                    try:
                        if requiere_metal_capa3:
                            w.grid()
                        else:
                            w.grid_remove()
                    except Exception:
                        pass

                # ANCLA_INICIO: AYUDA_MATERIAL_VS_METAL_CAPA3_P4
                # Distinción explícita (decisión del usuario, 17/09/2026):
                # Material = evidencia dura de campo (lo que el proveedor
                # dijo, aunque sea impreciso). Metal = decisión experta del
                # técnico, basada en su conocimiento del STAMP y el equipo —
                # es la que NEXO usa para procesar Capa 3, no el texto libre.
                if not hasattr(self, "lbl_ayuda_metal_capa3"):
                    self.lbl_ayuda_metal_capa3 = ttk.Label(
                        self, text="", foreground="#555555",
                        wraplength=480, justify="left", font=("Segoe UI", 8, "italic"),
                    )
                    self.lbl_ayuda_metal_capa3.grid(
                        row=96, column=3, columnspan=2, sticky="w", padx=(15, 0), pady=(6, 2)
                    )
                if requiere_metal_capa3:
                    self.lbl_ayuda_metal_capa3.configure(
                        text="Material (arriba) = lo que te dijeron en campo, tal cual, "
                             "aunque sea impreciso. Metal (aquí) = tu decisión experta según "
                             "el equipo y el STAMP — esta es la que NEXO usa para evaluar "
                             "compatibilidad, no el texto libre de arriba."
                    )
                    self.lbl_ayuda_metal_capa3.grid()
                else:
                    self.lbl_ayuda_metal_capa3.grid_remove()
                # ANCLA_FINAL: AYUDA_MATERIAL_VS_METAL_CAPA3_P4
                # ANCLA_FINAL: METAL_CAPA3_ESTRUCTURAL_P4
                # ANCLA_FINAL: FLUIDO_TEMP_CAPTURA_SIN_MOTOR_P4
                # ANCLA_FINAL: REGLA_TIPO_PIEZA_ESPECIAL_P4_CONSOLIDADA

            self.cbo_tipo_componente.bind("<<ComboboxSelected>>", _mostrar_ocultar_validacion_manual, add="+")
            _mostrar_ocultar_validacion_manual()
            # ANCLA_FINAL: VALIDACION_MANUAL_ESTRUCTURAL_P4

            # ANCLA_INICIO: ORING_EXTERNO_ENGANCHE_P4
            # Esta función (_actualizar_widgets_oring_externo) se llama en estos puntos:
            # 1. Al final de _callback en _abrir_selector_perfil (forzar=True)
            # 2. trace_add de var_quien_fabrica (abajo)
            # 3. Cambio de "Tipo de pieza" (bind abajo, forzar=True; se registra DESPUÉS
            #    del handler existente para correr una vez que éste ya fijó los materiales)
            # 4. Una vez al final de este bloque (sincroniza el estado inicial)
            # Si se agrega reset o carga de registros, llamar con forzar=True ahí también.
            self.var_quien_fabrica.trace_add("write", self._actualizar_widgets_oring_externo)
            self.cbo_tipo_componente.bind(
                "<<ComboboxSelected>>",
                lambda _e=None: self._actualizar_widgets_oring_externo(forzar=True),
                add="+",
            )
            self._actualizar_widgets_oring_externo()
            # ANCLA_FINAL: ORING_EXTERNO_ENGANCHE_P4
        # ANCLA_FINAL: PIEZA_ESPECIAL_TIPO_COMPONENTE_P4
  
    # ANCLA_INICIO: METODO_NOTIFICAR_CAMBIO_MEDIDAS (NUEVO)
    def _notificar_cambio_medidas(self, event=None):
        """
        Notifica al contenedor (App) que cambiaron las medidas de esta tarjeta.
        No hace la validación aquí; solo dispara un evento lógico que luego
        usará la App para validar todo el kit.
        """
        try:
            self.event_generate("<<MedidasCambiadas>>", when="tail")
        except Exception:
            pass
    # ANCLA_FINAL: METODO_NOTIFICAR_CAMBIO_MEDIDAS (NUEVO)

    # ANCLA_INICIO: DISPARO_GAP_P4_UI
    def actualizar_gap(self, info_gap):
        """
        Recibe la info del flujo de validación/evaluación y actualiza el estado GAP
        en esta tarjeta.

        Regla PASO 1:
        - Si info_gap es None, NO se borra el label (se mantiene el último resultado).
        """
        try:
            if info_gap is None:
                return
            self.mostrar_estado_gap(info_gap)
        except Exception:
            # Falla silenciosa para no bloquear la UI
            pass
    # ANCLA_FINAL: DISPARO_GAP_P4_UI

    # ANCLA_INICIO: ZOOM_IMG_GUARDAR_PERFIL_P4 (FIX)
    def _render_imagen_perfil(self, perfil_text: str):
        """
        Usa safe_open_perfil_image para cargar la imagen del perfil
        y la asigna al Label reservado en la tarjeta.
        """
        # Guardar el último perfil renderizado (para zoom a demanda)
        self._perfil_img_actual = (perfil_text or "").strip()

        img = safe_open_perfil_image(perfil_text)
        if img is not None:
            self._img_perfil = img
            self.lbl_img.configure(image=self._img_perfil, text="")
            self.lbl_img.image = self._img_perfil  # mantener referencia
        else:
            self._img_perfil = None
            self.lbl_img.configure(image="", text="")
            self.lbl_img.image = None
    # ANCLA_FINAL: ZOOM_IMG_GUARDAR_PERFIL_P4 (FIX)
    
    # ANCLA_INICIO: ZOOM_IMG_METODO_P4
    def _abrir_zoom_imagen_perfil(self):
        """
        Abre una ventana con la imagen del perfil en tamaño grande.
        No altera el tamaño estándar de las tarjetas.
        """
        try:
            perfil = (getattr(self, "_perfil_img_actual", "") or "").strip()
            if not perfil:
                return

            win = tk.Toplevel(self)
            win.title(f"Zoom perfil: {perfil}")
            win.transient(self.winfo_toplevel())
            win.grab_set()

            # Cargar imagen grande (si el helper no soporta tamaño, no rompe)
            try:
                img_big = safe_open_perfil_image(perfil, max_width=900, max_height=650)
            except TypeError:
                img_big = safe_open_perfil_image(perfil)

            lbl = ttk.Label(win, image=img_big)
            lbl.image = img_big  # mantener referencia
            lbl.pack(padx=10, pady=10)

        except Exception:
            pass
    # ANCLA_FINAL: ZOOM_IMG_METODO_P4

    # ANCLA_INICIO: MATERIALES_POR_PERFIL_P4 (NUEVO)
    def _actualizar_materiales_por_perfil(self, codigo_perfil: str):
        """
        Ajusta el/los selectores de material según datos.materiales_requeridos_por_perfil.
        Global y automático: no es por sello manual, es por perfil.
        """
        codigo = (codigo_perfil or "").strip().upper()
        try:
            from funciones.materiales.materiales_requeridos_por_perfil_p4 import materiales_requeridos_por_perfil
            n = int(materiales_requeridos_por_perfil.get(codigo, 1))
        except Exception:
            n = 1

        try:
            from .ui_materiales_p4 import build_material_dmh, build_materiales_dmh

            if n <= 1:
                build_material_dmh(self, fila=1, col_label=0, col_widget=1)
            else:
                labels = [f"M{i+1}" for i in range(n)]
                build_materiales_dmh(self, n_materiales=n, fila=1, col_label=0, col_widget=1, labels=labels)

        except Exception as e:
            try:
                print("[ERROR] _actualizar_materiales_por_perfil:", e)
            except Exception:
                pass
    # ANCLA_FINAL: MATERIALES_POR_PERFIL_P4 (NUEVO)
    
    # ANCLA_INICIO: FIX_RECONSTRUIR_MEDIDAS_ENTRIES_DESDE_FRAME (NUEVO)
    def _reconstruir_medidas_entries_desde_frame(self, letras=None):
        """
        Reconstruye self.medidas_entries SIN asumir grid/pack ni hijos directos.
        Estrategia:
        - Captura todos los ttk.Entry dentro de frm_medidas (recursivo).
        - Si se pasa `letras` (lista esperada A/A1/B/...), asigna por orden.
        """
        # 1) Capturar entries recursivamente
        entries = []

        def _walk(w):
            try:
                kids = w.winfo_children()
            except Exception:
                kids = []
            for k in kids:
                if isinstance(k, (ttk.Entry, tk.Entry)):
                    entries.append(k)
                _walk(k)

        try:
            _walk(self.frm_medidas)
        except Exception:
            entries = []

        # 2) Mapear cada Entry por su atributo .winfo_name()
        out = {}
        try:
            letras = [str(x).strip().upper() for x in (letras or []) if str(x).strip()]
            # Primero: por nombre explícito (más robusto)
            for ent in entries:
                try:
                    nm = ent.winfo_name().strip().upper()
                except Exception:
                    nm = ""
                if nm in letras:
                    out[nm] = ent

            # Segundo: completar por orden si faltan claves
            if letras:
                for i, letra in enumerate(letras):
                    if letra not in out and i < len(entries):
                        out[letra] = entries[i]
        except Exception:
            out = {}

        # 3) Si no hay letras, devolver vacío (no inventar llaves)
        return out
    # ANCLA_FINAL: FIX_RECONSTRUIR_MEDIDAS_ENTRIES_DESDE_FRAME (NUEVO)

    # ANCLA_INICIO: ACTUALIZAR_MEDIDAS_POR_PERFIL_P4_CORREGIDO
    def _actualizar_medidas_por_perfil(self, codigo_perfil: str):
        """
        Crea las medidas del perfil según catálogo de dimensiones y criterio vigente de O-ring.
        Reubica imagen y evita solapamientos.
        """
        if not codigo_perfil:
            return

        from .perfil_medidas_p4 import resolver_letras_medidas
        letras = resolver_letras_medidas(codigo_perfil)

        # ANCLA_INICIO: LIMPIAR_GAP_AL_CAMBIAR_PERFIL_P4
        try:
            self.lbl_gap.config(text="", foreground="black", font=("Segoe UI", 9, "normal"))
        except Exception:
            pass
        # ANCLA_FINAL: LIMPIAR_GAP_AL_CAMBIAR_PERFIL_P4

        # ANCLA_INICIO: MEDIDAS_EN_FRAME_DERECHA_P4_UI (FIX)
        # Renderizar dentro del frame anclado a la derecha,
        # pero guardar SIEMPRE el dict en la tarjeta (self).
        try:
            render_medidas_grid(self, letras, fila=0, col=0, entry_width=8, parent=self.frm_medidas)
        except Exception:
            pass
        # ANCLA_FINAL: MEDIDAS_EN_FRAME_DERECHA_P4_UI (FIX)

        # ANCLA_INICIO: RECONSTRUIR_DICT_MEDIDAS_ENTRIES_P4 (HOTFIX)
        # 1) reconstruir el dict con los Entry dentro del frame
        self.medidas_entries = self._reconstruir_medidas_entries_desde_frame(letras)

        # 2) forzar evento de validación inicial
        self._notificar_cambio_medidas()
        # ANCLA_FINAL: RECONSTRUIR_DICT_MEDIDAS_ENTRIES_P4 (HOTFIX)

        # ANCLA_INICIO: FIX_BIND_TECLADO_MEDIDAS_P4_UI (OFICIAL)
        # Ejecutar validación inicial
        self._notificar_cambio_medidas()

        # Asegurar refresco al teclear / salir del campo
        # (no toca reglas de coma/punto)
        try:
            def _evt_medidas(_evt=None):
                try:
                    self._notificar_cambio_medidas()
                except Exception:
                    pass

            if isinstance(getattr(self, "medidas_entries", None), dict):
                for _k, _pair in self.medidas_entries.items():
                    try:
                        _ent = _pair[1] if isinstance(_pair, (tuple, list)) and len(_pair) == 2 else _pair
                        _ent.bind("<KeyRelease>", _evt_medidas, add="+")
                        _ent.bind("<FocusOut>", _evt_medidas, add="+")
                    except Exception:
                        continue

        except Exception:
            pass
        # ANCLA_FINAL: FIX_BIND_TECLADO_MEDIDAS_P4_UI (OFICIAL)

        # ANCLA_FINAL: ACTUALIZAR_MEDIDAS_POR_PERFIL_P4_CORREGIDO
    
    def _abrir_selector_perfil(self):
        """
        Abre el selector de perfiles y coloca el perfil seleccionado en el Entry.
        Luego notifica a la App que cambió el perfil para que se vuelvan a evaluar
        las validaciones geométricas que ya existen.
        """
        try:
            from interfaz.selector_perfil_p4 import SelectorPerfil
            from datos.dimensiones_por_perfil_p4 import dimensiones_por_perfil
            import os

            # Ruta de imágenes que usa el selector (igual que antes)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            images_dir = os.path.join(os.path.dirname(base_dir), "imagenes")
        except Exception as e:
            print("[ERROR] No se pudo cargar selector o catálogo:", e)
            return

        def _callback(codigo, _medidas=None):
            codigo = (codigo or "").strip()

            # ANCLA_INICIO: PERFIL_SET_READONLY_SAFE_P4_UI (RESTORE_SELECTOR)
            try:
                if getattr(self, "ent_perfil", None):
                    self.ent_perfil.configure(state="normal")
            except Exception:
                pass
            # ANCLA_FINAL: PERFIL_SET_READONLY_SAFE_P4_UI (RESTORE_SELECTOR)

            # 1) Mostrar el perfil seleccionado
            self.ent_perfil.delete(0, "end")
            self.ent_perfil.insert(0, codigo)

            # ANCLA_INICIO: PERFIL_VOLVER_READONLY_P4_UI (RESTORE_SELECTOR)
            try:
                if getattr(self, "ent_perfil", None):
                    self.ent_perfil.configure(state="readonly")
            except Exception:
                pass
            # ANCLA_FINAL: PERFIL_VOLVER_READONLY_P4_UI (RESTORE_SELECTOR)

            # 2) Actualizar medidas según catálogo
            self._actualizar_medidas_por_perfil(codigo)

            # ANCLA_INICIO: HOOK_MATERIALES_TRAS_PERFIL_P4_UI (NUEVO)
            self._actualizar_materiales_por_perfil(codigo)
            # ANCLA_FINAL: HOOK_MATERIALES_TRAS_PERFIL_P4_UI (NUEVO)

            # 3) Mostrar imagen del perfil
            self._render_imagen_perfil(codigo)

            # 4) Disparar validaciones/GAP
            self._notificar_cambio_medidas()

            # ANCLA_INICIO: ORING_EXTERNO_HOOK_CALLBACK_P4
            # forzar=True: _actualizar_materiales_por_perfil acaba de reconstruir
            # el selector de material con catálogo DMH; si el modo O-RING externo
            # sigue activo hay que volver a imponer NBR/FKM/EPDM.
            self._actualizar_widgets_oring_externo(forzar=True)
            # ANCLA_FINAL: ORING_EXTERNO_HOOK_CALLBACK_P4

        SelectorPerfil(self, dimensiones_por_perfil, _callback, images_dir, self.tipo)

    # ANCLA_INICIO: ORING_EXTERNO_METODOS_P4
    def _limpiar_material_ui(self):
        """Vacía la selección de material (combobox único o entry)."""
        w = getattr(self, "cbo_material", None) or getattr(self, "ent_material", None)
        if w is None:
            return
        try:
            w.set("")
        except Exception:
            try:
                w.delete(0, "end")
            except Exception:
                pass

    def _actualizar_widgets_oring_externo(self, *_, forzar=False):
        """
        Modo "O-RING de compra externa": SELLO + perfil O-RING + Quién fabrica EXTERNO.
        Evalúa las tres condiciones juntas (el técnico puede cambiarlas en cualquier
        orden) y muestra/oculta Buscar O-RING, back-up AS 574 y materiales de mercado.

        forzar=True: reaplicar aunque el estado no haya cambiado, porque el caller
        acaba de reconstruir los materiales (ver _callback del selector de perfil).
        """
        var_fab = getattr(self, "var_quien_fabrica", None)
        if var_fab is None:  # solo existe en tarjetas ESPECIAL
            return
        try:
            ent_perfil = getattr(self, "ent_perfil", None)
            perfil = (ent_perfil.get() if ent_perfil else "").strip().upper()
            fabrica = (var_fab.get() or "").strip().upper()
            var_tipo = getattr(self, "var_tipo_componente", None)
            tipo_comp = (var_tipo.get() if var_tipo else "").strip().upper()
        except Exception:
            return

        activo = (perfil == _PERFIL_ORING and fabrica == _FAB_EXTERNO
                  and tipo_comp == _TIPO_COMP_SELLO)
        cambio = activo != getattr(self, "_oring_externo_activo", False)
        if not cambio and not forzar:
            return  # sin cambio de estado: no tocar nada (no perder el material elegido)
        self._oring_externo_activo = activo

        widgets = [getattr(self, n, None) for n in
                   ("lbl_oring_externo", "ent_codigo_oring_externo", "btn_buscar_oring", "chk_back_up")]
        cbo = getattr(self, "cbo_material", None)

        if activo:
            for w in widgets:
                if w is not None:
                    w.grid()
            if cbo is not None:
                try:
                    cbo["values"] = _MATS_ORING_EXTERNO
                except Exception:
                    pass
            if cambio:  # el material DMH previo ya no es válido
                self._limpiar_material_ui()
            return

        for w in widgets:
            if w is not None:
                w.grid_remove()
        try:
            self.var_codigo_oring_externo.set("")
            self.var_back_up_as574.set(False)
        except Exception:
            pass
        if cambio:
            self._limpiar_material_ui()
            # Con forzar=True el caller ya dejó los materiales correctos.
            if not forzar:
                self._restaurar_materiales_dmh()

    def _restaurar_materiales_dmh(self):
        """Devuelve el selector de material al catálogo DMH del perfil actual (solo SELLO)."""
        try:
            if (self.var_tipo_componente.get() or "").strip().upper() != _TIPO_COMP_SELLO:
                return
            perfil = (self.ent_perfil.get() or "").strip()
            if perfil:
                self._actualizar_materiales_por_perfil(perfil)
            elif getattr(self, "cbo_material", None) is not None:
                self.cbo_material["values"] = getattr(self, "_materiales_catalogo", None) or []
        except Exception:
            pass

    def _abrir_selector_oring_externo(self):
        """
        Abre el selector AS 568 / ISO 3601 (O-RING de mercado). El selector debe
        llamar a self._asignar_oring_externo(codigo) al elegir.
        PENDIENTE: la tabla/ventana AS 568 aún no existe en el proyecto.
        """
        try:
            from tkinter import messagebox
            messagebox.showinfo(
                "Buscar O-RING",
                "El selector AS 568 / ISO 3601 aún no está disponible.",
                parent=self,
            )
        except Exception:
            pass

    def _asignar_oring_externo(self, codigo):
        """Callback del selector AS 568 / ISO 3601."""
        try:
            self.var_codigo_oring_externo.set((codigo or "").strip())
        except Exception:
            pass

    def oring_externo_incompleto(self) -> bool:
        """True si el modo O-RING externo está activo y no se eligió O-RING."""
        try:
            return bool(self._oring_externo_activo
                        and not (self.var_codigo_oring_externo.get() or "").strip())
        except Exception:
            return False
    # ANCLA_FINAL: ORING_EXTERNO_METODOS_P4

    def leer_datos(self) -> dict:
        """Devuelve la información escrita por el usuario."""

        notas = self.txt_notas.get("1.0", "end").strip()

        # --- medidas ---
        from .perfil_medidas_p4 import leer_medidas_de_card
        medidas_out = leer_medidas_de_card(self.medidas_entries, getattr(self, "gap_entries", None))

        # ANCLA_INICIO: LIMPIEZA_Y_SPLIT_MEDIDAS_P4 (FIX_REAL)
        # NO reconvertir a string: respetar float/None que ya viene de perfil_medidas_p4
        medidas_clean = {}
        try:
            for k, v in (medidas_out or {}).items():
                kk = str(k).upper().strip()
                if v is None:
                    continue
                medidas_clean[kk] = v
        except Exception:
            medidas_clean = {}

        # Split: geometría vs GAP (D1/D2). C sigue siendo geométrica (NO cálculo).
        medidas_geom = {k: v for k, v in medidas_clean.items() if k not in ("D1", "D2")}
        medidas_gap  = {k: v for k, v in medidas_clean.items() if k in ("D1", "D2")}
        # ANCLA_FINAL: LIMPIEZA_Y_SPLIT_MEDIDAS_P4 (FIX_REAL)

        # ANCLA_INICIO: SALIDA_MATERIALES_MULTIPARTE_P4 (NUEVO)
        mats = []
        try:
            if hasattr(self, "ent_materiales") and self.ent_materiales:
                mats = [(c.get() or "").strip() for c in self.ent_materiales]
                mats = [m for m in mats if m]
            else:
                m1 = (self.ent_material.get() or "").strip() if self.ent_material else ""
                mats = [m1] if m1 else []
        except Exception:
            mats = []

        material_compat = mats[0] if mats else ""
        # ANCLA_FINAL: SALIDA_MATERIALES_MULTIPARTE_P4 (NUEVO)

        # ANCLA_INICIO: LECTURA_PIEZA_ESPECIAL_P4
        # Solo presentes en tarjetas tipo ESPECIAL (Pieza Especial).
        tipo_componente = None
        quien_fabrica = None
        if hasattr(self, "var_tipo_componente"):
            try:
                tipo_componente = (self.var_tipo_componente.get() or "").strip() or None
            except Exception:
                tipo_componente = None
        if hasattr(self, "var_quien_fabrica"):
            try:
                quien_fabrica = (self.var_quien_fabrica.get() or "").strip() or None
            except Exception:
                quien_fabrica = None

        validado_por = None
        fecha_validacion = None
        nota_validacion = None
        if hasattr(self, "ent_validado_por"):
            try:
                validado_por = (self.ent_validado_por.get() or "").strip() or None
                fecha_validacion = (self.ent_fecha_validacion.get() or "").strip() or None
                nota_validacion = (self.txt_nota_validacion.get("1.0", "end") or "").strip() or None
            except Exception:
                pass
        # ANCLA_FINAL: LECTURA_PIEZA_ESPECIAL_P4

        return {
            "tipo": self.tipo,
            "perfil": (self.ent_perfil.get() or "").strip(),
            "material": material_compat,
            "materiales": mats,
            "cantidad": max(self.var_cantidad.get(), 1),
            "medidas": medidas_clean,
            "medidas_geom": medidas_geom,
            "medidas_gap": medidas_gap,
            "solicitar_gap": bool(getattr(self, "_solicitar_gap_once", False)),
            "notas": notas,
            "tipo_componente": tipo_componente,
            "quien_fabrica": quien_fabrica,
            "origen": getattr(self, "origen", "KIT_NORMAL"),
            "plano_referencia": (self.ent_plano_referencia.get() or "").strip(),
            "validado_por": validado_por,
            "fecha_validacion": fecha_validacion,
            "nota_validacion": nota_validacion,
            "fluido_especial": (self.ent_fluido_especial.get() or "").strip() if hasattr(self, "ent_fluido_especial") else None,
            "temp_especial": (self.ent_temp_especial.get() or "").strip() if hasattr(self, "ent_temp_especial") else None,
            "metal_capa3": (self.var_metal_capa3.get() or "").strip() or None if hasattr(self, "var_metal_capa3") else None,
            # ANCLA_INICIO: ORING_EXTERNO_SALIDA_P4
            # Solo se exportan con el modo activo; si no, valores neutros.
            # El orquestador decide si el back-up aplica (solo hidráulico).
            "oring_externo": bool(getattr(self, "_oring_externo_activo", False)),
            "codigo_oring_externo": (
                (self.var_codigo_oring_externo.get() or "").strip() or None
                if getattr(self, "_oring_externo_activo", False) else None
            ),
            "back_up_as574": (
                bool(self.var_back_up_as574.get())
                if getattr(self, "_oring_externo_activo", False) else False
            ),
            # ANCLA_FINAL: ORING_EXTERNO_SALIDA_P4
        }
    # ANCLA_INICIO: METODO_MOSTRAR_ESTADO_GAP (REEMPLAZO COMPLETO)
    def mostrar_estado_gap(self, info_gap):
        """Actualiza la etiqueta GAP según resultado del motor (incluye valor numérico)."""

        if not info_gap:
            self.lbl_gap.config(text="", foreground="black")
            return

        estado = (info_gap.get("estado") or "").lower()
        _mensajes_raw = info_gap.get("mensajes") or []
        if isinstance(_mensajes_raw, list):
            mensajes = "; ".join(_mensajes_raw)
        else:
            mensajes = str(_mensajes_raw)

        # ANCLA_INICIO: BLINDAJE_NO_GAP_P4_UI (RESTORE)
        # Si el motor devuelve preview sin gap_real (rascadores/estáticos), no mostrar nada.
        if estado == "gap_preview" and (info_gap.get("gap_real", None) is None):
            self.lbl_gap.config(text="", foreground="black")
            return
        # ANCLA_FINAL: BLINDAJE_NO_GAP_P4_UI (RESTORE)

        # Prefijo numérico del GAP si está disponible
        gap_txt = ""
        try:
            g = info_gap.get("gap_real", None)
            if g is not None:
                gap_txt = f"GAP={float(g):.3f} mm"
        except Exception:
            gap_txt = ""

        # 1) Preview numérico (SIN STAMP / SIN recomendaciones)
        if estado == "gap_preview":
            txt = gap_txt if gap_txt else ""
            self.lbl_gap.config(text=txt, foreground="black")
            return

        # 2) Si viene en modo geo_warn (por UI), mantenemos mensajes
        # ANCLA_INICIO: PARCHE_ESTADO_GEO_ERROR_P4_UI (NUEVO)
        # Estado visual exclusivo para errores geométricos (NO GAP).
        if estado == "geo_error":
            if mensajes:
                self.lbl_gap.config(text=mensajes, foreground="red")
            else:
                self.lbl_gap.config(text="Error geométrico", foreground="red")
            return
        # ANCLA_FINAL: PARCHE_ESTADO_GEO_ERROR_P4_UI (NUEVO)

        # 3) Estados normales del motor (si algún día los querés usar aquí)
        if estado == "ok_sin_backup":
            txt = gap_txt if gap_txt else "GAP OK"
            self.lbl_gap.config(text=txt, foreground="green")
            return

        if estado == "ok_con_backup":
            # En este flujo no se fuerza recomendación sin STAMP;
            # pero si llegara aquí, se muestra neutro:
            txt = gap_txt if gap_txt else "GAP OK"
            self.lbl_gap.config(text=txt, foreground="goldenrod")
            return

        # ANCLA_INICIO: ESTADO_DIM_ADVERTENCIA_P4
        if estado == "dim_advertencia":
            txt = mensajes if mensajes else "Advertencia dimensional"
            color = info_gap.get("color", "darkorange")
            self.lbl_gap.config(
                text=txt,
                foreground=color,
                font=("Segoe UI", 11, "bold"),
            )
            return
        # ANCLA_FINAL: ESTADO_DIM_ADVERTENCIA_P4

        # Default / error
        txt = gap_txt if gap_txt else (mensajes if mensajes else "GAP incorrecto")
        self.lbl_gap.config(text=txt, foreground="red")
    # ANCLA_FINAL: METODO_MOSTRAR_ESTADO_GAP (REEMPLAZO COMPLETO)

    def _pedir_eliminar(self):
        """Solicita eliminar esta tarjeta."""
        try:
            if callable(self._on_delete):
                self._on_delete(self)
            else:
                self.destroy()
        except Exception:
            try:
                self.destroy()
            except Exception:
                pass
