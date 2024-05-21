from typing import Any, Dict, List, Optional, Union, cast
from uuid import uuid4

import boto3


class CloudFrontClient:
    """
    API wrapper for CloudFront to retrieve and create resources.
    """

    def __init__(self, region: str, access_key_id: str, secret_access_key: str) -> None:
        __session = boto3.Session(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region,
        )

        self.__client = __session.client("cloudfront")

    def __sanitize_name(self, name: str) -> str:
        """
        Takes the original name and returns an API compliant naming.
        """

        return name.lower().replace(".", "-").replace(" ", "-")

    def get_cache_policy(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find a cache policy by its name.
        """

        response = self.__client.list_cache_policies(Type="custom")
        policy_items = response["CachePolicyList"].get("Items", [])

        for item in policy_items:
            policy = cast(Dict[str, Dict[str, Any]], item["CachePolicy"])
            if policy["CachePolicyConfig"]["Name"] == self.__sanitize_name(name):
                return policy

        return None

    def create_cache_policy(
        self,
        name: str,
        min_ttl: int,
        default_ttl: int,
        max_ttl: int,
    ) -> Dict[str, Any]:
        """
        Create a new cache policy.
        """

        response = self.__client.create_cache_policy(
            CachePolicyConfig={
                "Name": self.__sanitize_name(name),
                "Comment": f"CloudFront cache policy for {name}.",
                "DefaultTTL": default_ttl,
                "MaxTTL": max_ttl,
                "MinTTL": min_ttl,
                "ParametersInCacheKeyAndForwardedToOrigin": {
                    "EnableAcceptEncodingGzip": True,
                    "EnableAcceptEncodingBrotli": True,
                    "HeadersConfig": {
                        "HeaderBehavior": "whitelist",
                        "Headers": {
                            "Quantity": 1,
                            "Items": [
                                "Origin",
                            ],
                        },
                    },
                    "CookiesConfig": {
                        "CookieBehavior": "none",
                    },
                    "QueryStringsConfig": {
                        "QueryStringBehavior": "all",
                    },
                },
            }
        )

        return cast(Dict[str, Any], response["CachePolicy"])

    def get_origin_request_policy(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find an origin request policy by its name.
        """

        response = self.__client.list_origin_request_policies(Type="custom")
        policy_items = response["OriginRequestPolicyList"].get("Items", [])

        for item in policy_items:
            policy = cast(Dict[str, Any], item["OriginRequestPolicy"])
            if policy["OriginRequestPolicyConfig"]["Name"] == self.__sanitize_name(name):
                return policy

        return None

    def create_origin_request_policy(self, name: str) -> Dict[str, Any]:
        """
        Create an origin request policy.
        """

        response = self.__client.create_origin_request_policy(
            OriginRequestPolicyConfig={
                "Name": self.__sanitize_name(name),
                "Comment": f"CloudFront origin request policy for {name}.",
                "HeadersConfig": {
                    "HeaderBehavior": "whitelist",
                    "Headers": {
                        "Quantity": 1,
                        "Items": [
                            "Origin",
                        ],
                    },
                },
                "CookiesConfig": {
                    "CookieBehavior": "none",
                },
                "QueryStringsConfig": {
                    "QueryStringBehavior": "all",
                },
            }
        )

        return cast(Dict[str, Any], response["OriginRequestPolicy"])

    def get_response_headers_policy(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find a response headers policy by its name.
        """

        response = self.__client.list_response_headers_policies(Type="custom")
        policy_items = response["ResponseHeadersPolicyList"].get("Items", [])

        for item in policy_items:
            policy = cast(Dict[str, Any], item["ResponseHeadersPolicy"])
            if policy["ResponseHeadersPolicyConfig"]["Name"] == self.__sanitize_name(name):
                return policy

        return None

    def create_response_headers_policy(self, name: str) -> Dict[str, Any]:
        """
        Create a response headers policy.
        """

        response = self.__client.create_response_headers_policy(
            ResponseHeadersPolicyConfig={
                "Name": self.__sanitize_name(name),
                "Comment": f"CloudFront response headers policy for {name}.",
                "CorsConfig": {
                    "OriginOverride": True,
                    "AccessControlAllowCredentials": False,
                    "AccessControlMaxAgeSec": 2592000,  # 30 days
                    "AccessControlAllowOrigins": {
                        "Quantity": 1,
                        "Items": [
                            "*",
                        ],
                    },
                    "AccessControlAllowHeaders": {
                        "Quantity": 1,
                        "Items": [
                            "*",
                        ],
                    },
                    "AccessControlAllowMethods": {
                        "Quantity": 1,
                        "Items": [
                            "ALL",
                        ],
                    },
                },
            }
        )

        return cast(Dict[str, Any], response["ResponseHeadersPolicy"])

    def get_distribution(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Finds a CloudFront distribution by its domain name.
        """

        response = self.__client.list_distributions()
        distribution_items = response["DistributionList"].get("Items", [])

        for item in distribution_items:
            distribution = cast(Dict[str, Any], item)
            if distribution["DomainName"] == domain:
                return distribution

        return None

    def create_distribution(
        self,
        domain: str,
        cache_policy_id: str,
        origin_request_policy_id: str,
        response_headers_policy_id: str,
        alias: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new CloudFront distribution.
        """

        if alias is None:
            alias = dict()

        config: Dict[str, Any] = {
            "Enabled": True,
            "Staging": False,
            "IsIPV6Enabled": True,
            "CallerReference": str(uuid4()),
            "Comment": f"Distribution config for {domain}",
            "ViewerCertificate": {
                "CloudFrontDefaultCertificate": len(alias) == 0,
                "SSLSupportMethod": "sni-only" if alias else "static-ip",
            },
            "Restrictions": {
                "GeoRestriction": {
                    "Quantity": 0,
                    "RestrictionType": "none",
                }
            },
            "DefaultCacheBehavior": {
                "TargetOriginId": domain,
                "Compress": True,
                "ViewerProtocolPolicy": "redirect-to-https",
                "CachePolicyId": cache_policy_id,
                "OriginRequestPolicyId": origin_request_policy_id,
                "ResponseHeadersPolicyId": response_headers_policy_id,
                "AllowedMethods": {
                    "Quantity": 2,
                    "Items": [
                        "GET",
                        "HEAD",
                    ],
                    "CachedMethods": {
                        "Quantity": 2,
                        "Items": [
                            "GET",
                            "HEAD",
                        ],
                    },
                },
            },
            "Origins": {
                "Quantity": 1,
                "Items": [
                    {
                        "Id": domain,
                        "DomainName": domain,
                        "CustomOriginConfig": {
                            "HTTPPort": 80,
                            "HTTPSPort": 443,
                            "OriginProtocolPolicy": "match-viewer",
                            "OriginSslProtocols": {
                                "Quantity": 3,
                                "Items": [
                                    "TLSv1",
                                    "TLSv1.1",
                                    "TLSv1.2",
                                ],
                            },
                            "OriginReadTimeout": 30,
                            "OriginKeepaliveTimeout": 5,
                        },
                    },
                ],
            },
        }

        if (alias_domain := alias.get("domain")) is not None:
            config["Aliases"] = {"Items": [alias_domain]}

        if (arn := alias.get("certificate_arn")) is not None:
            config["ViewerCertificate"]["ACMCertificateArn"] = arn

        response = self.__client.create_distribution(DistributionConfig=config)
        return cast(Dict[str, Any], response["Distribution"])
