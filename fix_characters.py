# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 11:14:12 2026

@author: Pedro Carvalho
"""

from glob import glob
import os
import json
import unicodedata

def fix_py_file(file_path):
    """Aplica substituições em arquivos de texto puro (.py)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    for old, new in dict_files.items():
        if old in content:
            content = content.replace(old, new)
            modified = True
            
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Atualizado: {file_path}")

def fix_ipynb_file(file_path):
    """Aplica substituições com segurança dentro das células de um Jupyter Notebook."""
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            notebook = json.load(f)
        except json.JSONDecodeError:
            print(f"[ERRO] Falha ao ler JSON do notebook: {file_path}")
            return

    modified = False
    
    # Navega pelas células do arquivo .ipynb
    if "cells" in notebook:
        for cell in notebook["cells"]:
            if "source" in cell:
                # O source pode vir como uma string única ou uma lista de strings
                if isinstance(cell["source"], list):
                    full_source = "".join(cell["source"])
                    cell_modified = False
                    
                    for old, new in dict_files.items():
                        if old in full_source:
                            full_source = full_source.replace(old, new)
                            cell_modified = True
                            modified = True
                    
                    # Se foi modificado, quebra de volta em lista de linhas para manter o padrão do Jupyter
                    if cell_modified:
                        cell["source"] = [line + '\n' for line in full_source.split('\n')]
                        # Remove a quebra de linha extra gerada no último item
                        if cell["source"] and cell["source"][-1] == '\n':
                            cell["source"][-1] = cell["source"][-1].strip('\n')
                
                elif isinstance(cell["source"], str):
                    for old, new in dict_files.items():
                        if old in cell["source"]:
                            cell["source"] = cell["source"].replace(old, new)
                            modified = True

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, ensure_ascii=False, indent=1)
        print(f"[OK] Atualizado: {file_path}")

files = glob("*")
dict_files = {}

for file in files:

    sp = file.split(" ")
    
    prex = sp[0]
    if '.' in prex:
        prex = "{:02d}_{:02d}".format(*map(int,prex.strip("()").split('.')))
    else:
        prex = "{:02d}".format(int(prex.strip("()")))

    sufx = "".join(
        c for c in unicodedata.normalize("NFD", "_".join(sp[1:])) if unicodedata.category(c) != "Mn"
        ).lower()

    new_file = prex + "_" + sufx
    
    os.rename(file, new_file)
    
    dict_files[file] = new_file

files = glob("*.py")

for file in files:
    fix_py_file(file)

files = glob("*.ipynb")

for file in files:
    fix_ipynb_file(file)