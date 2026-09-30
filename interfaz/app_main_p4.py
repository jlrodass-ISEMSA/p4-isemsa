# interfaz/app_main_p4.py

import tkinter as tk
from tkinter import ttk, messagebox
StringVar = tk.StringVar
from .ui_header_p4 import build_header
from .ui_scroll_general_p4 import build_scroll_general
from .ui_cliente_p4 import build_cliente
from .ui_cilindro_p4 import build_cilindro, activar_velocidad_auto
from .ui_botones_componentes_p4 import build_botones_componentes
from .ui_tarjetas_area_p4 import build_area_tarjetas

# Import directo: card_componente_p4.py está en la MISMA carpeta.
from .card_componente_p4 import CardComponente

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NEXO — CRM Técnico ISEMSA")
        # ANCLA_INICIO: ICONO_VENTANA_NEXO_P4
        try:
            from PIL import Image, ImageTk
            import os
            ruta_icono = os.path.join(os.path.dirname(__file__), "..", "imagenes", "nexo_simbolo.png")
            img_icono = Image.open(ruta_icono)
            self._icono_nexo_img = ImageTk.PhotoImage(img_icono)
            self.iconphoto(True, self._icono_nexo_img)
        except Exception:
            pass
        # ANCLA_FINAL: ICONO_VENTANA_NEXO_P4
        self.geometry("1200x800")

        # ANCLA_INICIO: INIT_CARDS_ANTES_BIND_P4
        self.cards = []
        # ANCLA_FINAL: INIT_CARDS_ANTES_BIND_P4

        # ANCLA_INICIO: INIT_REGIMEN_ACTUAL_P4
        self.regimen_actual = None  # "HIDRAULICO" | "NEUMATICO" | None
        # ANCLA_FINAL: INIT_REGIMEN_ACTUAL_P4

        from persistencia.base_de_datos_clientes_isemsa_p4 import cargar_base_de_datos_clientes

        # ANCLA_CLIENTES_DB_P4
        self.clientes_db = cargar_base_de_datos_clientes(
            r"C:\Users\Leonel\Documents\CUADERNO_DIGITAL_KIT_BUILDER P4\documentos\Base de Datos Clientes.xlsx"
        )
        # ANCLA_INICIO: LISTENERS_UI_P4
        self.bind("<<MedidasCambiadas>>", self._on_medidas_cambiadas, add="+")
        self.bind("<<SolicitarEvaluacionGap>>", self._on_gap_geometrico, add="+")
        # ANCLA_FINAL: LISTENERS_UI_P4

        # ==========================
        # ENCABEZADO EXACTO P2 (CLON) - MODULARIZADO
        # ==========================
        build_header(self, self)

        # ANCLA_INICIO: FRAME_CONTENEDOR_UI_P4
        build_scroll_general(self, self)
        # ANCLA_FINAL: FRAME_CONTENEDOR_UI_P4

        # --- Datos del cliente (estructura como P2) - MODULARIZADO ---
        build_cliente(self, self.frame_contenedor)

        # --- Tipo de trabajo (NUEVO) ---
        from .ui_tipo_trabajo_p4 import build_tipo_trabajo
        build_tipo_trabajo(self, self.frame_contenedor)

        # --- Datos del cilindro (clonado visualmente de P2) - MODULARIZADO ---
        self.frm_cil = build_cilindro(self, self.frame_contenedor)
        
        # ANCLA_INICIO: COND_OPERACION_UI_P4
        from .ui_condiciones_p4 import build_condiciones_operacion
        build_condiciones_operacion(self, parent=self.frame_contenedor)
        # ANCLA_FINAL: COND_OPERACION_UI_P4

        # Activar lógica de velocidad estimada del cilindro (MODULARIZADO)
        activar_velocidad_auto(self)

        # --- Botonera componentes - MODULARIZADO ---
        self.frm_botones_componentes = build_botones_componentes(self, self.frame_contenedor)

        # --- Área para tarjetas (scroll) - MODULARIZADO ---
        build_area_tarjetas(self, self.frame_contenedor)
      
        # Nota técnica:
        # - STAMP ya se crea y posiciona correctamente dentro de COND_OPERACION_UI_P4
        # - El evento <<MedidasCambiadas>> ya está vinculado de forma global
        # No se requiere lógica adicional aquí.

    # ANCLA_INICIO: AGREGAR_TARJETAS_UI_P4
    def _eliminar_tarjeta(self, card):
        """
        Elimina una tarjeta de forma segura:
        1) La saca de self.cards (modelo)
        2) Destruye el widget (UI)
        3) Refresca regiones de scroll (tarjetas y scroll general)
        """
        if card is None:
            return

        # 1) Modelo: quitar de la lista si existe
        try:
            if hasattr(self, "cards") and card in self.cards:
                self.cards.remove(card)
        except Exception:
            pass

        # 2) UI: destruir sin reventar si ya fue destruida
        try:
            # Si estaba empacada, esto ayuda a evitar "huecos" visuales en algunos casos
            try:
                card.pack_forget()
            except Exception:
                pass
            card.destroy()
        except Exception:
            pass

        # 3) Refrescar scroll (tarjetas)
        try:
            if hasattr(self, "canvas") and self.canvas is not None:
                self.canvas.update_idletasks()
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception:
            pass

        # 4) Refrescar scroll general (todo el contenido)
        try:
            if hasattr(self, "canvas_general") and self.canvas_general is not None:
                self.canvas_general.update_idletasks()
                self.canvas_general.configure(scrollregion=self.canvas_general.bbox("all"))
        except Exception:
            pass

    def _add_rascador(self):
        card = CardComponente(self.inner_cards, "Rascador", "RASCADOR", on_delete=self._eliminar_tarjeta)
        card.pack(fill="x", pady=5)
        self.cards.append(card)

    def _add_sello_vastago(self):
        card = CardComponente(self.inner_cards, "Sello de vástago", "VASTAGO", on_delete=self._eliminar_tarjeta)
        card.pack(fill="x", pady=5)
        self.cards.append(card)

    def _add_sello_piston(self):
        card = CardComponente(self.inner_cards, "Sello de pistón", "PISTON", on_delete=self._eliminar_tarjeta)
        card.pack(fill="x", pady=5)
        self.cards.append(card)

    def _add_anillo_guia(self):
        card = CardComponente(self.inner_cards, "Anillo guía", "GUIA", on_delete=self._eliminar_tarjeta)
        card.pack(fill="x", pady=5)
        self.cards.append(card)

    def _add_estatico(self):
        card = CardComponente(self.inner_cards, "Sello estático / O-ring", "ESTATICO", on_delete=self._eliminar_tarjeta)
        card.pack(fill="x", pady=5)
        self.cards.append(card)

    def _add_backup(self):
        card = CardComponente(self.inner_cards, "Back-up", "BACKUP", on_delete=self._eliminar_tarjeta)
        card.pack(fill="x", pady=5)
        self.cards.append(card)

    def _add_especial(self):
        card = CardComponente(self.inner_cards, "Pieza especial", "ESPECIAL", on_delete=self._eliminar_tarjeta)
        card.pack(fill="x", pady=5)
        self.cards.append(card)

        # ANCLA_INICIO: AGREGAR_PIEZA_TECNICA_ADICIONAL_P4
    def _add_pieza_tecnica(self, tipo_real, titulo):
        """
        Crea una tarjeta normal (mismo CardComponente, mismo motor según tipo_real
        y régimen del kit), marcada con origen="PIEZA_TECNICA_ADICIONAL" para que
        el reporte la distinga de las tarjetas del kit original.
        """
        card = CardComponente(self.inner_cards, titulo, tipo_real, on_delete=self._eliminar_tarjeta)
        card.origen = "PIEZA_TECNICA_ADICIONAL"
        card.pack(fill="x", pady=5)
        self.cards.append(card)
    # ANCLA_FINAL: AGREGAR_PIEZA_TECNICA_ADICIONAL_P4

    # ANCLA_INICIO: AGREGAR_ELEMENTO_ADICIONAL_P4
    def _add_elemento_adicional(self):
        """
        Crea una tarjeta CardElementoAdicional: elemento que forma parte del kit
        pero que NEXO no puede evaluar con sus motores (sin ficha de material
        propia, componente de otra marca, geometría fuera de catálogo, o no es
        un sello). Sin GAP, sin compatibilidad química automática. Se guarda en
        una lista separada (self.elementos_adicionales), NO en self.cards, porque
        preparacion_entrada_p4.py asume leer_datos() con campos de motor
        (perfil, material, medidas) que esta tarjeta no tiene.
        """
        from .card_elemento_adicional_p4 import CardElementoAdicional
        card = CardElementoAdicional(self.inner_cards, on_delete=self._eliminar_tarjeta)
        card.pack(fill="x", pady=5)
        if not hasattr(self, "elementos_adicionales"):
            self.elementos_adicionales = []
        self.elementos_adicionales.append(card)
    # ANCLA_FINAL: AGREGAR_ELEMENTO_ADICIONAL_P4
    # ANCLA_FINAL: AGREGAR_TARJETAS_UI_P4

    # ANCLA_INICIO: SELECCIONAR_REGIMEN_P4
    def _actualizar_visibilidad_campos_hidraulico(self):
        """
        Muestra/oculta campos exclusivos de Guiado (Long. libre vástago,
        Tipo de montaje) según el régimen activo. Fase 2 — pendiente
        registrado desde la sesión de habilitación del camino Neumático:
        estos campos alimentan el Motor de Guiado (pandeo), que no aplica
        a régimen NEUMATICO.
        """
        widgets = [
            getattr(self, "lbl_largo_retraido", None),
            getattr(self, "ent_largo_retraido", None),
            getattr(self, "lbl_largo_total", None),
            getattr(self, "ent_largo_total", None),
            getattr(self, "lbl_tipo_montaje", None),
            getattr(self, "cbo_tipo_montaje", None),
            getattr(self, "chk_cilindro_completo", None),
            # Efecto Diesel (STAMP §7.3): compresión adiabática de aire disuelto
            # en aceite — fenómeno exclusivo de HIDRAULICO, no aplica a NEUMATICO.
            getattr(self, "chk_cambios_bruscos_presion", None),
            getattr(self, "chk_presencia_aire", None),
        ]
        mostrar = self.regimen_actual != "NEUMATICO"
        for w in widgets:
            if w is None:
                continue
            try:
                if mostrar:
                    w.grid()
                else:
                    w.grid_remove()
            except Exception:
                pass

    # ANCLA_INICIO: POPUPS_UI_P4 — delegados a ui_popups_p4.py
    def _popup_disponibilidad(self):
        from .ui_popups_p4 import popup_disponibilidad
        return popup_disponibilidad(self)

    def _popup_piezas_incompletas_neumatico(self):
        from .ui_popups_p4 import popup_piezas_incompletas_neumatico
        return popup_piezas_incompletas_neumatico(self)

    def _popup_piezas_incompletas_hidraulico(self):
        from .ui_popups_p4 import popup_piezas_incompletas_hidraulico
        return popup_piezas_incompletas_hidraulico(self)

    def _popup_montaje_hidraulico(self):
        import os
        from .ui_popups_p4 import popup_montaje_hidraulico
        _images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "imagenes")
        return popup_montaje_hidraulico(self, _images_dir)
    # ANCLA_FINAL: POPUPS_UI_P4

    def _seleccionar_hidraulico(self):
        estado = self._popup_disponibilidad()
        if not estado:
            return
        self.estado_disponibilidad = estado
        self.detalle_piezas_incompletas = None
        self.tipo_montaje_hidraulico = None
        if estado == "ACCESO_COMPLETO":
            montaje = self._popup_montaje_hidraulico()
            if not montaje:
                return
            self.tipo_montaje_hidraulico = montaje
            if hasattr(self, "cbo_tipo_montaje"):
                cbo = self.cbo_tipo_montaje
                valores = list(cbo["values"])
                if montaje in valores:
                    cbo.current(valores.index(montaje))
        elif estado == "PIEZAS_INCOMPLETAS":
            detalle = self._popup_piezas_incompletas_hidraulico()
            if detalle is None:
                return
            self.detalle_piezas_incompletas = detalle
            self._aplicar_segregacion_visual(detalle)
        self._limpiar_todas_las_tarjetas()
        self.regimen_actual = "HIDRAULICO"
        self._mostrar_datos_cilindro(True)
        self._actualizar_visibilidad_campos_hidraulico()
        self._actualizar_visibilidad_muestra_usada(estado)

    def _seleccionar_neumatico(self):
        estado = self._popup_disponibilidad()
        if not estado:
            return
        self.estado_disponibilidad = estado
        self.detalle_piezas_incompletas = None
        if estado == "PIEZAS_INCOMPLETAS":
            detalle = self._popup_piezas_incompletas_neumatico()
            if detalle is None:
                return
            self.detalle_piezas_incompletas = detalle
        self._limpiar_todas_las_tarjetas()
        self.regimen_actual = "NEUMATICO"
        self._mostrar_datos_cilindro(True)
        self._actualizar_visibilidad_campos_hidraulico()
        self._actualizar_visibilidad_muestra_usada(estado)

    def _aplicar_segregacion_visual(self, detalle):
        """
        Deshabilita visualmente los campos de diámetro que el técnico
        declaró no tener disponibles en campo.
        Fuente: CRITERIOS_DE_ENTRADA_P4.docx §7.3
        """
        if not detalle:
            return
        def _set(widget_name, habilitado):
            w = getattr(self, widget_name, None)
            if w:
                w.config(state="normal" if habilitado else "disabled")
                if not habilitado:
                    w.delete(0, "end")
        _set("ent_diam_camisa",         detalle.get("tiene_camisa", True))
        _set("ent_diam_exterior_camisa", detalle.get("tiene_exterior", True))
        _set("ent_diam_vastago",         detalle.get("tiene_vastago", True))

        # Largos: deshabilitados si faltan ambos diámetros O si no hay tapas/clavijas
        sin_camisa = not detalle.get("tiene_camisa", True)
        sin_vastago = not detalle.get("tiene_vastago", True)
        sin_tapas = not detalle.get("tiene_tapas", True)
        bloquear_largos = (sin_camisa and sin_vastago) or (sin_camisa and sin_tapas)
        _set("ent_largo_retraido", not bloquear_largos)
        _set("ent_largo_total",    not bloquear_largos)
        cbo = getattr(self, "cbo_tipo_montaje", None)
        if cbo:
            cbo.config(state="disabled" if bloquear_largos else "readonly")
    # ANCLA_FINAL: SEGREGACION_VISUAL_PIEZAS_INCOMPLETAS_P4
    
    # ANCLA_INICIO: VISIBILIDAD_MUESTRA_USADA_P4
    # Fuente: CRITERIOS_DE_ENTRADA_P4.docx ?7.4
    def _actualizar_visibilidad_muestra_usada(self, estado):
        """Muestra/oculta datos del cilindro y checkbox muestra_usada segun estado.
        Fuente: CRITERIOS_DE_ENTRADA_P4.docx ?7.3 y ?7.4
        """
        try:
            if estado == "MUESTRA_DE_SELLO":
                # Solo ocultar datos del cilindro, NO los botones de perfiles
                # Fuente: CRITERIOS_DE_ENTRADA_P4.docx ?7.3
                frm = getattr(self, "frm_cil", None)
                if frm:
                    frm.grid_remove()
                self.chk_muestra_usada.grid()
            else:
                self._mostrar_datos_cilindro(True)
                self.var_muestra_usada.set(0)
                self.chk_muestra_usada.grid_remove()
        except AttributeError:
            pass

        # ANCLA_INICIO: HOBLIT_VISIBILIDAD_P4
        # Fuente: HOBLIT_ENGINE_P4.docx §10.1
        # frm_hoblit visible solo con ACCESO_COMPLETO hidráulico.
        try:
            frm_h = getattr(self, "frm_hoblit", None)
            if frm_h:
                tipo_trabajo = getattr(self, "tipo_trabajo_actual", None)
                es_hidraulico = (str(tipo_trabajo).upper() == "HIDRAULICO"
                                 if tipo_trabajo else False)
                if estado == "ACCESO_COMPLETO" and es_hidraulico:
                    frm_h.grid()
                else:
                    frm_h.grid_remove()
                    # Limpiar campos al ocultar para no contaminar evaluaciones
                    if hasattr(self, "ent_l3_mm"):
                        self.ent_l3_mm.delete(0, "end")
                    if hasattr(self, "ent_lp_mm"):
                        self.ent_lp_mm.delete(0, "end")
        except AttributeError:
            pass
        # ANCLA_FINAL: HOBLIT_VISIBILIDAD_P4
    # ANCLA_FINAL: VISIBILIDAD_MUESTRA_USADA_P4

    def _seleccionar_pieza_especial(self):
        """
        Pieza Especial es un flujo independiente (decisión de arquitectura
        31/08/2026): no usa "Datos del cilindro" — no hay régimen de cilindro
        que capturar antes de agregar la tarjeta. Fase 2 pendiente desde esa
        fecha, cerrada aquí.
        """
        self._limpiar_todas_las_tarjetas()
        self.regimen_actual = "ESPECIAL"
        self._mostrar_datos_cilindro(False)
        self._add_especial()

    # ANCLA_INICIO: LIMPIAR_TARJETAS_CAMBIO_TIPO_TRABAJO_P4
    def _limpiar_todas_las_tarjetas(self):
        """
        Elimina todas las tarjetas existentes (self.cards y
        self.elementos_adicionales) al cambiar de Tipo de trabajo
        (Hidráulico/Neumático/Pieza Especial) — antes se quedaban
        "pintadas" de un modo al pasar a otro, sin importar cuál.
        Reutiliza _eliminar_tarjeta para no duplicar la lógica de
        destrucción de widget + refresco de scroll.
        """
        for card in list(getattr(self, "cards", [])):
            self._eliminar_tarjeta(card)
        for card in list(getattr(self, "elementos_adicionales", [])):
            try:
                if card in self.elementos_adicionales:
                    self.elementos_adicionales.remove(card)
                card.pack_forget()
                card.destroy()
            except Exception:
                pass
    # ANCLA_FINAL: LIMPIAR_TARJETAS_CAMBIO_TIPO_TRABAJO_P4

    def _mostrar_datos_cilindro(self, mostrar):
        # ANCLA_INICIO: OCULTAR_BOTONERA_PIEZA_ESPECIAL_P4
        # Extendido para controlar también la botonera de componentes
        # (+ Rascador, + Sello de vástago, etc.) — Pieza Especial es
        # autosuficiente (un clic = una tarjeta), no necesita ninguno de
        # esos 8 botones, que asumen catálogo de 105 perfiles / régimen.
        for attr in ("frm_cil", "frm_botones_componentes"):
            frm = getattr(self, attr, None)
            if frm is None:
                continue
            try:
                if mostrar:
                    frm.grid()
                else:
                    frm.grid_remove()
            except Exception:
                pass
        # ANCLA_FINAL: OCULTAR_BOTONERA_PIEZA_ESPECIAL_P4
    # ANCLA_FINAL: SELECCIONAR_REGIMEN_P4

    # ANCLA_INICIO: ON_GAP_GEOMETRICO_P4
    def _on_gap_geometrico(self, event=None):
        from tkinter import messagebox
        from .preparacion_entrada_p4 import preparar_datos_gap_geometrico

        def _to_float(w):
            try:
                return float((w.get() or "").replace(",", "."))
            except Exception:
                return None

        diam_vastago = _to_float(self.ent_diam_vastago)
        diam_camisa = _to_float(self.ent_diam_camisa)

        resultados = preparar_datos_gap_geometrico(
            diam_vastago=diam_vastago,
            diam_camisa=diam_camisa,
            cards=getattr(self, "cards", []),
        )

        if not resultados:
            messagebox.showinfo(
                "Resultado GAP",
                "No hay resultados GAP disponibles."
            )
            return

        # ANCLA_INICIO: ORQUESTADOR_GAP_GEOMETRICO_P4
        from funciones.orquestador.nexo_orquestador import preparar_popup_gap_geometrico
        lineas = preparar_popup_gap_geometrico(
            resultados=resultados,
            regimen=getattr(self, "regimen_actual", None),
        )
        messagebox.showinfo(
            "Resultado GAP",
            "\n\n----------------------\n\n".join(lineas)
        )
        # ANCLA_FINAL: ORQUESTADOR_GAP_GEOMETRICO_P4
    # ANCLA_FINAL: ON_GAP_GEOMETRICO_P4

    # ANCLA_INICIO: ON_COMPATIBILIDAD_P4_PUENTE
    def _on_compatibilidad(self, event=None):
        """
        Evalúa compatibilidad química y % de uso técnico.

        Soporta perfiles multiparte:
        - Cada tarjeta puede contener uno o varios materiales (M1..Mn).
        - La evaluación se realiza por cada material seleccionado.
        - GAP/back-up se evalúa una sola vez por tarjeta (perfil + geometría + presión).
        """

        from tkinter import messagebox

        # ANCLA_INICIO: ORING_EXTERNO_ADVERTENCIA_P4
        # Advertencia no bloqueante: O-RING externo sin medida AS 568 / ISO 3601.
        try:
            if any(c.oring_externo_incompleto() for c in self.cards
                   if hasattr(c, "oring_externo_incompleto")):
                messagebox.showwarning(
                    "O-RING externo incompleto",
                    "Hay un O-RING de compra externa sin medida seleccionada "
                    "(botón 'Buscar O-RING'). La evaluación continuará sin ese dato.",
                )
        except Exception:
            pass
        # ANCLA_FINAL: ORING_EXTERNO_ADVERTENCIA_P4

        # -----------------------------
        # 1) Leer STAMP desde UI
        # -----------------------------
        fluido = (self.ent_fluido.get() or "").strip()
        # ANCLA_INICIO: FLUIDO_COMPARTIDO_NO_OBLIGATORIO_SIN_SELLO_P4
        # Antes: exigía Fluido (panel STAMP compartido) sin excepción,
        # incluso para kits de Pieza Especial compuestos solo por
        # ESTRUCTURAL/EXTRUIDO_COMERCIAL/OTRO -- tipos que usan su propio
        # "Fluido (referencia)" por tarjeta y nunca corren el motor
        # compartido (ver STAMP_PIEZA_ESPECIAL_P4). El fluido compartido
        # sigue siendo obligatorio si hay al menos una tarjeta SELLO
        # (dentro o fuera de Pieza Especial) o Hidráulico/Neumático normal.
        def _requiere_fluido_compartido():
            for card in self.cards:
                try:
                    if getattr(card, "tipo", None) != "ESPECIAL":
                        return True
                    if (card.leer_datos().get("tipo_componente") or "").upper() == "SELLO":
                        return True
                except Exception:
                    return True
            return False

        if not fluido and _requiere_fluido_compartido():
            messagebox.showwarning("STAMP incompleto", "Debes seleccionar un fluido.")
            return
        # ANCLA_FINAL: FLUIDO_COMPARTIDO_NO_OBLIGATORIO_SIN_SELLO_P4

        def _to_float(w):
            try:
                return float((w.get() or "").replace(",", "."))
            except Exception:
                return None

        from funciones.stamp.obtener_presion_valor_p4 import obtener_presion_valor_detallado
        
        presion_parse = obtener_presion_valor_detallado(self.ent_presion.get())
        presion = presion_parse.valor_psi if presion_parse.ok else None

        if presion_parse.estado == "ruptura_contractual_unidad":
            messagebox.showerror(
                "Ruptura contractual de presión",
                presion_parse.mensaje
            )
            return

        if not presion_parse.ok and (self.ent_presion.get() or "").strip():
            messagebox.showerror(
                "Presión inválida",
                presion_parse.mensaje
            )
            return
      
        temp_esp = _to_float(self.ent_temp_esp)
        vel_esp = _to_float(self.ent_vel_esp)

        # ANCLA_INICIO: VALIDACION_STAMP_RANGO_O_ESPECIFICO_P4
        temp_rango = (self.cbo_temp_rango.get() or "").strip()
        vel_rango = (self.cbo_vel_rango.get() or "").strip()

        errores_stamp = []

        if temp_esp is not None and temp_rango:
            errores_stamp.append(
                "Temperatura: no puedes definir temperatura específica y rango al mismo tiempo."
            )

        if vel_esp is not None and vel_rango:
            errores_stamp.append(
                "Velocidad: no puedes definir velocidad específica y rango al mismo tiempo."
            )

        if errores_stamp:
            messagebox.showerror(
                "Error de captura STAMP",
                "Corrige la captura antes de continuar:\n\n"
                + "\n".join(f"• {e}" for e in errores_stamp)
            )
            return
        # ANCLA_FINAL: VALIDACION_STAMP_RANGO_O_ESPECIFICO_P4

        # ANCLA_INICIO: LECTURA_DIAMETROS_CILINDRO_P4_REFERENCIA
        # Para evaluar GAP (vía motor profesional) necesitamos Ø vástago/Ø camisa globales como fallback.
        diam_vastago = _to_float(self.ent_diam_vastago)  # puede ser None
        diam_camisa  = _to_float(self.ent_diam_camisa)   # puede ser None
        largo_retraido = _to_float(self.ent_largo_retraido) if hasattr(self, "ent_largo_retraido") else None
        largo_total    = _to_float(self.ent_largo_total) if hasattr(self, "ent_largo_total") else None
        cilindro_completo = bool(self.var_cilindro_completo.get()) if hasattr(self, "var_cilindro_completo") else False
        tipo_montaje   = (self.cbo_tipo_montaje.get() or "").strip() if hasattr(self, "cbo_tipo_montaje") else None
        diam_exterior_camisa = _to_float(self.ent_diam_exterior_camisa) if hasattr(self, "ent_diam_exterior_camisa") else None  # Fuente: MOTOR_DE_GUIADO_P4.docx ?2 y ?4.1
        muestra_usada = bool(self.var_muestra_usada.get()) if hasattr(self, "var_muestra_usada") else False  # Fuente: CRITERIOS_DE_ENTRADA_P4.docx ?7.4
        estado_disponibilidad = getattr(self, "estado_disponibilidad", None)  # Fuente: CRITERIOS_DE_ENTRADA_P4.docx ?7.3
        # ANCLA_FINAL: LECTURA_DIAMETROS_CILINDRO_P4_REFERENCIA

        # ANCLA_INICIO: LECTURA_EFECTO_DIESEL_P4
        cambios_bruscos_presion = bool(self.var_cambios_bruscos_presion.get()) if hasattr(self, "var_cambios_bruscos_presion") else False
        presencia_aire = bool(self.var_presencia_aire.get()) if hasattr(self, "var_presencia_aire") else False
        # ANCLA_FINAL: LECTURA_EFECTO_DIESEL_P4

        # ANCLA_P4_IMPORT_PREPARACION_INICIO
        from .preparacion_entrada_p4 import preparar_datos_compatibilidad
        # ANCLA_P4_IMPORT_PREPARACION_FIN

        # ANCLA_P4_DELEGACION_PREPARACION_INICIO
        resultados = preparar_datos_compatibilidad(
            fluido=fluido,
            presion=presion,
            temp_esp=temp_esp,
            vel_esp=vel_esp,
            temp_rango=temp_rango,
            vel_rango=vel_rango,
            diam_vastago=diam_vastago,
            diam_camisa=diam_camisa,
            cards=getattr(self, "cards", []),
            largo_retraido=largo_retraido,
            largo_total=largo_total,
            cilindro_completo=cilindro_completo,
            tipo_montaje=tipo_montaje,
            regimen=self.regimen_actual,
            cambios_bruscos_presion=cambios_bruscos_presion,
            presencia_aire=presencia_aire,
            diam_exterior_camisa=diam_exterior_camisa,
            muestra_usada=muestra_usada,
            estado_disponibilidad=estado_disponibilidad,
            detalle_piezas_incompletas=getattr(self, "detalle_piezas_incompletas", None),
            tipo_montaje_hidraulico=getattr(self, "tipo_montaje_hidraulico", None),
        )
        # ANCLA_P4_DELEGACION_PREPARACION_FIN

        # ANCLA_INICIO: ORQUESTADOR_POPUP_COMPAT_P4
        from funciones.orquestador.nexo_orquestador import preparar_popup_compatibilidad

        errores_dc, lineas = preparar_popup_compatibilidad(
            resultados=resultados,
            fluido=fluido,
            temp_esp=temp_esp,
            temp_rango=temp_rango,
            vel_esp=vel_esp,
            vel_rango=vel_rango,
        )

        if errores_dc:
            messagebox.showerror(
                "Bloqueo por inconsistencia de diámetros",
                "No se puede continuar porque hay inconsistencias entre "
                "los datos del cilindro y las medidas ingresadas en las tarjetas.\n\n"
                + "\n".join(f"• {e}" for e in errores_dc)
            )
            return

        if not resultados:
            messagebox.showinfo("Compatibilidad", "No hay tarjetas válidas para evaluar.")
            return

        try:
            self._ultimo_reporte_compat_texto = "\n".join(lineas)
            self._ultimo_reporte_resultados = resultados
            self._ultimo_reporte_stamp = {
                "fluido": fluido,
                "presion": presion,
                "temp_esp": temp_esp,
                "vel_esp": vel_esp,
                "temp_rango": temp_rango,
                "vel_rango": vel_rango,
            }
        except Exception as e:
            print(f"[ERROR] Cache resultados P4 no guardado: {e}")

        messagebox.showinfo(
            "Compatibilidad y Uso Técnico",
            "\n".join(lineas)
        )
        # ANCLA_FINAL: ON_COMPATIBILIDAD_P4_PUENTE

    # ANCLA_INICIO: ON_REPORTES_P4_PUENTE
    def _on_reportes(self):
        """
        Genera reporte DOCX usando el generador disponible en el flujo actual.

        El reporte toma como base:
        - STAMP global.
        - Tarjetas activas del kit.
        - (Si existe) el texto del último popup de Compatibilidad y Uso Técnico.

        Soporta perfiles multiparte:
        - Cada tarjeta puede incluir uno o varios materiales (M1..Mn).
        - El reporte lista todos los materiales asociados a cada tarjeta.
        - GAP/back-up se reporta una sola vez por tarjeta
        (perfil + geometría + presión), no por material.
        """

        from tkinter import messagebox
        from datetime import datetime

        # 1) Debe haber al menos una tarjeta
        cards = getattr(self, "cards", []) or []
        if not cards:
            messagebox.showwarning("Reportes", "No hay tarjetas para generar reporte.")
            return

        # Helpers seguros
        def _get_txt(attr_names):
            for n in attr_names:
                try:
                    w = getattr(self, n, None)
                    if w is None:
                        continue
                    txt = (w.get() or "").strip()
                    if txt:
                        return txt
                except Exception:
                    continue
            return ""

        def _to_float_from_widget(widget):
            try:
                if widget is None:
                    return None
                s = (widget.get() or "").strip().replace(",", ".")
                return float(s) if s else None
            except Exception:
                return None

        # 2) Cliente / equipo (nombres pueden variar según build_cliente)
        nombre_cliente = _get_txt(["ent_cli_nombre", "ent_nombre_cliente", "ent_cliente", "ent_nombre"])
        nit_cliente    = _get_txt(["ent_cli_nit", "ent_nit_cliente", "ent_nit"])
        equipo         = _get_txt(["ent_equipo", "ent_maquina", "ent_aplicacion_equipo"])

        # 3) STAMP (ui_condiciones sí define estos atributos)
        fluido         = _get_txt(["ent_fluido"])
        aplicacion     = _get_txt(["cbo_aplicacion"])
        presion_psi    = _get_txt(["ent_presion"])
        temp_rango     = _get_txt(["cbo_temp_rango"])
        temp_especifica= _get_txt(["ent_temp_esp"])
        vel_rango      = _get_txt(["cbo_vel_rango"])
        vel_especifica = _get_txt(["ent_vel_esp"])

        # ANCLA_INICIO: ORQUESTADOR_PAYLOAD_REPORTE_P4
        from funciones.orquestador.nexo_orquestador import preparar_payload_reporte

        campos_cliente = {
            "nombre_cliente": nombre_cliente,
            "nit_cliente":    _get_txt(["ent_cli_nit", "ent_nit_cliente", "ent_nit"]),
            "contacto":       _get_txt(["ent_cli_contacto"]),
            "telefono":       _get_txt(["ent_cli_tel"]),
            "correo":         _get_txt(["ent_cli_correo"]),
            "equipo":         equipo,
            "vendedor":       _get_txt(["ent_cli_vendedor"]),
        }
        campos_cilindro = {
            "diam_vastago": _to_float_from_widget(getattr(self, "ent_diam_vastago", None)),
            "diam_camisa":  _to_float_from_widget(getattr(self, "ent_diam_camisa", None)),
            "carrera":      _to_float_from_widget(getattr(self, "ent_carrera", None)),
        }

        errores_rep, payload = preparar_payload_reporte(
            cards=cards,
            resultados_cache=getattr(self, "_ultimo_reporte_resultados", None),
            campos_cliente=campos_cliente,
            campos_cilindro=campos_cilindro,
            elementos_adicionales_cards=getattr(self, "elementos_adicionales", []),
        )

        if errores_rep:
            if "primero debe ejecutarse" in errores_rep[0]:
                messagebox.showerror("Reporte bloqueado", errores_rep[0])
            else:
                messagebox.showerror(
                    "Reporte bloqueado por inconsistencia de diámetros",
                    "No se puede generar el reporte porque hay inconsistencias entre "
                    "los datos del cilindro y las medidas ingresadas en las tarjetas.\n\n"
                    + "\n".join(f"• {e}" for e in errores_rep)
                )
            return

        correlativo_p4  = payload["correlativo"]
        nombre_archivo  = payload["nombre_archivo"]
        componentes_detalle = payload["componentes_detalle"]
        elementos_adicionales_detalle = payload["elementos_adicionales"]
        # ANCLA_FINAL: ORQUESTADOR_PAYLOAD_REPORTE_P4

        # ANCLA_INICIO: REPORTE_TRAZABILIDAD_P4_DESDE_RESULTADOS
        from funciones.reportes.generar_informe_pdf_p4 import extraer_trazabilidad
        trazabilidad_p4 = extraer_trazabilidad(getattr(self, "_ultimo_reporte_resultados", None) or [])
        # ANCLA_FINAL: REPORTE_TRAZABILIDAD_P4_DESDE_RESULTADOS

        from funciones.reportes.generar_informe_pdf_p4 import generar_y_mostrar_informe_pdf_p4

        try:
            generar_y_mostrar_informe_pdf_p4(
                nombre_cliente=payload["nombre_cliente"],
                nit_cliente=payload["nit_cliente"],
                contacto=payload["contacto"],
                telefono=payload["telefono"],
                correo=payload["correo"],
                equipo=payload["equipo"],
                vendedor=payload["vendedor"],
                nombre_archivo=nombre_archivo.replace(".docx", ".pdf"),
                correlativo=correlativo_p4,
                fluido=fluido,
                aplicacion=aplicacion,
                presion_psi=presion_psi,
                temp_rango=temp_rango,
                temp_especifica=temp_especifica,
                vel_rango=vel_rango,
                vel_especifica=vel_especifica,
                observaciones="",
                componentes_detalle=componentes_detalle,
                trazabilidad_P4=trazabilidad_p4,
                elementos_adicionales=elementos_adicionales_detalle,
            )
            messagebox.showinfo("Reportes", f"Reporte generado: {nombre_archivo.replace('.docx', '.pdf')}")
            if hasattr(self, "lbl_cli_correlativo"):
                self.lbl_cli_correlativo.config(text=correlativo_p4)
        except Exception as e:
            messagebox.showerror("Reportes", f"No se pudo generar el reporte.\n\nDetalle: {e}")

    # ANCLA_FINAL: ON_REPORTES_P4_PUENTE

    # ANCLA_INICIO: ON_MEDIDAS_CAMBIADAS_P4_LEGACY_UI
    def _on_medidas_cambiadas(self, event=None):
        """
        Se dispara cuando cambian las medidas (A/B/C/D1/D2) o el perfil
        en cualquier tarjeta. Delega validación a nexo_validador_geometrico.
        """
        from funciones.orquestador.nexo_validador_geometrico import validar_card_geometrico

        def _f_float(entry):
            try:
                txt = (entry.get() or "").strip().replace(",", ".")
                return float(txt) if txt else None
            except Exception:
                return None

        diam_vastago = _f_float(self.ent_diam_vastago)
        diam_camisa  = _f_float(self.ent_diam_camisa)

        presion_stamp = None
        try:
            from funciones.stamp.obtener_presion_valor_p4 import obtener_presion_valor
            ent = getattr(self, "ent_presion", None)
            txt = (ent.get() or "").strip() if ent is not None else ""
            presion_stamp = obtener_presion_valor(txt)
        except Exception:
            presion_stamp = None

        for card in getattr(self, "cards", []) or []:
            try:
                datos = card.leer_datos()
                datos["presion_stamp"] = presion_stamp

                try:
                    card.lbl_gap.config(text="", foreground="black",
                                        font=("Segoe UI", 9, "normal"))
                except Exception:
                    pass

                info_ui = validar_card_geometrico(
                    datos=datos,
                    diam_vastago=diam_vastago,
                    diam_camisa=diam_camisa,
                    presion_stamp=presion_stamp,
                )

                _res_dim = info_ui.pop("_resultado_dimensional", None)
                if _res_dim is not None:
                    card._ultimo_resultado_dimensional = _res_dim

                if info_ui.get("estado") == "dim_advertencia":
                    try:
                        card.actualizar_gap(info_ui)
                    except Exception:
                        pass
                    continue

                if info_ui.get("estado") == "geo_error":
                    try:
                        card.actualizar_gap(info_ui)
                    except Exception as e:
                        print(f"[ERROR] actualizar_gap falló en tarjeta: {e}")
                    continue

                if not info_ui:
                    info_ui = {}
                try:
                    if presion_stamp is None and isinstance(info_ui, dict):
                        g = info_ui.get("gap_real", None)
                        if g is not None:
                            info_ui = {"estado": "solo_num", "gap_real": g, "mensajes": []}
                        else:
                            info_ui = {}
                except Exception:
                    info_ui = {}

                try:
                    card.actualizar_gap(info_ui)
                except Exception:
                    pass

            except Exception as e:
                try:
                    card.actualizar_gap({
                        "estado": "geo_error",
                        "mensajes": [f"Error validando tarjeta: {e}"],
                        "gap_real": None
                    })
                except Exception:
                    pass
    # ANCLA_FINAL: ON_MEDIDAS_CAMBIADAS_P4_LEGACY_UI
    
if __name__ == "__main__":
    app = App()
    app.mainloop()
