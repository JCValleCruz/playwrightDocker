#!/usr/bin/env python3
"""
Script de automatización para CRM BeyondUp - AUTÓNOMOS NO CUALIFICADOS
Descarga reporte de empresas con:
- Cualificado = NO
- Tipo = Autónomo
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

def apply_filter(page, placeholder_text, value):
    """Aplica un filtro en un campo específico"""
    print(f"   🔍 Aplicando filtro '{placeholder_text}' = '{value}'...")
    
    try:
        input_field = page.locator(f'input[placeholder*="{placeholder_text}" i]').first
        if input_field.is_visible(timeout=2000):
            print(f"   ✅ Campo encontrado")
            input_field.click()
            time.sleep(0.3)
            input_field.fill('')
            time.sleep(0.2)
            input_field.fill(value)
            time.sleep(0.5)
            
            page.evaluate(f'''
                (selector) => {{
                    const input = document.querySelector(selector);
                    if (input) {{
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }}
            ''', f'input[placeholder*="{placeholder_text}"]')
            
            time.sleep(0.5)
            input_field.press('Enter')
            time.sleep(1)
            page.click('body')
            time.sleep(1.5)
            
            print(f"   ✅ Filtro aplicado")
            return True
    except Exception as e:
        print(f"   ⚠️  Error: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("🚀 AUTÓNOMOS NO CUALIFICADOS (Tipo = Autónomo)")
    print("=" * 70)
    
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
            
            # Navegar a Empresas
            page.click('text="CRM"', timeout=5000)
            time.sleep(2)
            page.click('text="Clientes"', timeout=5000)
            time.sleep(2)
            page.click('text="Empresas"', timeout=5000)
            time.sleep(3)
            print("✅ En vista Empresas")
            
            # Zoom
            page.evaluate("document.body.style.zoom = '0.8'")
            time.sleep(2)
            save_screenshot(page, "01_antes_filtros")
            
            # Aplicar filtros
            apply_filter(page, "Cualificado", "No")
            save_screenshot(page, "02_filtro_cualificado")
            
            apply_filter(page, "Tipo", "Autónomo")
            save_screenshot(page, "03_filtro_tipo")
            
            time.sleep(2)

            # Exportar
            page.click('button[title*="Excel"]', timeout=15000)
            time.sleep(3)
            # Confirmar exportación - seleccionar el último botón Aceptar visible (popup de confirmación)
            page.locator('button:has-text("Aceptar")').last.click(timeout=10000)
            time.sleep(3)
            
            print("\n✅ PROCESO COMPLETADO")
            print("📧 Revisa tu correo")
            print(f"📸 Screenshots: {SCREENSHOTS_DIR}\n")
            
            browser.close()
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}\n")
            save_screenshot(page, "99_error")
            browser.close()
            return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
