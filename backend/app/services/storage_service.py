class StorageService:
    """S3-ready adapter for Phase 1 exports/assets without forcing AWS locally."""

    async def put_object(self, key: str, content: bytes, content_type: str) -> str:
        return f"s3://local-placeholder/{key}?content_type={content_type}&bytes={len(content)}"
