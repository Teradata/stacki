import asyncio
from functools import wraps
from typing import Callable, Dict, Any


def map_kwargs(mappings: Dict) -> Callable:
	def inner(func: Callable) -> Callable:
		def do_mapping(kwargs: Dict) -> Dict:
			mapped_kwargs = {}
			for key, value in kwargs.items():
				if key in mappings:
					mapped_kwargs[mappings[key]] = value
				else:
					mapped_kwargs[key] = value
			return mapped_kwargs

		if asyncio.iscoroutinefunction(func):
			@wraps(func)
			async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
				return await func(*args, **do_mapping(kwargs))

			return async_wrapper

		@wraps(func)
		def wrapper(*args: Any, **kwargs: Any) -> Any:
			return func(*args, **do_mapping(kwargs))

		return wrapper
	return inner
