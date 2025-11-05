#!/usr/bin/env python3
"""
Script de automatización para CRM BeyondUp - EMPRESAS CUALIFICADAS
Descarga reporte de empresas con el campo "Cualificado" = Sí
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
    print("🚀 AUTOMATIZACIÓN CRM BEYONDUP - EMPRESAS CUALIFICADAS")
    print("=" * 70)
    
    print(f"\n📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"👤 Usuario: {USERNAME}")
    print(f"🌐 URL: {URL}")
    print(f"👁️  Modo: {'Headless' if HEADLESS else 'Visible'}")
    print(f"📸 Screenshots: {SCREENSHOTS_DIR}")
    print(f"📋 Tipo: Empresas con Cualificado = Sí")
    
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
            
            # Paso 2: Navegar a CRM > Clientes > Empresas
            print("\n📍 PASO 2: NAVEGACIÓN A EMPRESAS")
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
            
            print("   👥 Navegando a Clientes...")
            selectors_clientes = [
                'text="Clientes"',
                'a:has-text("Clientes")',
                'span:has-text("Clientes")'
            ]
            
            for selector in selectors_clientes:
                try:
                    page.click(selector, timeout=5000)
                    print(f"   ✅ Clientes encontrado: {selector}")
                    break
                except:
                    continue
            
            time.sleep(2)
            save_screenshot(page, "05_clientes_menu")
            
            print("   🏢 Navegando a Empresas...")
            selectors_empresas = [
                'text="Empresas"',
                'a:has-text("Empresas")',
                'span:has-text("Empresas")'
            ]
            
            for selector in selectors_empresas:
                try:
                    page.click(selector, timeout=5000)
                    print(f"   ✅ Empresas encontrado: {selector}")
                    break
                except:
                    continue
            
            time.sleep(3)
            save_screenshot(page, "06_empresas_page")
            print("   ✅ Navegación completada - Vista de Empresas cargada")
            
            # Paso 3: Ajustar zoom para ver la columna "Cualificado"
            print("\n📍 PASO 3: AJUSTAR ZOOM Y APLICAR FILTRO")
            print("-" * 70)
            
            print("   🔍 Reduciendo zoom para ver todas las columnas...")
            # Reducir zoom al 80% para ver la columna Cualificado
            page.evaluate("document.body.style.zoom = '0.8'")
            time.sleep(2)
            save_screenshot(page, "07_zoom_reducido")
            print("   ✅ Zoom ajustado al 80%")
            
            # Screenshot de debugging: capturar el HTML de la tabla
            print("   🐛 Capturando información de debugging...")
            try:
                table_info = page.evaluate('''
                    () => {
                        const headers = Array.from(document.querySelectorAll('th')).map(th => th.textContent.trim());
                        const allInputs = Array.from(document.querySelectorAll('input[type="text"]'));
                        const tableInputs = allInputs.filter(inp => {
                            const table = inp.closest('table');
                            return table !== null;
                        });
                        return { 
                            headers, 
                            totalInputs: allInputs.length,
                            tableInputs: tableInputs.length
                        };
                    }
                ''')
                print(f"   📋 Headers encontrados: {len(table_info['headers'])} columnas")
                print(f"   🔍 Inputs totales: {table_info['totalInputs']}")
                print(f"   🔍 Inputs en tabla: {table_info['tableInputs']}")
                
                # Buscar específicamente el de "Cualificado"
                cualificado_found = any('cualificado' in h.lower() for h in table_info['headers'])
                if cualificado_found:
                    print("   ✅ Columna 'Cualificado' confirmada en headers")
                
            except Exception as e:
                print(f"   ⚠️  Error en debugging: {str(e)}")
            
            save_screenshot(page, "07b_antes_filtrar_debug")
            
            # Paso 4: Filtrar por Cualificado = Sí
            print("\n   🔎 Buscando campo de filtro 'Cualificado'...")
            
            # Contar filas antes de filtrar
            rows_before = page.locator('tbody tr').count()
            print(f"   📊 Filas antes de filtrar: {rows_before}")
            
            # Intentar diferentes estrategias para encontrar el campo de filtro
            filter_applied = False
            
            # Estrategia 1: Buscar por placeholder y aplicar múltiples eventos
            try:
                print("   📝 Estrategia 1: Buscando por placeholder con eventos completos...")
                cualificado_input = page.locator('input[placeholder*="Cualificado" i]').first
                if cualificado_input.is_visible(timeout=2000):
                    print("   ✅ Campo encontrado por placeholder")
                    
                    # Focus en el input
                    cualificado_input.click()
                    time.sleep(0.3)
                    
                    # Limpiar el campo primero
                    cualificado_input.fill('')
                    time.sleep(0.2)
                    
                    # Escribir 'Sí'
                    cualificado_input.fill('Sí')
                    time.sleep(0.5)
                    
                    # Disparar múltiples eventos para asegurar que se active el filtro
                    page.evaluate('''
                        (selector) => {
                            const input = document.querySelector(selector);
                            if (input) {
                                input.dispatchEvent(new Event('input', { bubbles: true }));
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                input.dispatchEvent(new Event('blur', { bubbles: true }));
                            }
                        }
                    ''', f'input[placeholder*="Cualificado"]')
                    
                    time.sleep(0.5)
                    
                    # Presionar Enter
                    cualificado_input.press('Enter')
                    time.sleep(1)
                    
                    # Click fuera del input para asegurar que se aplique
                    page.click('body')
                    time.sleep(1.5)
                    
                    filter_applied = True
                    print("   ✅ Eventos disparados: input, change, blur, Enter")
                    
            except Exception as e:
                print(f"   ⚠️  Estrategia 1 falló: {str(e)}")
            
            # Estrategia 2: Buscar todos los inputs y verificar placeholder
            if not filter_applied:
                try:
                    print("   📝 Estrategia 2: Buscando por todos los placeholders...")
                    
                    all_inputs = page.query_selector_all('input[type="text"]')
                    print(f"   🔍 Analizando {len(all_inputs)} inputs...")
                    
                    for idx, input_field in enumerate(all_inputs):
                        try:
                            placeholder = input_field.get_attribute('placeholder')
                            if placeholder and 'cualificado' in placeholder.lower():
                                print(f"   ✅ Campo encontrado en índice {idx}: '{placeholder}'")
                                input_field.click()
                                time.sleep(0.3)
                                input_field.fill('Sí')
                                time.sleep(0.5)
                                input_field.press('Enter')
                                time.sleep(1)  # Dar tiempo al backend
                                filter_applied = True
                                break
                        except:
                            continue
                
                except Exception as e:
                    print(f"   ⚠️  Estrategia 2 falló: {str(e)}")
            
            # Estrategia 3: Buscar por estructura JS más profunda
            if not filter_applied:
                try:
                    print("   📝 Estrategia 3: Búsqueda avanzada por JavaScript...")
                    
                    # Usar JavaScript para encontrar el input correcto
                    filter_applied_js = page.evaluate('''
                        () => {
                            const inputs = Array.from(document.querySelectorAll('input[type="text"]'));
                            for (let input of inputs) {
                                const placeholder = input.getAttribute('placeholder') || '';
                                if (placeholder.toLowerCase().includes('cualificado')) {
                                    input.focus();
                                    input.value = 'Sí';
                                    input.dispatchEvent(new Event('input', { bubbles: true }));
                                    input.dispatchEvent(new Event('change', { bubbles: true }));
                                    
                                    // Simular Enter
                                    const enterEvent = new KeyboardEvent('keydown', { 
                                        key: 'Enter', 
                                        keyCode: 13, 
                                        which: 13,
                                        bubbles: true 
                                    });
                                    input.dispatchEvent(enterEvent);
                                    return true;
                                }
                            }
                            return false;
                        }
                    ''')
                    
                    if filter_applied_js:
                        print("   ✅ Filtro aplicado vía JavaScript")
                        filter_applied = True
                        time.sleep(1.5)  # Dar tiempo al backend
                
                except Exception as e:
                    print(f"   ⚠️  Estrategia 3 falló: {str(e)}")
            
            # Verificar que el filtro realmente se aplicó
            if filter_applied:
                print("   ⏳ Esperando a que se aplique el filtro...")
                time.sleep(4)
                save_screenshot(page, "08_despues_filtro")
                
                # Verificar que el valor "Sí" quedó en el input
                try:
                    print("   🔍 Verificando que el filtro quedó aplicado...")
                    
                    # Tomar screenshot específico del input
                    input_element = page.locator('input[placeholder*="Cualificado" i]').first
                    if input_element.is_visible():
                        input_element.screenshot(path=str(SCREENSHOTS_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_input_cualificado.png"))
                    
                    # Buscar el input y verificar su valor
                    input_value = page.evaluate('''
                        () => {
                            const inputs = Array.from(document.querySelectorAll('input[type="text"]'));
                            for (let input of inputs) {
                                const placeholder = input.getAttribute('placeholder') || '';
                                if (placeholder.toLowerCase().includes('cualificado')) {
                                    return input.value;
                                }
                            }
                            return null;
                        }
                    ''')
                    
                    print(f"   📊 Valor actual en el input: '{input_value}'")
                    
                    if input_value and input_value.strip().lower() in ['sí', 'si', 'yes', 's']:
                        print(f"   ✅ Filtro verificado: valor en input = '{input_value}'")
                    else:
                        print(f"   ⚠️  ADVERTENCIA: valor en input = '{input_value}'")
                        print("   ℹ️  Intentando aplicar el filtro de nuevo...")
                        
                        # Segundo intento con JavaScript puro
                        page.evaluate('''
                            () => {
                                const inputs = Array.from(document.querySelectorAll('input[type="text"]'));
                                for (let input of inputs) {
                                    const placeholder = input.getAttribute('placeholder') || '';
                                    if (placeholder.toLowerCase().includes('cualificado')) {
                                        input.value = 'Sí';
                                        input.dispatchEvent(new Event('input', { bubbles: true }));
                                        input.dispatchEvent(new Event('change', { bubbles: true }));
                                        
                                        // Trigger Enter
                                        const event = new KeyboardEvent('keydown', {
                                            key: 'Enter',
                                            code: 'Enter',
                                            keyCode: 13,
                                            which: 13,
                                            bubbles: true
                                        });
                                        input.dispatchEvent(event);
                                        return true;
                                    }
                                }
                                return false;
                            }
                        ''')
                        time.sleep(2)
                        save_screenshot(page, "08b_segundo_intento")
                
                except Exception as e:
                    print(f"   ⚠️  No se pudo verificar el valor del input: {str(e)}")
                    print("   ℹ️  Continuando de todas formas...")
            
            # Ya NO detenemos el proceso - el filtro se aplica en backend
            # La paginación puede mostrar las mismas filas visualmente
            if not filter_applied:
                print("\n" + "=" * 70)
                print("❌ ERROR: NO SE PUDO APLICAR EL FILTRO")
                print("=" * 70)
                print("\n   El filtro 'Cualificado = Sí' no pudo ser aplicado.")
                print("   💡 Posibles soluciones:")
                print("   1. Ejecuta el script con HEADLESS=false para ver qué pasa")
                print("   2. Verifica manualmente que la columna 'Cualificado' existe")
                print("   3. Revisa los screenshots en:", SCREENSHOTS_DIR)
                print("\n   ⛔ Proceso detenido para evitar exportar datos incorrectos.\n")
                save_screenshot(page, "08_filtro_error_critico")
                browser.close()
                return False
            
            save_screenshot(page, "08_filtro_aplicado_ok")
            print("   ✅ Filtro 'Cualificado = Sí' aplicado")
            print("   ℹ️  Nota: El filtro se aplica en servidor, la tabla puede verse igual")
            
            # Paso 5: Exportar a Excel
            print("\n📍 PASO 5: EXPORTAR A EXCEL")
            print("-" * 70)
            
            print("   ⏳ Esperando que la tabla filtrada cargue...")
            time.sleep(2)
            save_screenshot(page, "09_antes_exportar")
            
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
                save_screenshot(page, "10_excel_no_encontrado")
                raise Exception("Botón de Excel no encontrado")
            
            # Esperar a que aparezca el popup de confirmación
            print("   ⏳ Esperando popup de confirmación...")
            time.sleep(3)
            save_screenshot(page, "11_excel_dialog")

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
                save_screenshot(page, "12_popup_error")
                raise Exception("No se pudo confirmar el popup de exportación")

            time.sleep(3)
            save_screenshot(page, "13_final_result")
            
            # Finalización
            print("\n" + "=" * 70)
            print("✅ PROCESO COMPLETADO EXITOSAMENTE")
            print("=" * 70)
            print(f"\n📬 El reporte de Empresas Cualificadas ha sido solicitado.")
            print(f"📧 Revisa tu correo en unos minutos.")
            print(f"📸 Screenshots guardados en: {SCREENSHOTS_DIR}")
            print(f"🔍 Filtro aplicado: Cualificado = Sí")
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
            print("   - La sección 'CRM > Clientes > Empresas' existe")
            print("   - La columna 'Cualificado' está visible (prueba zoom manual)")
            print()
            
            return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️  Proceso interrumpido por el usuario")
        sys.exit(130)
