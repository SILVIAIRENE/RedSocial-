from django.contrib import admin
from django.utils.html import format_html
from .models import Usuario, Publicacion, Comentario, Like, Amistad, Grupo, PerfilUsuario


class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'nombre_usuario', 'nombres', 'is_staff', 'is_active')
    search_fields = ('email', 'nombre_usuario')
    list_filter = ('is_staff', 'is_active')

admin.site.register(Usuario, UsuarioAdmin)
    

class Publicaciones():
    list_display = ('autor', 'contenido', 'fecha_publicacion')
    search_fields = ('autor', 'fecha_publicacion')
admin.site.register(Publicacion)

admin.site.register(Comentario)

admin.site.register(Like)

admin.site.register(Amistad)

admin.site.register(Grupo)
