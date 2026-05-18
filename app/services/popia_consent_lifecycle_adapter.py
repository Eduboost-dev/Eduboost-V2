from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


def _value(kwargs: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if kwargs.get(name) is not None:
            return kwargs[name]
    return default


@dataclass
class POPIAConsentLifecycleAdapter:
    service: Any

    async def _call(self, method_names: tuple[str, ...], **kwargs: Any) -> Any:
        if "consent_version" not in kwargs and "privacy_notice_version" in kwargs:
            kwargs["consent_version"] = kwargs["privacy_notice_version"]
        if "privacy_notice_version" not in kwargs and "consent_version" in kwargs:
            kwargs["privacy_notice_version"] = kwargs["consent_version"]

        missing: list[str] = []
        for method_name in method_names:
            method = getattr(self.service, method_name, None)
            if method is None:
                missing.append(method_name)
                continue

            signature = inspect.signature(method)
            params = signature.parameters
            if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in params.values()):
                return await _maybe_await(method(**kwargs))

            filtered = {key: value for key, value in kwargs.items() if key in params}
            required = [
                name
                for name, param in params.items()
                if name != "self"
                and param.default is inspect.Parameter.empty
                and param.kind in {inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY}
                and name not in filtered
            ]

            positional: list[Any] = []
            for name in required:
                if name in {"guardian_id", "parent_id"}:
                    positional.append(_value(kwargs, "guardian_id", "parent_id", "actor_id"))
                elif name == "learner_id":
                    positional.append(kwargs.get("learner_id"))
                elif name in {"consent_version", "version"}:
                    positional.append(_value(kwargs, "consent_version", "privacy_notice_version"))
                elif name in {"actor_id", "user_id"}:
                    positional.append(_value(kwargs, "actor_id", "guardian_id"))
                else:
                    positional = []
                    break

            if required and positional and len(positional) == len(required):
                return await _maybe_await(method(*positional, **filtered))
            return await _maybe_await(method(**filtered))

        raise AttributeError(f"Canonical consent service lacks methods: {', '.join(missing)}")

    @staticmethod
    def _merge_positional(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
        names = ("guardian_id", "learner_id", "consent_version")
        merged = dict(kwargs)
        for name, value in zip(names, args):
            merged.setdefault(name, value)
        return merged

    async def grant(self, *args: Any, **kwargs: Any) -> Any:
        return await self._call(("grant", "grant_consent", "create_consent"), **self._merge_positional(args, kwargs))

    async def deny(self, *args: Any, **kwargs: Any) -> Any:
        merged = self._merge_positional(args, kwargs)
        if any(hasattr(self.service, name) for name in ("deny", "deny_consent")):
            return await self._call(("deny", "deny_consent"), **merged)
        merged.setdefault("reason", "denied")
        return await self._call(("revoke", "revoke_consent", "withdraw", "withdraw_consent"), **merged)

    async def withdraw(self, *args: Any, **kwargs: Any) -> Any:
        return await self._call(("withdraw", "withdraw_consent", "revoke", "revoke_consent"), **self._merge_positional(args, kwargs))

    async def revoke(self, *args: Any, **kwargs: Any) -> Any:
        return await self._call(("revoke", "revoke_consent", "withdraw", "withdraw_consent"), **self._merge_positional(args, kwargs))

    async def renew(self, *args: Any, **kwargs: Any) -> Any:
        merged = self._merge_positional(args, kwargs)
        if any(hasattr(self.service, name) for name in ("renew", "renew_consent")):
            return await self._call(("renew", "renew_consent"), **merged)
        return await self._call(("grant", "grant_consent"), **merged)

    async def erase(self, *args: Any, **kwargs: Any) -> Any:
        return await self._call(("erase", "erase_consent", "request_erasure", "delete_consent"), **self._merge_positional(args, kwargs))

    async def restrict_processing(self, *args: Any, **kwargs: Any) -> Any:
        return await self._call(("restrict_processing", "restrict", "request_restriction"), **self._merge_positional(args, kwargs))

    def __getattr__(self, name: str) -> Any:
        return getattr(self.service, name)
