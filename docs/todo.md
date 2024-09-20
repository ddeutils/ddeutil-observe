# To Do

Planing the todo list on this project.

## Future Development

- [ ] Implement caching

  - with [`aiocache`](https://github.com/aio-libs/aiocache)
  - with [`diskcache`](https://github.com/grantjenks/python-diskcache)

    ```python
    from functools import wraps
    from hashlib import sha256
    import json
    from diskcache import Cache

    cache = Cache('cache_dir')  # Initialize the disk cache

    def cache_decorator(expire=3600):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create a unique cache key based on function name and parameters
                key = sha256(json.dumps((func.__name__, args, kwargs), sort_keys=True).encode()).hexdigest()
                data = cache.get(key)
                if not data:
                    data = func(*args, **kwargs)
                    cache.set(key, data, expire=expire)
                return data
            return wrapper
        return decorator
    ```

    ```python
    from fastapi import FastAPI
    from decorators import cache_decorator, cache
    from functools_caching import get_factorial

    app = FastAPI()


    # Define your data processing function with the caching decorator
    @app.post("/data")
    @cache_decorator(expire=3600)
    def get_data(body: dict):
        # performing operations

        processed_data = body

        # For demonstration, we're just returning the input
        return processed_data

    @app.get("/clear-cache")
    def clear_cache():
        cache.clear()
        return {"message": "Cache invalidated"}


    @app.get("/factorial/{num}")
    async def compute(num: int):
        result = await get_factorial(num)
        return {"param": num, "result": result}
    ```

    [Read more ...](https://rajansahu713.medium.com/caching-in-fastapi-applications-4dbd49027966)

## Best Practices References

- [Fast FastAPI boilerplate](https://github.com/igorbenav/FastAPI-boilerplate)
- [Fast HTMX with Sync SQLAlchemy](https://github.com/marty331/fasthtmx)
