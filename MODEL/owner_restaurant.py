from BDD.Conexion import get_connection


class OwnerModel:
    @staticmethod
    def create_menu(rol_ejecutor, id_restaurante, nombre_plato, descripcion, precio):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC sp_CrearMenu ?, ?, ?, ?, ?", (rol_ejecutor, id_restaurante, nombre_plato, descripcion, precio))
        conn.commit()
        conn.close()

    @staticmethod
    def edit_menu(rol_ejecutor, id_menu, nuevo_nombre, nueva_descripcion, nuevo_precio):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC sp_EditarMenu ?, ?, ?, ?, ?", (rol_ejecutor, id_menu, nuevo_nombre, nueva_descripcion, nuevo_precio))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_menu(rol_ejecutor, id_menu):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC sp_EliminarMenu ?, ?", (rol_ejecutor, id_menu))
        conn.commit()
        conn.close()

    @staticmethod
    def list_menus_by_owner(id_dueno):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT m.ID_MENU, m.ID_RESTAURANTE, m.NOMBRE_PLATO, m.DESCRIPCION, m.PRECIO, m.DISPONIBLE "
            "FROM MENU m JOIN RESTAURANTE r ON m.ID_RESTAURANTE = r.ID_RESTAURANTE WHERE r.ID_DUENO = ?",
            (id_dueno,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    # Promociones: funciones básicas si existe tabla PROMOCIONES
    @staticmethod
    def create_promotion(id_restaurante, titulo, descripcion, descuento, fecha_vigencia):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO PROMOCIONES (ID_RESTAURANTE, TITULO, DESCRIPCION, DESCUENTO, FECHA_VIGENCIA) VALUES (?, ?, ?, ?, ?)", (id_restaurante, titulo, descripcion, descuento, fecha_vigencia))
            conn.commit()
        except Exception as e:
            raise
        finally:
            conn.close()
