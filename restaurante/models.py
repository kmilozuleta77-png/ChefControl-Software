# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


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


class Cargo(models.Model):
    id_cargo = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cargo'


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categoria'


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


class Detallepedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey('Pedido', models.DO_NOTHING, db_column='id_pedido')
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='id_producto')
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    observaciones = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detallepedido'


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


class Factura(models.Model):
    id_factura = models.AutoField(primary_key=True)
    id_pedido = models.OneToOneField('Pedido', models.DO_NOTHING, db_column='id_pedido')
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


class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, models.DO_NOTHING, db_column='id_cliente', blank=True, null=True)
    id_empleado = models.ForeignKey(Empleado, models.DO_NOTHING, db_column='id_empleado')
    id_mesa = models.ForeignKey(Mesa, models.DO_NOTHING, db_column='id_mesa', blank=True, null=True)
    fecha_pedido = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=14, blank=True, null=True)
    tipo_pedido = models.CharField(max_length=11, blank=True, null=True)
    observaciones = models.CharField(max_length=500, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pedido'


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
