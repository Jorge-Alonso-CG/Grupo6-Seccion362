import streamlit as st
from google import genai
from google.genai import types
import time
import random

# Configuración inicial de la página
st.set_page_config(
    page_title="Sweet & Healthy | Tienda de Postres Saludables",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de colores personalizada e inyección de CSS para un diseño premium y responsive
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Estilos Globales */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #FFF8F0 !important;
    font-family: 'Outfit', sans-serif !important;
    color: #2F3E46 !important;
}

/* Personalización del Sidebar */
[data-testid="stSidebar"] {
    background-color: #F4EBE1 !important;
    border-right: 2px solid #A8D5BA !important;
}

/* Títulos */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    color: #2D5A40 !important;
    font-weight: 700 !important;
}

/* Pestañas (Tabs) */
button[data-baseweb="tab"] {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: #2D5A40 !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 20px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #A8D5BA !important;
    color: #FFFFFF !important;
    border-bottom: 2px solid #E07A5F !important;
}

/* Tarjetas de Producto usando el contenedor nativo st.container(border=True) */
.stColumn [data-testid="stVerticalBlockBorder"] {
    background-color: #FFFFFF !important;
    border: 2px solid #EAE0D5 !important;
    border-top: 5px solid #A8D5BA !important; /* Borde superior verde menta */
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.3s ease-in-out !important;
}

.stColumn [data-testid="stVerticalBlockBorder"]:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 8px 25px rgba(168, 213, 186, 0.25) !important;
    border-top-color: #E07A5F !important; /* Cambia a terracota al pasar el mouse */
}

/* Contenedor de Etiquetas (Badges) */
.badge-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 6px;
    margin-bottom: 12px;
}
.badge {
    background-color: #E2ECE9 !important;
    color: #2D5A40 !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    border-radius: 12px !important;
    border: 1px solid #A8D5BA !important;
    display: inline-block !important;
}

/* Botones Personalizados */
.stButton > button {
    background-color: #E07A5F !important;
    color: #FFF8F0 !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: all 0.2s ease-in-out !important;
}

.stButton > button:hover {
    background-color: #C96045 !important;
    transform: scale(1.02) !important;
    box-shadow: 0 4px 12px rgba(224, 122, 95, 0.3) !important;
}

/* Botón deshabilitado */
.stButton > button:disabled, .stButton > button[disabled] {
    background-color: #EAE0D5 !important;
    color: #A09384 !important;
    cursor: not-allowed !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Footer corporativo */
.footer {
    text-align: center;
    padding: 30px;
    background-color: #F4EBE1;
    border-top: 2px solid #A8D5BA;
    margin-top: 50px;
    border-radius: 16px 16px 0 0;
}
.footer p {
    margin: 5px 0;
    color: #555;
}
</style>
""", unsafe_allow_html=True)

# 1. Base de datos estática de los 10 productos
PRODUCTS = [
    {
        "id": 1,
        "nombre": "Brownie de avena y cacao",
        "emoji": "🍫",
        "precio": 8.50,
        "kcal": "180 kcal",
        "stock": 15,
        "ingredientes": "Avena, cacao en polvo sin azúcar, huevo, plátano maduro, aceite de coco, endulzante natural (stevia).",
        "etiquetas": ["Sin gluten", "Bajo en azúcar"],
        "descripcion_breve": "Brownie denso y chocolatoso elaborado con ingredientes naturales y sin harinas refinadas."
    },
    {
        "id": 2,
        "nombre": "Cheesecake de frutos rojos",
        "emoji": "🍰",
        "precio": 12.00,
        "kcal": "210 kcal",
        "stock": 10,
        "ingredientes": "Queso crema light, yogur griego, frutos rojos frescos, galleta integral, miel de abeja, gelatina sin sabor.",
        "etiquetas": ["Sin azúcar refinada", "Alto en proteína"],
        "descripcion_breve": "Crema suave de queso light y yogur sobre base crujiente, coronada con salsa de frutos rojos."
    },
    {
        "id": 3,
        "nombre": "Galletas de avena y chía",
        "emoji": "🍪",
        "precio": 6.00,
        "precio_detalle": "S/ 6.00",
        "kcal": "90 kcal c/u",
        "stock": 30,
        "ingredientes": "Avena, semillas de chía, plátano, miel, canela, esencia de vainilla.",
        "etiquetas": ["Vegano", "Fuente de omega-3"],
        "descripcion_breve": "Galletas crujientes ricas en fibra y grasas saludables para tu snack de la tarde."
    },
    {
        "id": 4,
        "nombre": "Mousse de maracuyá",
        "emoji": "🍮",
        "precio": 9.00,
        "kcal": "140 kcal",
        "stock": 12,
        "ingredientes": "Pulpa de maracuyá, leche de coco, gelatina sin sabor, stevia, clara de huevo.",
        "etiquetas": ["Sin lactosa", "Bajo en calorías"],
        "descripcion_breve": "Postre aireado y refrescante con un equilibrio perfecto entre ácido y dulce."
    },
    {
        "id": 5,
        "nombre": "Trufas de cacao y dátil",
        "emoji": "🧆",
        "precio": 7.50,
        "precio_detalle": "S/ 7.50",
        "kcal": "95 kcal c/u",
        "stock": 0,
        "ingredientes": "Dátiles, cacao puro, coco rallado sin azúcar, almendras, esencia de vainilla.",
        "etiquetas": ["Endulzado naturalmente", "Vegano"],
        "descripcion_breve": "Bocaditos energéticos sin azúcar añadida, cubiertos de coco rallado."
    },
    {
        "id": 6,
        "nombre": "Tarta de manzana integral",
        "emoji": "🥧",
        "precio": 13.00,
        "kcal": "230 kcal",
        "stock": 8,
        "ingredientes": "Harina integral, manzana, canela, huevo, aceite de oliva, panela, polvo de hornear.",
        "etiquetas": ["Alto en fibra", "Sin mantequilla"],
        "descripcion_breve": "Clásica tarta con base integral y finas láminas de manzana horneadas con canela."
    },
    {
        "id": 7,
        "nombre": "Budín de chía y coco",
        "emoji": "🍧",
        "precio": 8.00,
        "kcal": "160 kcal",
        "stock": 20,
        "ingredientes": "Semillas de chía, leche de coco, mango, stevia, esencia de vainilla.",
        "etiquetas": ["Sin gluten", "Vegano"],
        "descripcion_breve": "Textura cremosa y refrescante con base de coco y topping de mango fresco."
    },
    {
        "id": 8,
        "nombre": "Alfajores de quinua",
        "emoji": "🫓",
        "precio": 5.50,
        "precio_detalle": "S/ 5.50",
        "kcal": "110 kcal c/u",
        "stock": 25,
        "ingredientes": "Harina de quinua, manjar blanco light, coco rallado, mantequilla, huevo, stevia.",
        "etiquetas": ["Proteína vegetal", "Sin colorantes"],
        "descripcion_breve": "Galletas de quinua rellenas de dulce de leche light y decoradas con coco."
    },
    {
        "id": 9,
        "nombre": "Helado de plátano y cacao",
        "emoji": "🍦",
        "precio": 7.00,
        "kcal": "120 kcal",
        "stock": 0,
        "ingredientes": "Plátano congelado, cacao en polvo sin azúcar, leche de almendra, esencia de vainilla.",
        "etiquetas": ["2 ingredientes base", "Vegano"],
        "descripcion_breve": "Crema fría 100% natural, cremosa, sin azúcares y libre de lácteos."
    },
    {
        "id": 10,
        "nombre": "Muffins de zanahoria",
        "emoji": "🧁",
        "precio": 6.50,
        "precio_detalle": "S/ 6.50",
        "kcal": "145 kcal c/u",
        "stock": 18,
        "ingredientes": "Zanahoria rallada, harina de avena, huevo, aceite de coco, stevia, canela, polvo de hornear, nueces.",
        "etiquetas": ["Sin azúcar", "Alto en fibra"],
        "descripcion_breve": "Esponjosos panquecitos con trozos de nueces crujientes y aroma a canela."
    }
]

# Inicialización de estados de sesión (Session State)
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "messages" not in st.session_state:
    # Mensaje de bienvenida inicial de Sweetie
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "¡Hola! Soy Sweetie 🌿, tu asistenta virtual de Sweet & Healthy. Estoy aquí para ayudarte a conocer nuestro menú de postres saludables, consultar ingredientes, calorías, disponibilidad de stock, detalles de entregas o nuestros métodos de pago. ¿En qué te puedo asesorar hoy?",
            "time_taken": None
        }
    ]

if "queries_count" not in st.session_state:
    st.session_state.queries_count = 0

# Encabezado principal de la página
st.markdown("""
<div style="text-align: center; padding: 25px 10px; background-color: #FFF8F0; margin-bottom: 20px;">
    <h1 style="color: #2D5A40; margin-bottom: 0; font-size: 3.2rem; font-weight: 800; letter-spacing: -1px;">
        Sweet & Healthy
    </h1>
    <p style="color: #E07A5F; font-size: 1.3rem; font-weight: 500; margin-top: 5px;">
        Postres que cuidan tu cuerpo 🌿
    </p>
</div>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR: CARRITO DE COMPRAS Y MÉTRICAS -----------------
st.sidebar.markdown("## 🛒 Carrito de Compras")

if not st.session_state.cart:
    st.sidebar.info("Tu carrito está vacío. ¡Elige un postre saludable en el catálogo!")
    total = 0.0
else:
    total = 0.0
    items_to_delete = []
    
    # Listar los productos agregados
    for pid, qty in list(st.session_state.cart.items()):
        if qty <= 0:
            continue
        # Buscar información del producto
        p = next((item for item in PRODUCTS if item['id'] == pid), None)
        if p:
            subtotal = p['precio'] * qty
            total += subtotal
            
            st.sidebar.markdown(f"### {p['emoji']} {p['nombre']}")
            
            # Formatear el precio
            precio_unit_desc = p.get('precio_detalle', f"S/ {p['precio']:.2f}")
            st.sidebar.write(f"Cant: **{qty}** | Subtotal: **S/ {subtotal:.2f}** ({precio_unit_desc})")
            
            # Botones para controlar cantidades
            col_dec, col_inc, col_rem = st.sidebar.columns([1, 1, 1.2])
            
            # Disminuir
            if col_dec.button("➖", key=f"dec_{pid}"):
                if qty == 1:
                    del st.session_state.cart[pid]
                else:
                    st.session_state.cart[pid] = qty - 1
                st.rerun()
            
            # Incrementar (bloqueado si supera el stock del producto)
            inc_disabled = (p['stock'] - qty <= 0)
            if col_inc.button("➕", key=f"inc_{pid}", disabled=inc_disabled):
                st.session_state.cart[pid] = qty + 1
                st.rerun()
                
            # Eliminar todo
            if col_rem.button("🗑️ Quitar", key=f"rem_{pid}"):
                del st.session_state.cart[pid]
                st.rerun()
            
            st.sidebar.markdown("---")
            
    st.sidebar.markdown(f"### **Total a Pagar: S/ {total:.2f}**")
    
    # Acciones del carrito
    col_cart_clear, col_cart_buy = st.sidebar.columns(2)
    
    if col_cart_clear.button("Vaciar Carrito"):
        st.session_state.cart = {}
        st.toast("Carrito vaciado 🗑️")
        st.rerun()
        
    if col_cart_buy.button("Realizar pedido"):
        order_id = random.randint(100000, 999999)
        st.session_state.last_order = {
            "id": order_id,
            "total": total,
            "items": st.session_state.cart.copy()
        }
        st.session_state.cart = {}
        st.rerun()

# Mostrar métrica de consultas del chatbot en el sidebar
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown("---")


# ----------------- NAVEGACIÓN POR PESTAÑAS (TABS) -----------------
tab_catalog, tab_chatbot = st.tabs(["🛍️ Catálogo", "💬 Atención al Cliente"])

# Muestra el banner de confirmación de pedido si existe
if "last_order" in st.session_state:
    order = st.session_state.last_order
    st.success(f"""
    ### 🎉 ¡Pedido Realizado con Éxito!
    Tu pedido **#SH-{order['id']}** ha sido registrado correctamente.
    * **Monto total:** S/ {order['total']:.2f}
    * **Tiempo estimado de entrega:** 2-3 horas dentro de la ciudad.
    
    ¡Gracias por preferir postres saludables que cuidan tu cuerpo! 🌿
    """)
    if st.button("Aceptar"):
        del st.session_state.last_order
        st.rerun()

# ----------------- TABS: 🛍️ CATÁLOGO -----------------
with tab_catalog:
    st.markdown("### Nuestro Menú Saludable")
    st.write("Explora nuestra selección de postres elaborados con insumos de alta calidad, libres de azúcares refinadas y llenos de beneficios.")
    
    # Buscador y Filtro interactivo para mejorar la UX (Wow factor)
    col_search, col_filter = st.columns([2, 1])
    search_query = col_search.text_input("🔍 Buscar postre...", placeholder="Escribe el nombre o ingrediente de un postre...")
    
    # Extraer todas las etiquetas únicas
    all_tags = sorted(list(set(tag for p in PRODUCTS for tag in p['etiquetas'])))
    selected_tag = col_filter.selectbox("🏷️ Filtrar por beneficio:", ["Todos"] + all_tags)
    
    # Filtrado lógico
    filtered_products = PRODUCTS
    if search_query:
        filtered_products = [p for p in filtered_products if search_query.lower() in p['nombre'].lower() or search_query.lower() in p['descripcion_breve'].lower() or search_query.lower() in p['ingredientes'].lower()]
    if selected_tag != "Todos":
        filtered_products = [p for p in filtered_products if selected_tag in p['etiquetas']]
        
    if not filtered_products:
        st.info("No se encontraron postres que coincidan con la búsqueda. ¡Prueba otra combinación! 🍰")
    else:
        # Renderizar en cuadrícula (grid) de 3 columnas
        cols = st.columns(3)
        for idx, p in enumerate(filtered_products):
            col = cols[idx % 3]
            
            # Calcular stock restante considerando el carrito
            en_carrito = st.session_state.cart.get(p['id'], 0)
            disponible_stock = p['stock'] - en_carrito
            
            with col:
                # Contenedor de tarjeta de producto st.container
                with st.container(border=True):
                    # Encabezado de la tarjeta: Emoji + Nombre
                    st.markdown(f"### {p['emoji']} {p['nombre']}")
                    
                    # Etiquetas de colores (Badges)
                    badges_html = "".join([f'<span class="badge">{tag}</span>' for tag in p['etiquetas']])
                    st.markdown(f'<div class="badge-container">{badges_html}</div>', unsafe_allow_html=True)
                    
                    # Cuerpo: Descripción breve
                    st.write(p['descripcion_breve'])
                    
                    # Expander con ingredientes y detalles
                    with st.expander("🔍 Ver ingredientes y detalles"):
                        st.markdown(f"**Ingredientes:** {p['ingredientes']}")
                        st.markdown(f"**Calorías:** **{p['kcal']}**")
                        
                        # Indicador visual del stock
                        if disponible_stock > 0:
                            st.markdown(f"**Stock:** 🟢 disponible ({disponible_stock} u.)")
                        else:
                            st.markdown("**Stock:** 🔴 agotado")
                    
                    # Pie de la tarjeta: Precio destacado + Botón
                    precio_display = p.get('precio_detalle', f"S/ {p['precio']:.2f}")
                    st.markdown(f"<h4 style='color: #E07A5F; margin: 15px 0 5px 0;'>{precio_display}</h4>", unsafe_allow_html=True)
                    
                    # Botón agregar al carrito
                    btn_disabled = (disponible_stock <= 0)
                    btn_label = "Agotado" if btn_disabled else "Agregar al carrito"
                    
                    if st.button(btn_label, key=f"add_{p['id']}", disabled=btn_disabled):
                        st.session_state.cart[p['id']] = en_carrito + 1
                        st.toast(f"¡{p['nombre']} agregado al carrito! 🛒")
                        st.rerun()


# ----------------- TABS: 💬 ATENCIÓN AL CLIENTE -----------------
with tab_chatbot:
    st.markdown("### Conversa con Sweetie 🌿")
    st.write("¿Tienes alguna pregunta sobre nuestros postres, stock, envíos o ingredientes? ¡Pregúntame!")
    
    # Configurar API Key de Gemini
    api_key = st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        st.warning("⚠️ **Clave de API no configurada**: Configura la clave `GEMINI_API_KEY` en tus secretos de Streamlit (`.streamlit/secrets.toml`) para chatear con Sweetie.")
    else:
        # Configurar el cliente de google-genai
        client = genai.Client(api_key=api_key)
        
        # Renderizar historial de mensajes
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg.get("time_taken") is not None:
                    st.markdown(f"<span style='color: gray; font-size: 0.8rem;'>⏱ Respondido en {msg['time_taken']:.2f}s</span>", unsafe_allow_html=True)
        
        # Captura de entrada del usuario
        user_input = st.chat_input("Pregúntale a Sweetie...")
        
        if user_input:
            # Añadir mensaje del usuario al historial y renderizarlo inmediatamente
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
                
            # Generar respuesta de Sweetie
            with st.chat_message("assistant"):
                with st.spinner("Sweetie está pensando..."):
                    start_time = time.perf_counter()
                    try:
                        # Construir cadena de detalles del catálogo para inyectar en la instrucción del sistema
                        catalogo_str = "\n".join([
                            f"- {p['nombre']}: Precio: S/ {p['precio']:.2f} | Kcal: {p['kcal']} | Stock: {p['stock']} unidades | Ingredientes: {p['ingredientes']} | Beneficios/Etiquetas: {', '.join(p['etiquetas'])}"
                            for p in PRODUCTS
                        ])
                        #Instrucción al sistema
                        system_instruction = f"""Eres "Sweetie", asistenta virtual de Sweet & Healthy, una tienda de postres saludables. Responde siempre en español, 
                        de forma amable y concisa. Solo debes responder preguntas relacionadas con: el catálogo de productos, lugares de envío (solo Lima Metropolitana)
                        precios, ingredientes, beneficios nutricionales, calorías, stock disponible, métodos de pago (Yape, Plin, efectivo), tiempos de entrega 
                        (1 hora en toda Lima Metropolitana), disponibilidad,ranking actual de productos más vendidos y políticas de devolución (no aplica para productos
                        perecederos). Si te preguntan algo fuera de estos temas, redirige  amablemente la conversación hacia los productos.
                        
                        Ranking actual de productos más vendidos:
                        1. Brownie de avena y cacao 🍫
                        2. Cheesecake de frutos rojos 🍰
                        3. Muffins de zanahoria 🧁
                        4. Galletas de avena y chía 🍪
                        5. Budín de chía y coco 🍧
                        6. Mousse de maracuyá 🍮
                        7. Tarta de manzana integral 🥧
                        8. Alfajores de quinua 🫓
                        9. Trufas de cacao y dátil 🧆
                        10. Helado de plátano y cacao 🍦

                        Reglas de recomendación:
                        - Si el cliente pregunta por recomendaciones y no especifica preferencias, prioriza sugerir productos del ranking de más vendidos.                        

                        
                        Aquí está el catálogo oficial y stock de la tienda para que respondas con exactitud:
                        {catalogo_str}
                        """
                        
                        # Construir el formato de historial de chat para google-genai
                        gemini_history = []
                        # Ignorar el último mensaje de la sesión ya que es el que se enviará con send_message
                        for m in st.session_state.messages[:-1]:
                            role = "model" if m["role"] == "assistant" else "user"
                            gemini_history.append(
                                types.Content(
                                    role=role,
                                    parts=[types.Part(text=m["content"])]
                                )
                            )
                            
                        # Iniciar la sesión de chat con el historial y la configuración en google-genai
                        chat = client.chats.create(
                            model="gemini-2.5-flash-lite",
                            history=gemini_history,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction
                            )
                        )
                        MAX_RETRIES = 3
                        response_text = None
                        for attempt in range(MAX_RETRIES):
                                try:
                                    response = chat.send_message(user_input)
                                    response_text = response.text
                                    break
                                except Exception as e:
                                    error_msg = str(e)
                                    if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                                        response_text = (
                                             "Sweetie 🌿 no está disponible temporalmente porque se alcanzó el límite diario de consultas. "
                                             "Por favor, inténtalo más tarde."
                                        )

                                    elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                                        if attempt < MAX_RETRIES - 1:
                                            time.sleep(2)
                                            continue
                                        else:
                                            response_text=(
                                            "Sweetie está atendiendo muchas solicitudes en este momento 🌿. "
                                            "Por favor, inténtalo nuevamente en unos segundos."  
                                            )
                                    else:
                                        response_text = (
                                            "Sweetie 🌿 reporta un problema temporal. "
                                            "Por favor, intenta nuevamente más tarde."
                                        )

                    except Exception as e:
                        print(f"Error Gemini: {e}")
                        response_text = "Ocurrió un problema temporal con Sweetie 🌿. Intenta nuevamente en unos momentos."


                    end_time = time.perf_counter()
                    time_taken = end_time - start_time
                    
                    # Mostrar la respuesta y el tiempo tomado
                    st.write(response_text)
                    st.markdown(f"<span style='color: gray; font-size: 0.8rem;'>⏱ Respondido en {time_taken:.2f}s</span>", unsafe_allow_html=True)
                    
                    # Actualizar historial y métrica
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "time_taken": time_taken
                    })
                    st.session_state.queries_count += 1
                    st.rerun()


# ----------------- FOOTER CORPORATIVO GENERAL -----------------
st.markdown("""
<div class="footer">
    <p style="font-size: 1.1rem; font-weight: 600; color: #2D5A40; margin-bottom: 8px;">Sweet & Healthy 🌿</p>
    <p>🕒 <b>Horario de Atención:</b> Lunes a Sábado de 9:00 AM a 8:00 PM</p>
    <p>📞 <b>WhatsApp de Pedidos:</b> +51 987 654 321 (Ficticio)</p>
    <div style="display: flex; justify-content: center; gap: 15px; font-size: 1.5rem; margin-top: 10px; margin-bottom: 15px;">
        <span title="Facebook" style="cursor: pointer;">📘</span>
        <span title="Instagram" style="cursor: pointer;">📸</span>
        <span title="TikTok" style="cursor: pointer;">🎵</span>
    </div>
    <p style="font-size: 0.8rem; color: #888; margin-top: 10px;">© 2026 Sweet & Healthy. Postres deliciosos y saludables que cuidan tu cuerpo.</p>
</div>
""", unsafe_allow_html=True)
