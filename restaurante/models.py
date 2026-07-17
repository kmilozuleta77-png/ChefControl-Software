# Modelos generados con 'inspectdb' desde el esquema MySQL existente.
# managed=False en todos los modelos de negocio: Django no crea ni altera estas tablas;
# el esquema está gestionado directamente en MySQL (ver chefcontrol_database/chefcontrol_database.sql).
from django.db import models


# -----------------------------------------------------------------------
# TABLAS INTERNAS DE DJANGO (autogeneradas — no modificar)
# -----------------------------------------------------------------------

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


# -----------------------------------------------------------------------
# MODELOS DE NEGOCIO
# -----------------------------------------------------------------------

class Cargo(models.Model):
    id_cargo = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cargo'

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categoria'

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.CharField(unique=True, max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(unique=True, max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    estado = models.CharField(max_length=8, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cliente'

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class Mesa(models.Model):
    id_mesa = models.AutoField(primary_key=True)
    numero_mesa = models.IntegerField(unique=True)
    capacidad = models.IntegerField()
    estado = models.CharField(max_length=16, blank=True, null=True)
    ubicacion = models.CharField(max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mesa'

    def __str__(self):
        return f"Mesa {self.numero_mesa}"


class Empleado(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    id_cargo = models.ForeignKey(Cargo, models.DO_NOTHING, db_column='id_cargo')
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.CharField(unique=True, max_length=20)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(unique=True, max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    fecha_ingreso = models.DateField()
    estado = models.CharField(max_length=8, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empleado'

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    id_categoria = models.ForeignKey(Categoria, models.DO_NOTHING, db_column='id_categoria')
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=300, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(blank=True, null=True)
    stock_minimo = models.IntegerField(blank=True, null=True)
    imagen = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=13, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'producto'
        # Índice en stock para acelerar el filtro de alertas de inventario (stock <= stock_minimo)
        indexes = [
            models.Index(fields=['stock'], name='idx_producto_stock'),
        ]

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    # id_cliente es nullable: soporta pedidos "para llevar" sin cliente registrado
    id_cliente = models.ForeignKey(Cliente, models.DO_NOTHING, db_column='id_cliente', blank=True, null=True)
    id_empleado = models.ForeignKey(Empleado, models.DO_NOTHING, db_column='id_empleado')
    # id_mesa es nullable: soporta pedidos "para llevar" sin mesa asignada
    id_mesa = models.ForeignKey(Mesa, models.DO_NOTHING, db_column='id_mesa', blank=True, null=True)
    fecha_pedido = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=14, blank=True, null=True)
    tipo_pedido = models.CharField(max_length=11, blank=True, null=True)
    observaciones = models.CharField(max_length=500, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pedido'
        indexes = [
            # Acelera los filtros por estado usados en KDS (cocina) y caja (facturación)
            models.Index(fields=['estado'], name='idx_pedido_estado'),
            # Acelera el ordenamiento por fecha en dashboard y KDS
            models.Index(fields=['-fecha_pedido'], name='idx_pedido_fecha_desc'),
        ]

    def __str__(self):
        return f"Pedido #{self.id_pedido}"


class Detallepedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    # PROTECT: impide borrar un Pedido si tiene detalles, preservando el historial
    id_pedido = models.ForeignKey(Pedido, models.PROTECT, db_column='id_pedido')
    # PROTECT: impide borrar un Producto que ya fue vendido, preservando integridad contable
    id_producto = models.ForeignKey(Producto, models.PROTECT, db_column='id_producto')
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detallepedido'


class Factura(models.Model):
    id_factura = models.AutoField(primary_key=True)
    # PROTECT: impide borrar un Pedido que ya tiene factura emitida (regla contable)
    id_pedido = models.OneToOneField(Pedido, models.PROTECT, db_column='id_pedido')
    id_empleado = models.ForeignKey(Empleado, models.DO_NOTHING, db_column='id_empleado')
    fecha_factura = models.DateTimeField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=15, blank=True, null=True)
    estado = models.CharField(max_length=9, blank=True, null=True)
    observaciones = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'factura'