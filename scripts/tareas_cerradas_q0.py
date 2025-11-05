#!/usr/bin/env python3
"""
Script de automatización para CRM BeyondUp - TAREAS CERRADAS Q ACTUAL
Descarga reporte de tareas cerradas del trimestre ACTUAL
"""

from playwright.sync_api import sync_playwright
from datetime import datetime
from pathlib import Path
import time
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

USERNAME = os.getenv('BEYONDUP_USER')
PASSWORD = os.getenv('BEYONDUP_PASS')
URL = os.getenv('BEYONDUP_URL', 'https://login.beyondup.es')
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
TIMEOUT = int(os.getenv('TIMEOUT', '60000'))
SCREENSHOTS_DIR = Path(os.getenv('SCREENSHOTS_DIR', '/tmp/beyondup_screenshots'))

SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def save_screenshot(page, name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = SCREENSHOTS_DIR / f"{timestamp}_{name}.png"
    page.screenshot(path=str(filepath))
    print(f"   📸 Screenshot: {filepath.name}")
    return filepath

def get_quarter(offset=0):
    """
    Calcula el trimestre con offset
    offset = 0: trimestre actual
    offset = -1: trimestre anterior
    offset = -2: hace 2 trimestres
    """
    today = datetime.now()
    month = today.month
    year = today.year
    
    # Determinar trimestre actual (0-3)
    current_quarter = (month - 1) // 3
    
    # Aplicar offset
    target_quarter = current_quarter + offset
    
    # Ajustar año si es necesario
    while target_quarter < 0:
        target_quarter += 4
        year -= 1
    
    # Calcular fechas
    start_month = target_quarter * 3 + 1
    
    if target_quarter == 0:  # Q1
        fecha_inicio = f"01/01/{year}"
        fecha_fin = f"31/03/{year}"
        quarter_name = f"Q1-{year}"
    elif target_quarter == 1:  # Q2
        fecha_inicio = f"01/04/{year}"
        fecha_fin = f"30/06/{year}"
        quarter_name = f"Q2-{year}"
    elif target_quarter == 2:  # Q3
        fecha_inicio = f"01/07/{year}"
        fecha_fin = f"30/09/{year}"
        quarter_name = f"Q3-{year}"
    else:  # Q4
        fecha_inicio = f"01/10/{year}"
        fecha_fin = f"31/12/{year}"
        quarter_name = f"Q4-{year}"
    
    return fecha_inicio, fecha_fin, quarter_name

def main():
    fecha_inicio, fecha_fin, quarter = get_quarter(0)  # Q ACTUAL
    
    print("=" * 70)
    print("🚀 TAREAS CERRADAS - TRIMESTRE ACTUAL")
    print("=" * 70)
    print(f"📅 Período: {quarter} ({fecha_inicio} al {fecha_fin})")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        page.set_default_timeout(TIMEOUT)
        
        try:
            # Login
            page.goto(URL)
            time.sleep(2)
            page.fill('input[name="formularioLogin:username"]', USERNAME)
            page.fill('input[name="formularioLogin:password"]', PASSWORD)
            page.click('button[type="submit"]')
            page.wait_for_load_state('networkidle')
            print("✅ Login exitoso")
            
            # Navegar a Tareas Cerradas
            page.click('text="CRM"', timeout=5000)
            time.sleep(2)
            page.click('text="Tareas"', timeout=10000)
            time.sleep(2)
            page.click('text="Cerradas"', timeout=10000)
            time.sleep(3)
            print("✅ En Tareas Cerradas")
            
            # Aplicar filtro de fechas
            save_screenshot(page, "01_antes_filtro")
            page.click('button[title*="Filtro"]', timeout=5000)
            time.sleep(2)
            
            # Limpiar campos fecha_fin
            fecha_fin_inputs = page.query_selector_all('input')
            for input_field in fecha_fin_inputs:
                name = input_field.get_attribute('name')
                if name and 'fecha_fin' in name.lower():
                    try:
                        input_field.fill('')
                    except:
                        pass
            
            time.sleep(1)
            
            # Establecer fechas en fecha_inicio
            for input_field in fecha_fin_inputs:
                name = input_field.get_attribute('name')
                if name and 'fecha_inicio' in name.lower():
                    if 'inicio' in name.lower() and 'fin' not in name.lower():
                        input_field.fill(fecha_inicio)
                        print(f"   ✅ Fecha inicio: {fecha_inicio}")
                    elif 'fin' in name.lower():
                        input_field.fill(fecha_fin)
                        print(f"   ✅ Fecha fin: {fecha_fin}")
            
            save_screenshot(page, "02_fechas_aplicadas")
            time.sleep(1)

            # Aceptar filtro - usar selector específico del botón del diálogo de filtro
            page.click('button[id*="btnFiltroAceptarTareas"]', timeout=10000)
            time.sleep(5)  # Esperar a que se procese el filtro y desaparezca el overlay
            print("✅ Filtro aplicado")

            # Exportar
            page.click('button[title*="Excel"]', timeout=15000)
            time.sleep(3)
            # Confirmar exportación - usar el segundo botón Aceptar (el del popup de confirmación)
            page.locator('button:has-text("Aceptar")').nth(1).click(timeout=10000)
            time.sleep(3)
            
            print(f"\n✅ COMPLETADO - Reporte de {quarter}")
            print("📧 Revisa tu correo\n")
            
            browser.close()
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}\n")
            save_screenshot(page, "99_error")
            browser.close()
            return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
