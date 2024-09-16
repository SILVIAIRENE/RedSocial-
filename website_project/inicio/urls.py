from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('login/', views.login_usuario, name='login_usuario'),
    
    # Esta es la URL para la lista de publicaciones
    path('publicaciones/', views.lista_publicaciones, name='lista_publicaciones'),
    
    path('publicaciones/crear/', views.crear_publicacion, name='crear_publicacion'),
    path('comentarios/<int:comentario_id>/editar/', views.editar_comentario, name='editar_comentario'),
    path('comentarios/<int:comentario_id>/eliminar/', views.eliminar_comentario, name='eliminar_comentario'),
    path('publicaciones/<int:publicacion_id>/comentar/', views.comentar_publicacion, name='comentar_publicacion'),
    
    # Esta es la URL para dar "like" a una publicación
    path('publicaciones/<int:publicacion_id>/', views.detalle_publicacion, name='detalle_publicacion'),
    path('publicaciones/<int:publicacion_id>/like/', views.like_publicacion, name='like_publicacion'),
    
    path('perfil/<int:usuario_id>/', views.ver_perfil, name='ver_perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    
    path('solicitudes/', views.solicitudes_amistad, name='solicitudes_amistad'),
    path('solicitud/enviar/<int:usuario_id>/', views.enviar_solicitud, name='enviar_solicitud'),
    path('solicitud/aceptar/<int:solicitud_id>/', views.aceptar_solicitud, name='aceptar_solicitud'),
    path('solicitud/rechazar/<int:solicitud_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
    
    path('amigos/', views.lista_amigos, name='lista_amigos'),
    path('grupos/', views.grupos_usuario, name='grupos_usuario'),
    path('grupos/crear/', views.crear_grupo, name='crear_grupo'),
    path('grupos/<int:grupo_id>/', views.detalle_grupo, name='detalle_grupo'),
    path('grupos/<int:grupo_id>/añadir_amigos/', views.detalle_grupo, name='añadir_amigos_a_grupo'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
