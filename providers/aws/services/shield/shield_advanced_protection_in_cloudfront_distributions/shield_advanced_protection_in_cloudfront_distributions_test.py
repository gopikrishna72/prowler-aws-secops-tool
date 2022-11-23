from unittest import mock

from moto.core import DEFAULT_ACCOUNT_ID
from providers.aws.services.cloudfront.cloudfront_service import Distribution
from providers.aws.services.shield.shield_service import Protection

AWS_REGION = "eu-west-1"


class Test_shield_advanced_protection_in_cloudfront_distributions:
    def test_no_shield_not_active(self):
        # Shield Client
        shield_client = mock.MagicMock
        shield_client.enabled = False
        # CloudFront Client
        cloudfront_client = mock.MagicMock
        with mock.patch(
            "providers.aws.services.shield.shield_service.Shield",
            new=shield_client,
        ), mock.patch(
            "providers.aws.services.cloudfront.cloudfront_service.CloudFront",
            new=cloudfront_client,
        ):
            # Test Check
            from providers.aws.services.shield.shield_advanced_protection_in_cloudfront_distributions.shield_advanced_protection_in_cloudfront_distributions import (
                shield_advanced_protection_in_cloudfront_distributions,
            )

            check = shield_advanced_protection_in_cloudfront_distributions()
            result = check.execute()

            assert len(result) == 0

    def test_shield_enabled_cloudfront_protected(self):
        # CloudFront Client
        cloudfront_client = mock.MagicMock
        distribution_id = "EDFDVBD632BHDS5"
        distribution_arn = (
            f"arn:aws:cloudfront::{DEFAULT_ACCOUNT_ID}:distribution/{distribution_id}"
        )
        cloudfront_client.distributions = {
            distribution_id: Distribution(
                arn=distribution_arn, id=distribution_id, region=AWS_REGION, origins=[]
            )
        }

        # Shield Client
        shield_client = mock.MagicMock
        shield_client.enabled = True
        shield_client.region = AWS_REGION
        protection_id = "test-protection"
        shield_client.protections = {
            protection_id: Protection(
                id=protection_id,
                name="",
                resource_arn=distribution_arn,
                protection_arn="",
                region=AWS_REGION,
            )
        }

        with mock.patch(
            "providers.aws.services.shield.shield_service.Shield",
            new=shield_client,
        ), mock.patch(
            "providers.aws.services.cloudfront.cloudfront_service.CloudFront",
            new=cloudfront_client,
        ):
            # Test Check
            from providers.aws.services.shield.shield_advanced_protection_in_cloudfront_distributions.shield_advanced_protection_in_cloudfront_distributions import (
                shield_advanced_protection_in_cloudfront_distributions,
            )

            check = shield_advanced_protection_in_cloudfront_distributions()
            result = check.execute()

            assert len(result) == 1
            assert result[0].region == AWS_REGION
            assert result[0].resource_id == distribution_id
            assert result[0].resource_arn == distribution_arn
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"CloudFront distribution {distribution_id} is protected by AWS Shield Advanced"
            )

    def test_shield_enabled_cloudfront_not_protected(self):
        # CloudFront Client
        cloudfront_client = mock.MagicMock
        distribution_id = "EDFDVBD632BHDS5"
        distribution_arn = (
            f"arn:aws:cloudfront::{DEFAULT_ACCOUNT_ID}:distribution/{distribution_id}"
        )
        cloudfront_client.distributions = {
            distribution_id: Distribution(
                arn=distribution_arn, id=distribution_id, region=AWS_REGION, origins=[]
            )
        }

        # Shield Client
        shield_client = mock.MagicMock
        shield_client.enabled = True
        shield_client.region = AWS_REGION
        shield_client.protections = {}

        with mock.patch(
            "providers.aws.services.shield.shield_service.Shield",
            new=shield_client,
        ), mock.patch(
            "providers.aws.services.cloudfront.cloudfront_service.CloudFront",
            new=cloudfront_client,
        ):
            # Test Check
            from providers.aws.services.shield.shield_advanced_protection_in_cloudfront_distributions.shield_advanced_protection_in_cloudfront_distributions import (
                shield_advanced_protection_in_cloudfront_distributions,
            )

            check = shield_advanced_protection_in_cloudfront_distributions()
            result = check.execute()

            assert len(result) == 1
            assert result[0].region == AWS_REGION
            assert result[0].resource_id == distribution_id
            assert result[0].resource_arn == distribution_arn
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"CloudFront distribution {distribution_id} is not protected by AWS Shield Advanced"
            )

    def test_shield_disabled_cloudfront_not_protected(self):
        # CloudFront Client
        cloudfront_client = mock.MagicMock
        distribution_id = "EDFDVBD632BHDS5"
        distribution_arn = (
            f"arn:aws:cloudfront::{DEFAULT_ACCOUNT_ID}:distribution/{distribution_id}"
        )
        cloudfront_client.distributions = {
            distribution_id: Distribution(
                arn=distribution_arn, id=distribution_id, region=AWS_REGION, origins=[]
            )
        }

        # Shield Client
        shield_client = mock.MagicMock
        shield_client.enabled = False
        shield_client.region = AWS_REGION
        shield_client.protections = {}

        with mock.patch(
            "providers.aws.services.shield.shield_service.Shield",
            new=shield_client,
        ), mock.patch(
            "providers.aws.services.cloudfront.cloudfront_service.CloudFront",
            new=cloudfront_client,
        ):
            # Test Check
            from providers.aws.services.shield.shield_advanced_protection_in_cloudfront_distributions.shield_advanced_protection_in_cloudfront_distributions import (
                shield_advanced_protection_in_cloudfront_distributions,
            )

            check = shield_advanced_protection_in_cloudfront_distributions()
            result = check.execute()

            assert len(result) == 0