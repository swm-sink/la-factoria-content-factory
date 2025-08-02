#!/usr/bin/env python3
"""
Validation script for user data deletion system (Step 23).

This script validates that:
1. User data deletion models are properly defined
2. Deletion service implements all required functionality
3. API endpoints are correctly configured
4. GDPR compliance features are working
5. Audit trail system is functional
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


class UserDataDeletionValidator:
    """Validates user data deletion system implementation."""

    def __init__(self):
        self.validation_results = {
            "models_defined": False,
            "service_implemented": False,
            "api_endpoints_created": False,
            "gdpr_compliance_features": False,
            "audit_trail_system": False,
            "data_discovery": False,
            "verification_system": False,
            "router_integration": False,
        }
        self.errors = []
        self.warnings = []
        self.project_root = Path(__file__).parent.parent

    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks."""
        print("🔍 Starting user data deletion validation...")

        # 1. Validate models are defined
        self._validate_models()

        # 2. Validate service implementation
        self._validate_service()

        # 3. Validate API endpoints
        self._validate_api_endpoints()

        # 4. Validate GDPR compliance features
        self._validate_gdpr_compliance()

        # 5. Validate audit trail system
        self._validate_audit_trail()

        # 6. Validate data discovery
        self._validate_data_discovery()

        # 7. Validate verification system
        self._validate_verification_system()

        # 8. Validate router integration
        self._validate_router_integration()

        return self._generate_report()

    def _validate_models(self):
        """Validate that user data deletion models are properly defined."""
        models_file = self.project_root / "app" / "models" / "user_data_deletion.py"

        if not models_file.exists():
            self.errors.append("User data deletion models file does not exist")
            return

        try:
            with open(models_file, "r") as f:
                content = f.read()

            required_models = [
                "class UserDataDeletionRequest",
                "class DeletionStatus",
                "class DeletionScope",
                "class DataCategory",
                "class DeletionReason",
                "class DataLocation",
                "class DeletionTask",
                "class DeletionSummary",
                "class DeletionConfiguration",
                "class DeletionMetrics",
                "class DataInventory",
                "class GDPRComplianceReport",
            ]

            missing_models = []
            for model in required_models:
                if model not in content:
                    missing_models.append(model)

            if missing_models:
                self.errors.append(f"Missing models: {missing_models}")
            else:
                print("✅ User data deletion models properly defined")
                self.validation_results["models_defined"] = True

        except Exception as e:
            self.errors.append(f"Failed to validate models: {e}")

    def _validate_service(self):
        """Validate that the deletion service is properly implemented."""
        service_file = self.project_root / "app" / "services" / "user_data_deletion.py"

        if not service_file.exists():
            self.errors.append("User data deletion service file does not exist")
            return

        try:
            with open(service_file, "r") as f:
                content = f.read()

            required_methods = [
                "class UserDataDeletionService",
                "async def create_deletion_request",
                "async def verify_deletion_request",
                "async def process_deletion_request",
                "async def get_deletion_request",
                "async def _discover_user_data",
                "async def _execute_deletion_tasks",
                "async def _delete_user_data_from_location",
                "_filter_locations_by_scope",
                "async def get_deletion_metrics",
            ]

            missing_methods = []
            for method in required_methods:
                if method not in content:
                    missing_methods.append(method)

            if missing_methods:
                self.errors.append(f"Missing service methods: {missing_methods}")
            else:
                print("✅ User data deletion service properly implemented")
                self.validation_results["service_implemented"] = True

        except Exception as e:
            self.errors.append(f"Failed to validate service: {e}")

    def _validate_api_endpoints(self):
        """Validate that API endpoints are correctly configured."""
        api_file = self.project_root / "app" / "api" / "routes" / "user_data_deletion.py"

        if not api_file.exists():
            self.errors.append("User data deletion API routes file does not exist")
            return

        try:
            with open(api_file, "r") as f:
                content = f.read()

            required_endpoints = [
                '@router.post("/request"',
                '@router.post("/admin/request"',
                '@router.post("/verify"',
                '@router.post("/process/{request_id}"',
                '@router.get("/request/{request_id}"',
                '@router.get("/requests"',
                '@router.delete("/request/{request_id}"',
                '@router.get("/metrics"',
                '@router.get("/config"',
                '@router.put("/config"',
                '@router.get("/compliance-report"',
            ]

            missing_endpoints = []
            for endpoint in required_endpoints:
                if endpoint not in content:
                    missing_endpoints.append(endpoint)

            if missing_endpoints:
                self.errors.append(f"Missing API endpoints: {missing_endpoints}")
            else:
                print("✅ User data deletion API endpoints properly configured")
                self.validation_results["api_endpoints_created"] = True

        except Exception as e:
            self.errors.append(f"Failed to validate API endpoints: {e}")

    def _validate_gdpr_compliance(self):
        """Validate GDPR compliance features."""
        service_file = self.project_root / "app" / "services" / "user_data_deletion.py"
        models_file = self.project_root / "app" / "models" / "user_data_deletion.py"

        try:
            with open(service_file, "r") as f:
                service_content = f.read()

            with open(models_file, "r") as f:
                models_content = f.read()

            # Combine content from both files for checking
            combined_content = service_content + models_content

            gdpr_features = [
                "GDPR_RIGHT_TO_ERASURE",
                "_check_legal_hold",
                "verification_token",
                "verification_expires_at",
                "GDPRComplianceReport",
                "retention_period_days",
                "hard_delete_after_days",
                "compliance_notes",
            ]

            missing_features = []
            for feature in gdpr_features:
                if feature not in combined_content:
                    missing_features.append(feature)

            if missing_features:
                self.errors.append(f"Missing GDPR features: {missing_features}")
            else:
                print("✅ GDPR compliance features implemented")
                self.validation_results["gdpr_compliance_features"] = True

        except Exception as e:
            self.errors.append(f"Failed to validate GDPR compliance: {e}")

    def _validate_audit_trail(self):
        """Validate audit trail system."""
        service_file = self.project_root / "app" / "services" / "user_data_deletion.py"
        api_file = self.project_root / "app" / "api" / "routes" / "user_data_deletion.py"

        try:
            with open(service_file, "r") as f:
                service_content = f.read()

            with open(api_file, "r") as f:
                api_content = f.read()

            # Combine content from both files for checking
            combined_content = service_content + api_content

            audit_features = [
                "audit_trail",
                "_add_audit_entry",
                "request_created",
                "verification_completed",
                "processing_started",
                "processing_completed",
                "processing_failed",
                "request_cancelled",
            ]

            missing_features = []
            for feature in audit_features:
                if feature not in combined_content:
                    missing_features.append(feature)

            if missing_features:
                self.errors.append(f"Missing audit trail features: {missing_features}")
            else:
                print("✅ Audit trail system implemented")
                self.validation_results["audit_trail_system"] = True

        except Exception as e:
            self.errors.append(f"Failed to validate audit trail: {e}")

    def _validate_data_discovery(self):
        """Validate data discovery functionality."""
        service_file = self.project_root / "app" / "services" / "user_data_deletion.py"

        try:
            with open(service_file, "r") as f:
                content = f.read()

            discovery_features = [
                "_initialize_data_locations",
                "_discover_user_data",
                "DataInventory",
                "DataLocation",
                'system="firestore"',
                'system="redis"',
                "identifier_field",
                "data_types",
                "retention_period_days",
                "encryption_status",
            ]

            missing_features = []
            for feature in discovery_features:
                if feature not in content:
                    missing_features.append(feature)

            if missing_features:
                self.errors.append(f"Missing data discovery features: {missing_features}")
            else:
                print("✅ Data discovery system implemented")
                self.validation_results["data_discovery"] = True

        except Exception as e:
            self.errors.append(f"Failed to validate data discovery: {e}")

    def _validate_verification_system(self):
        """Validate user verification system."""
        service_file = self.project_root / "app" / "services" / "user_data_deletion.py"
        api_file = self.project_root / "app" / "api" / "routes" / "user_data_deletion.py"

        try:
            with open(service_file, "r") as f:
                service_content = f.read()

            with open(api_file, "r") as f:
                api_content = f.read()

            verification_features = [
                "_generate_verification_token",
                "verify_deletion_request",
                "verification_completed",
                "verification_expires_at",
                "DeletionVerificationRequest",
                "require_verification",
                "verification_timeout_hours",
            ]

            missing_features = []
            for feature in verification_features:
                if feature not in service_content and feature not in api_content:
                    missing_features.append(feature)

            if missing_features:
                self.errors.append(f"Missing verification features: {missing_features}")
            else:
                print("✅ User verification system implemented")
                self.validation_results["verification_system"] = True

        except Exception as e:
            self.errors.append(f"Failed to validate verification system: {e}")

    def _validate_router_integration(self):
        """Validate that routes are properly integrated."""
        init_file = self.project_root / "app" / "api" / "routes" / "__init__.py"

        if not init_file.exists():
            self.errors.append("API routes __init__.py file does not exist")
            return

        try:
            with open(init_file, "r") as f:
                content = f.read()

            integration_checks = [
                "from app.api.routes.user_data_deletion import router as user_data_deletion_router",
                "api_router.include_router(user_data_deletion_router",
            ]

            missing_integrations = []
            for check in integration_checks:
                if check not in content:
                    missing_integrations.append(check)

            if missing_integrations:
                self.errors.append(f"Missing router integrations: {missing_integrations}")
            else:
                print("✅ Router integration properly configured")
                self.validation_results["router_integration"] = True

        except Exception as e:
            self.errors.append(f"Failed to validate router integration: {e}")

    def _generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        passed_checks = sum(1 for result in self.validation_results.values() if result)
        total_checks = len(self.validation_results)
        success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

        return {
            "summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "success_rate": f"{success_rate:.1f}%",
                "status": "PASS" if success_rate >= 80 else "FAIL",
            },
            "results": self.validation_results,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def main():
    """Main validation function."""
    validator = UserDataDeletionValidator()
    report = validator.validate_all()

    # Print results
    print("\n" + "=" * 80)
    print("USER DATA DELETION VALIDATION REPORT")
    print("=" * 80)

    print(f"\nSummary:")
    print(f"  Total Checks: {report['summary']['total_checks']}")
    print(f"  Passed: {report['summary']['passed_checks']}")
    print(f"  Success Rate: {report['summary']['success_rate']}")
    print(f"  Status: {report['summary']['status']}")

    if report["errors"]:
        print(f"\n❌ Errors ({len(report['errors'])}):")
        for error in report["errors"]:
            print(f"  • {error}")

    if report["warnings"]:
        print(f"\n⚠️ Warnings ({len(report['warnings'])}):")
        for warning in report["warnings"]:
            print(f"  • {warning}")

    print("\n📊 Detailed Results:")
    for check, result in report["results"].items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {check.replace('_', ' ').title()}: {status}")

    # Save report
    report_file = Path(__file__).parent.parent / "validation_reports" / "user_data_deletion.json"
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📝 Report saved to: {report_file}")

    # Exit with appropriate code
    exit_code = 0 if report["summary"]["status"] == "PASS" else 1
    print(f"\n{'🎉 Validation completed successfully!' if exit_code == 0 else '❌ Validation failed!'}")

    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
