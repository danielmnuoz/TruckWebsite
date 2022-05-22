# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Application(models.Model):
    application_id = models.IntegerField(db_column='APPLICATION_ID', primary_key=True)  # Field name made lowercase.
    org_id = models.IntegerField(db_column='ORG_ID', blank=True, null=True)  # Field name made lowercase.
    driver_id = models.IntegerField(db_column='DRIVER_ID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'APPLICATION'


class AuditLog(models.Model):
    log_id = models.AutoField(db_column='LOG_ID', primary_key=True)  # Field name made lowercase.
    date = models.DateField(db_column='DATE', blank=True, null=True)  # Field name made lowercase.
    event = models.CharField(db_column='EVENT', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AUDIT_LOG'


class Catalog(models.Model):
    row_id = models.AutoField(db_column='ROW_ID', primary_key=True)  # Field name made lowercase.
    catalog_id = models.IntegerField(db_column='CATALOG_ID', blank=True, null=True)  # Field name made lowercase.
    items = models.CharField(db_column='ITEMS', max_length=255, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='DESCRIPTION', max_length=4096, blank=True, null=True)  # Field name made lowercase.
    image = models.CharField(db_column='IMAGE', max_length=255, blank=True, null=True)  # Field name made lowercase.
    price = models.IntegerField(db_column='PRICE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CATALOG'


class Driver(models.Model):
    driver_id = models.IntegerField(db_column='DRIVER_ID', primary_key=True)  # Field name made lowercase.
    points = models.IntegerField(db_column='POINTS', blank=True, null=True)  # Field name made lowercase.
    application_id = models.IntegerField(db_column='APPLICATION_ID', blank=True, null=True)  # Field name made lowercase.
    user_id = models.IntegerField(db_column='USER_ID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'DRIVER'


class GeneralUser(models.Model):
    user_id = models.AutoField(db_column='USER_ID', primary_key=True)  # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=45)  # Field name made lowercase.
    password = models.CharField(db_column='PASSWORD', max_length=45)  # Field name made lowercase.
    user_type = models.IntegerField(db_column='USER_TYPE')  # Field name made lowercase.
    points = models.IntegerField(db_column='POINTS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GENERAL_USER'


class Logins(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    date = models.DateField(db_column='DATE', blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=45, blank=True, null=True)  # Field name made lowercase.
    passfail = models.IntegerField(db_column='PASSFAIL', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'LOGINS'


class Order(models.Model):
    order_id = models.AutoField(db_column='ORDER_ID', primary_key=True)  # Field name made lowercase.
    item_id = models.IntegerField(db_column='ITEM_ID', blank=True, null=True)  # Field name made lowercase.
    address = models.CharField(db_column='ADDRESS', max_length=45, blank=True, null=True)  # Field name made lowercase.
    zipcode = models.CharField(db_column='ZIPCODE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='STATE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    purchase_time = models.DateField(db_column='PURCHASE_TIME', blank=True, null=True)  # Field name made lowercase.
    total_cost = models.IntegerField(db_column='TOTAL_COST', blank=True, null=True)  # Field name made lowercase.
    driver_id = models.IntegerField(db_column='DRIVER_ID', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='STATUS', max_length=45, blank=True, null=True)  # Field name made lowercase.
    org_id = models.IntegerField(db_column='ORG_ID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ORDER'


class OrgConnections(models.Model):
    connection_id = models.AutoField(db_column='CONNECTION_ID', primary_key=True)  # Field name made lowercase.
    org_id = models.IntegerField(db_column='ORG_ID')  # Field name made lowercase.
    user_id = models.IntegerField(db_column='USER_ID')  # Field name made lowercase.
    pending_app = models.IntegerField(db_column='PENDING_APP')  # Field name made lowercase.
    points = models.IntegerField(db_column='POINTS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ORG_CONNECTIONS'


class PointHistory(models.Model):
    driver_id = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    change = models.IntegerField()
    org_id = models.IntegerField()
    newbalance = models.IntegerField(db_column='newBalance', blank=True, null=True)  # Field name made lowercase.
    date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'POINT_HISTORY'


class Sponsor(models.Model):
    sponsor_id = models.IntegerField(db_column='SPONSOR_ID', primary_key=True)  # Field name made lowercase.
    org_id = models.IntegerField(db_column='ORG_ID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SPONSOR'


class SponsorOrg(models.Model):
    org_id = models.AutoField(db_column='ORG_ID', primary_key=True)  # Field name made lowercase.
    catalog_id = models.IntegerField(db_column='CATALOG_ID', blank=True, null=True)  # Field name made lowercase.
    org_name = models.CharField(db_column='ORG_NAME', max_length=255, blank=True, null=True)  # Field name made lowercase.
    rate = models.FloatField(db_column='RATE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SPONSOR_ORG'


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


class ShopCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=200)

    class Meta:
        managed = False
        db_table = 'shop_category'


class ShopProduct(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    image = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.IntegerField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    category = models.ForeignKey(ShopCategory, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'shop_product'
