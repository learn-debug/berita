from newsagent.resilience.retry_policy import with_retry


def test_with_retry_decorator_exists() -> None:
    assert callable(with_retry)


def test_with_retry_default_params() -> None:
    decorator = with_retry()
    assert callable(decorator)


def test_with_retry_custom_params() -> None:
    decorator = with_retry(max_attempts=5, backoff=3.0)
    assert callable(decorator)
