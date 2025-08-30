#!/usr/bin/env python3
"""
Script de limpieza automática para EDUFACE
Elimina archivos temporales, cache y otros elementos innecesarios
"""

import os
import shutil
import glob
import sys
from pathlib import Path

def clean_project():
    """Limpia archivos innecesarios del proyecto"""
    project_root = Path(__file__).parent
    
    print("🧹 Iniciando limpieza del proyecto EDUFACE...")
    
    # Archivos y carpetas a eliminar
    patterns_to_clean = [
        # Cache de Python (solo en el proyecto, no en venv)
        "app/**/__pycache__",
        "app/**/*.pyc",
        "app/**/*.pyo",
        
        # Archivos temporales del proyecto
        "*.tmp",
        "*.temp",
        "*.log",
        "*.bak",
        
        # Archivos de sistema
        "**/Thumbs.db",
        "**/.DS_Store",
        
        # Modelos de DeepFace (se descargan automáticamente)
        "db/ds_model_*.pkl",
        
        # Build artifacts del proyecto
        "build",
        "dist",
        "*.egg-info"
    ]
    
    cleaned_count = 0
    
    # Directorios protegidos que nunca deben tocarse
    protected_dirs = {'.venv', '.venv_new', '.git', 'node_modules'}
    
    for pattern in patterns_to_clean:
        for item in project_root.glob(pattern):
            try:
                # Verificar si el item está dentro de un directorio protegido
                is_protected = False
                for part in item.parts:
                    if part in protected_dirs:
                        is_protected = True
                        break
                
                if is_protected:
                    continue  # Saltar archivos en directorios protegidos
                
                if item.is_file():
                    item.unlink()
                    print(f"  ✅ Eliminado archivo: {item.relative_to(project_root)}")
                    cleaned_count += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    print(f"  📁 Eliminada carpeta: {item.relative_to(project_root)}")
                    cleaned_count += 1
            except Exception as e:
                print(f"  ❌ Error eliminando {item}: {e}")
    
    # Limpiar carpetas vacías
    empty_dirs = []
    for root, dirs, files in os.walk(project_root):
        for directory in dirs:
            dir_path = Path(root) / directory
            try:
                # Si la carpeta está vacía (excepto .gitkeep)
                contents = list(dir_path.iterdir())
                if not contents or (len(contents) == 1 and contents[0].name == '.gitkeep'):
                    if dir_path.name not in ['.git', '.venv', 'node_modules']:
                        continue  # Mantener carpetas estructurales
            except:
                pass
    
    print(f"\n✅ Limpieza completada! Se eliminaron {cleaned_count} elementos.")
    print("\n📊 Estructura limpia del proyecto:")
    
    # Mostrar estructura limpia
    show_tree(project_root)

def show_tree(path, prefix="", max_depth=3, current_depth=0):
    """Muestra la estructura del proyecto de forma visual"""
    if current_depth >= max_depth:
        return
        
    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    
    # Filtrar elementos que no queremos mostrar
    exclude = {'.git', '.venv', '__pycache__', 'node_modules'}
    items = [item for item in items if item.name not in exclude]
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        
        if item.is_dir():
            print(f"{prefix}{current_prefix}📁 {item.name}/")
            extension = "    " if is_last else "│   "
            show_tree(item, prefix + extension, max_depth, current_depth + 1)
        else:
            # Agregar emoji según el tipo de archivo
            emoji = get_file_emoji(item.suffix)
            print(f"{prefix}{current_prefix}{emoji} {item.name}")

def get_file_emoji(suffix):
    """Retorna emoji apropiado para el tipo de archivo"""
    emoji_map = {
        '.py': '🐍',
        '.html': '🌐', 
        '.css': '🎨',
        '.js': '⚡',
        '.json': '📄',
        '.md': '📝',
        '.txt': '📄',
        '.yml': '⚙️',
        '.yaml': '⚙️',
        '.dockerfile': '🐳',
        '.png': '🖼️',
        '.jpg': '🖼️',
        '.jpeg': '🖼️',
        '.sqlite3': '🗃️',
        '.db': '🗃️'
    }
    return emoji_map.get(suffix.lower(), '📄')

if __name__ == "__main__":
    clean_project()
