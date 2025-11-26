"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import os
import boto3
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


def home(request):
    """Vue de la page d'accueil avec explorateur de fichiers"""
    current_path = request.GET.get('path', '')
    base_path = '/data'
    full_path = os.path.join(base_path, current_path.lstrip('/'))

    # Sécurité : empêcher de sortir du dossier /data
    if not os.path.abspath(full_path).startswith(os.path.abspath(base_path)):
        full_path = base_path
        current_path = ''

    # Lister les fichiers et dossiers
    items = []
    if os.path.exists(full_path) and os.path.isdir(full_path):
        try:
            for item in sorted(os.listdir(full_path)):
                item_path = os.path.join(full_path, item)
                relative_path = os.path.join(current_path, item)
                is_dir = os.path.isdir(item_path)
                try:
                    size = os.path.getsize(item_path) if not is_dir else 0
                except:
                    size = 0
                items.append({
                    'name': item,
                    'path': relative_path,
                    'is_dir': is_dir,
                    'size': size
                })
        except PermissionError:
            pass

    # Chemin parent
    parent_path = os.path.dirname(current_path) if current_path else None

    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DLS3 - Explorateur de fichiers</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            .header {{
                background: #667eea;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .header h1 {{
                font-size: 32px;
                margin-bottom: 10px;
            }}
            .breadcrumb {{
                background: #f5f5f5;
                padding: 15px 20px;
                border-bottom: 1px solid #ddd;
                font-size: 14px;
            }}
            .breadcrumb a {{
                color: #667eea;
                text-decoration: none;
            }}
            .breadcrumb a:hover {{
                text-decoration: underline;
            }}
            .controls {{
                padding: 20px;
                background: #f9f9f9;
                border-bottom: 1px solid #ddd;
            }}
            .btn {{
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s;
            }}
            .btn:hover {{
                background: #5568d3;
            }}
            .btn:disabled {{
                background: #ccc;
                cursor: not-allowed;
            }}
            .file-list {{
                padding: 20px;
                max-height: 500px;
                overflow-y: auto;
            }}
            .file-item {{
                display: flex;
                align-items: center;
                padding: 12px;
                border-bottom: 1px solid #eee;
                transition: background 0.2s;
            }}
            .file-item:hover {{
                background: #f5f5f5;
            }}
            .file-item input[type="checkbox"] {{
                width: 20px;
                height: 20px;
                margin-right: 15px;
                cursor: pointer;
            }}
            .file-icon {{
                width: 30px;
                height: 30px;
                margin-right: 15px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
            }}
            .file-name {{
                flex: 1;
                font-size: 16px;
                cursor: pointer;
            }}
            .file-name.dir {{
                color: #667eea;
                font-weight: 500;
            }}
            .file-name.dir:hover {{
                text-decoration: underline;
            }}
            .file-size {{
                color: #999;
                font-size: 14px;
                margin-left: 10px;
            }}
            .result {{
                padding: 20px;
                margin: 20px;
                border-radius: 5px;
                display: none;
            }}
            .result.success {{
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                display: block;
            }}
            .result.error {{
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
                display: block;
            }}
            .selected-count {{
                display: inline-block;
                margin-left: 15px;
                color: #667eea;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🗂️ Explorateur de fichiers DLS3</h1>
                <p>Sélectionnez des fichiers ou dossiers à transférer vers S3</p>
            </div>

            <div class="breadcrumb">
                <a href="/">🏠 Racine</a>
                {' / '.join([f'<a href="?path={"/".join(current_path.split("/")[:i+1])}">{part}</a>'
                            for i, part in enumerate(current_path.split('/')) if part])}
            </div>

            <div class="controls">
                <button class="btn" id="submitBtn" disabled>
                    Tester la connexion S3
                </button>
                <span class="selected-count" id="selectedCount">0 élément(s) sélectionné(s)</span>
            </div>

            <div id="result" class="result"></div>

            <form id="fileForm">
                <div class="file-list">
                    {'<div class="file-item"><div class="file-icon">⬆️</div><a href="?path=' + parent_path + '" class="file-name dir">.. (Dossier parent)</a></div>' if parent_path is not None else ''}
                    {''.join([f'''
                    <div class="file-item">
                        <input type="checkbox" name="selected_items" value="{item['path']}" data-type="{'dir' if item['is_dir'] else 'file'}">
                        {'<a href="?path=' + item['path'] + '" class="file-name dir">' if item['is_dir'] else '<span class="file-name">'}
                        <span class="file-icon">{'📁' if item['is_dir'] else '📄'}</span>
                        {item['name']}
                        {'</a>' if item['is_dir'] else '</span>'}
                        <span class="file-size">{'Dossier' if item['is_dir'] else f"{item['size']:,} octets".replace(',', ' ')}</span>
                    </div>
                    ''' for item in items])}
                    {'' if items else '<div class="file-item"><span class="file-name">Aucun fichier ou dossier</span></div>'}
                </div>
            </form>
        </div>

        <script>
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            const submitBtn = document.getElementById('submitBtn');
            const selectedCount = document.getElementById('selectedCount');
            const resultDiv = document.getElementById('result');

            function updateSubmitButton() {{
                const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
                submitBtn.disabled = checkedCount === 0;
                selectedCount.textContent = checkedCount + ' élément(s) sélectionné(s)';
            }}

            checkboxes.forEach(cb => {{
                cb.addEventListener('change', updateSubmitButton);
            }});

            submitBtn.addEventListener('click', async () => {{
                const selected = Array.from(checkboxes)
                    .filter(cb => cb.checked)
                    .map(cb => ({{
                        path: cb.value,
                        type: cb.dataset.type
                    }}));

                resultDiv.className = 'result';
                resultDiv.textContent = 'Test de connexion en cours...';
                resultDiv.style.display = 'block';
                submitBtn.disabled = true;

                try {{
                    const response = await fetch('/test-s3/', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{ selected_items: selected }})
                    }});

                    const data = await response.json();

                    if (data.success) {{
                        resultDiv.className = 'result success';
                        resultDiv.textContent = '✅ ' + data.message;
                    }} else {{
                        resultDiv.className = 'result error';
                        resultDiv.textContent = '❌ ' + data.message;
                    }}
                }} catch (error) {{
                    resultDiv.className = 'result error';
                    resultDiv.textContent = '❌ Erreur lors du test de connexion: ' + error.message;
                }} finally {{
                    updateSubmitButton();
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HttpResponse(html)


@csrf_exempt
def test_s3_connection(request):
    """Test de connexion au bucket S3"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

    try:
        import json
        data = json.loads(request.body)
        selected_items = data.get('selected_items', [])

        # Configuration S3
        s3_endpoint = os.environ.get('S3_ENDPOINT_URL', '')
        s3_access_key = os.environ.get('S3_ACCESS_KEY_ID', '')
        s3_secret_key = os.environ.get('S3_SECRET_ACCESS_KEY', '')
        s3_bucket = os.environ.get('S3_BUCKET_NAME', '')

        if not all([s3_endpoint, s3_access_key, s3_secret_key, s3_bucket]):
            return JsonResponse({
                'success': False,
                'message': 'Configuration S3 incomplète. Vérifiez les variables d\'environnement.'
            })

        # Test de connexion S3
        s3_client = boto3.client(
            's3',
            endpoint_url=s3_endpoint,
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key
        )

        # Vérifier que le bucket existe et est accessible
        s3_client.head_bucket(Bucket=s3_bucket)

        return JsonResponse({
            'success': True,
            'message': f'Connexion réussie au bucket S3 "{s3_bucket}" ! {len(selected_items)} élément(s) sélectionné(s).'
        })

    except boto3.exceptions.Boto3Error as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur S3: {str(e)}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


urlpatterns = [
    path("", home, name="home"),
    path("test-s3/", test_s3_connection, name="test_s3"),
    path("admin/", admin.site.urls),
]
