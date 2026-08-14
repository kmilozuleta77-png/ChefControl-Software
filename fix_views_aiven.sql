-- Recrea las 3 vistas de ChefControl sin DEFINER (usa el usuario que ejecuta el script)
-- Aiven no permite DEFINER=root@localhost porque ese usuario no existe en su servidor.

CREATE OR REPLACE VIEW `v_pedidos_detalle` AS
select `p`.`id_pedido` AS `id_pedido`,
       `p`.`fecha_pedido` AS `fecha_pedido`,
       `p`.`estado` AS `estado_pedido`,
       `p`.`tipo_pedido` AS `tipo_pedido`,
       `p`.`total` AS `total`,
       concat(`c`.`nombres`,' ',`c`.`apellidos`) AS `cliente`,
       concat(`e`.`nombres`,' ',`e`.`apellidos`) AS `empleado`,
       `ca`.`nombre` AS `cargo_empleado`,
       `m`.`numero_mesa` AS `numero_mesa`,
       `m`.`ubicacion` AS `ubicacion`
from (((`pedido` `p`
    left join `cliente` `c` on((`p`.`id_cliente` = `c`.`id_cliente`)))
    join `empleado` `e` on((`p`.`id_empleado` = `e`.`id_empleado`)))
    join `cargo` `ca` on((`e`.`id_cargo` = `ca`.`id_cargo`)))
    left join `mesa` `m` on((`p`.`id_mesa` = `m`.`id_mesa`));

CREATE OR REPLACE VIEW `v_productos_inventario` AS
select `pr`.`id_producto` AS `id_producto`,
       `pr`.`nombre` AS `producto`,
       `cat`.`nombre` AS `categoria`,
       `pr`.`precio` AS `precio`,
       `pr`.`stock` AS `stock`,
       `pr`.`stock_minimo` AS `stock_minimo`,
       `pr`.`estado` AS `estado`,
       (case when (`pr`.`stock` = 0) then 'Agotado'
             when (`pr`.`stock` <= `pr`.`stock_minimo`) then 'Stock Bajo'
             else 'Stock Normal' end) AS `alerta_inventario`
from (`producto` `pr`
    join `categoria` `cat` on((`pr`.`id_categoria` = `cat`.`id_categoria`)));

CREATE OR REPLACE VIEW `v_ventas_empleado` AS
select concat(`e`.`nombres`,' ',`e`.`apellidos`) AS `empleado`,
       `ca`.`nombre` AS `cargo`,
       count(`f`.`id_factura`) AS `total_facturas`,
       sum(`f`.`total`) AS `total_ventas`
from ((`factura` `f`
    join `empleado` `e` on((`f`.`id_empleado` = `e`.`id_empleado`)))
    join `cargo` `ca` on((`e`.`id_cargo` = `ca`.`id_cargo`)))
where (`f`.`estado` = 'Pagada')
group by `e`.`id_empleado`, `e`.`nombres`, `e`.`apellidos`, `ca`.`nombre`;
