from typing import Any, Dict, List

import click
from tutor import config
from tutor.commands.k8s import K8sContext

from .cloudfront import CloudFrontClient


@click.group(help="Commands for configuring CloudFront.")
@click.pass_context
def cloudfront(context: click.Context) -> None:
    """
    CloudFront command group.
    """

    context.obj = K8sContext(context.obj.root)


@cloudfront.command(help="Configure CloudFront resources")
@click.pass_obj
def create_cloudfront_resources(context: click.Context) -> None:
    """
    Create the necessary CloudFront resources on AWS for the instance.
    """

    loaded_config = config.load(context.root)  # type: ignore

    client = CloudFrontClient(
        region=str(loaded_config["CLOUDFRONT_AWS_REGION"]),
        access_key_id=str(loaded_config["CLOUDFRONT_AWS_ACCESS_KEY_ID"]),
        secret_access_key=str(loaded_config["CLOUDFRONT_AWS_SECRET_ACCESS_KEY"]),
    )

    cache_config: Dict[str, int] = loaded_config["CLOUDFRONT_CACHE_CONFIG"]  # type: ignore
    extra_config: List[dict] = loaded_config["CLOUDFRONT_EXTRA_DOMAINS"]  # type: ignore

    origins: Dict[str, Dict[str, Any]] = {
        f"{loaded_config['CLOUDFRONT_LMS_DOMAIN']}": {},
        f"{loaded_config['CLOUDFRONT_CMS_DOMAIN']}": {},
        **{
            x["domain"]: {"alias": {"domain": x["alias"], "certificate_arn": x["certificate_arn"]}}
            for x in extra_config
        },
    }

    for domain, origin_config in origins.items():
        request_policy_name = f"{domain}-origin-request-policy"
        if (request_policy := client.get_origin_request_policy(request_policy_name)) is None:
            request_policy = client.create_origin_request_policy(request_policy_name)

        response_policy_name = f"{domain}-response-headers-policy"
        if (response_policy := client.get_response_headers_policy(response_policy_name)) is None:
            response_policy = client.create_response_headers_policy(response_policy_name)

        cache_policy_name = f"{domain}-cache-policy"
        if (cache_policy := client.get_cache_policy(cache_policy_name)) is None:
            cache_policy = client.create_cache_policy(
                name=cache_policy_name,
                default_ttl=cache_config["default_ttl"],
                min_ttl=cache_config["min_ttl"],
                max_ttl=cache_config["max_ttl"],
            )

        if client.get_distribution(domain) is None:
            client.create_distribution(
                domain=domain,
                cache_policy_id=cache_policy["Id"],
                origin_request_policy_id=request_policy["Id"],
                response_headers_policy_id=response_policy["Id"],
                alias=origin_config.get("alias"),
            )

    click.echo(f"CloudFront is set up for {domain}")
