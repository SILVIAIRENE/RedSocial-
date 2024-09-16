# Importa las funciones para manejar las vistas y redirecciones
from django.shortcuts import render, redirect, get_object_or_404
# Importa las herramientas para manejar mensajes de éxito y error en la vista
from django.contrib import messages
# Importa la función para autenticar a los usuarios
from django.contrib.auth import authenticate, login as auth_login
# Importa la excepción para manejar errores cuando no se encuentra un objeto
from django.core.exceptions import ObjectDoesNotExist
# Importa las clases para manejar respuestas HTTP y errores
from django.http import JsonResponse, HttpResponseBadRequest
# Importa los modelos del proyecto para trabajar con la base de datos
from .models import Publicacion, Comentario, PerfilUsuario, Usuario, Amistad, Grupo, PublicacionGrupo
# Importa el decorador para restringir vistas a usuarios autenticados
from django.contrib.auth.decorators import login_required
# Importa la clase para manejar el registro de logs
import logging
# Importa los formularios personalizados para manejar el perfil de usuario
from .forms import RegistroUsuarioForm, EditarPerfilForm, CrearGrupoForm, PublicacionGrupoForm

# Configuración del logger para depuración
logger = logging.getLogger(__name__)

##### CRUD ########

def lista_usuarios(request):
    """
    Muestra una lista de todos los usuarios en la base de datos.
    """
    usuarios = Usuario.objects.all()  # Obtiene todos los usuarios
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})

def crear_usuario(request):
    """
    Permite crear un nuevo usuario a través de un formulario POST.
    """
    if request.method == 'POST':
        nombres = request.POST['nombres']
        nombre_usuario = request.POST['nombre_usuario']
        email = request.POST['email']
        contrasena = request.POST['contrasena']
        
        # Verifica si el nombre de usuario o el correo electrónico ya existen
        if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return redirect('crear_usuario')
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está en uso.')
            return redirect('crear_usuario')

        # Crea y guarda el nuevo usuario
        usuario = Usuario(
            nombres=nombres,
            nombre_usuario=nombre_usuario,
            email=email,
        )
        usuario.set_password(contrasena)  # Encripta la contraseña
        usuario.save()

        messages.success(request, 'Usuario creado con éxito.')
        return redirect('lista_usuarios')
    
    return render(request, 'crear_usuario.html')

def editar_usuario(request, usuario_id):
    """
    Permite editar un usuario existente. Si se proporciona una nueva contraseña, se actualizará.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)  # Obtiene el usuario o lanza 404 si no existe
    if request.method == 'POST':
        usuario.nombres = request.POST['nombres']
        usuario.nombre_usuario = request.POST['nombre_usuario']
        usuario.email = request.POST['email']
        
        # Maneja la actualización de la contraseña solo si se proporciona
        contrasena = request.POST.get('contrasena')
        if contrasena:
            usuario.set_password(contrasena)
        
        usuario.is_staff = 'is_staff' in request.POST  # Actualiza el estado de staff si está presente en el POST
        usuario.save()
        messages.success(request, 'Usuario actualizado con éxito.')
        return redirect('lista_usuarios')
    return render(request, 'editar_usuario.html', {'usuario': usuario})

def eliminar_usuario(request, usuario_id):
    """
    Permite eliminar un usuario existente. Se solicita una confirmación a través de un formulario POST.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)  # Obtiene el usuario o lanza 404 si no existe
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado con éxito.')
        return redirect('lista_usuarios')
    return render(request, 'eliminar_usuario.html', {'usuario': usuario})

####### LOGIN & REGISTER ############
def registro_usuario(request):
    """
    Permite registrar un nuevo usuario a través de un formulario POST.
    """
    if request.method == 'POST':
        # Procesa el formulario de registro
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            # Obtiene los datos del formulario
            nombres = form.cleaned_data['nombres']
            nombre_usuario = form.cleaned_data['nombre_usuario']
            email = form.cleaned_data['email']
            contrasena = form.cleaned_data['contrasena']
            
            # Verifica si el nombre de usuario o el correo electrónico ya existen
            if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
                messages.error(request, 'El nombre de usuario ya está en uso.')
                return redirect('registro_usuario')
            if Usuario.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está en uso.')
                return redirect('registro_usuario')

            # Crea y guarda el nuevo usuario
            usuario = Usuario(
                nombre_usuario=nombre_usuario,
                email=email,
                nombres=nombres
            )
            usuario.set_password(contrasena)  # Encripta la contraseña
            usuario.save()

            messages.success(request, 'Usuario registrado con éxito. Ahora puedes iniciar sesión.')
            return redirect('login_usuario')
    
    else:
        # Inicializa el formulario vacío
        form = RegistroUsuarioForm()

    return render(request, 'registro.html', {'form': form})

def login_usuario(request):
    """
    Permite a un usuario iniciar sesión mediante la autenticación de sus credenciales.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        contrasena = request.POST.get('contrasena')
        
        # Autenticación del usuario
        usuario = authenticate(request, email=email, password=contrasena)
        if usuario is not None:
            auth_login(request, usuario)  # Inicia sesión al usuario
            messages.success(request, f'Bienvenido, {usuario.email}!')
            return redirect('lista_publicaciones')
        else:
            messages.error(request, 'Credenciales incorrectas.')

    return render(request, 'login.html')

############### POSTS ####################

@login_required
def lista_publicaciones(request):
    """
    Muestra una lista de todas las publicaciones.
    """
    publicaciones = Publicacion.objects.all()  # Obtiene todas las publicaciones
    return render(request, 'publicaciones/lista_publicaciones.html', {'publicaciones': publicaciones})

@login_required
def crear_publicacion(request):
    """
    Permite crear una nueva publicación. Se puede incluir una imagen.
    """
    if request.method == 'POST':
        contenido = request.POST['contenido']
        imagen = request.FILES.get('imagen')  # Obtiene el archivo de imagen
        #importante url silvia
        map_url = request.POST.get('map_url')#obtiene la url del mapa 
        # Crea y guarda la nueva publicación
        publicacion = Publicacion(
            autor=request.user,  # Establece el usuario como autor
            contenido=contenido,
            imagen=imagen,
            #importante url silvia
            map_url=map_url #Guarda la URL del mapa 
        )
        publicacion.save()

        messages.success(request, 'Publicación creada con éxito.')
        return redirect('lista_publicaciones')

    return render(request, 'publicaciones/crear_publicacion.html')

@login_required
def editar_publicacion(request, publicacion_id):
    """
    Permite editar una publicación existente.
    """
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)  # Obtiene la publicación o lanza 404 si no existe
    if request.method == 'POST':
        publicacion.contenido = request.POST['contenido']
        publicacion.map_url = request.POST.get('map_url') #actualiza url silvia
        publicacion.save()
        messages.success(request, 'Publicación actualizada con éxito.')
        return redirect('lista_publicaciones')
    return render(request, 'publicaciones/editar_publicacion.html', {'publicacion': publicacion})

@login_required
def eliminar_publicacion(request, publicacion_id):
    """
    Permite eliminar una publicación existente. Se solicita confirmación a través de un formulario POST.
    """
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)  # Obtiene la publicación o lanza 404 si no existe
    if request.method == 'POST':
        publicacion.delete()
        messages.success(request, 'Publicación eliminada con éxito.')
        return redirect('lista_publicaciones')
    return render(request, 'publicaciones/eliminar_publicacion.html', {'publicacion': publicacion})

#=====================

@login_required
def comentar_publicacion(request, publicacion_id):
    """
    Permite a un usuario agregar un comentario a una publicación.
    """
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)  # Obtiene la publicación o lanza 404 si no existe
    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        # Crea y guarda el nuevo comentario
        Comentario.objects.create(
            autor=request.user,  # Establece el usuario como autor
            publicacion=publicacion,
            contenido=contenido
        )
        messages.success(request, 'Comentario agregado con éxito.')
        return redirect('detalle_publicacion', publicacion_id=publicacion_id)
    return redirect('detalle_publicacion', publicacion_id=publicacion_id)

@login_required
def detalle_publicacion(request, publicacion_id):
    """
    Muestra los detalles de una publicación, incluyendo sus comentarios.
    """
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)  # Obtiene la publicación o lanza 404 si no existe
    comentarios = publicacion.comentarios.all()  # Obtiene todos los comentarios asociados
    return render(request, 'publicaciones/detalle_publicacion.html', {
        'publicacion': publicacion,
        'comentarios': comentarios
    })

@login_required
def editar_comentario(request, comentario_id):
    """
    Permite editar un comentario existente.
    """
    comentario = get_object_or_404(Comentario, id=comentario_id)  # Obtiene el comentario o lanza 404 si no existe
    
    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        comentario.contenido = contenido
        comentario.save()
        messages.success(request, 'Comentario actualizado con éxito.')
        return redirect('detalle_publicacion', comentario.publicacion.id)

    return render(request, 'publicaciones/editar_comentario.html', {'comentario': comentario})

@login_required
def eliminar_comentario(request, comentario_id):
    """
    Permite eliminar un comentario existente. Se solicita confirmación a través de un formulario POST.
    """
    comentario = get_object_or_404(Comentario, id=comentario_id)  # Obtiene el comentario o lanza 404 si no existe
    
    if request.method == 'POST':
        publicacion_id = comentario.publicacion.id
        comentario.delete()
        messages.success(request, 'Comentario eliminado con éxito.')
        return redirect('detalle_publicacion', publicacion_id)

    return render(request, 'publicaciones/eliminar_comentario.html', {'comentario': comentario})

@login_required
def like_publicacion(request, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    user = request.user

    if user in publicacion.likes.all():
        publicacion.likes.remove(user)
        liked = False
    else:
        publicacion.likes.add(user)
        liked = True

    data = {
        'liked': liked,
        'count': publicacion.likes.count(),
    }

    return JsonResponse(data)

#======== PERFIL ===========

@login_required
def ver_perfil(request, usuario_id):
    """
    Muestra el perfil de un usuario y permite enviar una solicitud de amistad.
    """
    perfil = get_object_or_404(PerfilUsuario, usuario_id=usuario_id)
    es_propietario = perfil.usuario == request.user
    solicitud = Amistad.objects.filter(solicitante=request.user, receptor=perfil.usuario).first()
    
    # Comprueba si ya hay una solicitud de amistad pendiente
    solicitud_enviada = solicitud is not None
    es_amigo = request.user in perfil.usuario.perfilusuario.amigos.all()

    return render(request, 'perfil/ver_perfil.html', {
        'perfil': perfil,
        'solicitud_enviada': solicitud_enviada,
        'es_amigo': es_amigo,
        'es_propietario': es_propietario
    })
    
def editar_perfil(request):
    perfil = PerfilUsuario.objects.get(usuario=request.user)
    
    if request.method == 'POST':
        if 'confirmar' in request.POST:
            form = EditarPerfilForm(request.POST, request.FILES, instance=perfil)
            if form.is_valid():
                form.save()
                messages.success(request, 'Imagen subida con éxito.')
                return redirect('ver_perfil', usuario_id=request.user.id)
            else:
                messages.error(request, 'Hubo un error al intentar subir la imagen.')
                return redirect('editar_perfil')
        else:
            form = EditarPerfilForm(request.POST, request.FILES, instance=perfil)
            nueva_foto_perfil = request.FILES.get('foto_perfil')
            nueva_foto_portada = request.FILES.get('foto_portada')
            return render(request, 'perfil/confirmar_edicion.html', {
                'form': form,
                'nueva_foto_perfil': nueva_foto_perfil,
                'nueva_foto_portada': nueva_foto_portada
            })
    else:
        form = EditarPerfilForm(instance=perfil)
    
    return render(request, 'perfil/editar_perfil.html', {'form': form})


# ================= Amigos ======================

@login_required
def enviar_solicitud(request, usuario_id):
    """
    Permite a un usuario enviar una solicitud de amistad.
    """
    receptor = get_object_or_404(Usuario, id=usuario_id)
    
    # Verifica si ya existe una solicitud pendiente o si ya son amigos
    if Amistad.objects.filter(solicitante=request.user, receptor=receptor).exists():
        return redirect('ver_perfil', usuario_id=usuario_id)
    
    if request.user == receptor:
        return redirect('ver_perfil', usuario_id=usuario_id)
    
    Amistad.objects.create(solicitante=request.user, receptor=receptor)
    return redirect('ver_perfil', usuario_id=usuario_id)

@login_required
def solicitudes_amistad(request):
    # Obtiene las solicitudes de amistad donde el usuario logueado es el receptor
    solicitudes = Amistad.objects.filter(receptor=request.user, aceptado=False)
    return render(request, 'amistad/solicitudes.html', {'solicitudes': solicitudes})

@login_required
def aceptar_solicitud(request, solicitud_id):
    """
    Acepta una solicitud de amistad.
    """
    solicitud = get_object_or_404(Amistad, id=solicitud_id, receptor=request.user)
    solicitud.aceptado = True
    solicitud.save()
    
    # Añade a los usuarios como amigos
    request.user.perfilusuario.amigos.add(solicitud.solicitante)
    solicitud.solicitante.perfilusuario.amigos.add(request.user)
    
    return redirect('solicitudes_amistad')

@login_required
def rechazar_solicitud(request, solicitud_id):
    """
    Rechaza una solicitud de amistad.
    """
    solicitud = get_object_or_404(Amistad, id=solicitud_id, receptor=request.user)
    solicitud.delete()
    
    return redirect('solicitudes_amistad')

@login_required
def eliminar_amigo(request, usuario_id):
    amigo = get_object_or_404(Usuario, id=usuario_id)
    request.user.perfilusuario.amigos.remove(amigo.perfilusuario)
    return redirect('ver_perfil', usuario_id=usuario_id)

@login_required
def lista_amigos(request):
    """
    Muestra la lista de amigos del usuario.
    """
    perfil = PerfilUsuario.objects.get(usuario=request.user)
    amigos = perfil.amigos.all()
    return render(request, 'amistad/lista_amigos.html', {'amigos': amigos})


#=========== GRUPOS ===============

def grupos_usuario(request):
    user = request.user
    grupos = Grupo.objects.filter(miembros=request.user)  # Filtra los grupos en los que el usuario está
    return render(request, 'grupos/grupos_usuario.html', {'grupos': grupos})

def crear_grupo(request):
    if request.method == 'POST':
        form = CrearGrupoForm(request.POST)
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.creador = request.user
            grupo.save()
            form.save_m2m()  # Guarda la relación ManyToMany de amigos

            # Añadir al creador como miembro del grupo
            grupo.miembros.add(request.user)

            
            return redirect('grupos_usuario')  # Cambiar a la vista adecuada
    else:
        form = CrearGrupoForm()

    return render(request, 'grupos/crear_grupo.html', {'form': form})

def detalle_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    amigos = Usuario.objects.exclude(grupos=grupo).exclude(id=request.user.id)  # Amigos que no son miembros y que no son el usuario actual

    if request.method == 'POST':
        amigos_ids = request.POST.getlist('amigos')
        grupo.miembros.add(*amigos_ids)  # Añadir amigos al grupo
        return redirect('detalle_grupo', grupo_id=grupo.id)
    
    return render(request, 'grupos/detalle_grupo.html', {'grupo': grupo, 'amigos': amigos})


