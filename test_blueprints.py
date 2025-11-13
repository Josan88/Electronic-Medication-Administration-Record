"""
Test suite for Flask Blueprint implementation in eMAR.

This test suite verifies that the route blueprints are correctly registered
and that all endpoints remain functional after the refactoring.
"""

import sys
import time


def test_blueprint_registration():
    """Test that all blueprints are registered correctly"""
    print("\n" + "="*60)
    print("BLUEPRINT REGISTRATION TEST")
    print("="*60)
    
    try:
        import app
        
        # Check that Flask app is created
        assert app.app is not None, "Flask app not created"
        print("✓ Flask app created successfully")
        
        # Check blueprint registration
        blueprints = app.app.blueprints
        expected_blueprints = ['patients', 'prescriptions', 'tracking']
        
        for bp_name in expected_blueprints:
            assert bp_name in blueprints, f"Blueprint '{bp_name}' not registered"
            print(f"✓ Blueprint '{bp_name}' registered")
        
        print(f"\n✓ All {len(expected_blueprints)} blueprints registered successfully")
        
        # Check route registration
        routes = [rule.rule for rule in app.app.url_map.iter_rules() if rule.endpoint != 'static']
        expected_routes = [
            '/',
            '/api/health',
            '/api/patients',
            '/api/patient/<patient_id>',
            '/api/patient/<patient_id>/prescriptions',
            '/api/patient/<patient_id>/tracking',
            '/api/check_patient/<patient_id>',
            '/api/prescriptions',
            '/api/medication-tracking',
        ]
        
        print(f"\n✓ Found {len(routes)} routes registered")
        
        for route in expected_routes:
            # Check if route exists (with or without parameters)
            route_found = any(
                route.replace('<', '').replace('>', '') in r.replace('<', '').replace('>', '') 
                for r in routes
            )
            assert route_found, f"Route '{route}' not found"
        
        print("✓ All expected routes are registered")
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_route_endpoints():
    """Test that route endpoints have correct blueprint references"""
    print("\n" + "="*60)
    print("ROUTE ENDPOINT TEST")
    print("="*60)
    
    try:
        import app
        
        # Map of routes to expected blueprint endpoints
        expected_mappings = {
            '/api/patients': ['patients.get_patients', 'patients.add_patient'],
            '/api/patient/<patient_id>': ['patients.get_patient_by_id'],
            '/api/patient/<patient_id>/prescriptions': ['patients.get_patient_prescriptions'],
            '/api/patient/<patient_id>/tracking': ['patients.get_patient_tracking'],
            '/api/check_patient/<patient_id>': ['patients.check_patient'],
            '/api/prescriptions': ['prescriptions.get_prescriptions', 'prescriptions.add_prescription'],
            '/api/medication-tracking': ['tracking.get_medication_tracking', 'tracking.add_medication_tracking'],
        }
        
        for rule in app.app.url_map.iter_rules():
            if rule.rule in expected_mappings:
                assert rule.endpoint in expected_mappings[rule.rule], \
                    f"Route {rule.rule} has unexpected endpoint {rule.endpoint}"
                print(f"✓ {rule.rule:45s} -> {rule.endpoint}")
        
        print(f"\n✓ All route endpoints map to correct blueprints")
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_app_structure():
    """Test that app.py has been properly refactored"""
    print("\n" + "="*60)
    print("APP STRUCTURE TEST")
    print("="*60)
    
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        # Check that blueprints are imported
        assert 'from routes import register_blueprints' in app_content, \
            "Blueprint registration import not found"
        print("✓ Blueprint registration imported")
        
        # Check that register_blueprints is called
        assert 'register_blueprints(app' in app_content, \
            "register_blueprints() call not found"
        print("✓ register_blueprints() called")
        
        # Check that old route decorators are removed
        old_patterns = [
            '@app.route("/api/patients"',
            '@app.route("/api/prescriptions"',
            '@app.route("/api/medication-tracking"',
        ]
        
        for pattern in old_patterns:
            assert pattern not in app_content, \
                f"Old route decorator found: {pattern}"
        
        print("✓ Old route decorators removed from app.py")
        
        # Check that essential app components are still present
        assert 'def process_prescription_queue()' in app_content, \
            "Background worker function missing"
        print("✓ Background worker function present")
        
        # Check for persistent queue import (new implementation)
        assert 'from services.queue_service import persistent_queue' in app_content, \
            "Persistent queue import missing"
        print("✓ Persistent queue imported")
        
        print(f"\n✓ app.py properly refactored")
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def main():
    """Run all blueprint tests"""
    print("="*60)
    print("FLASK BLUEPRINT IMPLEMENTATION TEST SUITE")
    print("="*60)
    
    tests = [
        test_blueprint_registration,
        test_route_endpoints,
        test_app_structure,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        time.sleep(0.5)
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✓ ALL BLUEPRINT TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
