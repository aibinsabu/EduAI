from playwright.sync_api import sync_playwright
import os

def run():
    print("Starting Comprehensive Playwright capture...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        try:
            # 1. Admin Dashboard
            print("Logging in as Admin...")
            page.goto('http://127.0.0.1:8080/login/')
            page.fill('input[name="email"]', 'admin@test.com')
            page.fill('input[name="password"]', 'password')
            page.click('button[type="submit"]')
            page.wait_for_timeout(3000)
            page.screenshot(path='d:/New folder (2)/project/admin_dashboard_ui_real.png', full_page=True)
            print("Saved admin_dashboard_ui_real.png")
            page.goto('http://127.0.0.1:8080/logout/')
            page.wait_for_timeout(1000)
            
            # 2. Principal Dashboard
            print("Logging in as Principal...")
            page.goto('http://127.0.0.1:8080/login/')
            page.fill('input[name="email"]', 'p@test.com')
            page.fill('input[name="password"]', 'password')
            page.click('button[type="submit"]')
            page.wait_for_timeout(3000)
            page.screenshot(path='d:/New folder (2)/project/principal_dashboard_ui_real.png', full_page=True)
            print("Saved principal_dashboard_ui_real.png")
            page.goto('http://127.0.0.1:8080/logout/')
            page.wait_for_timeout(1000)
            
            # 3. HOD Dashboard
            print("Logging in as HOD...")
            page.goto('http://127.0.0.1:8080/login/')
            page.fill('input[name="email"]', 'h@test.com')
            page.fill('input[name="password"]', 'password')
            page.click('button[type="submit"]')
            page.wait_for_timeout(3000)
            page.screenshot(path='d:/New folder (2)/project/hod_dashboard_ui_real.png', full_page=True)
            print("Saved hod_dashboard_ui_real.png")
            page.goto('http://127.0.0.1:8080/logout/')
            page.wait_for_timeout(1000)
            
            # 4. Student Dashboard
            print("Logging in as Student...")
            page.goto('http://127.0.0.1:8080/login/')
            page.fill('input[name="email"]', 's@test.com')
            page.fill('input[name="password"]', 'password')
            page.click('button[type="submit"]')
            page.wait_for_timeout(3000)
            page.screenshot(path='d:/New folder (2)/project/student_dashboard_ui_real.png', full_page=True)
            print("Saved student_dashboard_ui_real.png")
            page.goto('http://127.0.0.1:8080/logout/')
            page.wait_for_timeout(1000)
            
            # 5. Teacher Courses & Results
            print("Logging in as Teacher...")
            page.goto('http://127.0.0.1:8080/login/')
            page.fill('input[name="email"]', 't@test.com')
            page.fill('input[name="password"]', 'password')
            page.click('button[type="submit"]')
            page.wait_for_timeout(2000)
            
            page.goto('http://127.0.0.1:8080/teacher/courses/')
            page.wait_for_timeout(3000)
            page.screenshot(path='d:/New folder (2)/project/teacher_courses_ui_real.png', full_page=True)
            print("Saved teacher_courses_ui_real.png")
            
            page.goto('http://127.0.0.1:8080/teacher/results/')
            page.wait_for_timeout(3000)
            page.screenshot(path='d:/New folder (2)/project/teacher_results_ui_real.png', full_page=True)
            print("Saved teacher_results_ui_real.png")
            
        except Exception as e:
            print(f"Error during capture: {e}")
        finally:
            browser.close()
            print("Browser closed.")

if __name__ == '__main__':
    run()
