"""Classify a social post receipt without turning a submission into a publication."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PublicationReceipt:
    state: str
    public_url: str | None
    platform_id: str | None


def classify(post: dict[str, Any], network: str = "tiktok") -> PublicationReceipt:
    providers = [p for p in post.get("providers", []) if p.get("network") == network]
    if len(providers) != 1:
        return PublicationReceipt("UNVERIFIED", None, None)

    provider = providers[0]
    status = provider.get("status")
    public_url = provider.get("publicUrl")
    platform_id = provider.get("id")

    if status == "PUBLISHED" and public_url and platform_id:
        return PublicationReceipt("PUBLISHED", public_url, str(platform_id))
    if status == "ERROR":
        return PublicationReceipt("FAILED", None, None)
    return PublicationReceipt("PENDING", None, None)


if __name__ == "__main__":
    pending = {"providers": [{"network": "tiktok", "status": "AWAITING_CONFIRMATION",
                              "detailedStatus": "Published:7689933063992379406"}]}
    confirmed = {"providers": [{"network": "tiktok", "status": "PUBLISHED",
                                "id": "7689933131448700173",
                                "publicUrl": "https://www.tiktok.com/@builditsmaller/video/7689933131448700173"}]}
    assert classify(pending).state == "PENDING"
    assert classify(pending).public_url is None
    assert classify(confirmed).state == "PUBLISHED"
    assert classify(confirmed).platform_id == "7689933131448700173"
    assert classify({"providers": [{"network": "tiktok", "status": "ERROR"}]}).state == "FAILED"
    print("receipt gate: all checks passed")
