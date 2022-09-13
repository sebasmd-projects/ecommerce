from django.db import models

from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator

from apps.authentication.managers import ManagerPersonas

"""
    nombre, correo, tipo_id, ident, rol, ciudad, direccion
    celular o tel, genero
"""


class ModeloPersonas(AbstractBaseUser, PermissionsMixin):
    """
        To do:
            -   Añadir un campo para el genero del usuario utilizando la elección de
                generos, y añadirlo a la lista de campos que se exportan. Recordar realizar
                el makemigrations y el migrate.
    """
    SUPERUSUARIO = 'S'
    MANAGER = 'M'
    USUARIO = 'U'

    HOMBRE = 'H'
    MUJER = 'M'
    OTRO = 'O'
    
    CEDULA = 'CC'
    TARJETA_IDENTIDAD = 'TI'
    PASAPORTE = 'PP'
    CEDULA_EXTRANJERA = 'CE'

    ELECCION_DE_ROLES = [
        (SUPERUSUARIO, 'Superusuario'),
        (MANAGER, 'Manager'),
        (USUARIO, 'Usuario'),
    ]

    ELECCION_DE_GENEROS = [
        (HOMBRE, 'Hombre'),
        (MUJER, 'Mujer'),
        (OTRO, 'Otro'),
    ]
    
    ELECCION_DE_TIPOS_DE_IDENTIFICACION = [
        (CEDULA, 'Cédula de ciudadanía'),
        (TARJETA_IDENTIDAD, 'Tarjeta de identidad'),
        (PASAPORTE, 'Pasaporte'),
        (CEDULA_EXTRANJERA, 'Cédula de extranjería'),
    ]

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        "Nombre de usuario (Username)",
        max_length=150,
        unique=True,
        help_text="Requerido, único. 150 caracteres o menos. Letras y dígitos",
        validators=[username_validator],
    )
    
    tipo_identificacion = models.CharField(
        'Tipo de identificación',
        max_length=2,
        choices=ELECCION_DE_TIPOS_DE_IDENTIFICACION,
        default=CEDULA,
        help_text="Requerido. Seleccione el tipo de identificación",
    )
    
    identificacion = models.CharField(
        'Identificación',
        max_length=20,
        help_text="Requerido. 20 caracteres o menos. Letras y dígitos",
    )
    
    pais = models.CharField(
        'País',
        max_length=50,
        help_text="Requerido. 50 caracteres o menos. Letras y dígitos",
    )
    
    ciudad = models.CharField(
        'Ciudad, Región o Departamento',
        max_length=50,
        help_text="Requerido. 50 caracteres o menos. Letras y dígitos",
    )
    
    direccion = models.CharField(
        'Dirección',
        max_length=150,
        help_text="Especificar la dirección de residencia",
    )
    
    anotaciones_direccion = models.CharField(
        'Anotaciones de la dirección (Casa, Apto, Edificio, etc.)',
        max_length=200,
        help_text="Especificar anotaciones de la dirección",
    )

    email = models.EmailField(
        "Correo electrónico",
        max_length=254,
        unique=True,
        help_text="Requerido, único. 254 caracteres o menos. Dirección de correo válida",
    )

    termsYcond = models.BooleanField(
        "Acepto los términos y condiciones",
        default=False,
        help_text="Requerido. Acepto los términos y condiciones",
    )

    cod_verificacion = models.CharField(
        'Código de verificación',
        max_length=4,
        default='0000',
        help_text='Requerido. 4 caracteres o menos. Código de verificación',
    )

    is_staff = models.BooleanField(
        "Miembro del staff",
        default=False,
        help_text="Designa si el usuario puede acceder al administrador de Django"
    )

    nombres = models.CharField(
        'Nombres',
        max_length=50,
        help_text='Nombre(s) de la persona',
    )

    apellidos = models.CharField(
        'Apellidos',
        max_length=50,
        help_text='Apellido(s) de la persona'
    )

    nombre_completo = models.CharField(
        'Nombre completo',
        max_length=100,
        help_text='Nombre completo de la persona',
        null=True,
        blank=True,
    )

    celular = models.CharField(
        'Celular',
        max_length=20,
        help_text='Celular de la persona (ejm: +573002001010)',
    )

    rol = models.CharField(
        'Rol',
        max_length=1,
        choices=ELECCION_DE_ROLES,
        default=USUARIO,
        help_text='Rol de la persona',
    )

    is_active = models.BooleanField(
        '¿Es un usuario activo?',
        default=True,
        help_text='¿El usuario está activo?',
    )

    created = models.DateTimeField(
        'Fecha de creación',
        default=timezone.now,
        help_text='Fecha de creación del usuario',
        blank=True,
        null=True,
    )

    updated = models.DateTimeField(
        'Fecha de actualización o edición',
        auto_now=True,
        help_text='Fecha de actualización o edición del usuario',
        blank=True,
        null=True,
    )

    order = models.PositiveIntegerField(
        'Orden',
        default=0,
        help_text='Orden de aparición dentro de la base de datos',
    )

    objects = ManagerPersonas()
    
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = [
        'nombres',
        'apellidos',
        'username'
    ]

    def save(self, *args, **kwargs):
        self.nombre_completo = f"{self.nombres} {self.apellidos}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        db_table = 'apps_auth_personas'
        ordering = ['order', 'apellidos']

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
