"""
SAGA Orchestrator Test Suite
Tests all SAGA scenarios: success, and 4 failure scenarios
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any
from .saga_orchestrator import BookingSAGAOrchestrator

logger = logging.getLogger(__name__)


class SAGATestSuite:
    """Comprehensive test suite for SAGA orchestrator"""
    
    def __init__(self):
        self.test_results = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all SAGA tests"""
        logger.info("\n" + "=" * 80)
        logger.info("STARTING COMPREHENSIVE SAGA TEST SUITE")
        logger.info("=" * 80 + "\n")
        
        self.test_results = []
        
        # Test 1: Success scenario - no failures
        self._test_success_scenario()
        
        # Test 2-5: Failure scenarios for each step
        self._test_reserve_seat_failure()
        self._test_deduct_points_failure()
        self._test_payment_failure()
        self._test_confirm_booking_failure()
        
        # Generate report
        return self._generate_report()
    
    def _test_success_scenario(self):
        """Test successful booking without failures"""
        logger.info("\n" + "-" * 80)
        logger.info("TEST 1: SUCCESS SCENARIO - All steps completed")
        logger.info("-" * 80)
        
        booking_data = {
            'flight_id': 123,
            'user_id': 1,
            'total_fare': 500.00,
            'loyalty_points_to_use': 1000,
            'payment_method': 'card',
            'passengers': [
                {
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'gender': 'male'
                }
            ]
        }
        
        # No failure scenarios - all steps should succeed
        orchestrator = BookingSAGAOrchestrator()
        result = orchestrator.start_booking_saga(booking_data, failure_scenarios={})
        
        self.test_results.append({
            'test_name': 'Success Scenario',
            'expected': 'All steps completed',
            'result': 'SUCCESS' if result.get('success') else 'FAILED',
            'details': result,
            'status': result.get('success')
        })
        
        logger.info(f"Result: {'✅ PASSED' if result.get('success') else '❌ FAILED'}")
        if result.get('success'):
            logger.info(f"Booking Reference: {result.get('booking_reference')}")
        else:
            logger.error(f"Failed at step: {result.get('failed_step')}")
            logger.error(f"Error: {result.get('error')}")
    
    def _test_reserve_seat_failure(self):
        """Test failure at RESERVE_SEAT step"""
        logger.info("\n" + "-" * 80)
        logger.info("TEST 2: FAILURE SCENARIO - Reserve Seat fails")
        logger.info("-" * 80)
        
        booking_data = {
            'flight_id': 123,
            'user_id': 1,
            'total_fare': 500.00,
            'loyalty_points_to_use': 1000,
            'payment_method': 'card',
            'passengers': [
                {
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'gender': 'female'
                }
            ]
        }
        
        # Fail at RESERVE_SEAT
        failure_scenarios = {
            'reserve_seat': True,
            'deduct_loyalty_points': False,
            'process_payment': False,
            'confirm_booking': False
        }
        
        orchestrator = BookingSAGAOrchestrator()
        result = orchestrator.start_booking_saga(booking_data, failure_scenarios=failure_scenarios)
        
        expected_failed = result.get('failed_step') == 'RESERVE_SEAT'
        
        self.test_results.append({
            'test_name': 'Reserve Seat Failure',
            'expected': 'Failure at RESERVE_SEAT, compensation executed',
            'result': 'SUCCESS' if (not result.get('success') and expected_failed) else 'FAILED',
            'details': result,
            'status': not result.get('success') and expected_failed
        })
        
        logger.info(f"Result: {'✅ PASSED' if (not result.get('success') and expected_failed) else '❌ FAILED'}")
        logger.info(f"Failed at: {result.get('failed_step')}")
        logger.info(f"Compensation executed: {result.get('compensation_result', {}).get('successful_compensations', 0)} steps")
    
    def _test_deduct_points_failure(self):
        """Test failure at DEDUCT_LOYALTY_POINTS step"""
        logger.info("\n" + "-" * 80)
        logger.info("TEST 3: FAILURE SCENARIO - Deduct Loyalty Points fails")
        logger.info("-" * 80)
        
        booking_data = {
            'flight_id': 124,
            'user_id': 2,
            'total_fare': 600.00,
            'loyalty_points_to_use': 500,
            'payment_method': 'card',
            'passengers': [
                {
                    'first_name': 'Bob',
                    'last_name': 'Johnson',
                    'gender': 'male'
                }
            ]
        }
        
        # Fail at DEDUCT_LOYALTY_POINTS
        failure_scenarios = {
            'reserve_seat': False,
            'deduct_loyalty_points': True,
            'process_payment': False,
            'confirm_booking': False
        }
        
        orchestrator = BookingSAGAOrchestrator()
        result = orchestrator.start_booking_saga(booking_data, failure_scenarios=failure_scenarios)
        
        expected_failed = result.get('failed_step') == 'DEDUCT_LOYALTY_POINTS'
        expected_compensations = result.get('compensation_result', {}).get('successful_compensations', 0) >= 1
        
        self.test_results.append({
            'test_name': 'Deduct Points Failure',
            'expected': 'Failure at DEDUCT_LOYALTY_POINTS, previous steps compensated',
            'result': 'SUCCESS' if (not result.get('success') and expected_failed and expected_compensations) else 'FAILED',
            'details': result,
            'status': not result.get('success') and expected_failed and expected_compensations
        })
        
        logger.info(f"Result: {'✅ PASSED' if (not result.get('success') and expected_failed) else '❌ FAILED'}")
        logger.info(f"Failed at: {result.get('failed_step')}")
        logger.info(f"Compensation executed: {result.get('compensation_result', {}).get('successful_compensations', 0)} steps")
    
    def _test_payment_failure(self):
        """Test failure at PROCESS_PAYMENT step"""
        logger.info("\n" + "-" * 80)
        logger.info("TEST 4: FAILURE SCENARIO - Process Payment fails")
        logger.info("-" * 80)
        
        booking_data = {
            'flight_id': 125,
            'user_id': 3,
            'total_fare': 700.00,
            'loyalty_points_to_use': 0,
            'payment_method': 'card',
            'passengers': [
                {
                    'first_name': 'Alice',
                    'last_name': 'Williams',
                    'gender': 'female'
                }
            ]
        }
        
        # Fail at PROCESS_PAYMENT
        failure_scenarios = {
            'reserve_seat': False,
            'deduct_loyalty_points': False,
            'process_payment': True,
            'confirm_booking': False
        }
        
        orchestrator = BookingSAGAOrchestrator()
        result = orchestrator.start_booking_saga(booking_data, failure_scenarios=failure_scenarios)
        
        expected_failed = result.get('failed_step') == 'PROCESS_PAYMENT'
        expected_compensations = result.get('compensation_result', {}).get('successful_compensations', 0) >= 2
        
        self.test_results.append({
            'test_name': 'Payment Failure',
            'expected': 'Failure at PROCESS_PAYMENT, previous steps compensated',
            'result': 'SUCCESS' if (not result.get('success') and expected_failed and expected_compensations) else 'FAILED',
            'details': result,
            'status': not result.get('success') and expected_failed and expected_compensations
        })
        
        logger.info(f"Result: {'✅ PASSED' if (not result.get('success') and expected_failed) else '❌ FAILED'}")
        logger.info(f"Failed at: {result.get('failed_step')}")
        logger.info(f"Compensation executed: {result.get('compensation_result', {}).get('successful_compensations', 0)} steps")
    
    def _test_confirm_booking_failure(self):
        """Test failure at CONFIRM_BOOKING step"""
        logger.info("\n" + "-" * 80)
        logger.info("TEST 5: FAILURE SCENARIO - Confirm Booking fails")
        logger.info("-" * 80)
        
        booking_data = {
            'flight_id': 126,
            'user_id': 4,
            'total_fare': 800.00,
            'loyalty_points_to_use': 2000,
            'payment_method': 'counter',
            'passengers': [
                {
                    'first_name': 'David',
                    'last_name': 'Brown',
                    'gender': 'male'
                },
                {
                    'first_name': 'Emma',
                    'last_name': 'Davis',
                    'gender': 'female'
                }
            ]
        }
        
        # Fail at CONFIRM_BOOKING
        failure_scenarios = {
            'reserve_seat': False,
            'deduct_loyalty_points': False,
            'process_payment': False,
            'confirm_booking': True
        }
        
        orchestrator = BookingSAGAOrchestrator()
        result = orchestrator.start_booking_saga(booking_data, failure_scenarios=failure_scenarios)
        
        expected_failed = result.get('failed_step') == 'CONFIRM_BOOKING'
        expected_compensations = result.get('compensation_result', {}).get('successful_compensations', 0) >= 3
        
        self.test_results.append({
            'test_name': 'Confirm Booking Failure',
            'expected': 'Failure at CONFIRM_BOOKING, all previous steps compensated',
            'result': 'SUCCESS' if (not result.get('success') and expected_failed and expected_compensations) else 'FAILED',
            'details': result,
            'status': not result.get('success') and expected_failed and expected_compensations
        })
        
        logger.info(f"Result: {'✅ PASSED' if (not result.get('success') and expected_failed) else '❌ FAILED'}")
        logger.info(f"Failed at: {result.get('failed_step')}")
        logger.info(f"Compensation executed: {result.get('compensation_result', {}).get('successful_compensations', 0)} steps")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUITE SUMMARY")
        logger.info("=" * 80)
        
        passed = sum(1 for r in self.test_results if r['status'])
        total = len(self.test_results)
        
        logger.info(f"\nTotal Tests: {total}")
        logger.info(f"Passed: {passed} ✅")
        logger.info(f"Failed: {total - passed} ❌")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%\n")
        
        for result in self.test_results:
            status_symbol = "✅" if result['status'] else "❌"
            logger.info(f"{status_symbol} {result['test_name']}: {result['result']}")
        
        logger.info("\n" + "=" * 80)
        
        # Save detailed report
        self._save_test_report()
        
        return {
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': (passed/total)*100,
            'results': self.test_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _save_test_report(self):
        """Save detailed test report to file"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(self.test_results),
                'results': self.test_results
            }
            
            with open('saga_test_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info("Test report saved to saga_test_report.json")
            
        except Exception as e:
            logger.error(f"Error saving test report: {e}")


def run_saga_tests():
    """Run all SAGA tests"""
    test_suite = SAGATestSuite()
    return test_suite.run_all_tests()


if __name__ == "__main__":
    from typing import Dict, Any
    run_saga_tests()
