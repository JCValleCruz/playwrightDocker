#!/usr/bin/env python3
"""
Script de automatización para CRM BeyondUp - TAREAS FUTURAS
Descarga reporte de tareas futuras SIN FILTROS
Usa variables de entorno para mayor seguridad
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from datetime import datetime
from pathlib import Path
import time
import os
import sys

# Intentar cargar python-dotenv si está disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Variables de entorno cargadas desde .env")
except ImportError:
    print("⚠️  python-dotenv no instalado. Usando variables de entorno del sistema.")
    print("   Para usar .env: pip install python-dotenv")

# Configuración desde variables de entorno
USERNAME = os.getenv('BEYONDUP_USER')
PASSWORD = os.getenv('BEYONDUP_PASS')
URL = os.getenv('BEYONDUP_URL', 'https://login.beyondup.es')
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
TIMEOUT = int(os.getenv('TIMEOUT', '60000'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
SCREENSHOTS_DIR = Path(os.getenv('SCREENSHOTS_DIR', '/tmp/beyondup_screenshots'))

# Validar credenciales
if not USERNAME or not PASSWORD:
    print("❌ ERROR: Credenciales no configuradas")
    print("   Configura las variables de entorno:")
    print("   - BEYONDUP_USER")
    print("   - BEYONDUP_PASS")
    print("\n   O crea un archivo .env basado en .env.example")
    sys.exit(1)

# Crear directorio para screenshots si no existe
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def save_screenshot(page, name):
    """Guardar screenshot con timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = SCREENSHOTS_DIR / f"{timestamp}_{name}.png"
    page.screenshot(path=str(filepath))
    print(f"   📸 Screenshot: {filepath.name}")
    return filepath

def retry_operation(operation, max_attempts=MAX_RETRIES, delay=2):
    """Reintentar una operación con backoff exponencial"""
    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except Exception as e:
            if attempt == max_attempts:
                raise
            
            wait_time = delay * (2 ** (attempt - 1))
            print(f"   ⚠️  Intento {attempt}/{max_attempts} falló. Reintentando en {wait_time}s...")
            time.sleep(wait_time)

def main():
    print("=" * 70)
    print("🚀 AUTOMATIZACIÓN CRM BEYONDUP - TAREAS FUTURAS")
    print("=" * 70)
    
    print(f"\n📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"👤 Usuario: {USERNAME}")
    print(f"🌐 URL: {URL}")
    print(f"👁️  Modo: {'Headless' if HEADLESS else 'Visible'}")
    print(f"📸 Screenshots: {SCREENSHOTS_DIR}")
    print(f"📋 Tipo: Tareas Futuras (sin filtros)")
    
    with sync_playwright() as p:
        try:
            # Lanzar navegador
            print("\n" + "=" * 70)
            print("🌐 INICIANDO NAVEGADOR")
            print("=" * 70)
            
            browser = p.chromium.launch(
                headless=HEADLESS,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                ignore_https_errors=True,
                bypass_csp=True
            )
            
            page = context.new_page()
            page.set_default_timeout(TIMEOUT)
            
            # Paso 1: Login
            print("\n📍 PASO 1: INICIO DE SESIÓN")
            print("-" * 70)
            
            def do_login():
                page.goto(URL)
                time.sleep(2)
                save_screenshot(page, "01_login_page")
                
                print("   🔐 Ingresando credenciales...")
                page.fill('input[name="formularioLogin:username"]', USERNAME)
                page.fill('input[name="formularioLogin:password"]', PASSWORD)
                save_screenshot(page, "02_credentials_filled")
                
                print("   👆 Haciendo clic en login...")
                page.click('button[type="submit"]')
                page.wait_for_load_state('networkidle')
                save_screenshot(page, "03_after_login")
            
            retry_operation(do_login)
            print("   ✅ Login exitoso")
            
            # Paso 2: Navegar a CRM > Tareas > Futuras
            print("\n📍 PASO 2: NAVEGACIÓN A TAREAS FUTURAS")
            print("-" * 70)
            
            print("   📂 Navegando a CRM...")
            selectors_crm = [
                'text="CRM"',
                'a:has-text("CRM")',
                'a[href*="crm"]'
            ]
            
            for selector in selectors_crm:
                try:
                    page.click(selector, timeout=5000)
                    print(f"   ✅ CRM encontrado: {selector}")
                    break
                except:
                    continue
            
            time.sleep(2)
            save_screenshot(page, "04_crm_menu")
            
            print("   📋 Navegando a Tareas...")
            page.click('text="Tareas"', timeout=10000)
            time.sleep(2)
            
            print("   🔮 Navegando a Futuras...")
            page.click('text="Futuras"', timeout=10000)
            time.sleep(3)
            save_screenshot(page, "05_tareas_futuras")
            print("   ✅ Navegación completada - Vista de Tareas Futuras cargada")
            
            # Paso 3: Exportar directamente a Excel (SIN FILTROS)
            print("\n📍 PASO 3: EXPORTAR A EXCEL (SIN FILTROS)")
            print("-" * 70)
            
            print("   ⏳ Esperando que la tabla cargue...")
            time.sleep(2)
            save_screenshot(page, "06_antes_exportar")
            
            print("   📊 Buscando botón de Excel...")
            selectors_excel = [
                'button[title*="Excel"]',
                'button:has-text("Excel")',
                'i.fa-file-excel',
                '.excel-icon',
                'button[aria-label*="Excel"]'
            ]
            
            excel_clicked = False
            for selector in selectors_excel:
                try:
                    page.click(selector, timeout=3000)
                    excel_clicked = True
                    print(f"   ✅ Botón Excel encontrado: {selector}")
                    break
                except:
                    continue
            
            if not excel_clicked:
                print("   ⚠️  No se pudo encontrar el botón de Excel")
                save_screenshot(page, "07_excel_no_encontrado")
                raise Exception("Botón de Excel no encontrado")
            
            # Esperar a que aparezca el popup de confirmación
            print("   ⏳ Esperando popup de confirmación...")
            time.sleep(3)
            save_screenshot(page, "08_excel_dialog")

            # Confirmar envío por correo
            print("   📧 Confirmando envío por correo...")
            popup_confirmed = False

            # Usar .last para seleccionar el último botón Aceptar (el del popup de confirmación)
            try:
                page.locator('button:has-text("Aceptar")').last.click(timeout=10000)
                popup_confirmed = True
                print("   ✅ Confirmación enviada")
            except:
                # Fallback a selectores alternativos
                selectors_aceptar = [
                    'button:text("Aceptar")',
                    '.ui-button:has-text("Aceptar")',
                    'button[type="button"]:has-text("Aceptar")',
                    '.ui-confirmdialog-yes'
                ]

                for selector in selectors_aceptar:
                    try:
                        page.click(selector, timeout=10000)
                        popup_confirmed = True
                        print(f"   ✅ Confirmación enviada: {selector}")
                        break
                    except:
                        continue

            if not popup_confirmed:
                print("   ⚠️  No se pudo confirmar el popup")
                save_screenshot(page, "09_popup_error")
                raise Exception("No se pudo confirmar el popup de exportación")

            time.sleep(3)
            save_screenshot(page, "10_final_result")
            
            # Finalización
            print("\n" + "=" * 70)
            print("✅ PROCESO COMPLETADO EXITOSAMENTE")
            print("=" * 70)
            print(f"\n📬 El reporte de Tareas Futuras ha sido solicitado.")
            print(f"📧 Revisa tu correo en unos minutos.")
            print(f"📸 Screenshots guardados en: {SCREENSHOTS_DIR}")
            print(f"📊 Exportación: TODAS las tareas futuras (sin filtros)")
            print("\n🎉 ¡Todo listo!\n")
            
            # Cerrar navegador
            browser.close()
            return True
            
        except Exception as e:
            print("\n" + "=" * 70)
            print("❌ ERROR DURANTE LA EJECUCIÓN")
            print("=" * 70)
            print(f"\n💥 {str(e)}\n")
            
            # Tomar screenshot de error
            try:
                save_screenshot(page, "99_error_final")
            except:
                pass
            
            print(f"📸 Revisa los screenshots en: {SCREENSHOTS_DIR}")
            print("📋 Verifica que:")
            print("   - Las credenciales son correctas")
            print("   - La interfaz de BeyondUp no ha cambiado")
            print("   - Tu conexión a internet funciona")
            print("   - La sección 'Tareas > Futuras' existe")
            print()
            
            return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️  Proceso interrumpido por el usuario")
        sys.exit(130)
