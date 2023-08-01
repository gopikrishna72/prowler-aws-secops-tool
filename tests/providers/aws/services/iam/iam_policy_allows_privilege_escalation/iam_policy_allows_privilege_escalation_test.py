from json import dumps
from re import search
from unittest import mock

from boto3 import client, session
from moto import mock_iam

from prowler.providers.aws.lib.audit_info.models import AWS_Audit_Info
from prowler.providers.common.models import Audit_Metadata

AWS_REGION = "us-east-1"
AWS_ACCOUNT_NUMBER = "123456789012"


class Test_iam_policy_allows_privilege_escalation:
    def set_mocked_audit_info(self):
        audit_info = AWS_Audit_Info(
            session_config=None,
            original_session=None,
            audit_session=session.Session(
                profile_name=None,
                botocore_session=None,
            ),
            audited_account=AWS_ACCOUNT_NUMBER,
            audited_account_arn=f"arn:aws:iam::{AWS_ACCOUNT_NUMBER}:root",
            audited_user_id=None,
            audited_partition="aws",
            audited_identity_arn=None,
            profile=None,
            profile_region=None,
            credentials=None,
            assumed_role_info=None,
            audited_regions=["us-east-1", "eu-west-1"],
            organizations_metadata=None,
            audit_resources=None,
            mfa_enabled=False,
            audit_metadata=Audit_Metadata(
                services_scanned=0,
                expected_checks=[],
                completed_checks=0,
                audit_progress=0,
            ),
        )

        return audit_info

    @mock_iam
    def test_iam_policy_allows_privilege_escalation_sts(self):
        iam_client = client("iam", region_name=AWS_REGION)
        policy_name = "policy1"
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": "sts:*", "Resource": "*"},
            ],
        }
        policy_arn = iam_client.create_policy(
            PolicyName=policy_name, PolicyDocument=dumps(policy_document)
        )["Policy"]["Arn"]

        current_audit_info = self.set_mocked_audit_info()
        from prowler.providers.aws.services.iam.iam_service import IAM

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ), mock.patch(
            "prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation.iam_client",
            new=IAM(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation import (
                iam_policy_allows_privilege_escalation,
            )

            check = iam_policy_allows_privilege_escalation()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"Custom Policy {policy_arn} allows privilege escalation using the following actions: {{'sts:*'}}"
            )
            assert result[0].resource_id == policy_name
            assert result[0].resource_arn == policy_arn

    @mock_iam
    def test_iam_policy_not_allows_privilege_escalation(self):
        iam_client = client("iam", region_name=AWS_REGION)
        policy_name = "policy1"
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": "sts:*", "Resource": "*"},
                {"Effect": "Deny", "Action": "sts:*", "Resource": "*"},
                {"Effect": "Deny", "NotAction": "sts:*", "Resource": "*"},
            ],
        }
        policy_arn = iam_client.create_policy(
            PolicyName=policy_name, PolicyDocument=dumps(policy_document)
        )["Policy"]["Arn"]

        current_audit_info = self.set_mocked_audit_info()
        from prowler.providers.aws.services.iam.iam_service import IAM

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ), mock.patch(
            "prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation.iam_client",
            new=IAM(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation import (
                iam_policy_allows_privilege_escalation,
            )

            check = iam_policy_allows_privilege_escalation()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"Custom Policy {policy_arn} does not allow privilege escalation"
            )
            assert result[0].resource_id == policy_name
            assert result[0].resource_arn == policy_arn

    @mock_iam
    def test_iam_policy_not_allows_privilege_escalation_glue_GetDevEndpoints(self):
        iam_client = client("iam", region_name=AWS_REGION)
        policy_name = "policy1"
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": "lambda:*", "Resource": "*"},
                {"Effect": "Deny", "Action": "lambda:InvokeFunction", "Resource": "*"},
                {
                    "Effect": "Deny",
                    "NotAction": "glue:GetDevEndpoints",
                    "Resource": "*",
                },
            ],
        }
        policy_arn = iam_client.create_policy(
            PolicyName=policy_name, PolicyDocument=dumps(policy_document)
        )["Policy"]["Arn"]

        current_audit_info = self.set_mocked_audit_info()
        from prowler.providers.aws.services.iam.iam_service import IAM

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ), mock.patch(
            "prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation.iam_client",
            new=IAM(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation import (
                iam_policy_allows_privilege_escalation,
            )

            check = iam_policy_allows_privilege_escalation()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"Custom Policy {policy_arn} does not allow privilege escalation"
            )
            assert result[0].resource_id == policy_name
            assert result[0].resource_arn == policy_arn

    # @mock_iam
    # def test_iam_policy_not_allows_privilege_escalation_dynamodb_PutItem(self):
    #     iam_client = client("iam", region_name=AWS_REGION)
    #     policy_name = "policy1"
    #     policy_document = {
    #         "Version": "2012-10-17",
    #         "Statement": [
    #             {
    #                 "Effect": "Allow",
    #                 "Action": [
    #                     "lambda:*",
    #                     "iam:PassRole",
    #                     "dynamodb:PutItem",
    #                     "cloudformation:CreateStack",
    #                     "cloudformation:DescribeStacks",
    #                     "ec2:RunInstances",
    #                 ],
    #                 "Resource": "*",
    #             },
    #             {
    #                 "Effect": "Deny",
    #                 "Action": ["lambda:InvokeFunction", "cloudformation:CreateStack"],
    #                 "Resource": "*",
    #             },
    #             {"Effect": "Deny", "NotAction": "dynamodb:PutItem", "Resource": "*"},
    #         ],
    #     }
    #     policy_arn = iam_client.create_policy(
    #         PolicyName=policy_name, PolicyDocument=dumps(policy_document)
    #     )["Policy"]["Arn"]

    #     current_audit_info = self.set_mocked_audit_info()
    #     from prowler.providers.aws.services.iam.iam_service import IAM

    #     with mock.patch(
    #         "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
    #         new=current_audit_info,
    #     ), mock.patch(
    #         "prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation.iam_client",
    #         new=IAM(current_audit_info),
    #     ):
    #         # Test Check
    #         from prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation import (
    #             iam_policy_allows_privilege_escalation,
    #         )

    #         check = iam_policy_allows_privilege_escalation()
    #         result = check.execute()
    #         assert len(result) == 1
    #         assert result[0].status == "FAIL"
    #         assert (
    #             result[0].status_extended
    #             == f"Custom Policy {policy_arn} allows privilege escalation using the following actions: {{'dynamodb:PutItem'}}"
    #         )
    #         assert result[0].resource_id == policy_name
    #         assert result[0].resource_arn == policy_arn

    @mock_iam
    def test_iam_policy_allows_privilege_escalation_iam_PassRole_and_ec2_RunInstances(
        self,
    ):
        iam_client = client("iam", region_name=AWS_REGION)
        policy_name = "policy1"
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:PassRole",
                    ],
                    "Resource": "*",
                },
                {
                    "Effect": "Allow",
                    "Action": ["ec2:RunInstances"],
                    "Resource": "*",
                },
            ],
        }
        policy_arn = iam_client.create_policy(
            PolicyName=policy_name, PolicyDocument=dumps(policy_document)
        )["Policy"]["Arn"]

        current_audit_info = self.set_mocked_audit_info()
        from prowler.providers.aws.services.iam.iam_service import IAM

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ), mock.patch(
            "prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation.iam_client",
            new=IAM(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation import (
                iam_policy_allows_privilege_escalation,
            )

            check = iam_policy_allows_privilege_escalation()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert result[0].resource_id == policy_name
            assert result[0].resource_arn == policy_arn

            assert search(
                f"Custom Policy {policy_arn} allows privilege escalation using the following actions: ",
                result[0].status_extended,
            )
            assert search("iam:PassRole", result[0].status_extended)
            assert search("ec2:RunInstances", result[0].status_extended)

    @mock_iam
    def test_iam_policy_allows_privilege_escalation_iam_PassRole(
        self,
    ):
        iam_client = client("iam", region_name=AWS_REGION)
        policy_name = "policy1"
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "iam:PassRole",
                    "Resource": f"arn:aws:iam::{AWS_ACCOUNT_NUMBER}:role/ecs",
                }
            ],
        }
        policy_arn = iam_client.create_policy(
            PolicyName=policy_name, PolicyDocument=dumps(policy_document)
        )["Policy"]["Arn"]

        current_audit_info = self.set_mocked_audit_info()
        from prowler.providers.aws.services.iam.iam_service import IAM

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ), mock.patch(
            "prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation.iam_client",
            new=IAM(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation import (
                iam_policy_allows_privilege_escalation,
            )

            check = iam_policy_allows_privilege_escalation()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert result[0].resource_id == policy_name
            assert result[0].resource_arn == policy_arn

            assert search(
                f"Custom Policy {policy_arn} allows privilege escalation using the following actions: ",
                result[0].status_extended,
            )
            assert search("iam:PassRole", result[0].status_extended)

    @mock_iam
    def test_iam_policy_allows_privilege_escalation_iam_PassRole_and_other_actions(
        self,
    ):
        iam_client = client("iam", region_name=AWS_REGION)
        policy_name = "policy1"
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "iam:PassRole",
                    "Resource": f"arn:aws:iam::{AWS_ACCOUNT_NUMBER}:role/ecs",
                },
                {
                    "Action": "account:GetAccountInformation",
                    "Effect": "Allow",
                    "Resource": "*",
                },
            ],
        }
        policy_arn = iam_client.create_policy(
            PolicyName=policy_name, PolicyDocument=dumps(policy_document)
        )["Policy"]["Arn"]

        current_audit_info = self.set_mocked_audit_info()
        from prowler.providers.aws.services.iam.iam_service import IAM

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=current_audit_info,
        ), mock.patch(
            "prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation.iam_client",
            new=IAM(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.iam.iam_policy_allows_privilege_escalation.iam_policy_allows_privilege_escalation import (
                iam_policy_allows_privilege_escalation,
            )

            check = iam_policy_allows_privilege_escalation()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert result[0].resource_id == policy_name
            assert result[0].resource_arn == policy_arn

            assert search(
                f"Custom Policy {policy_arn} allows privilege escalation using the following actions: ",
                result[0].status_extended,
            )
            assert search("iam:PassRole", result[0].status_extended)
