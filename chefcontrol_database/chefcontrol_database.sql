-- ============================================================
--  ChefControl Software - Script de Base de Datos
--  Base de Datos: MySQL
--  Proyecto: Tecnología en ADSO - SENA
--  Descripción: Sistema integral de gestión para restaurantes
-- ============================================================

-- Crear y seleccionar la base de datos
CREATE DATABASE IF NOT EXISTS chefcontrol_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE chefcontrol_db;

-- ============================================================
-- TABLA: Cargo
-- Almacena los cargos de los empleados
-- ============================================================
CREATE TABLE Cargo (
    id_cargo        INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(50)     NOT NULL UNIQUE,
    descripcion     VARCHAR(200)    NULL,
    fecha_creacion  DATETIME        DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: Empleado
-- Almacena la información de los empleados
-- ============================================================
CREATE TABLE Empleado (
    id_empleado     INT AUTO_INCREMENT PRIMARY KEY,
    id_cargo        INT             NOT NULL,
    nombres         VARCHAR(100)    NOT NULL,
    apellidos       VARCHAR(100)    NOT NULL,
    cedula          VARCHAR(20)     NOT NULL UNIQUE,
    telefono        VARCHAR(20)     NULL,
    email           VARCHAR(100)    NULL UNIQUE,
    direccion       VARCHAR(200)    NULL,
    fecha_ingreso   DATE            NOT NULL,
    estado          ENUM('Activo', 'Inactivo') DEFAULT 'Activo',
    fecha_creacion  DATETIME        DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_empleado_cargo FOREIGN KEY (id_cargo)
        REFERENCES Cargo(id_cargo)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- ============================================================
-- TABLA: Cliente
-- Almacena la información de los clientes
-- ============================================================
CREATE TABLE Cliente (
    id_cliente      INT AUTO_INCREMENT PRIMARY KEY,
    nombres         VARCHAR(100)    NOT NULL,
    apellidos       VARCHAR(100)    NOT NULL,
    cedula          VARCHAR(20)     NULL UNIQUE,
    telefono        VARCHAR(20)     NULL,
    email           VARCHAR(100)    NULL UNIQUE,
    direccion       VARCHAR(200)    NULL,
    estado          ENUM('Activo', 'Inactivo') DEFAULT 'Activo',
    fecha_creacion  DATETIME        DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: Categoria
-- Almacena las categorías de los productos
-- ============================================================
CREATE TABLE Categoria (
    id_categoria    INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(50)     NOT NULL UNIQUE,
    descripcion     VARCHAR(200)    NULL,
    fecha_creacion  DATETIME        DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: Producto
-- Almacena los productos del restaurante
-- ============================================================
CREATE TABLE Producto (
    id_producto     INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria    INT             NOT NULL,
    nombre          VARCHAR(100)    NOT NULL,
    descripcion     VARCHAR(300)    NULL,
    precio          DECIMAL(10,2)   NOT NULL,
    stock           INT             DEFAULT 0,
    stock_minimo    INT             DEFAULT 5,
    imagen          VARCHAR(255)    NULL,
    estado          ENUM('Disponible', 'No Disponible', 'Agotado') DEFAULT 'Disponible',
    fecha_creacion  DATETIME        DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_producto_categoria FOREIGN KEY (id_categoria)
        REFERENCES Categoria(id_categoria)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- ============================================================
-- TABLA: Mesa
-- Almacena la información de las mesas del restaurante
-- ============================================================
CREATE TABLE Mesa (
    id_mesa         INT AUTO_INCREMENT PRIMARY KEY,
    numero_mesa     INT             NOT NULL UNIQUE,
    capacidad       INT             NOT NULL,
    estado          ENUM('Disponible', 'Ocupada', 'Reservada', 'En Mantenimiento') DEFAULT 'Disponible',
    ubicacion       VARCHAR(100)    NULL,
    fecha_creacion  DATETIME        DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: Pedido
-- Almacena los pedidos realizados
-- ============================================================
CREATE TABLE Pedido (
    id_pedido       INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente      INT             NULL,
    id_empleado     INT             NOT NULL,
    id_mesa         INT             NULL,
    fecha_pedido    DATETIME        DEFAULT CURRENT_TIMESTAMP,
    estado          ENUM('Pendiente', 'En Preparación', 'Listo', 'Entregado', 'Cancelado') DEFAULT 'Pendiente',
    tipo_pedido     ENUM('En Mesa', 'Para Llevar', 'Domicilio') DEFAULT 'En Mesa',
    observaciones   VARCHAR(500)    NULL,
    total           DECIMAL(10,2)   DEFAULT 0.00,
    CONSTRAINT fk_pedido_cliente FOREIGN KEY (id_cliente)
        REFERENCES Cliente(id_cliente)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT fk_pedido_empleado FOREIGN KEY (id_empleado)
        REFERENCES Empleado(id_empleado)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_pedido_mesa FOREIGN KEY (id_mesa)
        REFERENCES Mesa(id_mesa)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

-- ============================================================
-- TABLA: DetallePedido
-- Almacena los productos de cada pedido
-- ============================================================
CREATE TABLE DetallePedido (
    id_detalle      INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido       INT             NOT NULL,
    id_producto     INT             NOT NULL,
    cantidad        INT             NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10,2)   NOT NULL,
    subtotal        DECIMAL(10,2)   GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
    observaciones   VARCHAR(300)    NULL,
    CONSTRAINT fk_detalle_pedido FOREIGN KEY (id_pedido)
        REFERENCES Pedido(id_pedido)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_detalle_producto FOREIGN KEY (id_producto)
        REFERENCES Producto(id_producto)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- ============================================================
-- TABLA: Factura
-- Almacena las facturas generadas
-- ============================================================
CREATE TABLE Factura (
    id_factura          INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido           INT             NOT NULL UNIQUE,
    id_empleado         INT             NOT NULL,
    fecha_factura       DATETIME        DEFAULT CURRENT_TIMESTAMP,
    subtotal            DECIMAL(10,2)   NOT NULL,
    impuesto            DECIMAL(10,2)   DEFAULT 0.00,
    descuento           DECIMAL(10,2)   DEFAULT 0.00,
    total               DECIMAL(10,2)   NOT NULL,
    metodo_pago         ENUM('Efectivo', 'Tarjeta Débito', 'Tarjeta Crédito', 'Transferencia') DEFAULT 'Efectivo',
    estado              ENUM('Pagada', 'Pendiente', 'Anulada') DEFAULT 'Pendiente',
    observaciones       VARCHAR(300)    NULL,
    CONSTRAINT fk_factura_pedido FOREIGN KEY (id_pedido)
        REFERENCES Pedido(id_pedido)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_factura_empleado FOREIGN KEY (id_empleado)
        REFERENCES Empleado(id_empleado)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- ============================================================
-- DATOS INICIALES (Seed Data)
-- ============================================================

-- Cargos iniciales
INSERT INTO Cargo (nombre, descripcion) VALUES
('Administrador',   'Gestiona y supervisa todas las operaciones del restaurante'),
('Cajero',          'Responsable del cobro y facturación'),
('Mesero',          'Atiende a los clientes y toma los pedidos'),
('Cocinero',        'Prepara los alimentos según los pedidos'),
('Auxiliar Cocina', 'Apoya las labores de cocina');

-- Categorías de productos
INSERT INTO Categoria (nombre, descripcion) VALUES
('Entradas',    'Platos de entrada y aperitivos'),
('Platos Fuertes', 'Platos principales del menú'),
('Bebidas',     'Bebidas frías y calientes'),
('Postres',     'Postres y dulces'),
('Combos',      'Combos y menús especiales');

-- Mesas del restaurante
INSERT INTO Mesa (numero_mesa, capacidad, ubicacion) VALUES
(1,  2,  'Zona Interior'),
(2,  2,  'Zona Interior'),
(3,  4,  'Zona Interior'),
(4,  4,  'Zona Interior'),
(5,  4,  'Zona Exterior'),
(6,  6,  'Zona Exterior'),
(7,  6,  'Zona VIP'),
(8,  8,  'Zona VIP');

-- ============================================================
-- VISTAS ÚTILES
-- ============================================================

-- Vista: Pedidos con información completa
CREATE OR REPLACE VIEW v_pedidos_detalle AS
SELECT
    p.id_pedido,
    p.fecha_pedido,
    p.estado AS estado_pedido,
    p.tipo_pedido,
    p.total,
    CONCAT(c.nombres, ' ', c.apellidos) AS cliente,
    CONCAT(e.nombres, ' ', e.apellidos) AS empleado,
    ca.nombre AS cargo_empleado,
    m.numero_mesa,
    m.ubicacion
FROM Pedido p
LEFT JOIN Cliente c ON p.id_cliente = c.id_cliente
JOIN Empleado e ON p.id_empleado = e.id_empleado
JOIN Cargo ca ON e.id_cargo = ca.id_cargo
LEFT JOIN Mesa m ON p.id_mesa = m.id_mesa;

-- Vista: Productos con categoría y estado de inventario
CREATE OR REPLACE VIEW v_productos_inventario AS
SELECT
    pr.id_producto,
    pr.nombre AS producto,
    cat.nombre AS categoria,
    pr.precio,
    pr.stock,
    pr.stock_minimo,
    pr.estado,
    CASE
        WHEN pr.stock = 0 THEN 'Agotado'
        WHEN pr.stock <= pr.stock_minimo THEN 'Stock Bajo'
        ELSE 'Stock Normal'
    END AS alerta_inventario
FROM Producto pr
JOIN Categoria cat ON pr.id_categoria = cat.id_categoria;

-- Vista: Reporte de ventas por empleado
CREATE OR REPLACE VIEW v_ventas_empleado AS
SELECT
    CONCAT(e.nombres, ' ', e.apellidos) AS empleado,
    ca.nombre AS cargo,
    COUNT(f.id_factura) AS total_facturas,
    SUM(f.total) AS total_ventas
FROM Factura f
JOIN Empleado e ON f.id_empleado = e.id_empleado
JOIN Cargo ca ON e.id_cargo = ca.id_cargo
WHERE f.estado = 'Pagada'
GROUP BY e.id_empleado, e.nombres, e.apellidos, ca.nombre;

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================
