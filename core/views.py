from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, UserProfileForm
from django.http import JsonResponse
import json
import base64
import face_recognition
import numpy as np
from django.views.decorators.csrf import csrf_exempt

def data_uri_to_cv2_img(data_uri):
    from PIL import Image
    import io
    try:
        if "," in data_uri:
            encoded_data = data_uri.split(',')[1]
        else:
            encoded_data = data_uri

        image_bytes = base64.b64decode(encoded_data)
        img_pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img_rgb = np.array(img_pil).astype(np.uint8)
        img_rgb = np.ascontiguousarray(img_rgb)
        
        return img_rgb
    except Exception:
        return None

def index(request):
    return render(request, 'core/index.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('note_list')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('note_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

@csrf_exempt
@login_required
def save_face_encoding(request):
    if request.method == 'POST':
        from PIL import Image
        import io
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            
            if "," in image_data:
                encoded_data = image_data.split(',')[1]
            else:
                encoded_data = image_data
            image_bytes = base64.b64decode(encoded_data)
            
            img_pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            img_rgb = np.array(img_pil).astype(np.uint8)
            img_rgb = np.ascontiguousarray(img_rgb)
            
            encodings = face_recognition.face_encodings(img_rgb)
            if not encodings:
                return JsonResponse({'success': False, 'message': 'Aucun visage détecté'})

            request.user.face_encoding = encodings[0].tolist()
            request.user.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid method'})

@csrf_exempt
def face_login_api(request):
    if request.method == 'POST':
        from PIL import Image
        import io
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            if not image_data:
                return JsonResponse({'success': False, 'message': 'No image provided'})

            if "," in image_data:
                encoded_data = image_data.split(',')[1]
            else:
                encoded_data = image_data
            image_bytes = base64.b64decode(encoded_data)
            
            img_pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            img_rgb = np.array(img_pil, dtype=np.uint8)
            img_rgb = np.ascontiguousarray(img_rgb)

            unknown_encoding = face_recognition.face_encodings(img_rgb)
            if not unknown_encoding:
                return JsonResponse({'success': False, 'message': 'Aucun visage détecté'})
            
            unknown_encoding = unknown_encoding[0]
            
            from .models import User
            users_with_faces = User.objects.exclude(face_encoding__isnull=True)
            
            for user in users_with_faces:
                known_encoding = np.array(user.face_encoding)
                results = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.5)
                if results[0]:
                    login(request, user)
                    return JsonResponse({'success': True, 'redirect_url': '/notes/'})

            return JsonResponse({'success': False, 'message': 'Visage non reconnu'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid method'})

@login_required
def profile_view(request):
    from django.contrib import messages
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès !")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'core/profile_settings.html', {'form': form})
