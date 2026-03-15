from playwright.sync_api import sync_playwright
import time
import os

def run():
    print("Starting Playwright capture...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        try:
            # 1. Login Page
            print("Capturing Login UI...")
            page.goto('http://127.0.0.1:8080/login/')
            page.wait_for_timeout(3000)
            page.screenshot(path='d:/New folder (2)/project/admin_login_ui_real.png', full_page=True)
            print("Saved admin_login_ui_real.png")
            
            # 2. Teacher Dashboard
            print("Logging in as Teacher...")
            page.fill('input[name="email"]', 't@test.com')
            page.fill('input[name="password"]', 'password')
            page.click('button[type="submit"]')
            page.wait_for_timeout(4000)
            page.screenshot(path='d:/New folder (2)/project/teacher_dashboard_ui_real.png', full_page=True)
            print("Saved teacher_dashboard_ui_real.png")
            
            # Logout
            page.goto('http://127.0.0.1:8080/logout/')
            page.wait_for_timeout(2000)
            
            # 3. AI Exam Interface
            print("Logging in as Student...")
            page.goto('http://127.0.0.1:8080/login/')
            page.fill('input[name="email"]', 's@test.com')
            page.fill('input[name="password"]', 'password')
            page.click('button[type="submit"]')
            page.wait_for_timeout(3000)
            
            print("Navigating to Exam Interface...")
            # Read exam id dynamically from the file we saved
            with open('exam_id.txt', 'r') as f:
                exam_id = f.read().strip()
                
            page.goto(f'http://127.0.0.1:8080/student/exam/{exam_id}/')
            page.wait_for_timeout(4000) # Wait for streams, UI, etc to load
            page.screenshot(path='d:/New folder (2)/project/ai_exam_interface_real.png', full_page=True)
            print("Saved ai_exam_interface_real.png")
            
        except Exception as e:
            print(f"Error during capture: {e}")
        finally:
            browser.close()
            print("Browser closed.")

if __name__ == '__main__':
    run()
